"""
财务指标分析Agent（LLM Agent模式）

专门负责A股公司的财务指标分析，采用LLM动态工具选择模式。
LLM可以根据需要自主选择和调用合适的工具，实现更灵活的分析流程。

与financial_analyst.py的区别：
- financial_analyst.py：顺序执行所有工具，然后LLM生成报告
- financial_analyst_llm.py：LLM动态选择需要的工具，更智能的分析流程
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ..utils.data_tools import AShareDataTools, DataProcessor
from ..utils.mcp_tools import MCPToolsWrapper
from ..utils.calculation_utils import FinancialCalculator, RiskCalculator
from ..utils.state_models import AnalysisStage, AnalysisDepth
from ..prompts.financial_prompts import FINANCIAL_ANALYSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def create_financial_analyst_llm(llm, toolkit, config, return_executor=False):
    """
    创建财务指标分析Agent（LLM动态工具选择模式）
    
    Args:
        llm: 语言模型实例
        toolkit: 工具集（可选，保持接口兼容性）
        config: 配置字典
        
    Returns:
        LLM Agent执行器
    """
    
    # 初始化数据工具
    data_tools = AShareDataTools(config)
    mcp_tools = MCPToolsWrapper(config) if config.get("mcp_tools_enabled") else None
    
    # 创建财务分析工具（为LLM Agent优化的描述）
    @tool
    def get_financial_data(stock_code: str, years: int = 5) -> Dict[str, Any]:
        """
        【第1步/共4步】获取股票的综合财务数据，包括多年历史数据和分红信息。

        ⚠️ 这是财务分析的第1步，必须首先调用！完成后必须立即调用第2步工具：calculate_financial_ratios

        Args:
            stock_code: 股票代码（如002594）
            years: 获取历史数据的年数，建议使用5年获得更好的趋势分析

        Returns:
            包含基本信息、最新财报、历史报告、分红数据等的完整财务数据字典

        ⚠️ 完成此步骤后，必须立即调用 calculate_financial_ratios 工具（第2步）！
        """
        try:
            logger.info(f"[LLM Tool] Getting comprehensive financial data for {stock_code} (last {years} years)")
            
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
            
            # 获取历史财务报告
            historical_reports = data_tools.get_financial_reports(
                stock_code, 
                start_date=start_date,
                end_date=end_date,
                limit=years * 4
            )
            
            # 获取年报数据（用于趋势分析）
            annual_reports = []
            if historical_reports:
                annual_reports = [report for report in historical_reports if report.get('report_type') == 'A']
                annual_reports.sort(key=lambda x: x.get('report_date', ''), reverse=True)
            
            # 获取财务摘要
            financial_summary = data_tools.get_financial_summary(stock_code, years)
            
            # 获取分红送配数据
            dividend_details = data_tools.get_dividend_details(
                stock_code,
                start_date=start_date,
                end_date=end_date,
                limit=years * 2
            )
            
            # 获取最新分红信息
            latest_dividend = data_tools.get_latest_dividend_info(stock_code)
            
            logger.info(f"[LLM Tool] Successfully retrieved data: {len(historical_reports) if historical_reports else 0} reports, {len(dividend_details) if dividend_details else 0} dividend records")
            
            return {
                "stock_code": stock_code,
                "basic_info": basic_info,
                "latest_report": latest_report,
                "financial_reports": historical_reports,
                "annual_reports": annual_reports,
                "financial_summary": financial_summary,
                "dividend_details": dividend_details,
                "latest_dividend": latest_dividend,
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
            logger.error(f"[LLM Tool] Error getting financial data for {stock_code}: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_financial_ratios(financial_data) -> Dict[str, Any]:
        """
        【第2步/共4步】基于财务数据计算各类财务比率指标，包括多年趋势分析。

        ⚠️ 这是财务分析的第2步，必须在第1步get_financial_data后调用！完成后必须立即调用第3步工具：calculate_financial_health_score

        Args:
            financial_data: 从get_financial_data工具获得的完整财务数据（支持字典对象或JSON字符串）

        Returns:
            包含所有财务比率和趋势分析的详细字典，涵盖：
            - 盈利能力比率（ROE、ROA、毛利率、净利率等）
            - 偿债能力比率（资产负债率、流动比率、速动比率等）
            - 运营效率比率（资产周转率等）
            - 现金流比率
            - 成长性指标
            - 分红比率
            - 多年趋势分析

        ⚠️ 完成此步骤后，必须立即调用 calculate_financial_health_score 工具（第3步）！
        """
        try:
            logger.info("[LLM Tool] Calculating comprehensive financial ratios with trend analysis")
            
            # 处理输入参数类型（支持字典对象或JSON字符串）
            if isinstance(financial_data, str):
                try:
                    import json
                    financial_data = json.loads(financial_data)
                    logger.info("[LLM Tool] Successfully parsed JSON string input to dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"[LLM Tool] Failed to parse JSON string: {e}")
                    return {"error": f"Invalid JSON string format: {e}"}
            
            if not isinstance(financial_data, dict):
                logger.error(f"[LLM Tool] Invalid input type: {type(financial_data)}")
                return {"error": f"Expected dictionary or JSON string, got {type(financial_data)}"}

            # 处理LLM传递的包装数据结构
            if "get_financial_data_response" in financial_data:
                financial_data = financial_data["get_financial_data_response"]
                logger.info("[LLM Tool] Unwrapped get_financial_data_response structure")

            if "latest_report" not in financial_data or not financial_data["latest_report"]:
                return {"error": "No latest financial report available"}
            
            latest_report = financial_data["latest_report"]
            financial_reports = financial_data.get("financial_reports", [])
            annual_reports = financial_data.get("annual_reports", [])
            
            # 计算各类财务比率
            profitability = FinancialCalculator.calculate_profitability_ratios(latest_report)
            liquidity = FinancialCalculator.calculate_liquidity_ratios(latest_report)
            leverage = FinancialCalculator.calculate_leverage_ratios(latest_report)
            efficiency = FinancialCalculator.calculate_efficiency_ratios(latest_report)
            cashflow = FinancialCalculator.calculate_cashflow_ratios(latest_report)
            
            # 成长性指标和趋势分析
            growth = {}
            trend_analysis = {}
            dividend_ratios = {}
            
            # 计算分红相关比率
            dividend_ratios = _calculate_dividend_ratios(financial_data)
            
            if annual_reports and len(annual_reports) >= 2:
                growth = FinancialCalculator.calculate_growth_rates(annual_reports)
                trend_analysis = _analyze_multi_year_trends(annual_reports)
                logger.info(f"[LLM Tool] Generated trend analysis from {len(annual_reports)} annual reports")
            elif financial_reports and len(financial_reports) >= 2:
                growth = FinancialCalculator.calculate_growth_rates(financial_reports)
                logger.info(f"[LLM Tool] Generated growth rates from {len(financial_reports)} reports")
            else:
                logger.warning("[LLM Tool] Insufficient historical data for trend analysis")
                growth = {"note": "需要至少2年的历史数据进行趋势分析"}
            
            result = {
                "profitability_ratios": profitability,
                "liquidity_ratios": liquidity,
                "leverage_ratios": leverage,
                "efficiency_ratios": efficiency,
                "cashflow_ratios": cashflow,
                "growth_ratios": growth,
                "dividend_ratios": dividend_ratios,
                "trend_analysis": trend_analysis,
                "data_quality": {
                    "annual_reports_count": len(annual_reports),
                    "total_reports_count": len(financial_reports),
                    "trend_analysis_available": len(annual_reports) >= 3,
                    "growth_analysis_available": len(annual_reports) >= 2 or len(financial_reports) >= 2,
                    "dividend_data_available": dividend_ratios.get("dividend_data_available", False)
                },
                "calculation_date": datetime.now().isoformat()
            }
            
            logger.info("[LLM Tool] Successfully calculated comprehensive financial ratios")
            return result
            
        except Exception as e:
            logger.error(f"[LLM Tool] Error calculating financial ratios: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_financial_health_score(ratios, financial_data=None) -> Dict[str, Any]:
        """
        【第3步/共4步】基于财务比率计算综合财务健康度评分，提供量化的财务状况评估。

        ⚠️ 这是财务分析的第3步，必须在第2步calculate_financial_ratios后调用！完成后必须立即调用第4步工具：generate_financial_analysis_report

        Args:
            ratios: 从calculate_financial_ratios工具获得的财务比率数据（支持字典对象或JSON字符串）
            financial_data: 原始财务数据（可选，用于更准确的分红评分，支持字典对象或JSON字符串）

        Returns:
            包含总评分、健康等级和各维度评分明细的字典：
            - 盈利能力评分（25分）
            - 偿债能力评分（20分）
            - 运营能力评分（15分）
            - 现金流质量评分（20分）
            - 成长性评分（10分）
            - 股东回报评分（10分）

        ⚠️ 完成此步骤后，必须立即调用 generate_financial_analysis_report 工具（第4步，最后一步）！
        """
        try:
            logger.info("[LLM Tool] Calculating financial health score")
            
            # 处理ratios参数类型
            if isinstance(ratios, str):
                try:
                    import json
                    ratios = json.loads(ratios)
                    logger.info("[LLM Tool] Successfully parsed ratios JSON string to dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"[LLM Tool] Failed to parse ratios JSON string: {e}")
                    return {"error": f"Invalid ratios JSON string format: {e}"}
            
            if not isinstance(ratios, dict):
                logger.error(f"[LLM Tool] Invalid ratios input type: {type(ratios)}")
                return {"error": f"Expected ratios as dictionary or JSON string, got {type(ratios)}"}

            # 处理LLM传递的包装ratios数据结构
            if "calculate_financial_ratios_response" in ratios:
                ratios = ratios["calculate_financial_ratios_response"]
                logger.info("[LLM Tool] Unwrapped calculate_financial_ratios_response structure")

            # 处理financial_data参数类型（可选）
            if financial_data and isinstance(financial_data, str):
                try:
                    import json
                    financial_data = json.loads(financial_data)
                    logger.info("[LLM Tool] Successfully parsed financial_data JSON string to dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"[LLM Tool] Failed to parse financial_data JSON string: {e}")
                    financial_data = None  # 继续执行，但不使用分红评分

            # 处理LLM传递的包装financial_data数据结构
            if financial_data and isinstance(financial_data, dict) and "get_financial_data_response" in financial_data:
                financial_data = financial_data["get_financial_data_response"]
                logger.info("[LLM Tool] Unwrapped get_financial_data_response structure for financial_data")
            
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
            
            # 股东回报评分 (10分) - 基于分红数据
            dividend_score = _calculate_dividend_score(financial_data) if financial_data else 6
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
            
            result = {
                "total_score": score,
                "health_level": health_level,
                "score_breakdown": score_breakdown,
                "max_score": 100,
                "scoring_date": datetime.now().isoformat()
            }
            
            logger.info(f"[LLM Tool] Calculated health score: {score}/100 ({health_level})")
            return result
            
        except Exception as e:
            logger.error(f"[LLM Tool] Error calculating health score: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def generate_financial_analysis_report(
        stock_code: str,
        stock_name: str,
        financial_data,
        financial_ratios,
        health_score
    ) -> Dict[str, Any]:
        """
        【第4步/共4步】基于所有分析数据生成专业的财务分析报告。

        ⚠️ 这是财务分析的最后一步（第4步），必须在前3步完成后调用！完成后财务分析流程结束。

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            financial_data: 基础财务数据（支持字典对象或JSON字符串）
            financial_ratios: 财务比率分析结果（支持字典对象或JSON字符串）
            health_score: 财务健康度评分结果（支持字典对象或JSON字符串）

        Returns:
            包含完整财务分析报告的字典，包括：
            - 专业分析报告文本
            - 投资建议和风险提示
            - 数据来源和计算方法说明

        ✅ 完成此步骤后，财务分析流程全部结束！
        """
        try:
            logger.info(f"[LLM Tool] Generating financial analysis report for {stock_code}")
            
            # 处理financial_data参数类型
            if isinstance(financial_data, str):
                try:
                    import json
                    financial_data = json.loads(financial_data)
                    logger.info("[LLM Tool] Successfully parsed financial_data JSON string to dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"[LLM Tool] Failed to parse financial_data JSON string: {e}")
                    return {"error": f"Invalid financial_data JSON string format: {e}"}
            
            # 处理financial_ratios参数类型
            if isinstance(financial_ratios, str):
                try:
                    import json
                    financial_ratios = json.loads(financial_ratios)
                    logger.info("[LLM Tool] Successfully parsed financial_ratios JSON string to dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"[LLM Tool] Failed to parse financial_ratios JSON string: {e}")
                    return {"error": f"Invalid financial_ratios JSON string format: {e}"}
            
            # 处理health_score参数类型
            if isinstance(health_score, str):
                try:
                    import json
                    health_score = json.loads(health_score)
                    logger.info("[LLM Tool] Successfully parsed health_score JSON string to dictionary")
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"[LLM Tool] Failed to parse health_score JSON string: {e}")
                    return {"error": f"Invalid health_score JSON string format: {e}"}
            
            # 验证所有参数都是字典类型
            for param_name, param_value in [
                ("financial_data", financial_data),
                ("financial_ratios", financial_ratios), 
                ("health_score", health_score)
            ]:
                if not isinstance(param_value, dict):
                    logger.error(f"[LLM Tool] Invalid {param_name} input type: {type(param_value)}")
                    return {"error": f"Expected {param_name} as dictionary or JSON string, got {type(param_value)}"}
            
            analysis_date = datetime.now().strftime("%Y-%m-%d")
            
            # 获取数据范围信息
            data_range = financial_data.get("data_range", {})
            
            # 准备报告数据
            report_data = {
                "stock_code": stock_code,
                "stock_name": stock_name,
                "analysis_date": analysis_date,
                "years_analyzed": data_range.get("years_requested", 3),
                "date_range": f"{data_range.get('start_date', '')} 至 {data_range.get('end_date', '')}",
                "annual_reports_count": data_range.get("annual_reports", 0),
                "trend_analysis_available": "是" if financial_ratios.get("data_quality", {}).get("trend_analysis_available", False) else "否",
                "health_score": health_score.get("total_score", 0),
                "health_level": health_score.get("health_level", "未知"),
                "score_breakdown": json.dumps(health_score.get("score_breakdown", {}), ensure_ascii=False, indent=2),
                "revenue_trend": json.dumps(financial_ratios.get("trend_analysis", {}).get("revenue_trend", {}), ensure_ascii=False, indent=2),
                "profit_trend": json.dumps(financial_ratios.get("trend_analysis", {}).get("profit_trend", {}), ensure_ascii=False, indent=2),
                "roe_trend": json.dumps(financial_ratios.get("trend_analysis", {}).get("roe_trend", {}), ensure_ascii=False, indent=2),
                "overall_assessment": financial_ratios.get("trend_analysis", {}).get("overall_assessment", "数据不足"),
                "profitability_ratios": json.dumps(financial_ratios.get("profitability_ratios", {}), ensure_ascii=False, indent=2),
                "leverage_ratios": json.dumps(financial_ratios.get("leverage_ratios", {}), ensure_ascii=False, indent=2),
                "efficiency_ratios": json.dumps(financial_ratios.get("efficiency_ratios", {}), ensure_ascii=False, indent=2),
                "cashflow_ratios": json.dumps(financial_ratios.get("cashflow_ratios", {}), ensure_ascii=False, indent=2),
                "growth_ratios": json.dumps(financial_ratios.get("growth_ratios", {}), ensure_ascii=False, indent=2),
                "dividend_ratios": json.dumps(financial_ratios.get("dividend_ratios", {}), ensure_ascii=False, indent=2),
                "raw_financial_data": json.dumps(financial_data.get("latest_report", {}), ensure_ascii=False, indent=2)[:3000]
            }
            
            # 使用提示词模板生成报告
            from ..prompts.financial_prompts import FINANCIAL_ANALYSIS_ENHANCED_REPORT_PROMPT
            
            report_prompt = FINANCIAL_ANALYSIS_ENHANCED_REPORT_PROMPT.format(**report_data)
            
            # 基于数据生成简化版报告（如果LLM调用失败，可作为备用）
            simplified_report = f"""
{stock_name}（{stock_code}）财务分析报告（LLM Agent模式）

分析日期：{analysis_date}
数据覆盖：{report_data['years_analyzed']}年（{report_data['date_range']}）

== 财务健康度评估 ==
总评分：{report_data['health_score']}/100分
健康等级：{report_data['health_level']}
评分明细：{health_score.get('score_breakdown', {})}

== 趋势分析摘要 ==
整体评估：{report_data['overall_assessment']}
营收趋势：{financial_ratios.get('trend_analysis', {}).get('revenue_trend', {}).get('direction', '待分析')}
利润趋势：{financial_ratios.get('trend_analysis', {}).get('profit_trend', {}).get('direction', '待分析')}
ROE趋势：{financial_ratios.get('trend_analysis', {}).get('roe_trend', {}).get('direction', '待分析')}

== 关键财务指标 ==
ROE：{financial_ratios.get('profitability_ratios', {}).get('roe', 0):.2f}%
资产负债率：{financial_ratios.get('leverage_ratios', {}).get('debt_to_asset_ratio', 0):.2f}%
营收增长率：{financial_ratios.get('growth_ratios', {}).get('total_revenue_yoy', 0):.2f}%
股息率：{financial_ratios.get('dividend_ratios', {}).get('dividend_yield', 0)*100:.2f}%

== 投资建议 ==
基于{report_data['health_score']}分的财务健康度评分，建议投资者关注该股票的{report_data['health_level']}财务表现。
具体投资决策需结合市场环境、行业前景等因素综合考虑。

数据来源：A股数据API
生成模式：LLM Agent动态工具选择模式
"""
            
            result = {
                "financial_analysis_report": simplified_report,
                "report_prompt": report_prompt,  # 可供外部LLM使用的详细提示词
                "analysis_summary": {
                    "health_score": report_data['health_score'],
                    "health_level": report_data['health_level'],
                    "trend_assessment": report_data['overall_assessment'],
                    "data_coverage": f"{report_data['years_analyzed']}年历史数据",
                    "report_generation_mode": "LLM Agent动态工具选择"
                },
                "data_sources": ["A股数据API"],
                "generation_time": datetime.now().isoformat()
            }
            
            logger.info(f"[LLM Tool] Successfully generated financial analysis report")
            return result
            
        except Exception as e:
            logger.error(f"[LLM Tool] Error generating report: {str(e)}")
            return {"error": str(e)}

    # 辅助函数（与原版保持一致）
    def _analyze_multi_year_trends(annual_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析多年财务趋势"""
        try:
            if len(annual_reports) < 3:
                return {"note": "需要至少3年数据进行趋势分析"}
            
            recent_reports = annual_reports[:5]
            
            trends = {
                "revenue_trend": _calculate_trend(recent_reports, "total_revenue"),
                "profit_trend": _calculate_trend(recent_reports, "net_profit"),
                "asset_trend": _calculate_trend(recent_reports, "total_assets"),
                "roe_trend": _calculate_trend(recent_reports, "roe"),
                "debt_ratio_trend": _calculate_trend(recent_reports, "debt_to_asset_ratio")
            }
            
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
                recent_avg = sum(values[:2]) / 2
                earlier_avg = sum(values[-2:]) / 2
                
                if recent_avg > earlier_avg * 1.1:
                    trend_direction = "上升"
                elif recent_avg < earlier_avg * 0.9:
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
                ratios["dividend_yield"] = float(latest_dividend.get("dividend_yield", 0))
                ratios["cash_dividend_per_10_shares"] = float(latest_dividend.get("cash_dividend_ratio", 0))
                
                cash_dividend_ratio = float(latest_dividend.get("cash_dividend_ratio", 0))
                ratios["dividend_per_share"] = cash_dividend_ratio / 10 if cash_dividend_ratio > 0 else 0
                
                eps = float(latest_report.get("eps", 0)) if latest_report else 0
                if eps > 0 and ratios["dividend_per_share"] > 0:
                    ratios["dividend_payout_ratio"] = (ratios["dividend_per_share"] / eps) * 100
                else:
                    ratios["dividend_payout_ratio"] = 0
                
                ratios["scheme_progress"] = latest_dividend.get("scheme_progress", "")
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
                return 5
            
            score = 0
            
            if latest_dividend:
                # 股息率评分 (最高5分)
                dividend_yield = float(latest_dividend.get("dividend_yield", 0))
                if dividend_yield > 0.03:
                    score += 5
                elif dividend_yield > 0.02:
                    score += 4
                elif dividend_yield > 0.01:
                    score += 3
                elif dividend_yield > 0:
                    score += 2
                else:
                    score += 1
                
                # 现金分红比例评分 (最高3分)
                cash_dividend = float(latest_dividend.get("cash_dividend_ratio", 0))
                if cash_dividend > 10:
                    score += 3
                elif cash_dividend > 5:
                    score += 2
                elif cash_dividend > 0:
                    score += 1
                
                # 分红稳定性评分 (最高2分)
                if len(dividend_details) >= 3:
                    consecutive_dividends = 0
                    for detail in dividend_details[:5]:
                        if float(detail.get("cash_dividend_ratio", 0)) > 0:
                            consecutive_dividends += 1
                    
                    if consecutive_dividends >= 5:
                        score += 2
                    elif consecutive_dividends >= 3:
                        score += 1
            
            return min(score, 10)
            
        except Exception as e:
            logger.warning(f"Error calculating dividend score: {str(e)}")
            return 6

    # 创建工具列表
    tools = [
        get_financial_data,
        calculate_financial_ratios,
        calculate_financial_health_score,
        generate_financial_analysis_report
    ]
    
    # 如果启用MCP工具，添加MCP相关工具
    if mcp_tools:
        @tool
        def get_mcp_financial_data(stock_code: str) -> Dict[str, Any]:
            """
            使用MCP服务获取补充财务数据，可以作为主要数据源的补充。
            
            Args:
                stock_code: 股票代码
                
            Returns:
                MCP财务数据
                
            使用场景：
            - 当主要数据源数据不足时
            - 需要交叉验证数据时
            - 获取特殊的MCP独有数据时
            """
            try:
                logger.info(f"[LLM Tool] Getting MCP financial data for {stock_code}")
                return mcp_tools.get_financial_reports(stock_code)
            except Exception as e:
                logger.error(f"[LLM Tool] Error getting MCP financial data: {str(e)}")
                return {"error": str(e)}
        
        tools.append(get_mcp_financial_data)
    
    # 创建LLM Agent专用的系统提示词（强制执行版本）
    system_prompt = """你是一个财务分析专家。你必须严格按照4步流程完成财务分析，缺一不可！

**强制执行流程（必须全部完成）：**
1. get_financial_data - 获取基础数据（第1步，必须首先执行）
2. calculate_financial_ratios - 计算比率（第2步，必须在第1步后执行）
3. calculate_financial_health_score - 计算评分（第3步，必须在第2步后执行）
4. generate_financial_analysis_report - 生成报告（第4步，必须在第3步后执行）

**严格执行规则：**
- 你必须调用所有4个工具，缺一不可
- 必须按照1→2→3→4的顺序执行
- 每完成一个工具后，立即检查：我完成了几步？还剩几步？
- 如果未完成4步，必须立即调用下一个工具
- 只有完成全部4步后才能结束，绝不能提前停止

**第4步特别说明：**
调用 generate_financial_analysis_report 时，需要传递以下参数：
- stock_code: 股票代码（如"002594"）
- stock_name: 股票名称（如"比亚迪"）
- financial_data: 第1步的结果
- financial_ratios: 第2步的结果
- health_score: 第3步的结果

**重要：你的任务没有完成，直到你调用了所有4个工具！**"""
    
    # 创建ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 创建Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # 创建AgentExecutor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # 始终启用详细输出用于调试
        handle_parsing_errors=True,
        max_iterations=8,  # 减少到8次，确保有足够次数调用4个工具
        return_intermediate_steps=True,
        max_execution_time=300  # 5分钟超时
    )
    
    def financial_analyst_llm_node(state):
        """
        财务分析Agent节点函数（LLM Agent模式）
        
        Args:
            state: 当前分析状态
            
        Returns:
            更新后的状态
        """
        try:
            logger.info("Starting financial analysis (LLM Agent mode)")
            
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
            
            # 构建用户请求（简化版）
            user_input = f"请使用工具分析股票{stock_code}（{stock_name}）的财务状况"
            
            # 调用LLM Agent
            result = executor.invoke({
                "input": user_input
            })
            
            # 提取分析结果
            agent_output = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # 尝试从中间步骤中提取具体的分析数据
            financial_data = {}
            financial_ratios = {}
            health_score = {}
            
            for step in intermediate_steps:
                action, observation = step
                tool_name = action.tool
                
                if tool_name == "get_financial_data":
                    if isinstance(observation, dict) and "error" not in observation:
                        financial_data = observation
                elif tool_name == "calculate_financial_ratios":
                    if isinstance(observation, dict) and "error" not in observation:
                        financial_ratios = observation
                elif tool_name == "calculate_financial_health_score":
                    if isinstance(observation, dict) and "error" not in observation:
                        health_score = observation
            
            # 构建返回状态
            return {
                "messages": [{"role": "assistant", "content": agent_output}],
                "financial_analysis_report": agent_output,
                "financial_analysis_results": {
                    "success": True,
                    "agent_mode": "LLM Agent动态工具选择",
                    "tool_calls": len(intermediate_steps),
                    "intermediate_steps": intermediate_steps
                },
                "analysis_stage": AnalysisStage.FINANCIAL_ANALYSIS,
                "financial_data": financial_data,
                "key_financial_metrics": financial_ratios,
                "health_score": health_score,
                "data_sources": state.get("data_sources", []) + ["A股数据API（LLM Agent模式）"],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in financial analysis (LLM Agent mode): {str(e)}")
            return {
                "messages": [{"role": "assistant", "content": f"财务分析过程中出现错误: {str(e)}"}],
                "financial_analysis_report": f"LLM Agent模式分析失败: {str(e)}",
                "analysis_stage": AnalysisStage.ERROR
            }
    
    # 根据参数决定返回类型
    if return_executor:
        return executor  # 返回原始executor用于测试
    else:
        return financial_analyst_llm_node  # 返回包装函数用于生产