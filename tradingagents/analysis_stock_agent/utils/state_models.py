"""
A股分析系统状态模型定义

定义了分析过程中使用的状态数据结构，包括输入数据、分析结果、元数据等。
"""

from typing import Annotated, Dict, List, Optional, Any
from typing_extensions import TypedDict
from langgraph.graph import MessagesState, add_messages
from datetime import datetime
import operator


class StockAnalysisState(MessagesState):
    """A股分析主状态模型"""
    
    # 基础信息
    stock_code: Annotated[str, "A股代码 (e.g., 000001.SZ)"]
    stock_name: Annotated[str, "股票名称"]
    analysis_date: Annotated[str, "分析日期 YYYY-MM-DD"]
    analyst_name: Annotated[str, "分析师/用户名称"]
    
    # 原始数据
    financial_data: Annotated[Dict[str, Any], "财务报表数据"]
    industry_data: Annotated[Dict[str, Any], "行业数据"]
    market_data: Annotated[Dict[str, Any], "市场交易数据"] 
    peer_data: Annotated[Dict[str, Any], "同业对比数据"]
    technical_data: Annotated[Dict[str, Any], "技术指标数据"]
    
    # 分析报告
    financial_analysis_report: Annotated[str, "财务指标分析报告"]
    industry_analysis_report: Annotated[str, "行业对比分析报告"]
    valuation_analysis_report: Annotated[str, "估值分析报告"]
    integrated_analysis_report: Annotated[str, "综合分析报告"]
    
    # 分析元数据
    analysis_stage: Annotated[List[str], operator.add, "当前分析阶段列表"]
    confidence_score: Annotated[float, "分析置信度 (0-1)"]
    data_quality_score: Annotated[float, "数据质量评分 (0-1)"]
    analysis_depth: Annotated[str, "分析深度 (basic/standard/comprehensive)"]
    
    # 投资建议
    investment_rating: Annotated[str, "投资评级 (强烈推荐/推荐/中性/减持/卖出)"]
    target_price: Annotated[Optional[float], "目标价位"]
    risk_level: Annotated[str, "风险等级 (低/中/高)"]
    investment_horizon: Annotated[str, "投资期限 (短期/中期/长期)"]
    
    # 关键指标摘要
    key_financial_metrics: Annotated[Dict[str, float], "关键财务指标"]
    key_valuation_metrics: Annotated[Dict[str, float], "关键估值指标"]
    industry_ranking: Annotated[Dict[str, Any], "行业排名信息"]
    
    # 数据来源追踪
    data_sources: Annotated[List[str], "使用的数据源列表"]
    api_calls_made: Annotated[List[str], "调用的API列表"]
    calculation_methods: Annotated[Dict[str, str], "计算方法说明"]
    
    # 时间戳
    analysis_start_time: Annotated[str, "分析开始时间"]
    analysis_end_time: Annotated[str, "分析结束时间"]
    last_updated: Annotated[str, "最后更新时间"]


class FinancialAnalysisState(TypedDict):
    """财务分析子状态"""
    profitability_metrics: Annotated[Dict[str, float], "盈利能力指标"]
    liquidity_metrics: Annotated[Dict[str, float], "流动性指标"] 
    leverage_metrics: Annotated[Dict[str, float], "杠杆指标"]
    efficiency_metrics: Annotated[Dict[str, float], "运营效率指标"]
    growth_metrics: Annotated[Dict[str, float], "成长性指标"]
    cashflow_metrics: Annotated[Dict[str, float], "现金流指标"]
    
    financial_health_score: Annotated[float, "财务健康度评分 (0-100)"]
    financial_trend: Annotated[str, "财务趋势 (改善/稳定/恶化)"]
    financial_analysis_summary: Annotated[str, "财务分析摘要"]


class IndustryAnalysisState(TypedDict):
    """行业分析子状态"""
    industry_info: Annotated[Dict[str, Any], "申万行业分类信息"]
    industry_growth_rate: Annotated[float, "行业增长率"]
    market_concentration: Annotated[float, "市场集中度"]
    competitive_position: Annotated[str, "竞争地位 (领先/跟随/落后)"]
    
    peer_comparison: Annotated[Dict[str, Any], "同业对比结果"]
    competitive_advantages: Annotated[List[str], "竞争优势列表"]
    industry_risks: Annotated[List[str], "行业风险列表"]
    
    industry_analysis_summary: Annotated[str, "行业分析摘要"]


class ValuationAnalysisState(TypedDict):
    """估值分析子状态"""
    relative_valuation: Annotated[Dict[str, float], "相对估值指标 (PE, PB, PS等)"]
    absolute_valuation: Annotated[Dict[str, float], "绝对估值结果"]
    historical_valuation: Annotated[Dict[str, Any], "历史估值分位数"]
    
    valuation_level: Annotated[str, "估值水平 (低估/合理/高估)"]
    valuation_risk: Annotated[str, "估值风险 (低/中/高)"]
    price_targets: Annotated[Dict[str, float], "价格目标 (保守/中性/乐观)"]
    
    market_sentiment: Annotated[str, "市场情绪"]
    technical_signals: Annotated[Dict[str, Any], "技术信号"]
    
    valuation_analysis_summary: Annotated[str, "估值分析摘要"]


class IntegrationAnalysisState(TypedDict):
    """整合分析子状态"""
    overall_score: Annotated[float, "综合评分 (0-100)"]
    investment_thesis: Annotated[str, "投资逻辑"]
    key_investment_highlights: Annotated[List[str], "投资亮点"]
    key_risk_factors: Annotated[List[str], "关键风险因素"]
    
    recommendation_rationale: Annotated[str, "推荐理由"]
    risk_assessment: Annotated[str, "风险评估"]
    portfolio_fit: Annotated[str, "组合适配性"]
    
    action_items: Annotated[List[str], "行动建议"]
    follow_up_schedule: Annotated[str, "跟踪计划"]


# 分析阶段常量
class AnalysisStage:
    INIT = "initialization"
    DATA_COLLECTION = "data_collection"
    FINANCIAL_ANALYSIS = "financial_analysis" 
    INDUSTRY_ANALYSIS = "industry_analysis"
    VALUATION_ANALYSIS = "valuation_analysis"
    INTEGRATION_ANALYSIS = "integration_analysis"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"
    ERROR = "error"


# 投资评级常量
class InvestmentRating:
    STRONG_BUY = "强烈推荐"
    BUY = "推荐"
    HOLD = "中性"
    REDUCE = "减持"
    SELL = "卖出"


# 风险等级常量  
class RiskLevel:
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


# 分析深度常量
class AnalysisDepth:
    BASIC = "basic"
    STANDARD = "standard" 
    COMPREHENSIVE = "comprehensive"