"""
财务指标分析Agent

专门负责A股公司的财务指标分析，包括盈利能力、偿债能力、运营能力、
现金流、成长性和股东回报等6个维度的全面分析。
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ..utils.data_tools import AShareDataTools, DataProcessor
from ..utils.mcp_tools import MCPToolsWrapper
from ..utils.calculation_utils import FinancialCalculator, RiskCalculator
from ..utils.state_models import AnalysisStage, AnalysisDepth
from ..utils.sequential_tool_executor import (
    SequentialToolExecutor, 
    FINANCIAL_ANALYSIS_SEQUENCE
)
from ..prompts.financial_prompts import (
    FINANCIAL_ANALYSIS_SYSTEM_PROMPT,
    FINANCIAL_ANALYSIS_USER_PROMPT,
    FINANCIAL_HEALTH_SCORING_CRITERIA,
    FINANCIAL_ANALYSIS_REPORT_TEMPLATE
)


logger = logging.getLogger(__name__)


def create_financial_analyst(llm, toolkit, config):
    """
    创建财务指标分析Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 工具集
        config: 配置字典
        
    Returns:
        财务分析Agent节点函数
    """
    
    # 初始化数据工具
    data_tools = AShareDataTools(config)
    mcp_tools = MCPToolsWrapper(config) if config.get("mcp_tools_enabled") else None
    
    # 创建财务分析工具
    @tool
    def get_financial_data(stock_code: str, years: int = 5) -> Dict[str, Any]:
        """
        获取股票财务数据（增强版：支持多年历史数据趋势分析+分红数据）
        
        Args:
            stock_code: 股票代码
            years: 历史年数，增加到5年以支持更好的趋势分析
            
        Returns:
            包含多年历史数据和分红信息的财务数据字典
        """
        try:
            logger.info(f"Getting comprehensive financial data for {stock_code} (last {years} years)")
            
            # 获取股票基础信息
            basic_info = data_tools.get_stock_basic_info(stock_code)
            
            # 获取最新财务报告
            latest_report = data_tools.get_latest_financial_report(stock_code, "A")
            
            # 计算起始日期 - 获取过去N年的数据
            from datetime import datetime, timedelta
            current_year = datetime.now().year
            start_year = current_year - years
            start_date = f"{start_year}-01-01"
            end_date = f"{current_year}-12-31"
            
            # 获取历史财务报告 - 使用日期范围和更大的limit确保获取完整历史数据
            historical_reports = data_tools.get_financial_reports(
                stock_code, 
                start_date=start_date,
                end_date=end_date,
                limit=years * 4  # 每年可能有季报+年报，所以乘以4确保获取完整数据
            )
            
            # 获取年报数据（用于趋势分析）
            annual_reports = []
            if historical_reports:
                annual_reports = [report for report in historical_reports if report.get('report_type') == 'A']
                # 按年份排序，最新的在前
                annual_reports.sort(key=lambda x: x.get('report_date', ''), reverse=True)
            
            # 获取财务摘要（支持指定年数）
            financial_summary = data_tools.get_financial_summary(stock_code, years)
            
            # 🆕 获取分红送配数据（多年历史）
            dividend_details = data_tools.get_dividend_details(
                stock_code,
                start_date=start_date,
                end_date=end_date,
                limit=years * 2  # 每年可能有多次分红
            )
            
            # 获取最新分红信息
            latest_dividend = data_tools.get_latest_dividend_info(stock_code)
            
            # 记录获取到的数据统计
            logger.info(f"Retrieved data summary for {stock_code}:")
            logger.info(f"  - Total historical reports: {len(historical_reports) if historical_reports else 0}")
            logger.info(f"  - Annual reports: {len(annual_reports) if annual_reports else 0}")
            logger.info(f"  - Dividend records: {len(dividend_details) if dividend_details else 0}")
            logger.info(f"  - Date range: {start_date} to {end_date}")
            
            return {
                "stock_code": stock_code,
                "basic_info": basic_info,
                "latest_report": latest_report,
                "financial_reports": historical_reports,  # 完整历史数据
                "annual_reports": annual_reports,  # 年报数据（用于趋势分析）
                "financial_summary": financial_summary,
                "dividend_details": dividend_details,  # 🆕 分红送配历史数据
                "latest_dividend": latest_dividend,  # 🆕 最新分红信息
                "data_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "years_requested": years,
                    "total_reports": len(historical_reports) if historical_reports else 0,
                    "annual_reports": len(annual_reports) if annual_reports else 0,
                    "dividend_records": len(dividend_details) if dividend_details else 0
                },
                "data_source": "A股数据API（多年历史数据+分红信息）"
            }
            
        except Exception as e:
            logger.error(f"Error getting financial data for {stock_code}: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_financial_ratios(financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算财务比率指标（增强版：支持多年趋势分析）
        
        Args:
            financial_data: 包含多年历史数据的财务数据
            
        Returns:
            包含趋势分析的财务比率字典
        """
        try:
            logger.info("Calculating comprehensive financial ratios with trend analysis")
            
            if "latest_report" not in financial_data or not financial_data["latest_report"]:
                return {"error": "No latest financial report available"}
            
            latest_report = financial_data["latest_report"]
            financial_reports = financial_data.get("financial_reports", [])
            annual_reports = financial_data.get("annual_reports", [])
            
            # 记录可用数据统计
            logger.info(f"Available data for ratio calculation:")
            logger.info(f"  - Latest report: {'Yes' if latest_report else 'No'}")
            logger.info(f"  - Total reports: {len(financial_reports)}")
            logger.info(f"  - Annual reports: {len(annual_reports)}")
            
            # 计算各类财务比率
            profitability = FinancialCalculator.calculate_profitability_ratios(latest_report)
            liquidity = FinancialCalculator.calculate_liquidity_ratios(latest_report)
            leverage = FinancialCalculator.calculate_leverage_ratios(latest_report)
            efficiency = FinancialCalculator.calculate_efficiency_ratios(latest_report)
            cashflow = FinancialCalculator.calculate_cashflow_ratios(latest_report)
            
            # 增强的成长性指标计算（使用年报数据进行多年趋势分析）
            growth = {}
            trend_analysis = {}
            dividend_ratios = {}  # 新增：分红相关比率
            
            # 计算分红相关比率
            dividend_ratios = _calculate_dividend_ratios(financial_data)
            
            if annual_reports and len(annual_reports) >= 2:
                # 使用年报数据进行趋势分析
                growth = FinancialCalculator.calculate_growth_rates(annual_reports)
                logger.info(f"Calculated growth rates from {len(annual_reports)} annual reports")
                
                # 多年趋势分析
                trend_analysis = _analyze_multi_year_trends(annual_reports)
                logger.info(f"Generated multi-year trend analysis")
            elif financial_reports and len(financial_reports) >= 2:
                # 如果年报数据不足，使用所有历史报告
                growth = FinancialCalculator.calculate_growth_rates(financial_reports)
                logger.info(f"Calculated growth rates from {len(financial_reports)} total reports")
            else:
                logger.warning("Insufficient historical data for growth rate calculation")
                growth = {"note": "需要至少2年的历史数据进行趋势分析"}
            
            return {
                "profitability_ratios": profitability,
                "liquidity_ratios": liquidity,
                "leverage_ratios": leverage,
                "efficiency_ratios": efficiency,
                "cashflow_ratios": cashflow,
                "growth_ratios": growth,
                "dividend_ratios": dividend_ratios,  # 新增：分红比率
                "trend_analysis": trend_analysis,  # 新增：多年趋势分析
                "data_quality": {
                    "annual_reports_count": len(annual_reports),
                    "total_reports_count": len(financial_reports),
                    "trend_analysis_available": len(annual_reports) >= 3,
                    "growth_analysis_available": len(annual_reports) >= 2 or len(financial_reports) >= 2,
                    "dividend_data_available": dividend_ratios.get("dividend_data_available", False)
                },
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_multi_year_trends(annual_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析多年财务趋势
        
        Args:
            annual_reports: 年报数据列表（按年份排序）
            
        Returns:
            趋势分析结果
        """
        try:
            if len(annual_reports) < 3:
                return {"note": "需要至少3年数据进行趋势分析"}
            
            # 取前5年的数据进行分析
            recent_reports = annual_reports[:5]
            
            trends = {
                "revenue_trend": _calculate_trend(recent_reports, "total_revenue"),
                "profit_trend": _calculate_trend(recent_reports, "net_profit"),
                "asset_trend": _calculate_trend(recent_reports, "total_assets"),
                "roe_trend": _calculate_trend(recent_reports, "roe"),
                "debt_ratio_trend": _calculate_trend(recent_reports, "debt_to_asset_ratio")
            }
            
            # 综合趋势评估
            trends["overall_assessment"] = _assess_overall_trend(trends)
            trends["years_analyzed"] = len(recent_reports)
            trends["data_period"] = f"{recent_reports[-1].get('report_date', '')[:4]} - {recent_reports[0].get('report_date', '')[:4]}"
            
            return trends
            
        except Exception as e:
            logger.error(f"Error in multi-year trend analysis: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_trend(reports: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
        """计算指定字段的趋势"""
        try:
            values = []
            dates = []
            
            for report in reports:
                if field in report and report[field] is not None:
                    # 处理不同的数据类型
                    value = report[field]
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except:
                            continue
                    elif isinstance(value, (int, float)):
                        value = float(value)
                    else:
                        continue
                    
                    values.append(value)
                    dates.append(report.get('report_date', '')[:4])
            
            if len(values) < 2:
                return {"note": f"{field}数据不足"}
            
            # 计算趋势方向
            if len(values) >= 3:
                # 简单的趋势判断：比较最近值与最早值
                recent_avg = sum(values[:2]) / 2  # 最近2年平均值
                earlier_avg = sum(values[-2:]) / 2  # 较早2年平均值
                
                if recent_avg > earlier_avg * 1.1:  # 增长超过10%
                    trend_direction = "上升"
                elif recent_avg < earlier_avg * 0.9:  # 下降超过10%
                    trend_direction = "下降"
                else:
                    trend_direction = "稳定"
            else:
                if values[0] > values[1]:
                    trend_direction = "上升"
                elif values[0] < values[1]:
                    trend_direction = "下降"
                else:
                    trend_direction = "稳定"
            
            # 计算变化率
            if len(values) >= 2:
                change_rate = ((values[0] - values[-1]) / abs(values[-1])) * 100 if values[-1] != 0 else 0
            else:
                change_rate = 0
            
            return {
                "direction": trend_direction,
                "change_rate_percent": round(change_rate, 2),
                "latest_value": values[0] if values else None,
                "earliest_value": values[-1] if values else None,
                "data_points": len(values),
                "period": f"{dates[-1]}-{dates[0]}" if dates else ""
            }
            
        except Exception as e:
            return {"error": f"计算{field}趋势时出错: {str(e)}"}
    
    def _assess_overall_trend(trends: Dict[str, Any]) -> str:
        """综合评估整体趋势"""
        try:
            positive_trends = 0
            negative_trends = 0
            
            # 检查关键指标趋势
            key_indicators = ["revenue_trend", "profit_trend", "roe_trend"]
            
            for indicator in key_indicators:
                if indicator in trends and isinstance(trends[indicator], dict):
                    direction = trends[indicator].get("direction", "")
                    if direction == "上升":
                        positive_trends += 1
                    elif direction == "下降":
                        negative_trends += 1
            
            # 债务比率趋势的特殊处理（下降是好事）
            if "debt_ratio_trend" in trends and isinstance(trends["debt_ratio_trend"], dict):
                debt_direction = trends["debt_ratio_trend"].get("direction", "")
                if debt_direction == "下降":
                    positive_trends += 0.5
                elif debt_direction == "上升":
                    negative_trends += 0.5
            
            if positive_trends > negative_trends:
                return "整体向好"
            elif negative_trends > positive_trends:
                return "需要关注"
            else:
                return "表现稳定"
                
        except Exception:
            return "趋势分析需要更多数据"
    
    def _calculate_dividend_ratios(financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算分红相关比率"""
        try:
            dividend_details = financial_data.get("dividend_details", [])
            latest_dividend = financial_data.get("latest_dividend", {})
            latest_report = financial_data.get("latest_report", {})
            
            ratios = {
                "dividend_data_available": len(dividend_details) > 0 or bool(latest_dividend),
                "dividend_records_count": len(dividend_details)
            }
            
            if latest_dividend:
                # 股息率
                ratios["dividend_yield"] = float(latest_dividend.get("dividend_yield", 0))
                
                # 现金分红比例（每10股）
                ratios["cash_dividend_per_10_shares"] = float(latest_dividend.get("cash_dividend_ratio", 0))
                
                # 每股分红
                cash_dividend_ratio = float(latest_dividend.get("cash_dividend_ratio", 0))
                ratios["dividend_per_share"] = cash_dividend_ratio / 10 if cash_dividend_ratio > 0 else 0
                
                # 分红支付率（需要每股收益数据）
                eps = float(latest_report.get("eps", 0)) if latest_report else 0
                if eps > 0 and ratios["dividend_per_share"] > 0:
                    ratios["dividend_payout_ratio"] = (ratios["dividend_per_share"] / eps) * 100
                else:
                    ratios["dividend_payout_ratio"] = 0
                
                # 分红方案进度
                ratios["scheme_progress"] = latest_dividend.get("scheme_progress", "")
                
                # 净利润同比增长率
                ratios["net_profit_growth_rate"] = float(latest_dividend.get("net_profit_growth_rate", 0)) * 100
            
            # 分红连续性分析
            if len(dividend_details) >= 2:
                consecutive_years = 0
                for detail in dividend_details:
                    if float(detail.get("cash_dividend_ratio", 0)) > 0:
                        consecutive_years += 1
                    else:
                        break
                ratios["consecutive_dividend_years"] = consecutive_years
                
                # 分红增长趋势
                recent_dividends = [float(d.get("cash_dividend_ratio", 0)) for d in dividend_details[:3]]
                if len(recent_dividends) >= 2 and recent_dividends[1] > 0:
                    dividend_growth = ((recent_dividends[0] - recent_dividends[1]) / recent_dividends[1]) * 100
                    ratios["dividend_growth_rate"] = dividend_growth
                else:
                    ratios["dividend_growth_rate"] = 0
            
            return ratios
            
        except Exception as e:
            logger.warning(f"Error calculating dividend ratios: {str(e)}")
            return {"dividend_data_available": False, "error": str(e)}

    def _calculate_dividend_score(financial_data: Dict[str, Any]) -> int:
        """计算基于分红数据的股东回报评分"""
        try:
            dividend_details = financial_data.get("dividend_details", [])
            latest_dividend = financial_data.get("latest_dividend", {})
            
            if not dividend_details and not latest_dividend:
                return 5  # 无分红数据，给中等评分
            
            score = 0
            
            # 基于最新分红信息计算评分
            if latest_dividend:
                # 股息率评分 (最高5分)
                dividend_yield = float(latest_dividend.get("dividend_yield", 0))
                if dividend_yield > 0.03:  # >3%
                    score += 5
                elif dividend_yield > 0.02:  # >2%
                    score += 4
                elif dividend_yield > 0.01:  # >1%
                    score += 3
                elif dividend_yield > 0:  # >0%
                    score += 2
                else:
                    score += 1
                
                # 现金分红比例评分 (最高3分)
                cash_dividend = float(latest_dividend.get("cash_dividend_ratio", 0))
                if cash_dividend > 10:  # 每10股超过10元
                    score += 3
                elif cash_dividend > 5:  # 每10股超过5元
                    score += 2
                elif cash_dividend > 0:  # 有现金分红
                    score += 1
                
                # 分红稳定性评分 (最高2分) - 基于历史分红记录
                if len(dividend_details) >= 3:  # 至少3年分红记录
                    consecutive_dividends = 0
                    for detail in dividend_details[:5]:  # 检查最近5年
                        if float(detail.get("cash_dividend_ratio", 0)) > 0:
                            consecutive_dividends += 1
                    
                    if consecutive_dividends >= 5:
                        score += 2
                    elif consecutive_dividends >= 3:
                        score += 1
            
            return min(score, 10)  # 最高10分
            
        except Exception as e:
            logger.warning(f"Error calculating dividend score: {str(e)}")
            return 6  # 出错时给中等评分
    
    @tool 
    def calculate_financial_health_score(ratios: Dict[str, Any], financial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        计算财务健康度评分
        
        Args:
            ratios: 财务比率数据
            
        Returns:
            健康度评分结果
        """
        try:
            logger.info("Calculating financial health score")
            
            score = 0
            score_breakdown = {}
            
            # 盈利能力评分 (25分)
            profitability = ratios.get("profitability_ratios", {})
            roe = profitability.get("roe", 0)
            if roe > 15:
                prof_score = 25
            elif roe > 10:
                prof_score = 20
            elif roe > 5:
                prof_score = 15
            else:
                prof_score = 10
            score += prof_score
            score_breakdown["profitability"] = prof_score
            
            # 偿债能力评分 (20分)
            leverage = ratios.get("leverage_ratios", {})
            debt_ratio = leverage.get("debt_to_asset_ratio", 100)
            if debt_ratio < 50:
                debt_score = 20
            elif debt_ratio < 70:
                debt_score = 15
            elif debt_ratio < 85:
                debt_score = 10
            else:
                debt_score = 5
            score += debt_score
            score_breakdown["solvency"] = debt_score
            
            # 运营能力评分 (15分)
            efficiency = ratios.get("efficiency_ratios", {})
            asset_turnover = efficiency.get("total_asset_turnover", 0)
            if asset_turnover > 1.0:
                eff_score = 15
            elif asset_turnover > 0.7:
                eff_score = 12
            elif asset_turnover > 0.4:
                eff_score = 8
            else:
                eff_score = 5
            score += eff_score
            score_breakdown["efficiency"] = eff_score
            
            # 现金流质量评分 (20分)
            cashflow = ratios.get("cashflow_ratios", {})
            ocf_ratio = cashflow.get("ocf_to_net_income", 0)
            if ocf_ratio > 1.2:
                cf_score = 20
            elif ocf_ratio > 0.8:
                cf_score = 15
            elif ocf_ratio > 0.5:
                cf_score = 10
            else:
                cf_score = 5
            score += cf_score
            score_breakdown["cashflow"] = cf_score
            
            # 成长性评分 (10分)
            growth = ratios.get("growth_ratios", {})
            revenue_growth = growth.get("total_revenue_yoy", 0)
            if revenue_growth > 20:
                growth_score = 10
            elif revenue_growth > 10:
                growth_score = 8
            elif revenue_growth > 0:
                growth_score = 6
            else:
                growth_score = 3
            score += growth_score
            score_breakdown["growth"] = growth_score
            
            # 股东回报评分 (10分) - 基于分红数据的真实评分
            dividend_score = _calculate_dividend_score(financial_data) if financial_data else 6  # 默认评分
            score += dividend_score
            score_breakdown["dividend"] = dividend_score
            
            # 确定健康度等级
            if score >= 90:
                health_level = "优秀"
            elif score >= 80:
                health_level = "良好"
            elif score >= 70:
                health_level = "一般"
            elif score >= 60:
                health_level = "较差"
            else:
                health_level = "堪忧"
            
            return {
                "total_score": score,
                "health_level": health_level,
                "score_breakdown": score_breakdown,
                "max_score": 100,
                "scoring_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def prepare_analysis_data_for_llm(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备分析数据供LLM生成智能报告（增强版：包含趋势分析数据）
        
        Args:
            analysis_data: 包含历史趋势的分析数据
            
        Returns:
            格式化的分析数据字典，包含多年趋势信息
        """
        try:
            logger.info("Preparing enhanced analysis data for LLM report generation")
            
            stock_code = analysis_data.get("stock_code", "")
            stock_name = analysis_data.get("stock_name", "")
            
            # 基础信息
            basic_info = analysis_data.get("basic_info", {})
            if basic_info and "name" in basic_info:
                stock_name = basic_info["name"]
            
            # 财务比率和趋势分析
            ratios = analysis_data.get("financial_ratios", {})
            health_score_data = analysis_data.get("health_score", {})
            
            # 获取数据范围信息
            data_range = analysis_data.get("data_range", {})
            
            # 准备结构化数据供LLM分析
            structured_data = {
                "company_info": {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                    "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "data_coverage": {
                    "years_analyzed": data_range.get("years_requested", 3),
                    "date_range": f"{data_range.get('start_date', '')} 至 {data_range.get('end_date', '')}",
                    "total_reports": data_range.get("total_reports", 0),
                    "annual_reports": data_range.get("annual_reports", 0),
                    "trend_analysis_available": ratios.get("data_quality", {}).get("trend_analysis_available", False)
                },
                "financial_health": {
                    "total_score": health_score_data.get("total_score", 0),
                    "health_level": health_score_data.get("health_level", "未知"),
                    "score_breakdown": health_score_data.get("score_breakdown", {})
                },
                "financial_ratios": {
                    "profitability": ratios.get("profitability_ratios", {}),
                    "leverage": ratios.get("leverage_ratios", {}),
                    "efficiency": ratios.get("efficiency_ratios", {}),
                    "cashflow": ratios.get("cashflow_ratios", {}),
                    "growth": ratios.get("growth_ratios", {})
                },
                # 新增：多年趋势分析数据
                "trend_analysis": ratios.get("trend_analysis", {}),
                "historical_context": {
                    "revenue_trend": ratios.get("trend_analysis", {}).get("revenue_trend", {}),
                    "profit_trend": ratios.get("trend_analysis", {}).get("profit_trend", {}),
                    "roe_trend": ratios.get("trend_analysis", {}).get("roe_trend", {}),
                    "overall_assessment": ratios.get("trend_analysis", {}).get("overall_assessment", "数据不足")
                },
                "raw_financial_data": analysis_data.get("latest_report", {}),
                "historical_reports": analysis_data.get("annual_reports", [])[:5],  # 限制为最近5年
                "financial_summary": analysis_data.get("financial_summary", {})
            }
            
            # 记录准备的数据统计
            logger.info(f"Prepared LLM data with:")
            logger.info(f"  - Trend analysis: {structured_data['data_coverage']['trend_analysis_available']}")
            logger.info(f"  - Historical reports: {len(structured_data['historical_reports'])}")
            logger.info(f"  - Years covered: {structured_data['data_coverage']['years_analyzed']}")
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error preparing analysis data for LLM: {str(e)}")
            return {"error": str(e)}
    
    # 工具列表  
    tools = [
        get_financial_data,
        calculate_financial_ratios,
        calculate_financial_health_score,
        prepare_analysis_data_for_llm
    ]
    
    # 如果启用MCP工具，添加MCP相关工具
    if mcp_tools:
        @tool
        def get_mcp_financial_data(stock_code: str) -> Dict[str, Any]:
            """
            使用MCP服务获取财务数据
            
            Args:
                stock_code: 股票代码
                
            Returns:
                MCP财务数据
            """
            try:
                return mcp_tools.get_financial_reports(stock_code)
            except Exception as e:
                logger.error(f"Error getting MCP financial data: {str(e)}")
                return {"error": str(e)}
        
        tools.append(get_mcp_financial_data)
    
    def financial_analyst_node(state):
        """
        财务分析Agent节点函数
        
        Args:
            state: 当前分析状态
            
        Returns:
            更新后的状态
        """
        def _format_tool_results_for_report(results: Dict[str, Any]) -> str:
            """格式化工具结果用于报告生成"""
            formatted_results = []
            
            for tool_name, result in results.items():
                formatted_results.append(f"\n=== {tool_name} 结果 ===")
                if isinstance(result, dict):
                    for key, value in result.items():
                        formatted_results.append(f"{key}: {value}")
                else:
                    formatted_results.append(str(result))
            
            return "\n".join(formatted_results)
        
        try:
            logger.info("Starting financial analysis")
            
            # 获取分析参数
            stock_code = state.get("stock_code", "")
            stock_name = state.get("stock_name", "")
            analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
            
            if not stock_code:
                return {
                    "messages": [{"role": "assistant", "content": "错误：缺少股票代码"}],
                    "financial_analysis_report": "分析失败：缺少股票代码",
                    "analysis_stage": AnalysisStage.ERROR
                }
            
            # 构建系统提示词
            system_prompt = FINANCIAL_ANALYSIS_SYSTEM_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name,
                analysis_date=analysis_date
            )
            
            # 构建用户提示词
            user_prompt = FINANCIAL_ANALYSIS_USER_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name
            )
            
            # 使用序列化工具执行器
            executor = SequentialToolExecutor(tools, debug=config.get("debug", False))
            
            # 执行工具序列
            execution_results = executor.execute_tool_sequence(
                FINANCIAL_ANALYSIS_SEQUENCE,
                stock_code,
                stock_name,
                context={"analysis_date": analysis_date}
            )
            
            # 生成最终报告 - 使用真正的LLM分析
            if execution_results["success"]:
                try:
                    # 准备LLM分析所需的结构化数据
                    final_tool_results = execution_results.get("tool_results", {})
                    
                    # 获取财务数据、比率和健康度评分
                    financial_data = final_tool_results.get("get_financial_data", {})
                    financial_ratios = final_tool_results.get("calculate_financial_ratios", {})
                    health_score = final_tool_results.get("calculate_financial_health_score", {})
                    
                    # 合并所有分析数据
                    comprehensive_data = {
                        **financial_data,
                        "financial_ratios": financial_ratios,
                        "health_score": health_score,
                        "stock_name": stock_name,
                        "analysis_date": analysis_date
                    }
                    
                    # 使用LLM生成智能财务分析报告
                    # 重要修复：格式化系统提示词模板
                    formatted_system_prompt = FINANCIAL_ANALYSIS_SYSTEM_PROMPT.format(
                        stock_code=stock_code,
                        stock_name=stock_name,
                        analysis_date=analysis_date
                    )
                    
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", formatted_system_prompt),
                        ("human", """
基于以下多年历史财务分析数据，请生成一份专业、深入的财务分析报告：

## 公司基本信息
股票代码：{stock_code}
股票名称：{stock_name}
分析日期：{analysis_date}

## 数据覆盖范围
分析年限：{years_analyzed}年
数据时间范围：{date_range}
历史年报数量：{annual_reports_count}个
趋势分析可用性：{trend_analysis_available}

## 财务健康度评分
总分：{health_score}/100分
健康等级：{health_level}
评分明细：{score_breakdown}

## 多年趋势分析（核心亮点）
### 营收趋势
{revenue_trend}

### 利润趋势
{profit_trend}

### ROE趋势
{roe_trend}

### 整体趋势评估
{overall_assessment}

## 最新期财务比率数据
### 盈利能力指标
{profitability_ratios}

### 偿债能力指标  
{leverage_ratios}

### 运营能力指标
{efficiency_ratios}

### 现金流指标
{cashflow_ratios}

### 成长性指标
{growth_ratios}

### 股东回报和分红指标
{dividend_ratios}

## 历史财务数据
### 最新财务报告
{raw_financial_data}

**重要分析要求（基于多年数据）：**
1. **趋势分析为核心**：重点分析公司多年来的发展趋势，而非仅仅分析单年数据
2. **历史对比**：将最新财务表现与历史数据进行对比，识别变化趋势和拐点
3. **预测性洞察**：基于历史趋势预测未来可能的发展方向和潜在风险
4. **深度解读**：解释每个财务指标变化背后的业务驱动因素
5. **股东回报分析**：重点分析公司的分红政策、分红稳定性、股息率水平和分红增长趋势
6. **投资建议**：结合趋势分析给出具体的投资建议和风险提示
7. **专业判断**：展现对行业和公司深度理解的专业分析能力

**请确保报告包含：**
- 详细的多年趋势分析章节
- 基于历史数据的预测性判断
- 专门的股东回报和分红分析章节
- 明确的投资建议和风险警示
- 专业的财务分析深度和洞察力
                        """)
                    ])
                    
                    # 使用LLM生成报告
                    chain = prompt | llm
                    
                    # 准备输入数据（增强版：包含趋势分析数据）
                    llm_input = {
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "analysis_date": analysis_date,
                        
                        # 数据覆盖范围信息
                        "years_analyzed": comprehensive_data.get("data_range", {}).get("years_requested", 5),
                        "date_range": f"{comprehensive_data.get('data_range', {}).get('start_date', '')} 至 {comprehensive_data.get('data_range', {}).get('end_date', '')}",
                        "annual_reports_count": comprehensive_data.get("data_range", {}).get("annual_reports", 0),
                        "trend_analysis_available": "是" if financial_ratios.get("data_quality", {}).get("trend_analysis_available", False) else "否",
                        
                        # 财务健康度评分
                        "health_score": health_score.get("total_score", 0),
                        "health_level": health_score.get("health_level", "未知"),
                        "score_breakdown": json.dumps(health_score.get("score_breakdown", {}), ensure_ascii=False, indent=2),
                        
                        # 趋势分析数据
                        "revenue_trend": json.dumps(financial_ratios.get("trend_analysis", {}).get("revenue_trend", {}), ensure_ascii=False, indent=2),
                        "profit_trend": json.dumps(financial_ratios.get("trend_analysis", {}).get("profit_trend", {}), ensure_ascii=False, indent=2),
                        "roe_trend": json.dumps(financial_ratios.get("trend_analysis", {}).get("roe_trend", {}), ensure_ascii=False, indent=2),
                        "overall_assessment": financial_ratios.get("trend_analysis", {}).get("overall_assessment", "数据不足"),
                        
                        # 财务比率数据
                        "profitability_ratios": json.dumps(financial_ratios.get("profitability_ratios", {}), ensure_ascii=False, indent=2),
                        "leverage_ratios": json.dumps(financial_ratios.get("leverage_ratios", {}), ensure_ascii=False, indent=2),
                        "efficiency_ratios": json.dumps(financial_ratios.get("efficiency_ratios", {}), ensure_ascii=False, indent=2),
                        "cashflow_ratios": json.dumps(financial_ratios.get("cashflow_ratios", {}), ensure_ascii=False, indent=2),
                        "growth_ratios": json.dumps(financial_ratios.get("growth_ratios", {}), ensure_ascii=False, indent=2),
                        "dividend_ratios": json.dumps(financial_ratios.get("dividend_ratios", {}), ensure_ascii=False, indent=2),  # 新增：分红指标
                        
                        # 原始财务数据（限制长度）
                        "raw_financial_data": json.dumps(financial_data.get("latest_report", {}), ensure_ascii=False, indent=2)[:3000]  # 增加到3000字符
                    }
                    
                    # 验证输入数据完整性（增强版）
                    validation_passed = all([
                        llm_input.get("health_score", 0),
                        llm_input.get("profitability_ratios", "{}") != "{}",
                        llm_input.get("stock_code"),
                        llm_input.get("stock_name"),
                        llm_input.get("years_analyzed", 0) > 0
                    ])
                    
                    if not validation_passed:
                        logger.warning("⚠️ LLM输入数据不完整，可能影响报告质量")
                        logger.warning(f"健康度评分: {llm_input.get('health_score', 0)}")
                        logger.warning(f"盈利能力指标: {llm_input.get('profitability_ratios', '空')[:100]}")
                        logger.warning(f"分析年限: {llm_input.get('years_analyzed', 0)}")
                        logger.warning(f"趋势分析可用: {llm_input.get('trend_analysis_available', '否')}")
                    else:
                        logger.info("✅ 数据验证通过，包含多年历史数据和趋势分析")
                    
                    logger.debug(f"LLM输入数据检查完成，数据键: {list(llm_input.keys())}")
                    
                    # 调用LLM生成智能分析报告（增强版日志）
                    logger.info(f"正在调用LLM生成增强版分析报告")
                    logger.info(f"  - 输入数据键数量: {len(llm_input.keys())}")
                    logger.info(f"  - 分析年限: {llm_input.get('years_analyzed', 0)}年")
                    logger.info(f"  - 年报数量: {llm_input.get('annual_reports_count', 0)}个")
                    logger.info(f"  - 趋势分析: {llm_input.get('trend_analysis_available', '否')}")
                    logger.debug(f"LLM输入数据键列表: {list(llm_input.keys())}")
                    logger.debug(f"基础数据: stock_code={llm_input.get('stock_code')}, health_score={llm_input.get('health_score')}")
                    
                    llm_result = chain.invoke(llm_input)
                    financial_report = llm_result.content
                    
                    # 关键修复：检查并记录LLM返回的完整结果（增强版）
                    logger.info(f"✅ 增强版LLM调用成功")
                    logger.info(f"LLM返回结果类型: {type(llm_result)}")
                    logger.info(f"LLM返回内容字符数: {len(financial_report) if financial_report else 0}")
                    if financial_report:
                        logger.info(f"报告开头: {financial_report[:100]}")
                        logger.info(f"报告结尾: {financial_report[-100:]}")
                        # 检查是否包含趋势分析内容
                        if "趋势" in financial_report or "历史" in financial_report or "变化" in financial_report:
                            logger.info("✅ 报告包含趋势分析内容")
                        else:
                            logger.warning("⚠️ 报告可能缺少趋势分析内容")
                    else:
                        logger.warning("⚠️ LLM返回空内容")
                    
                    # 验证报告完整性
                    if not financial_report or len(financial_report.strip()) == 0:
                        logger.warning("⚠️ LLM返回了空内容！")
                        logger.warning(f"原始LLM结果对象: {llm_result}")
                        logger.warning(f"llm_result.content: {repr(llm_result.content)}")
                        
                        # 提供备用报告
                        financial_report = f"""【LLM分析报告生成异常】

{stock_name}（{stock_code}）财务分析报告

⚠️ AI智能分析返回空内容，可能原因：
1. LLM模型响应异常
2. 输入数据格式问题  
3. API调用限制或超时

基础分析摘要：
- 财务健康度评分：{health_score.get('total_score', 0)}/100分
- 健康等级：{health_score.get('health_level', '未知')}
- 分析日期：{analysis_date}

请检查LLM配置并重新尝试完整分析。"""
                    else:
                        logger.info("✅ LLM报告生成成功，内容完整")
                        # 确保报告完整性 - 检查是否被意外截断
                        if len(financial_report) < 500:  # 如果报告过短，可能有问题
                            logger.warning(f"⚠️ 报告内容可能过短（{len(financial_report)}字符），请检查LLM配置")
                    
                    logger.info("📋 Financial analysis completed with LLM report generation")
                    
                    # 重要：直接将完整的financial_report保存到状态中，不做任何截断
                    logger.info(f"💾 准备保存报告到状态，报告总长度: {len(financial_report)}字符")
                    
                except Exception as llm_error:
                    logger.error(f"LLM report generation failed: {str(llm_error)}")
                    # 如果LLM分析失败，提供工具结果摘要作为备用
                    financial_report = f"""{stock_name}（{stock_code}）财务分析报告

⚠️ 智能分析生成失败，以下为基础分析结果：

工具执行结果：
{executor.generate_tool_results_summary(execution_results)}

错误信息：{str(llm_error)}

建议：请检查LLM配置或稍后重试智能分析。
分析日期：{analysis_date}
数据来源：A股数据API"""
            else:
                # 如果工具执行失败，生成错误报告
                financial_report = f"""{stock_name}（{stock_code}）财务分析执行失败

错误详情：
{'; '.join(execution_results['errors'])}

已完成的步骤：
{executor.generate_tool_results_summary(execution_results)}

建议：请检查数据源连接或稍后重试。"""
                
                logger.error(f"Financial analysis failed: {execution_results['errors']}")
            
            return {
                "messages": [{"role": "assistant", "content": financial_report}],
                "financial_analysis_report": financial_report,
                "financial_analysis_results": execution_results,  # 保存详细执行结果
                "analysis_stage": AnalysisStage.FINANCIAL_ANALYSIS,
                "financial_data": execution_results.get("tool_results", {}).get("get_financial_data", {}),
                "key_financial_metrics": execution_results.get("tool_results", {}).get("calculate_financial_ratios", {}),
                "data_sources": state.get("data_sources", []) + ["A股数据API"],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in financial analysis: {str(e)}")
            return {
                "messages": [{"role": "assistant", "content": f"财务分析过程中出现错误: {str(e)}"}],
                "financial_analysis_report": f"分析失败: {str(e)}",
                "analysis_stage": AnalysisStage.ERROR
            }
    
    return financial_analyst_node