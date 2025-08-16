"""
A股投资分析Multi-Agent系统

这个模块提供了专门针对A股市场的投资分析multi-agent框架，
包含4个核心分析代理：
- 财务指标分析Agent
- 行业对比分析Agent  
- 估值分析Agent
- 信息整合Agent

基于TradingAgents框架，使用LangGraph进行工作流orchestration。
"""

from .graph.a_share_analysis_graph import AShareAnalysisGraph
from .config.a_share_config import A_SHARE_DEFAULT_CONFIG
from .utils.state_models import StockAnalysisState, AnalysisStage, AnalysisDepth

__version__ = "1.0.0"
__author__ = "TradingAgents Team"

__all__ = [
    "AShareAnalysisGraph",
    "A_SHARE_DEFAULT_CONFIG",
    "StockAnalysisState",
    "AnalysisStage",
    "AnalysisDepth"
]