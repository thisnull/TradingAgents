"""
A股分析Multi-Agent System

专门针对A股市场的智能分析系统，通过Multi-Agent协作机制，
为投资者提供全面、专业的投资分析报告。
"""

from .agents import (
    FinancialAnalystAgent,
    IndustryAnalystAgent,
    ValuationAnalystAgent,
    ReportIntegrationAgent,
)

from .tools import AStockToolkit

from .graph import StockAnalysisGraph

from .config import StockAnalysisConfig

__version__ = "1.0.0"

__all__ = [
    "FinancialAnalystAgent",
    "IndustryAnalystAgent", 
    "ValuationAnalystAgent",
    "ReportIntegrationAgent",
    "AStockToolkit",
    "StockAnalysisGraph",
    "StockAnalysisConfig",
]
