"""
Agent状态定义
定义Multi-Agent系统中的状态管理
"""

from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

class StockAnalysisState(MessagesState):
    """A股分析系统的全局状态"""
    
    # 基础信息
    stock_code: Annotated[str, "股票代码（6位数字）"]
    company_name: Annotated[str, "公司名称"]
    analysis_date: Annotated[str, "分析日期（YYYY-MM-DD）"]
    
    # 原始数据状态
    raw_financial_data: Annotated[Dict[str, Any], "原始财务数据"]
    raw_industry_data: Annotated[Dict[str, Any], "原始行业数据"]
    raw_market_data: Annotated[Dict[str, Any], "原始市场数据"]
    
    # 财务分析状态
    financial_report: Annotated[str, "财务分析报告"]
    financial_score: Annotated[float, "财务健康评分（0-100）"]
    financial_metrics: Annotated[Dict[str, Any], "关键财务指标"]
    financial_risks: Annotated[List[str], "财务风险点"]
    
    # 行业分析状态
    industry_report: Annotated[str, "行业对比报告"]
    industry_position: Annotated[str, "行业地位评估"]
    competitive_advantages: Annotated[List[str], "竞争优势列表"]
    industry_ranking: Annotated[Dict[str, int], "行业排名情况"]
    
    # 估值分析状态
    valuation_report: Annotated[str, "估值分析报告"]
    pr_ratio: Annotated[float, "PR值(PE/ROE)"]
    pe_percentile: Annotated[float, "PE历史百分位"]
    shareholder_structure: Annotated[Dict[str, Any], "股东结构分析"]
    valuation_level: Annotated[str, "估值水平（低估/合理/高估）"]
    
    # 最终报告状态
    final_report: Annotated[str, "完整分析报告"]
    investment_rating: Annotated[str, "投资评级"]
    target_price: Annotated[float, "目标价格"]
    key_risks: Annotated[List[str], "主要风险提示"]
    key_opportunities: Annotated[List[str], "主要机会点"]
    
    # 决策支持
    confidence_score: Annotated[float, "决策置信度（0-100）"]
    data_quality_score: Annotated[float, "数据质量评分（0-100）"]
    
    # 元数据
    analysis_version: Annotated[str, "分析版本"]
    analysis_duration: Annotated[float, "分析耗时（秒）"]
    error_messages: Annotated[List[str], "错误信息列表"]
