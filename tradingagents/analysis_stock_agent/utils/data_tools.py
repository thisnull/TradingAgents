"""
A股数据工具模块

提供与A股数据同步服务API的集成，包括股票基础信息、财务数据、
行情数据、行业数据等的获取和处理功能。
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import pandas as pd


logger = logging.getLogger(__name__)


class AShareDataTools:
    """A股数据API工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("a_share_api_url", "http://localhost:8000/api/v1")
        self.api_key = config.get("a_share_api_key", "")
        self.timeout = config.get("a_share_api_timeout", 300)
        self.retry_times = config.get("a_share_api_retry_times", 3)
        
        # 创建session以复用连接
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发起API请求的通用方法
        
        Args:
            endpoint: API端点
            params: 查询参数
            method: HTTP方法
            data: 请求体数据
            
        Returns:
            API响应数据
            
        Raises:
            Exception: API请求失败时抛出异常
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.retry_times):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == "POST":
                    response = self.session.post(url, params=params, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                result = response.json()
                
                if result.get("success", False):
                    return result
                else:
                    logger.warning(f"API returned error: {result.get('message', 'Unknown error')}")
                    if attempt == self.retry_times - 1:
                        raise Exception(f"API error: {result.get('message', 'Unknown error')}")
                        
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_times - 1:
                    raise Exception(f"API request failed after {self.retry_times} attempts: {str(e)}")
                    
        return {}
    
    def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基础信息
        
        Args:
            symbol: 股票代码 (e.g., "000001")
            
        Returns:
            股票基础信息字典
        """
        try:
            result = self._make_request(f"market/{symbol}")
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Failed to get stock basic info for {symbol}: {str(e)}")
            return {}
    
    def get_stocks_list(self, market: Optional[str] = None, 
                       status: str = "normal", 
                       limit: int = 100, 
                       offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取股票列表
        
        Args:
            market: 市场类型 (main/gem/star/bj)
            status: 交易状态 (normal/suspend/delist)
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            股票列表
        """
        params = {
            "status": status,
            "limit": limit,
            "offset": offset
        }
        if market:
            params["market"] = market
            
        try:
            result = self._make_request("market/basic", params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get stocks list: {str(e)}")
            return []
    
    def get_financial_reports(self, symbol: str, 
                            report_type: str = "A",
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        
        Args:
            symbol: 股票代码
            report_type: 报告类型 (Q1/Q2/Q3/A)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回数量
            
        Returns:
            财务报表列表
        """
        params = {
            "symbols": symbol,
            # "report_type": report_type,
            "limit": limit
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        try:
            result = self._make_request("financial/reports", params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get financial reports for {symbol}: {str(e)}")
            return []
    
    def get_latest_financial_report(self, symbol: str, 
                                  report_type: str = "A") -> Dict[str, Any]:
        """
        获取最新财务报表
        
        Args:
            symbol: 股票代码
            report_type: 报告类型
            
        Returns:
            最新财务报表数据
        """
        params = {
            "symbols": symbol,
            "report_type": report_type,
            "limit": 1
        }
        
        try:
            result = self._make_request("financial/reports/latest", params=params)
            data = result.get("data", [])
            return data[0] if data else {}
        except Exception as e:
            logger.error(f"Failed to get latest financial report for {symbol}: {str(e)}")
            return {}
    
    def get_financial_summary(self, symbol: str, years: int = 3) -> Dict[str, Any]:
        """
        获取财务摘要
        
        Args:
            symbol: 股票代码
            years: 历史年数
            
        Returns:
            财务摘要数据
        """
        try:
            result = self._make_request(f"financial/summary/{symbol}", 
                                      params={"years": years})
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Failed to get financial summary for {symbol}: {str(e)}")
            return {}
    
    def get_daily_quotes(self, symbol: str,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        limit: int = 10000) -> List[Dict[str, Any]]:
        """
        获取日线行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量
            
        Returns:
            日线行情列表
        """
        params = {
            "symbols": symbol,
            "limit": limit
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        try:
            result = self._make_request("market/quotes/daily", params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get daily quotes for {symbol}: {str(e)}")
            return []
    
    def get_shenwan_industry_info(self, level: int = 1,
                                 industry_codes: Optional[List[str]] = None,
                                 status: str = "active") -> List[Dict[str, Any]]:
        """
        获取申万行业信息
        
        Args:
            level: 行业级别 (1/2/3)
            industry_codes: 行业代码列表
            status: 状态筛选
            
        Returns:
            申万行业信息列表
        """
        if level == 1:
            endpoint = "sw-industries/first"
        elif level == 2:
            endpoint = "sw-industries/second"
        elif level == 3:
            endpoint = "sw-industries/third"
        else:
            raise ValueError("Industry level must be 1, 2, or 3")
        
        params = {"status": status}
        if industry_codes:
            params["industry_codes"] = ",".join(industry_codes)
            
        try:
            result = self._make_request(endpoint, params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get SW industry info: {str(e)}")
            return []
    
    def get_industry_constituents(self, industry_codes: List[str],
                                 levels: Optional[List[int]] = None,
                                 status: str = "active") -> List[Dict[str, Any]]:
        """
        获取行业成分股
        
        Args:
            industry_codes: 行业代码列表
            levels: 行业级别列表
            status: 状态筛选
            
        Returns:
            行业成分股列表
        """
        params = {
            "industry_codes": ",".join(industry_codes),
            "status": status
        }
        if levels:
            params["levels"] = ",".join(map(str, levels))
            
        try:
            result = self._make_request("sw-industries/constituents", params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get industry constituents: {str(e)}")
            return []
    
    def get_stock_industry_hierarchy(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票行业层级信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            行业层级信息
        """
        try:
            result = self._make_request(f"sw-industries/hierarchy/{symbol}")
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Failed to get industry hierarchy for {symbol}: {str(e)}")
            return {}
    
    def search_industries(self, keyword: str,
                         levels: str = "1,2,3",
                         exact_match: bool = False) -> List[Dict[str, Any]]:
        """
        搜索申万行业
        
        Args:
            keyword: 搜索关键词
            levels: 搜索级别
            exact_match: 是否精确匹配
            
        Returns:
            搜索结果列表
        """
        params = {
            "keyword": keyword,
            "levels": levels,
            "exact_match": exact_match
        }
        
        try:
            result = self._make_request("sw-industries/search", params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to search industries: {str(e)}")
            return []
    
    def get_index_info(self, index_codes: Optional[List[str]] = None,
                      market: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取指数信息
        
        Args:
            index_codes: 指数代码列表
            market: 市场类型
            
        Returns:
            指数信息列表
        """
        params = {}
        if index_codes:
            params["index_codes"] = ",".join(index_codes)
        if market:
            params["market"] = market
            
        try:
            result = self._make_request("market/indices", params=params)
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get index info: {str(e)}")
            return []
    
    def get_index_constituents(self, index_code: str) -> List[Dict[str, Any]]:
        """
        获取指数成分股
        
        Args:
            index_code: 指数代码
            
        Returns:
            成分股列表
        """
        try:
            result = self._make_request(f"market/indices/{index_code}/constituents")
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get index constituents for {index_code}: {str(e)}")
            return []
    
    def initialize_stock_data(self, symbol: str,
                            start_date: str = "1970-01-01",
                            end_date: Optional[str] = None,
                            force_update: bool = False) -> Dict[str, Any]:
        """
        初始化股票数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            force_update: 是否强制更新
            
        Returns:
            初始化结果
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            
        data = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "force_update": force_update
        }
        
        try:
            result = self._make_request(f"initialization/stocks/{symbol}/initialize",
                                      method="POST", data=data)
            return result
        except Exception as e:
            logger.error(f"Failed to initialize stock data for {symbol}: {str(e)}")
            return {}
    
    def check_rate_limit(self, symbol: str) -> Dict[str, Any]:
        """
        检查速率限制状态
        
        Args:
            symbol: 股票代码
            
        Returns:
            速率限制状态
        """
        try:
            result = self._make_request(f"initialization/stocks/{symbol}/rate-limit")
            return result
        except Exception as e:
            logger.error(f"Failed to check rate limit for {symbol}: {str(e)}")
            return {}


class DataProcessor:
    """数据处理工具类"""
    
    @staticmethod
    def clean_financial_data(financial_reports: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        清理和格式化财务数据
        
        Args:
            financial_reports: 财务报表列表
            
        Returns:
            处理后的DataFrame
        """
        if not financial_reports:
            return pd.DataFrame()
            
        df = pd.DataFrame(financial_reports)
        
        # 转换数值列
        numeric_columns = [
            'total_revenue', 'operating_revenue', 'net_profit', 'total_assets',
            'total_liabilities', 'total_equity', 'roa', 'roe', 'eps'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 转换日期列
        date_columns = ['report_date', 'announce_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 按报告日期排序
        if 'report_date' in df.columns:
            df = df.sort_values('report_date', ascending=False)
        
        return df
    
    @staticmethod
    def calculate_growth_rates(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        计算增长率
        
        Args:
            df: 财务数据DataFrame
            columns: 需要计算增长率的列
            
        Returns:
            包含增长率的DataFrame
        """
        for col in columns:
            if col in df.columns:
                growth_col = f"{col}_growth_rate"
                df[growth_col] = df[col].pct_change(periods=-1) * 100
        
        return df
    
    @staticmethod
    def calculate_financial_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算常用财务比率
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            财务比率字典
        """
        ratios = {}
        
        try:
            # 获取基础数据
            revenue = float(financial_data.get('total_revenue', 0))
            net_profit = float(financial_data.get('net_profit', 0))
            total_assets = float(financial_data.get('total_assets', 0))
            total_equity = float(financial_data.get('total_equity', 0))
            total_liabilities = float(financial_data.get('total_liabilities', 0))
            
            # 计算比率
            if revenue > 0:
                ratios['net_profit_margin'] = (net_profit / revenue) * 100
            
            if total_assets > 0:
                ratios['roa'] = (net_profit / total_assets) * 100
                ratios['asset_liability_ratio'] = (total_liabilities / total_assets) * 100
            
            if total_equity > 0:
                ratios['roe'] = (net_profit / total_equity) * 100
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating financial ratios: {str(e)}")
        
        return ratios
    
    if __name__ == "__main__":
        data_tools = AShareDataTools({})
        # print(data_tools.initialize_stock_data("002594"))
        # print(data_tools.get_financial_reports("002594"))
        print(data_tools.get_financial_reports("600900"))
        # print(data_tools.get_stock_basic_info("002594"))
        # print(data_tools.get_financial_reports("002594"))
        # print(data_tools.get_latest_financial_report("002594"))
        # print(data_tools.get_financial_summary("002594"))
        # print(data_tools.get_daily_quotes("600900"))
        # print(data_tools.get_shenwan_industry_info())
        # print(data_tools.get_industry_constituents(["002594"]))