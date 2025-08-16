"""
A股分析系统配置模块

包含系统配置、分析参数配置、行业配置等。
"""

from .a_share_config import (
    A_SHARE_DEFAULT_CONFIG,
    ANALYSIS_DEPTH_CONFIG,
    INDUSTRY_CONFIG,
    DATA_SOURCE_CONFIG,
    get_analysis_config
)

__all__ = [
    "A_SHARE_DEFAULT_CONFIG",
    "ANALYSIS_DEPTH_CONFIG", 
    "INDUSTRY_CONFIG",
    "DATA_SOURCE_CONFIG",
    "get_analysis_config",
]