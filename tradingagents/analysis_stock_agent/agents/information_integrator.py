"""
信息整合Agent

专门负责整合财务分析、行业分析、估值分析等多个维度的研究结果，
形成最终的综合投资分析结论和投资建议。
"""

import json
import logging
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ..utils.data_tools import AShareDataTools, DataProcessor
from ..utils.mcp_tools import MCPToolsWrapper
from ..utils.calculation_utils import FinancialCalculator, RiskCalculator
from ..utils.state_models import AnalysisStage, AnalysisDepth
from ..prompts.integration_prompts import (
    INFORMATION_INTEGRATION_SYSTEM_PROMPT,
    INFORMATION_INTEGRATION_USER_PROMPT,
    COMPREHENSIVE_SCORING_WEIGHTS,
    INVESTMENT_RECOMMENDATION_MATRIX,
    COMPREHENSIVE_ANALYSIS_REPORT_TEMPLATE
)


logger = logging.getLogger(__name__)


def create_information_integrator(llm, toolkit, config):
    """
    创建信息整合Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 工具集
        config: 配置字典
        
    Returns:
        信息整合Agent节点函数
    """
    
    # 初始化数据工具
    data_tools = AShareDataTools(config)
    mcp_tools = MCPToolsWrapper(config) if config.get("mcp_tools_enabled") else None
    
    # 创建分析结果收集工具
    @tool
    def collect_analysis_results(state_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        收集所有分析结果
        
        Args:
            state_data: 状态数据
            
        Returns:
            收集到的分析结果
        """
        try:
            logger.info("Collecting analysis results")
            
            analysis_results = {
                "financial_analysis": {
                    "available": bool(state_data.get("financial_analysis_report")),
                    "report": state_data.get("financial_analysis_report", ""),
                    "data": state_data.get("financial_data", {}),
                    "metrics": state_data.get("key_financial_metrics", {}),
                    "score": None  # 将从报告中提取
                },
                "industry_analysis": {
                    "available": bool(state_data.get("industry_analysis_report")),
                    "report": state_data.get("industry_analysis_report", ""),
                    "data": state_data.get("industry_data", {}),
                    "metrics": state_data.get("key_industry_metrics", {}),
                    "position": state_data.get("competitive_position", {}),
                    "score": None
                },
                "valuation_analysis": {
                    "available": bool(state_data.get("valuation_analysis_report")),
                    "report": state_data.get("valuation_analysis_report", ""),
                    "data": state_data.get("valuation_data", {}),
                    "signals": state_data.get("market_signals", {}),
                    "indicators": state_data.get("technical_indicators", {}),
                    "score": None
                },
                "metadata": {
                    "stock_code": state_data.get("stock_code", ""),
                    "stock_name": state_data.get("stock_name", ""),
                    "analysis_date": state_data.get("analysis_date", ""),
                    "data_sources": state_data.get("data_sources", []),
                    "last_updated": state_data.get("last_updated", "")
                }
            }
            
            # 尝试从报告中提取评分信息
            for analysis_type in ["financial", "industry", "valuation"]:
                report = analysis_results[f"{analysis_type}_analysis"]["report"]
                if report:
                    # 简化的评分提取逻辑（实际应该更复杂）
                    if "评分" in report or "分" in report:
                        # 这里可以用正则表达式提取评分
                        analysis_results[f"{analysis_type}_analysis"]["score"] = 80  # 默认评分
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error collecting analysis results: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def analyze_consistency(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析各维度结果的一致性
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            一致性分析结果
        """
        try:
            logger.info("Analyzing consistency across dimensions")
            
            consistency_analysis = {
                "overall_consistency": "high",  # high/medium/low
                "consistent_signals": [],
                "conflicting_signals": [],
                "uncertainty_areas": [],
                "confidence_level": 0.85  # 0-1
            }
            
            # 检查财务和估值的一致性
            financial_available = analysis_results.get("financial_analysis", {}).get("available", False)
            valuation_available = analysis_results.get("valuation_analysis", {}).get("available", False)
            industry_available = analysis_results.get("industry_analysis", {}).get("available", False)
            
            consistent_signals = []
            conflicting_signals = []
            
            # 简化的一致性分析逻辑
            if financial_available and valuation_available:
                financial_score = analysis_results["financial_analysis"].get("score", 75)
                valuation_score = analysis_results["valuation_analysis"].get("score", 75)
                
                if abs(financial_score - valuation_score) < 10:
                    consistent_signals.append("财务分析与估值分析结论基本一致")
                else:
                    conflicting_signals.append("财务分析与估值分析存在分歧")
            
            if industry_available and financial_available:
                industry_score = analysis_results["industry_analysis"].get("score", 75)
                financial_score = analysis_results["financial_analysis"].get("score", 75)
                
                if abs(industry_score - financial_score) < 15:
                    consistent_signals.append("行业分析与财务分析相互印证")
                else:
                    conflicting_signals.append("行业竞争力与财务表现不匹配")
            
            # 根据一致性信号确定整体一致性水平
            if len(conflicting_signals) == 0:
                overall_consistency = "high"
                confidence_level = 0.9
            elif len(conflicting_signals) <= len(consistent_signals):
                overall_consistency = "medium"
                confidence_level = 0.7
            else:
                overall_consistency = "low"
                confidence_level = 0.5
            
            consistency_analysis.update({
                "overall_consistency": overall_consistency,
                "consistent_signals": consistent_signals,
                "conflicting_signals": conflicting_signals,
                "confidence_level": confidence_level
            })
            
            return consistency_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing consistency: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_comprehensive_score(analysis_results: Dict[str, Any], 
                                    consistency_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算综合投资评分
        
        Args:
            analysis_results: 分析结果
            consistency_analysis: 一致性分析
            
        Returns:
            综合评分结果
        """
        try:
            logger.info("Calculating comprehensive investment score")
            
            # 默认权重配置
            weights = {
                "financial": 0.30,
                "industry": 0.25,
                "valuation": 0.25,
                "market_factors": 0.20
            }
            
            # 获取各维度评分
            financial_score = analysis_results.get("financial_analysis", {}).get("score", 75)
            industry_score = analysis_results.get("industry_analysis", {}).get("score", 75)
            valuation_score = analysis_results.get("valuation_analysis", {}).get("score", 75)
            market_score = 75  # 市场因素综合评分，简化处理
            
            # 基于一致性调整权重
            consistency_level = consistency_analysis.get("overall_consistency", "medium")
            confidence_level = consistency_analysis.get("confidence_level", 0.7)
            
            if consistency_level == "low":
                # 一致性低时，降低整体评分
                adjustment_factor = 0.9
            elif consistency_level == "high":
                # 一致性高时，给予奖励
                adjustment_factor = 1.05
            else:
                adjustment_factor = 1.0
            
            # 计算加权综合评分
            comprehensive_score = (
                financial_score * weights["financial"] +
                industry_score * weights["industry"] +
                valuation_score * weights["valuation"] +
                market_score * weights["market_factors"]
            )
            
            # 应用一致性调整
            comprehensive_score = comprehensive_score * adjustment_factor
            
            # 确保评分在合理范围内
            comprehensive_score = max(0, min(100, comprehensive_score))
            
            # 确定投资建议
            if comprehensive_score >= 90:
                recommendation = "强烈买入"
                position_size = "5-10%"
                investment_horizon = "长期持有（1年以上）"
            elif comprehensive_score >= 80:
                recommendation = "买入"
                position_size = "3-5%"
                investment_horizon = "中长期（6-12个月）"
            elif comprehensive_score >= 70:
                recommendation = "增持"
                position_size = "1-3%"
                investment_horizon = "中期（3-6个月）"
            elif comprehensive_score >= 60:
                recommendation = "持有"
                position_size = "维持现有仓位"
                investment_horizon = "根据后续发展决定"
            elif comprehensive_score >= 50:
                recommendation = "减持"
                position_size = "逐步减少仓位"
                investment_horizon = "短期（1-3个月）"
            else:
                recommendation = "卖出"
                position_size = "清仓或大幅减仓"
                investment_horizon = "立即执行"
            
            return {
                "comprehensive_score": round(comprehensive_score, 1),
                "dimension_scores": {
                    "financial": financial_score,
                    "industry": industry_score,
                    "valuation": valuation_score,
                    "market_factors": market_score
                },
                "weights_used": weights,
                "adjustment_factor": adjustment_factor,
                "investment_recommendation": recommendation,
                "position_sizing": position_size,
                "investment_horizon": investment_horizon,
                "confidence_level": confidence_level,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive score: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def identify_risks_and_catalysts(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        识别风险因素和催化剂
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            风险和催化剂分析
        """
        try:
            logger.info("Identifying risks and catalysts")
            
            risk_factors = {
                "financial_risks": [],
                "industry_risks": [],
                "market_risks": [],
                "valuation_risks": [],
                "overall_risk_level": "medium"  # low/medium/high
            }
            
            catalyst_factors = {
                "positive_catalysts": [],
                "negative_catalysts": [],
                "catalyst_timeline": {},
                "catalyst_impact": "medium"  # low/medium/high
            }
            
            # 从各分析维度中提取风险和催化剂
            financial_data = analysis_results.get("financial_analysis", {})
            industry_data = analysis_results.get("industry_analysis", {})
            valuation_data = analysis_results.get("valuation_analysis", {})
            
            # 财务风险分析
            if financial_data.get("available"):
                financial_score = financial_data.get("score", 75)
                if financial_score < 60:
                    risk_factors["financial_risks"].append("财务健康度偏低")
                if financial_score < 40:
                    risk_factors["financial_risks"].append("财务状况堪忧")
            
            # 行业风险分析
            if industry_data.get("available"):
                industry_score = industry_data.get("score", 75)
                if industry_score < 60:
                    risk_factors["industry_risks"].append("行业竞争地位不佳")
                if industry_score < 40:
                    risk_factors["industry_risks"].append("行业前景悲观")
            
            # 估值风险分析
            if valuation_data.get("available"):
                valuation_score = valuation_data.get("score", 75)
                if valuation_score < 60:
                    risk_factors["valuation_risks"].append("估值偏高风险")
                if valuation_score > 90:
                    catalyst_factors["positive_catalysts"].append("估值修复空间大")
            
            # 通用市场风险
            risk_factors["market_risks"].extend([
                "宏观经济波动风险",
                "政策变化风险",
                "流动性风险"
            ])
            
            # 确定整体风险水平
            total_risks = sum(len(risks) for risks in risk_factors.values() if isinstance(risks, list))
            if total_risks > 6:
                risk_factors["overall_risk_level"] = "high"
            elif total_risks > 3:
                risk_factors["overall_risk_level"] = "medium"
            else:
                risk_factors["overall_risk_level"] = "low"
            
            # 积极催化剂
            catalyst_factors["positive_catalysts"].extend([
                "业绩增长预期",
                "政策利好因素",
                "市场情绪改善"
            ])
            
            return {
                "risk_factors": risk_factors,
                "catalyst_factors": catalyst_factors,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error identifying risks and catalysts: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def develop_investment_strategy(comprehensive_score_data: Dict[str, Any],
                                  risk_catalyst_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        制定投资策略
        
        Args:
            comprehensive_score_data: 综合评分数据
            risk_catalyst_data: 风险和催化剂数据
            
        Returns:
            投资策略建议
        """
        try:
            logger.info("Developing investment strategy")
            
            recommendation = comprehensive_score_data.get("investment_recommendation", "持有")
            comprehensive_score = comprehensive_score_data.get("comprehensive_score", 70)
            risk_level = risk_catalyst_data.get("risk_factors", {}).get("overall_risk_level", "medium")
            
            # 基础策略框架
            strategy = {
                "investment_recommendation": recommendation,
                "target_return": "10-15%",  # 默认预期回报
                "investment_horizon": comprehensive_score_data.get("investment_horizon", "中期"),
                "position_sizing": comprehensive_score_data.get("position_sizing", "1-3%"),
                "buying_strategy": {},
                "holding_strategy": {},
                "selling_strategy": {},
                "risk_management": {}
            }
            
            # 买入策略
            if recommendation in ["强烈买入", "买入", "增持"]:
                strategy["buying_strategy"] = {
                    "approach": "分批建仓" if risk_level == "high" else "适当建仓",
                    "price_levels": ["当前价格", "回调5-10%时加仓"],
                    "timing": "技术指标确认时",
                    "volume": "控制单日成交量占比"
                }
            
            # 持有策略
            strategy["holding_strategy"] = {
                "monitoring_frequency": "每月" if recommendation == "持有" else "每周",
                "rebalancing_trigger": "仓位偏差超过20%",
                "performance_review": "季度业绩跟踪",
                "thesis_validation": "定期验证投资逻辑"
            }
            
            # 卖出策略
            if recommendation in ["减持", "卖出"]:
                strategy["selling_strategy"] = {
                    "approach": "分批减仓",
                    "stop_loss": "跌破重要支撑位",
                    "take_profit": f"达到目标价位（{comprehensive_score + 20}分对应价位）",
                    "timing": "在适当流动性下执行"
                }
            else:
                strategy["selling_strategy"] = {
                    "stop_loss": "跌破止损位（-15%）",
                    "take_profit": "达到目标收益（+25%）",
                    "review_triggers": ["基本面恶化", "行业前景变化"]
                }
            
            # 风险管理
            strategy["risk_management"] = {
                "max_position_size": "10%" if risk_level == "low" else "5%" if risk_level == "medium" else "3%",
                "correlation_check": "与组合其他持仓的相关性",
                "hedge_consideration": "在高风险时考虑对冲",
                "monitoring_indicators": ["财务指标", "行业指标", "技术指标"]
            }
            
            # 预期回报调整
            if comprehensive_score >= 90:
                strategy["target_return"] = "20-30%"
            elif comprehensive_score >= 80:
                strategy["target_return"] = "15-25%"
            elif comprehensive_score >= 70:
                strategy["target_return"] = "10-20%"
            elif comprehensive_score >= 60:
                strategy["target_return"] = "5-15%"
            else:
                strategy["target_return"] = "0-10%"
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error developing investment strategy: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def generate_comprehensive_report(integration_data: Dict[str, Any]) -> str:
        """
        生成综合分析报告
        
        Args:
            integration_data: 整合数据
            
        Returns:
            格式化的综合分析报告
        """
        try:
            logger.info("Generating comprehensive analysis report")
            
            # 获取基础信息
            metadata = integration_data.get("metadata", {})
            stock_code = metadata.get("stock_code", "")
            stock_name = metadata.get("stock_name", "")
            
            # 获取分析结果
            comprehensive_score_data = integration_data.get("comprehensive_score", {})
            consistency_data = integration_data.get("consistency_analysis", {})
            risk_catalyst_data = integration_data.get("risk_catalyst_analysis", {})
            strategy_data = integration_data.get("investment_strategy", {})
            
            # 构建报告内容
            comprehensive_score = comprehensive_score_data.get("comprehensive_score", 70)
            recommendation = comprehensive_score_data.get("investment_recommendation", "持有")
            target_return = strategy_data.get("target_return", "10-15%")
            investment_horizon = strategy_data.get("investment_horizon", "中期")
            
            # 维度评分汇总
            dimension_scores = comprehensive_score_data.get("dimension_scores", {})
            scores_summary = f"""
            - 财务健康度：{dimension_scores.get('financial', 75)}/100分
            - 行业竞争力：{dimension_scores.get('industry', 75)}/100分
            - 估值合理性：{dimension_scores.get('valuation', 75)}/100分
            - 市场因素：{dimension_scores.get('market_factors', 75)}/100分
            """
            
            # 一致性分析
            consistent_signals = consistency_data.get("consistent_signals", [])
            conflicting_signals = consistency_data.get("conflicting_signals", [])
            consistency_summary = f"""
            一致性信号：{'; '.join(consistent_signals) if consistent_signals else '各维度分析基本协调'}
            冲突信号：{'; '.join(conflicting_signals) if conflicting_signals else '无明显冲突'}
            """
            
            # 投资亮点
            risk_factors = risk_catalyst_data.get("risk_factors", {})
            catalyst_factors = risk_catalyst_data.get("catalyst_factors", {})
            
            investment_highlights = '; '.join(catalyst_factors.get("positive_catalysts", ["投资逻辑清晰"]))
            major_risks = '; '.join([
                risk for risk_list in risk_factors.values() 
                if isinstance(risk_list, list) 
                for risk in risk_list
            ][:3])  # 取前3个主要风险
            
            # 投资策略总结
            position_sizing = strategy_data.get("position_sizing", "1-3%")
            buying_approach = strategy_data.get("buying_strategy", {}).get("approach", "适当建仓")
            
            report_sections = {
                "stock_name": stock_name,
                "stock_code": stock_code,
                "comprehensive_score": comprehensive_score,
                "investment_recommendation": recommendation,
                "target_price": "待估算",  # 需要从估值分析中获取
                "current_price": "待获取",  # 需要从市场数据中获取
                "expected_return": target_return,
                "investment_horizon": investment_horizon,
                "core_investment_logic": f"基于多维度分析，该股票综合评分{comprehensive_score}分，{recommendation}",
                "dimension_scores_summary": scores_summary,
                "consistency_analysis": consistency_summary,
                "conflict_points": '; '.join(conflicting_signals) if conflicting_signals else "暂无重大冲突",
                "investment_highlights": investment_highlights,
                "major_risk_factors": major_risks if major_risks else "风险可控",
                "investment_recommendation_rationale": f"基于{comprehensive_score}分的综合评分，建议{recommendation}",
                "position_sizing_recommendation": position_sizing,
                "buying_strategy": buying_approach,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_sources": '; '.join(metadata.get("data_sources", ["A股数据API"]))
            }
            
            # 生成简化的报告
            report = f"""
# {stock_name}（{stock_code}）综合投资分析报告

## 执行摘要
- **综合投资评分**：{report_sections['comprehensive_score']}/100分
- **投资建议**：{report_sections['investment_recommendation']}
- **预期回报**：{report_sections['expected_return']}
- **投资期限**：{report_sections['investment_horizon']}
- **核心逻辑**：{report_sections['core_investment_logic']}

## 分析结果整合

### 各维度评分汇总
{report_sections['dimension_scores_summary']}

### 一致性分析
{report_sections['consistency_analysis']}

### 关键冲突点
{report_sections['conflict_points']}

## 投资评估

### 投资亮点
{report_sections['investment_highlights']}

### 主要风险
{report_sections['major_risk_factors']}

## 投资策略建议

### 投资建议与理由
{report_sections['investment_recommendation_rationale']}

### 仓位配置建议
建议仓位：{report_sections['position_sizing_recommendation']}

### 执行策略
{report_sections['buying_strategy']}

## 结论
基于多维度综合分析，该股票当前投资价值评估为{report_sections['comprehensive_score']}分，
建议投资者{report_sections['investment_recommendation']}，预期回报{report_sections['expected_return']}。

---
**综合分析师**：AI投资分析助手
**分析日期**：{report_sections['analysis_date']}
**报告生成时间**：{report_sections['report_time']}
**数据来源**：{report_sections['data_sources']}

**免责声明**：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
            """
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            return f"报告生成失败: {str(e)}"
    
    # 工具列表
    tools = [
        collect_analysis_results,
        analyze_consistency,
        calculate_comprehensive_score,
        identify_risks_and_catalysts,
        develop_investment_strategy,
        generate_comprehensive_report
    ]
    
    # 如果启用MCP工具，添加MCP相关工具
    if mcp_tools:
        @tool
        def get_mcp_integration_data(stock_code: str) -> Dict[str, Any]:
            """
            使用MCP服务获取整合所需的额外数据
            
            Args:
                stock_code: 股票代码
                
            Returns:
                MCP整合数据
            """
            try:
                return mcp_tools.get_comprehensive_analysis(stock_code)
            except Exception as e:
                logger.error(f"Error getting MCP integration data: {str(e)}")
                return {"error": str(e)}
        
        tools.append(get_mcp_integration_data)
    
    def information_integrator_node(state):
        """
        信息整合Agent节点函数
        
        Args:
            state: 当前分析状态
            
        Returns:
            更新后的状态
        """
        try:
            logger.info("Starting information integration")
            
            # 获取分析参数
            stock_code = state.get("stock_code", "")
            stock_name = state.get("stock_name", "")
            analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
            
            if not stock_code:
                return {
                    "messages": [{"role": "assistant", "content": "错误：缺少股票代码"}],
                    "comprehensive_analysis_report": "分析失败：缺少股票代码",
                    "analysis_stage": AnalysisStage.ERROR
                }
            
            # 检查前置分析是否完成
            has_financial = bool(state.get("financial_analysis_report"))
            has_industry = bool(state.get("industry_analysis_report"))
            has_valuation = bool(state.get("valuation_analysis_report"))
            
            # 构建系统提示词
            system_prompt = INFORMATION_INTEGRATION_SYSTEM_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name,
                analysis_date=analysis_date
            )
            
            # 构建用户提示词
            user_prompt = INFORMATION_INTEGRATION_USER_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name,
                financial_analysis_available=has_financial,
                industry_analysis_available=has_industry,
                valuation_analysis_available=has_valuation
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
            comprehensive_report = ""
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # 执行工具调用并获取结果
                logger.info(f"Executing {len(result.tool_calls)} tool calls")
                
                # 执行所有工具调用
                tool_results = []
                for tool_call in result.tool_calls:
                    tool_name = tool_call.get('name')
                    tool_args = tool_call.get('args', {})
                    
                    # 找到对应的工具并执行
                    for tool in tools:
                        if tool.name == tool_name:
                            try:
                                tool_result = tool.invoke(tool_args)
                                tool_results.append({
                                    "tool_call_id": tool_call.get('id'),
                                    "tool_name": tool_name,
                                    "result": tool_result
                                })
                                logger.info(f"Tool {tool_name} executed successfully")
                            except Exception as tool_error:
                                logger.error(f"Tool {tool_name} failed: {str(tool_error)}")
                                tool_results.append({
                                    "tool_call_id": tool_call.get('id'),
                                    "tool_name": tool_name,
                                    "result": f"工具执行失败: {str(tool_error)}"
                                })
                            break
                
                # 如果有工具调用结果，让LLM基于结果生成完整报告
                if tool_results:
                    # 构建包含工具结果的消息
                    messages_with_tools = messages + [result]
                    for tool_result in tool_results:
                        messages_with_tools.append({
                            "role": "tool",
                            "content": str(tool_result["result"]),
                            "tool_call_id": tool_result["tool_call_id"]
                        })
                    
                    # 让LLM基于工具结果生成最终报告
                    final_result = chain.invoke({"messages": messages_with_tools})
                    comprehensive_report = final_result.content if hasattr(final_result, 'content') else str(final_result)
                    
                    # 更新messages为最终结果
                    result = final_result
                else:
                    # 如果工具调用失败，返回占位符
                    comprehensive_report = f"{stock_name}（{stock_code}）综合分析启动，但工具调用失败"
            else:
                # 如果没有工具调用，使用LLM直接回答
                comprehensive_report = result.content if hasattr(result, 'content') else str(result)
            
            # 计算简化的综合评分（当没有工具调用时）
            if not hasattr(result, 'tool_calls') or not result.tool_calls:
                # 基于已有报告简单估算评分
                available_analyses = sum([has_financial, has_industry, has_valuation])
                base_score = 60 + (available_analyses * 10)  # 基础分60，每个分析+10分
                comprehensive_score = min(100, base_score)
                
                if comprehensive_score >= 80:
                    investment_recommendation = "买入"
                elif comprehensive_score >= 70:
                    investment_recommendation = "增持"
                elif comprehensive_score >= 60:
                    investment_recommendation = "持有"
                else:
                    investment_recommendation = "观望"
            else:
                comprehensive_score = 75  # 默认评分
                investment_recommendation = "持有"
            
            logger.info("Information integration completed")
            
            return {
                "messages": [result],
                "comprehensive_analysis_report": comprehensive_report,
                "analysis_stage": AnalysisStage.INTEGRATION_ANALYSIS,
                "comprehensive_score": comprehensive_score,
                "investment_recommendation": investment_recommendation,
                "integration_data": {},  # 从分析中提取
                "final_conclusion": f"基于多维度分析，{stock_name}综合评分{comprehensive_score}分，建议{investment_recommendation}",
                "data_sources": state.get("data_sources", []) + ["综合分析"],
                "analysis_completed": True,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in information integration: {str(e)}")
            return {
                "messages": [{"role": "assistant", "content": f"信息整合过程中出现错误: {str(e)}"}],
                "comprehensive_analysis_report": f"整合失败: {str(e)}",
                "analysis_stage": AnalysisStage.ERROR
            }
    
    return information_integrator_node