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
    def get_financial_data(stock_code: str, years: int = 3) -> Dict[str, Any]:
        """
        获取股票财务数据
        
        Args:
            stock_code: 股票代码
            years: 历史年数
            
        Returns:
            财务数据字典
        """
        try:
            logger.info(f"Getting financial data for {stock_code}")
            
            # 获取股票基础信息
            basic_info = data_tools.get_stock_basic_info(stock_code)
            
            # 获取最新财务报告
            latest_report = data_tools.get_latest_financial_report(stock_code, "A")
            
            # 获取历史财务报告
            financial_reports = data_tools.get_financial_reports(
                stock_code, 
                limit=years
            )
            
            # 获取财务摘要
            financial_summary = data_tools.get_financial_summary(stock_code, years)
            
            return {
                "stock_code": stock_code,
                "basic_info": basic_info,
                "latest_report": latest_report,
                "financial_reports": financial_reports,
                "financial_summary": financial_summary,
                "data_source": "A股数据API"
            }
            
        except Exception as e:
            logger.error(f"Error getting financial data for {stock_code}: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_financial_ratios(financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算财务比率指标
        
        Args:
            financial_data: 财务数据
            
        Returns:
            财务比率字典
        """
        try:
            logger.info("Calculating financial ratios")
            
            if "latest_report" not in financial_data or not financial_data["latest_report"]:
                return {"error": "No latest financial report available"}
            
            latest_report = financial_data["latest_report"]
            financial_reports = financial_data.get("financial_reports", [])
            
            # 计算各类财务比率
            profitability = FinancialCalculator.calculate_profitability_ratios(latest_report)
            liquidity = FinancialCalculator.calculate_liquidity_ratios(latest_report)
            leverage = FinancialCalculator.calculate_leverage_ratios(latest_report)
            efficiency = FinancialCalculator.calculate_efficiency_ratios(latest_report)
            cashflow = FinancialCalculator.calculate_cashflow_ratios(latest_report)
            
            # 计算成长性指标（需要历史数据）
            growth = {}
            if financial_reports:
                growth = FinancialCalculator.calculate_growth_rates(financial_reports)
            
            return {
                "profitability_ratios": profitability,
                "liquidity_ratios": liquidity,
                "leverage_ratios": leverage,
                "efficiency_ratios": efficiency,
                "cashflow_ratios": cashflow,
                "growth_ratios": growth,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {str(e)}")
            return {"error": str(e)}
    
    @tool 
    def calculate_financial_health_score(ratios: Dict[str, Any]) -> Dict[str, Any]:
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
            
            # 股东回报评分 (10分) - 简化处理
            dividend_score = 8  # 默认评分，实际需要股利数据
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
    def generate_financial_analysis_report(analysis_data: Dict[str, Any]) -> str:
        """
        生成财务分析报告
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            格式化的分析报告
        """
        try:
            logger.info("Generating financial analysis report")
            
            stock_code = analysis_data.get("stock_code", "")
            stock_name = analysis_data.get("stock_name", "")
            
            # 基础信息
            basic_info = analysis_data.get("basic_info", {})
            if basic_info and "name" in basic_info:
                stock_name = basic_info["name"]
            
            # 财务比率
            ratios = analysis_data.get("financial_ratios", {})
            health_score_data = analysis_data.get("health_score", {})
            
            # 生成报告内容
            report_sections = {
                "stock_name": stock_name,
                "stock_code": stock_code,
                "health_score": health_score_data.get("total_score", 0),
                "health_level": health_score_data.get("health_level", "未知"),
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 构建详细分析内容
            profitability = ratios.get("profitability_ratios", {})
            leverage = ratios.get("leverage_ratios", {})
            efficiency = ratios.get("efficiency_ratios", {})
            cashflow = ratios.get("cashflow_ratios", {})
            growth = ratios.get("growth_ratios", {})
            
            # 盈利能力分析
            prof_analysis = f"""
            该公司最新财务报告显示：
            - 净资产收益率(ROE): {profitability.get('roe', 'N/A'):.2f}%
            - 总资产回报率(ROA): {profitability.get('roa', 'N/A'):.2f}%
            - 毛利率: {profitability.get('gross_profit_margin', 'N/A'):.2f}%
            - 净利率: {profitability.get('net_profit_margin', 'N/A'):.2f}%
            
            盈利能力分析表明公司在股东回报和资产利用效率方面的表现。
            """
            
            # 偿债能力分析
            debt_analysis = f"""
            偿债能力指标显示：
            - 资产负债率: {leverage.get('debt_to_asset_ratio', 'N/A'):.2f}%
            - 权益乘数: {leverage.get('equity_multiplier', 'N/A'):.2f}
            
            这些指标反映了公司的财务杠杆水平和偿债风险。
            """
            
            # 现金流分析  
            cf_analysis = f"""
            现金流分析结果：
            - 经营现金流与净利润比: {cashflow.get('ocf_to_net_income', 'N/A'):.2f}
            - 自由现金流: {cashflow.get('free_cashflow', 'N/A')}万元
            
            现金流质量是评估公司盈利真实性的重要指标。
            """
            
            report_sections.update({
                "core_conclusion": f"基于财务指标分析，该公司财务健康度评分为{health_score_data.get('total_score', 0)}分，属于{health_score_data.get('health_level', '未知')}水平。",
                "profitability_analysis": prof_analysis,
                "solvency_analysis": debt_analysis, 
                "cashflow_analysis": cf_analysis,
                "data_sources": "A股数据同步服务API"
            })
            
            # 使用简化的报告模板
            report = f"""
# {stock_name}（{stock_code}）财务指标分析报告

## 执行摘要
- **财务健康度评分**：{report_sections['health_score']}/100分 ({report_sections['health_level']})
- **核心结论**：{report_sections['core_conclusion']}

## 盈利能力分析
{report_sections['profitability_analysis']}

## 偿债能力分析
{report_sections['solvency_analysis']}

## 现金流分析
{report_sections['cashflow_analysis']}

## 综合结论
基于以上财务指标分析，该公司在盈利能力、偿债能力、现金流质量等方面的表现已进行全面评估。
投资者应重点关注财务健康度评分及各项关键指标的变化趋势。

---
**数据来源**：{report_sections['data_sources']}
**分析日期**：{report_sections['analysis_date']}
**报告生成时间**：{report_sections['report_time']}
            """
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating financial analysis report: {str(e)}")
            return f"报告生成失败: {str(e)}"
    
    # 工具列表
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
            
            # 创建提示词模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt),
                MessagesPlaceholder(variable_name="messages")
            ])
            
            # 创建LLM链
            chain = prompt | llm.bind_tools(tools)
            
            # 执行分析
            messages = state.get("messages", [])
            if not messages:
                messages = [{"role": "user", "content": user_prompt}]
            
            result = chain.invoke({"messages": messages})
            
            # 处理工具调用结果
            financial_report = ""
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # 如果有工具调用，处理工具调用结果
                # 这里简化处理，实际应该执行工具调用
                financial_report = f"{stock_name}（{stock_code}）财务分析已启动，正在处理财务数据..."
            else:
                # 如果没有工具调用，使用LLM直接回答
                financial_report = result.content
            
            logger.info("Financial analysis completed")
            
            return {
                "messages": [result],
                "financial_analysis_report": financial_report,
                "analysis_stage": AnalysisStage.FINANCIAL_ANALYSIS,
                "financial_data": state.get("financial_data", {}),
                "key_financial_metrics": {},  # 从分析中提取
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