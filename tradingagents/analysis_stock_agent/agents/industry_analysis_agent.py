"""
行业分析Agent - 基于LLM的智能行业分析师
使用大语言模型进行A股行业地位分析和竞争优势评估
"""
import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..tools.ashare_toolkit import AShareToolkit
from ..utils.analysis_states import AnalysisStatus, DataSource

logger = logging.getLogger(__name__)


def create_industry_analysis_agent(llm, ashare_toolkit: AShareToolkit):
    """创建行业分析Agent - 基于LLM的智能行业分析师"""
    
    def industry_analyst_node(state):
        """行业分析Agent节点 - 使用LLM进行深度行业分析"""
        symbol = state.get("symbol")
        company_name = state.get("company_name", symbol)
        current_date = state.get("analysis_date", "当前")
        
        # 获取行业分析工具
        if ashare_toolkit.config.get("online_tools", True):
            tools = [
                ashare_toolkit.get_sw_industry_competitors,
                ashare_toolkit.get_stock_sw_industry_hierarchy,
                ashare_toolkit.get_sw_industry_info,
                ashare_toolkit.analyze_sw_industry_constituents,
                ashare_toolkit.batch_get_financial_ratios
            ]
        else:
            tools = [
                ashare_toolkit.get_sw_industry_competitors,
                ashare_toolkit.get_stock_sw_industry_hierarchy,
                ashare_toolkit.batch_get_financial_ratios
            ]
        
        system_message = (
            "你是一位资深的A股行业研究专家，拥有超过12年的行业分析和策略研究经验。"
            "你擅长基于申万行业分类体系，对A股上市公司进行精准的行业地位分析和竞争优势评估。\n\n"
            "你的分析框架包括：\n"
            "1. **申万行业分类解读** - 基于申万一、二、三级行业分类，准确定位公司所处细分行业\n"
            "2. **行业竞争格局分析** - 识别主要竞争对手，分析市场集中度和竞争态势\n"
            "3. **财务指标行业对比** - 将公司关键财务指标与同行业公司进行客观对比\n"
            "4. **竞争优势识别** - 基于数据分析识别公司相对竞争对手的优势和劣势\n"
            "5. **行业发展趋势评估** - 分析行业整体发展阶段、成长性和未来前景\n"
            "6. **市场地位评级** - 综合评估公司在行业中的地位和竞争力等级\n"
            "7. **投资角度行业建议** - 从投资价值角度提供行业配置建议\n\n"
            "分析要求：\n"
            "- 严格基于申万行业分类数据，避免主观臆测\n"
            "- 重点关注相对竞争优势，而非绝对指标\n"
            "- 识别可能影响公司行业地位的关键因素\n"
            "- 结合A股市场特点和行业发展阶段分析\n"
            "- 提供具体的数据支撑和同业对比证据\n"
            "- 最后给出明确的行业竞争力评级和投资建议"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "你是一位专业的A股行业研究分析师，正在协助投资团队进行行业地位评估。"
                "使用提供的工具获取申万行业数据和竞争对手信息，基于你的专业知识进行客观分析。"
                "如果某些数据无法获取，请说明数据限制并基于可用信息进行分析。"
                "你的分析将直接影响投资决策，请确保基于事实、客观严谨。\n"
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
            "content": f"请对{company_name}({symbol})进行全面的行业地位分析。"
                      f"需要获取申万行业分类信息、竞争对手数据、同业财务对比等，"
                      f"并基于这些数据分析公司在行业中的竞争地位和投资价值。"
                      f"特别关注：1)申万行业精准分类 2)主要竞争对手识别 3)关键财务指标同业对比 4)竞争优势劣势分析。"
        }
        
        messages = [initial_message]
        result = chain.invoke({"messages": messages})
        
        # 处理工具调用结果
        industry_report = ""
        if len(result.tool_calls) == 0:
            industry_report = result.content
        else:
            # 如果有工具调用，这里可以处理工具执行结果
            industry_report = result.content or "行业分析进行中，正在获取申万行业数据..."
        
        return {
            "messages": [result],
            "industry_analysis_report": industry_report,
            "analysis_status": AnalysisStatus.COMPLETED,
            "competitive_score": None,  # 可以从LLM响应中解析评分
        }
    
    return industry_analyst_node


# 工具函数 - 兼容性包装
async def create_industry_analysis_agent_legacy(config: Dict[str, Any], 
                                               ashare_toolkit: AShareToolkit):
    """创建行业分析Agent实例 - 兼容旧版本API"""
    # 从config中获取LLM实例
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=config.get("deep_think_llm", "gpt-4o"),
        base_url=config.get("backend_url", "https://api.openai.com/v1")
    )
    
    return create_industry_analysis_agent(llm, ashare_toolkit)