"""
财务分析Agent - 基于LLM的智能财务分析师
使用大语言模型进行A股财务数据的深度分析和专业解读
"""
import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..tools.ashare_toolkit import AShareToolkit
from ..utils.analysis_states import AnalysisStatus, DataSource

logger = logging.getLogger(__name__)


def create_financial_analysis_agent(llm, ashare_toolkit: AShareToolkit):
    """创建财务分析Agent - 基于LLM的智能财务分析师"""
    
    def financial_analyst_node(state):
        """财务分析Agent节点 - 使用LLM进行深度财务分析"""
        symbol = state.get("symbol")
        company_name = state.get("company_name", symbol)
        current_date = state.get("analysis_date", "当前")
        
        # 获取财务工具
        if ashare_toolkit.config.get("online_tools", True):
            tools = [
                ashare_toolkit.get_financial_reports,
                ashare_toolkit.get_financial_ratios,
                ashare_toolkit.get_financial_summary
            ]
        else:
            tools = [
                ashare_toolkit.get_financial_reports,
                ashare_toolkit.get_financial_ratios
            ]
        
        system_message = (
            "你是一位资深的A股财务分析师，拥有超过15年的投资银行和证券研究经验。"
            "你的任务是对A股上市公司进行深度财务分析，为投资者提供专业、客观的财务健康度评估。\n\n"
            "请按照以下框架进行分析：\n"
            "1. **财务健康度总览** - 公司整体财务状况的快速诊断\n"
            "2. **盈利能力深度分析** - ROE、ROA、净利率等核心指标的趋势分析和行业对比\n"
            "3. **成长性评估** - 营收和利润增长的可持续性分析\n"
            "4. **资产负债结构分析** - 债务风险和资本效率评估\n"
            "5. **现金流质量分析** - 经营现金流与净利润的匹配度分析\n"
            "6. **关键财务风险识别** - 潜在的财务风险点和预警信号\n"
            "7. **投资价值综合评分** - 基于财务数据的投资建议（1-10分）\n\n"
            "要求：\n"
            "- 提供具体的数据支撑，避免空泛的结论\n"
            "- 重点关注趋势变化而非单一时点数据\n"
            "- 结合A股市场特点进行分析\n"
            "- 识别可能影响投资决策的关键财务因素\n"
            "- 最后提供明确的财务健康度评级和投资建议"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "你是一位专业的A股财务分析师，正在协助投资团队进行深度财务分析。"
                "使用提供的工具获取财务数据，并基于你的专业知识进行分析。"
                "如果无法获取完整数据，请说明数据限制并基于可用信息进行分析。"
                "你的分析将帮助投资决策，请确保客观、准确、有洞察力。\n"
                "可用工具: {tool_names}\n{system_message}\n"
                "当前分析日期: {current_date}\n"
                "分析标的: {company_name} ({symbol})"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.__name__ for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(company_name=company_name)
        prompt = prompt.partial(symbol=symbol)
        
        chain = prompt | llm.bind_tools(tools)
        
        # 初始消息
        initial_message = {
            "role": "user",
            "content": f"请对{company_name}({symbol})进行全面的财务分析。"
                      f"需要获取最新的财务报表、财务比率等数据，"
                      f"并从投资角度提供专业的财务健康度评估和投资建议。"
        }
        
        messages = [initial_message]
        result = chain.invoke({"messages": messages})
        
        # 处理工具调用结果
        financial_report = ""
        if len(result.tool_calls) == 0:
            financial_report = result.content
        else:
            # 如果有工具调用，这里可以处理工具执行结果
            financial_report = result.content or "财务分析进行中，正在获取数据..."
        
        return {
            "messages": [result],
            "financial_analysis_report": financial_report,
            "analysis_status": AnalysisStatus.COMPLETED,
            "financial_score": None,  # 可以从LLM响应中解析评分
        }
    
    return financial_analyst_node


# 工具函数 - 兼容性包装
async def create_financial_analysis_agent_legacy(config: Dict[str, Any], 
                                                ashare_toolkit: AShareToolkit):
    """创建财务分析Agent实例 - 兼容旧版本API"""
    # 从config中获取LLM实例，这里需要根据实际配置创建
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=config.get("deep_think_llm", "gpt-4o"),
        base_url=config.get("backend_url", "https://api.openai.com/v1")
    )
    
    return create_financial_analysis_agent(llm, ashare_toolkit)