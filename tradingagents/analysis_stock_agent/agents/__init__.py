"""
A股分析代理模块

包含4个专业化的分析代理：
- financial_analyst: 财务指标分析代理
- industry_analyst: 行业对比分析代理  
- valuation_analyst: 估值分析代理
- information_integrator: 信息整合代理
"""

from .financial_analyst import create_financial_analyst
from .industry_analyst import create_industry_analyst  
from .valuation_analyst import create_valuation_analyst
from .information_integrator import create_information_integrator

__all__ = [
    "create_financial_analyst",
    "create_industry_analyst",
    "create_valuation_analyst", 
    "create_information_integrator",
]