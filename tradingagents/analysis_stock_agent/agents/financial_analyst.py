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
    def prepare_analysis_data_for_llm(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备分析数据供LLM生成智能报告
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            格式化的分析数据字典
        """
        try:
            logger.info("Preparing analysis data for LLM report generation")
            
            stock_code = analysis_data.get("stock_code", "")
            stock_name = analysis_data.get("stock_name", "")
            
            # 基础信息
            basic_info = analysis_data.get("basic_info", {})
            if basic_info and "name" in basic_info:
                stock_name = basic_info["name"]
            
            # 财务比率
            ratios = analysis_data.get("financial_ratios", {})
            health_score_data = analysis_data.get("health_score", {})
            
            # 准备结构化数据供LLM分析
            structured_data = {
                "company_info": {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                    "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                "raw_financial_data": analysis_data.get("latest_report", {}),
                "historical_reports": analysis_data.get("financial_reports", []),
                "financial_summary": analysis_data.get("financial_summary", {})
            }
            
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
基于以下财务分析数据，请生成一份专业、深入的财务分析报告：

## 公司基本信息
股票代码：{stock_code}
股票名称：{stock_name}
分析日期：{analysis_date}

## 财务健康度评分
总分：{health_score}/100分
健康等级：{health_level}
评分明细：{score_breakdown}

## 财务比率数据
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

## 原始财务数据
{raw_financial_data}

**请基于以上真实数据，按照你的专业分析框架，生成一份深入、专业的财务分析报告。**

**重要要求：**
1. 必须深度解读每个财务指标背后的经营含义
2. 识别关键风险和机会
3. 提供具体的投资建议和风险提示
4. 展现AI的分析洞察能力，不要简单罗列数据
5. 报告要有明确的结论和建议
                        """)
                    ])
                    
                    # 使用LLM生成报告
                    chain = prompt | llm
                    
                    # 准备输入数据
                    llm_input = {
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "analysis_date": analysis_date,
                        "health_score": health_score.get("total_score", 0),
                        "health_level": health_score.get("health_level", "未知"),
                        "score_breakdown": json.dumps(health_score.get("score_breakdown", {}), ensure_ascii=False, indent=2),
                        "profitability_ratios": json.dumps(financial_ratios.get("profitability_ratios", {}), ensure_ascii=False, indent=2),
                        "leverage_ratios": json.dumps(financial_ratios.get("leverage_ratios", {}), ensure_ascii=False, indent=2),
                        "efficiency_ratios": json.dumps(financial_ratios.get("efficiency_ratios", {}), ensure_ascii=False, indent=2),
                        "cashflow_ratios": json.dumps(financial_ratios.get("cashflow_ratios", {}), ensure_ascii=False, indent=2),
                        "growth_ratios": json.dumps(financial_ratios.get("growth_ratios", {}), ensure_ascii=False, indent=2),
                        "raw_financial_data": json.dumps(financial_data.get("latest_report", {}), ensure_ascii=False, indent=2)[:2000]  # 限制长度
                    }
                    
                    # 验证输入数据完整性
                    if not all([
                        llm_input.get("health_score", 0),
                        llm_input.get("profitability_ratios", "{}") != "{}",
                        llm_input.get("stock_code"),
                        llm_input.get("stock_name")
                    ]):
                        logger.warning("⚠️ LLM输入数据不完整，可能影响报告质量")
                        logger.warning(f"健康度评分: {llm_input.get('health_score', 0)}")
                        logger.warning(f"盈利能力指标: {llm_input.get('profitability_ratios', '空')[:100]}")
                    
                    logger.debug(f"LLM输入数据检查完成，数据键: {list(llm_input.keys())}")
                    
                    # 调用LLM生成智能分析报告
                    logger.info(f"正在调用LLM生成分析报告，输入数据键: {list(llm_input.keys())}")
                    logger.debug(f"LLM输入数据预览: stock_code={llm_input.get('stock_code')}, health_score={llm_input.get('health_score')}")
                    
                    llm_result = chain.invoke(llm_input)
                    financial_report = llm_result.content
                    
                    # 关键修复：检查并记录LLM返回的完整结果
                    logger.info(f"✅ LLM调用成功")
                    logger.info(f"LLM返回结果类型: {type(llm_result)}")
                    logger.info(f"LLM返回内容字符数: {len(financial_report) if financial_report else 0}")
                    logger.info(f"LLM返回内容前100字符: {financial_report[:100] if financial_report else 'None或空字符串'}")
                    logger.info(f"LLM返回内容后100字符: {financial_report[-100:] if financial_report and len(financial_report) > 100 else '内容不足100字符'}")
                    
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