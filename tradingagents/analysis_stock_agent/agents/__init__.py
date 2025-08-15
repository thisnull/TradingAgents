"""
分析Agent模块
实现4个核心分析Agent：财务分析、行业分析、估值分析、报告整合
"""

from .financial_analysis_agent import (
    FinancialAnalysisAgent,
    FinancialMetrics,
    create_financial_analysis_agent
)

from .industry_analysis_agent import (
    IndustryAnalysisAgent,
    IndustryMetrics,
    CompetitorInfo,
    create_industry_analysis_agent
)

from .valuation_analysis_agent import (
    ValuationAnalysisAgent,
    ValuationMetrics,
    MarketSignal,
    create_valuation_analysis_agent
)

from .report_integration_agent import (
    ReportIntegrationAgent,
    IntegratedMetrics,
    create_report_integration_agent
)

__all__ = [
    # 财务分析Agent
    "FinancialAnalysisAgent",
    "FinancialMetrics", 
    "create_financial_analysis_agent",
    
    # 行业分析Agent
    "IndustryAnalysisAgent",
    "IndustryMetrics",
    "CompetitorInfo",
    "create_industry_analysis_agent",
    
    # 估值分析Agent
    "ValuationAnalysisAgent",
    "ValuationMetrics", 
    "MarketSignal",
    "create_valuation_analysis_agent",
    
    # 报告整合Agent
    "ReportIntegrationAgent",
    "IntegratedMetrics",
    "create_report_integration_agent"
]