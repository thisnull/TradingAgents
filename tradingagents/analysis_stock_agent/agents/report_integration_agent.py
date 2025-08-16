"""
报告整合Agent - 基于LLM的智能报告整合师
使用大语言模型整合各专业分析，生成综合投资研究报告
"""
import logging
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from ..utils.analysis_states import AnalysisStatus, DataSource

logger = logging.getLogger(__name__)


def create_report_integration_agent(llm):
    """创建报告整合Agent - 基于LLM的智能报告整合师"""
    
    def report_integration_node(state):
        """报告整合Agent节点 - 使用LLM进行综合分析报告生成"""
        symbol = state.get("symbol")
        company_name = state.get("company_name", symbol)
        current_date = state.get("analysis_date", "当前")
        
        # 获取各专业分析的结果
        financial_report = state.get("financial_analysis_report", "")
        industry_report = state.get("industry_analysis_report", "")
        valuation_report = state.get("valuation_analysis_report", "")
        
        system_message = (
            "你是一位资深的投资研究总监，拥有超过20年的证券研究和投资管理经验。"
            "你的任务是整合财务分析师、行业分析师、估值分析师的专业报告，"
            "形成一份综合的投资研究报告，为投资决策提供全面、客观的分析结论。\n\n"
            "报告整合框架：\n"
            "1. **执行摘要** - 核心投资观点和关键结论的高度概括（200字以内）\n"
            "2. **投资亮点** - 该投资标的最具吸引力的3-5个核心优势\n"
            "3. **关键风险** - 需要重点关注的3-5个主要投资风险\n"
            "4. **财务质量评估** - 基于财务分析的公司基本面健康度结论\n"
            "5. **行业竞争地位** - 基于行业分析的公司竞争优势和市场地位\n"
            "6. **估值与时机** - 基于估值分析的当前投资价值和时机判断\n"
            "7. **综合投资建议** - 明确的投资建议（强烈推荐/推荐/中性/不推荐）\n"
            "8. **目标价格与期限** - 具体的目标价格区间和预期持有期\n\n"
            "整合要求：\n"
            "- 保持各专业分析的核心观点和关键数据\n"
            "- 识别不同分析之间的一致性和分歧点\n"
            "- 基于综合分析形成平衡、客观的投资判断\n"
            "- 避免简单罗列，要有逻辑性和层次感\n"
            "- 突出对投资决策最关键的信息\n"
            "- 语言精炼专业，适合机构投资者阅读"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "你是一位专业的投资研究总监，正在整合团队各专业分析师的研究成果。"
                "基于提供的财务分析、行业分析、估值分析报告，形成综合投资研究报告。"
                "如果某些分析报告缺失或不完整，请说明信息限制并基于可用信息进行整合。"
                "你的报告将直接服务于投资决策，请确保结论明确、逻辑清晰、风险充分揭示。\n"
                "{system_message}\n"
                "当前整合日期: {current_date}\n"
                "分析标的: {company_name} ({symbol})"
            ),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(company_name=company_name)
        prompt = prompt.partial(symbol=symbol)
        
        chain = prompt | llm
        
        # 构建整合消息
        integration_content = f"请基于以下专业分析报告，为{company_name}({symbol})生成综合投资研究报告：\n\n"
        
        if financial_report:
            integration_content += f"**财务分析报告：**\n{financial_report}\n\n"
        else:
            integration_content += "**财务分析报告：** 暂未获得完整财务分析\n\n"
            
        if industry_report:
            integration_content += f"**行业分析报告：**\n{industry_report}\n\n"
        else:
            integration_content += "**行业分析报告：** 暂未获得完整行业分析\n\n"
            
        if valuation_report:
            integration_content += f"**估值分析报告：**\n{valuation_report}\n\n"
        else:
            integration_content += "**估值分析报告：** 暂未获得完整估值分析\n\n"
        
        integration_content += ("请整合以上分析，形成逻辑清晰、结论明确的综合投资研究报告。"
                              "特别注意识别各分析之间的一致性和分歧，形成平衡的投资判断。")
        
        initial_message = {
            "role": "user",
            "content": integration_content
        }
        
        messages = [initial_message]
        result = chain.invoke({"messages": messages})
        
        # 提取综合评分和投资建议
        comprehensive_report = result.content
        
        return {
            "messages": [result],
            "comprehensive_analysis_report": comprehensive_report,
            "analysis_status": AnalysisStatus.COMPLETED,
            "investment_recommendation": None,  # 可以从LLM响应中解析投资建议
            "comprehensive_score": None,        # 可以从LLM响应中解析综合评分
        }
    
    return report_integration_node


# 工具函数 - 兼容性包装
async def create_report_integration_agent_legacy(config: Dict[str, Any]):
    """创建报告整合Agent实例 - 兼容旧版本API"""
    # 从config中获取LLM实例
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=config.get("deep_think_llm", "gpt-4o"),
        base_url=config.get("backend_url", "https://api.openai.com/v1")
    )
    
    return create_report_integration_agent(llm)