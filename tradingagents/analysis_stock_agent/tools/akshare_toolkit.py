"""
AKShare数据工具包
提供A股市场数据获取功能
"""

import pandas as pd
import akshare as ak
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path
from langchain_core.tools import tool
from functools import lru_cache
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AStockToolkit:
    """A股数据工具包"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化工具包
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.cache_dir = Path(config.get("cache_dir", "./cache"))
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_ttl = config.get("cache_ttl", 3600)
        
    @tool
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_financial_statements(
        self,
        stock_code: str,
        report_type: str = "report",
        period: str = "年报"
    ) -> Dict[str, Any]:
        """
        获取财务报表数据
        
        Args:
            stock_code: 股票代码（6位数字）
            report_type: 报表类型 report/year/quarter
            period: 报告期类型
            
        Returns:
            包含资产负债表、利润表、现金流量表的字典
        """
        try:
            result = {}
            
            # 获取资产负债表
            balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=stock_code)
            if not balance_sheet.empty:
                # 获取最近3年数据
                balance_sheet = balance_sheet.head(12)  # 最近12个季度
                result["balance_sheet"] = balance_sheet.to_dict('records')
            
            # 获取利润表
            profit_sheet = ak.stock_profit_sheet_by_report_em(symbol=stock_code)
            if not profit_sheet.empty:
                profit_sheet = profit_sheet.head(12)
                result["profit_sheet"] = profit_sheet.to_dict('records')
            
            # 获取现金流量表
            cash_flow = ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)
            if not cash_flow.empty:
                cash_flow = cash_flow.head(12)
                result["cash_flow"] = cash_flow.to_dict('records')
                
            # 计算关键财务指标
            result["metrics"] = self._calculate_financial_metrics(
                balance_sheet, profit_sheet, cash_flow
            )
            
            return result
            
        except Exception as e:
            logger.error(f"获取财务报表失败: {e}")
            return {"error": str(e)}
    
    @tool
    def get_financial_indicators(self, stock_code: str) -> Dict[str, Any]:
        """
        获取财务分析指标
        
        Args:
            stock_code: 股票代码
            
        Returns:
            财务指标字典
        """
        try:
            # 获取财务分析指标
            df = ak.stock_financial_analysis_indicator(
                symbol=stock_code, 
                indicator="按年度"
            )
            
            if df.empty:
                return {"error": "无财务指标数据"}
            
            # 提取关键指标
            indicators = {}
            key_columns = [
                "净资产收益率", "总资产收益率", "销售净利率", 
                "销售毛利率", "资产负债率", "流动比率", "速动比率"
            ]
            
            for col in key_columns:
                if col in df.columns:
                    # 获取最近3年数据
                    indicators[col] = df[col].head(3).tolist()
            
            # 添加增长率指标
            if "营业总收入" in df.columns:
                revenue = df["营业总收入"].head(4).tolist()
                indicators["营收增长率"] = self._calculate_growth_rate(revenue)
            
            if "净利润" in df.columns:
                profit = df["净利润"].head(4).tolist()
                indicators["净利润增长率"] = self._calculate_growth_rate(profit)
            
            return indicators
            
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            return {"error": str(e)}
    
    @tool
    def get_industry_classification(self, stock_code: str) -> Dict[str, str]:
        """
        获取股票行业分类
        
        Args:
            stock_code: 股票代码
            
        Returns:
            行业分类信息
        """
        try:
            # 获取行业分类
            df = ak.stock_board_industry_cons_em(symbol="所有行业")
            
            # 查找股票所属行业
            stock_industry = {}
            for index, row in df.iterrows():
                if stock_code in str(row.get("成分股代码", "")):
                    stock_industry = {
                        "行业名称": row.get("板块名称", ""),
                        "行业代码": row.get("板块代码", ""),
                    }
                    break
            
            if not stock_industry:
                # 尝试获取申万行业分类
                sw_df = ak.sw_index_third_info()
                # 这里需要进一步匹配逻辑
                stock_industry = {"行业名称": "未分类", "行业代码": ""}
            
            return stock_industry
            
        except Exception as e:
            logger.error(f"获取行业分类失败: {e}")
            return {"error": str(e)}
    
    @tool
    def get_industry_comparison(
        self,
        industry_code: str,
        metrics: List[str] = None
    ) -> pd.DataFrame:
        """
        获取行业对比数据
        
        Args:
            industry_code: 行业代码
            metrics: 对比指标列表
            
        Returns:
            行业内公司对比数据
        """
        try:
            # 获取行业成分股
            df = ak.stock_board_industry_cons_em(symbol=industry_code)
            
            if df.empty:
                return pd.DataFrame()
            
            # 获取前10家公司
            top_companies = df.head(10)
            
            # 构建对比数据
            comparison_data = []
            for _, row in top_companies.iterrows():
                company_data = {
                    "股票代码": row["代码"],
                    "公司名称": row["名称"],
                    "市值": row.get("总市值", 0),
                    "PE": row.get("市盈率-动态", 0),
                    "PB": row.get("市净率", 0),
                }
                comparison_data.append(company_data)
            
            return pd.DataFrame(comparison_data)
            
        except Exception as e:
            logger.error(f"获取行业对比数据失败: {e}")
            return pd.DataFrame()
    
    @tool
    def get_stock_valuation(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股票估值数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            估值指标字典
        """
        try:
            # 获取实时行情数据
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df["代码"] == stock_code]
            
            if stock_data.empty:
                return {"error": "未找到股票数据"}
            
            valuation = {
                "当前价格": float(stock_data["最新价"].iloc[0]),
                "PE_动态": float(stock_data["市盈率-动态"].iloc[0]) if "市盈率-动态" in stock_data.columns else None,
                "PB": float(stock_data["市净率"].iloc[0]) if "市净率" in stock_data.columns else None,
                "总市值": float(stock_data["总市值"].iloc[0]) if "总市值" in stock_data.columns else None,
                "流通市值": float(stock_data["流通市值"].iloc[0]) if "流通市值" in stock_data.columns else None,
            }
            
            # 计算PR值（PE/ROE）
            if valuation["PE_动态"]:
                # 需要获取ROE数据
                indicators = self.get_financial_indicators(stock_code)
                if "净资产收益率" in indicators and indicators["净资产收益率"]:
                    latest_roe = indicators["净资产收益率"][0]
                    if latest_roe and latest_roe > 0:
                        valuation["PR值"] = valuation["PE_动态"] / latest_roe
            
            return valuation
            
        except Exception as e:
            logger.error(f"获取估值数据失败: {e}")
            return {"error": str(e)}
    
    @tool 
    def get_shareholder_structure(self, stock_code: str) -> Dict[str, Any]:
        """
        获取股东结构数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股东结构信息
        """
        try:
            result = {}
            
            # 获取股东人数
            shareholder_num = ak.stock_zh_a_gdhs(symbol=stock_code)
            if not shareholder_num.empty:
                result["股东人数变化"] = shareholder_num.head(4).to_dict('records')
            
            # 获取十大流通股东
            top_holders = ak.stock_circulate_stock_holder(
                symbol=stock_code,
                period="最新"
            )
            if not top_holders.empty:
                result["十大流通股东"] = top_holders.to_dict('records')
            
            # 分析股东结构特点
            result["股东特点"] = self._analyze_shareholder_structure(result)
            
            return result
            
        except Exception as e:
            logger.error(f"获取股东结构失败: {e}")
            return {"error": str(e)}
    
    @tool
    def get_dividend_history(self, stock_code: str) -> List[Dict]:
        """
        获取分红历史
        
        Args:
            stock_code: 股票代码
            
        Returns:
            历史分红记录
        """
        try:
            df = ak.stock_dividend_cninfo(
                symbol=stock_code,
                start_date="2019-01-01",
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            if df.empty:
                return []
            
            # 计算股息率等指标
            dividends = df.to_dict('records')
            for div in dividends:
                if "每股派息" in div and "股权登记日收盘价" in div:
                    div["股息率"] = (div["每股派息"] / div["股权登记日收盘价"]) * 100
            
            return dividends
            
        except Exception as e:
            logger.error(f"获取分红历史失败: {e}")
            return []
    
    @tool
    def get_stock_info(self, stock_code: str) -> Dict[str, str]:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票基本信息
        """
        try:
            # 获取A股代码名称映射
            df = ak.stock_info_a_code_name()
            stock_info = df[df["code"] == stock_code]
            
            if stock_info.empty:
                return {"error": "未找到股票信息"}
            
            return {
                "股票代码": stock_code,
                "股票名称": stock_info["name"].iloc[0],
            }
            
        except Exception as e:
            logger.error(f"获取股票信息失败: {e}")
            return {"error": str(e)}
    
    def _calculate_financial_metrics(
        self,
        balance_sheet: pd.DataFrame,
        profit_sheet: pd.DataFrame,
        cash_flow: pd.DataFrame
    ) -> Dict[str, Any]:
        """计算关键财务指标"""
        metrics = {}
        
        try:
            # ROE计算
            if not profit_sheet.empty and not balance_sheet.empty:
                if "净利润" in profit_sheet.columns and "股东权益合计" in balance_sheet.columns:
                    net_profit = profit_sheet["净利润"].iloc[0]
                    equity = balance_sheet["股东权益合计"].iloc[0]
                    if equity and equity > 0:
                        metrics["ROE"] = (net_profit / equity) * 100
            
            # 资产负债率
            if not balance_sheet.empty:
                if "负债合计" in balance_sheet.columns and "资产总计" in balance_sheet.columns:
                    debt = balance_sheet["负债合计"].iloc[0]
                    assets = balance_sheet["资产总计"].iloc[0]
                    if assets and assets > 0:
                        metrics["资产负债率"] = (debt / assets) * 100
            
            # 现金流质量
            if not cash_flow.empty and not profit_sheet.empty:
                if "经营活动产生的现金流量净额" in cash_flow.columns and "净利润" in profit_sheet.columns:
                    operating_cf = cash_flow["经营活动产生的现金流量净额"].iloc[0]
                    net_profit = profit_sheet["净利润"].iloc[0]
                    if net_profit and net_profit > 0:
                        metrics["现金流质量"] = operating_cf / net_profit
            
        except Exception as e:
            logger.error(f"计算财务指标失败: {e}")
        
        return metrics
    
    def _calculate_growth_rate(self, values: List[float]) -> List[float]:
        """计算增长率"""
        growth_rates = []
        for i in range(1, len(values)):
            if values[i] and values[i] != 0:
                rate = ((values[i-1] - values[i]) / abs(values[i])) * 100
                growth_rates.append(round(rate, 2))
        return growth_rates
    
    def _analyze_shareholder_structure(self, shareholder_data: Dict) -> Dict[str, str]:
        """分析股东结构特点"""
        analysis = {}
        
        # 分析股东人数变化趋势
        if "股东人数变化" in shareholder_data:
            changes = shareholder_data["股东人数变化"]
            if len(changes) >= 2:
                latest = changes[0].get("股东人数", 0)
                previous = changes[1].get("股东人数", 0)
                if previous > 0:
                    change_rate = ((latest - previous) / previous) * 100
                    if change_rate < -10:
                        analysis["股东集中度"] = "明显集中"
                    elif change_rate > 10:
                        analysis["股东集中度"] = "明显分散"
                    else:
                        analysis["股东集中度"] = "相对稳定"
        
        # 分析机构持股情况
        if "十大流通股东" in shareholder_data:
            holders = shareholder_data["十大流通股东"]
            institution_count = 0
            for holder in holders:
                holder_name = holder.get("股东名称", "")
                if any(keyword in holder_name for keyword in ["基金", "保险", "社保", "信托", "资管"]):
                    institution_count += 1
            
            if institution_count >= 5:
                analysis["机构持股"] = "机构重仓"
            elif institution_count >= 2:
                analysis["机构持股"] = "机构关注"
            else:
                analysis["机构持股"] = "散户为主"
        
        return analysis

    def get_all_tools(self) -> List:
        """获取所有工具列表"""
        return [
            self.get_financial_statements,
            self.get_financial_indicators,
            self.get_industry_classification,
            self.get_industry_comparison,
            self.get_stock_valuation,
            self.get_shareholder_structure,
            self.get_dividend_history,
            self.get_stock_info,
        ]
