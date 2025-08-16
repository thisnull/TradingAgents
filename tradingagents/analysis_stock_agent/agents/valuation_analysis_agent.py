"""
估值分析Agent - 基于LLM的智能估值分析师
使用大语言模型进行A股估值水平分析和投资时机判断
"""
import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..tools.ashare_toolkit import AShareToolkit
from ..utils.analysis_states import AnalysisStatus, DataSource

logger = logging.getLogger(__name__)


def create_valuation_analysis_agent(llm, ashare_toolkit: AShareToolkit):
    """创建估值分析Agent - 基于LLM的智能估值分析师"""
    
    def valuation_analyst_node(state):
        """估值分析Agent节点 - 使用LLM进行深度估值分析"""
        symbol = state.get("symbol")
        company_name = state.get("company_name", symbol)
        current_date = state.get("analysis_date", "当前")
        
        # 获取估值分析工具
        if ashare_toolkit.config.get("online_tools", True):
            tools = [
                ashare_toolkit.get_daily_quotes,
                ashare_toolkit.get_financial_ratios,
                ashare_toolkit.get_financial_reports,
                ashare_toolkit.get_stock_basic_info
            ]
        else:
            tools = [
                ashare_toolkit.get_daily_quotes,
                ashare_toolkit.get_financial_ratios,
                ashare_toolkit.get_stock_basic_info
            ]
        
        system_message = (
            "你是一位资深的A股估值分析专家，拥有超过15年的投资银行和资产管理经验。"
            "你擅长运用多种估值方法，对A股上市公司进行全面的估值分析和投资时机判断。\n\n"
            "你的估值分析框架包括：\n"
            "1. **相对估值分析** - PE、PB、PS等市场倍数的历史分位和行业对比分析\n"
            "2. **PEG估值模型** - 基于成长性调整的估值水平评估\n"
            "3. **历史估值回归分析** - 分析估值的历史波动区间和均值回归特征\n"
            "4. **股价技术面分析** - 结合技术指标判断当前股价的技术位置\n"
            "5. **市场情绪评估** - 分析当前市场对该股票的情绪偏向\n"
            "6. **投资时机判断** - 基于估值水平判断买入、持有、卖出时机\n"
            "7. **目标价格测算** - 基于合理估值区间给出目标价格区间\n\n"
            "分析要求：\n"
            "- 结合多种估值方法进行交叉验证\n"
            "- 重点关注估值的相对性而非绝对水平\n"
            "- 考虑A股市场的估值特征和投资者结构\n"
            "- 结合公司基本面变化判断估值合理性\n"
            "- 提供明确的投资时机建议和风险提示\n"
            "- 给出具体的目标价格区间和持有期建议"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "你是一位专业的A股估值分析师，正在协助投资团队进行估值评估和投资时机判断。"
                "使用提供的工具获取股价、财务和市场数据，基于你的专业知识进行估值分析。"
                "如果某些数据无法获取，请说明数据限制并基于可用信息进行分析。"
                "你的分析将直接影响投资时机选择，请确保客观、严谨、实用。\n"
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
            "content": f"请对{company_name}({symbol})进行全面的估值分析。"
                      f"需要获取当前股价、历史行情、财务比率、基本面数据等，"
                      f"并基于这些数据进行多维度估值评估和投资时机判断。"
                      f"特别关注：1)当前估值水平的合理性 2)历史估值分位分析 3)投资时机判断 4)目标价格测算。"
        }
        
        messages = [initial_message]
        result = chain.invoke({"messages": messages})
        
        # 处理工具调用结果
        valuation_report = ""
        if len(result.tool_calls) == 0:
            valuation_report = result.content
        else:
            # 如果有工具调用，这里可以处理工具执行结果
            valuation_report = result.content or "估值分析进行中，正在获取市场数据..."
        
        return {
            "messages": [result],
            "valuation_analysis_report": valuation_report,
            "analysis_status": AnalysisStatus.COMPLETED,
            "valuation_score": None,  # 可以从LLM响应中解析评分
            "target_price": None,     # 可以从LLM响应中解析目标价
        }
    
    return valuation_analyst_node


# 工具函数 - 兼容性包装
async def create_valuation_analysis_agent_legacy(config: Dict[str, Any], 
                                                ashare_toolkit: AShareToolkit):
    """创建估值分析Agent实例 - 兼容旧版本API"""
    # 从config中获取LLM实例
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=config.get("deep_think_llm", "gpt-4o"),
        base_url=config.get("backend_url", "https://api.openai.com/v1")
    )
    
    return create_valuation_analysis_agent(llm, ashare_toolkit)