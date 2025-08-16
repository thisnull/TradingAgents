"""
A股分析系统配置

包含A股市场特定的配置参数，继承并扩展了基础TradingAgents配置。
"""

import os
from tradingagents.default_config import DEFAULT_CONFIG


# A股分析系统默认配置
A_SHARE_DEFAULT_CONFIG = {
    # 继承基础配置
    **DEFAULT_CONFIG,
    
    # === A股数据源配置 ===
    "a_share_api_url": "http://localhost:8000/api/v1",
    "a_share_api_key": os.getenv("A_SHARE_API_KEY", ""),
    "a_share_api_timeout": 30,
    "a_share_api_retry_times": 3,
    
    # === MCP服务配置 ===
    "mcp_service_url": "ws://localhost:8001",
    "mcp_service_key": os.getenv("MCP_SERVICE_KEY", ""),
    "mcp_tools_enabled": True,
    "mcp_timeout": 30,
    
    # === LLM配置覆盖 ===
    "llm_provider": "openai",
    "backend_url": "https://oned.lvtu.in",  # 用户自定义endpoint
    "deep_think_llm": "gpt-4o-mini",       # 深度分析使用
    "quick_think_llm": "gpt-4o-mini",      # 快速分析使用
    "report_generation_llm": "gpt-4o",     # 报告生成使用
    
    # === Ollama本地配置 ===
    "ollama_enabled": True,
    "ollama_url": "http://localhost:10000",
    "ollama_embedding_model": "nomic-embed-text",
    "ollama_fallback_enabled": True,
    
    # === 分析参数配置 ===
    "analysis_depth": "comprehensive",     # basic, standard, comprehensive
    "analysis_language": "chinese",        # 报告语言
    "include_charts": True,                # 是否包含图表
    "include_data_sources": True,          # 是否包含数据来源
    "data_update_interval": "daily",       # 数据更新频率
    "analysis_timeout": 300,               # 分析超时时间(秒)
    
    # === A股市场特定配置 ===
    "market_code": "A_SHARE",
    "currency": "CNY", 
    "trading_calendar": "SSE",             # 上交所交易日历
    "market_hours": {
        "morning_start": "09:30",
        "morning_end": "11:30", 
        "afternoon_start": "13:00",
        "afternoon_end": "15:00"
    },
    
    # === 申万行业配置 ===
    "shenwan_industry_enabled": True,
    "shenwan_industry_level": 2,           # 1, 2, 3级行业分类
    "peer_comparison_count": 5,            # 同业对比公司数量
    "industry_analysis_depth": "standard", # 行业分析深度
    
    # === 财务分析配置 ===
    "financial_analysis_periods": 5,       # 分析年份数
    "financial_ratio_categories": [
        "profitability",    # 盈利能力
        "liquidity",        # 流动性 
        "leverage",         # 杠杆
        "efficiency",       # 运营效率
        "growth",           # 成长性
        "cashflow"          # 现金流
    ],
    "benchmark_comparison": True,          # 是否进行基准对比
    
    # === 估值分析配置 ===
    "valuation_methods": [
        "pe_ratio",         # PE估值
        "pb_ratio",         # PB估值
        "ps_ratio",         # PS估值
        "dcf_model",        # DCF模型
        "dividend_model"    # 股利贴现模型
    ],
    "valuation_scenarios": ["conservative", "base", "optimistic"],
    "historical_valuation_periods": 5,     # 历史估值分析年数
    
    # === 技术分析配置 ===
    "technical_indicators": [
        "ma_20",            # 20日均线
        "ma_50",            # 50日均线
        "rsi",              # RSI指标
        "macd",             # MACD指标
        "bollinger_bands"   # 布林带
    ],
    "technical_analysis_period": 252,      # 技术分析交易日数
    
    # === 报告生成配置 ===
    "report_format": "markdown",           # markdown, html, pdf
    "report_template": "pyramid_principle", # 金字塔原理模板
    "report_sections": [
        "executive_summary",   # 执行摘要
        "investment_thesis",   # 投资逻辑
        "financial_analysis",  # 财务分析
        "industry_analysis",   # 行业分析
        "valuation_analysis",  # 估值分析
        "risk_analysis",       # 风险分析
        "recommendation",      # 投资建议
        "appendix"            # 附录
    ],
    "max_report_length": 10000,           # 报告最大字数
    
    # === 数据质量配置 ===
    "data_quality_threshold": 0.8,        # 数据质量最低要求
    "missing_data_tolerance": 0.1,        # 缺失数据容忍度
    "data_freshness_days": 30,            # 数据新鲜度要求(天)
    "data_validation_enabled": True,      # 是否启用数据验证
    
    # === 缓存配置 ===
    "cache_enabled": True,
    "cache_dir": "./cache/a_share_analysis",
    "cache_ttl": {
        "stock_basic": 86400,             # 股票基础信息缓存1天
        "financial_data": 86400,          # 财务数据缓存1天  
        "market_data": 3600,              # 行情数据缓存1小时
        "industry_data": 86400,           # 行业数据缓存1天
        "analysis_result": 3600           # 分析结果缓存1小时
    },
    
    # === 并发配置 ===
    "max_concurrent_analysis": 3,         # 最大并发分析数
    "rate_limit_requests_per_minute": 60, # API请求频率限制
    "agent_timeout": 120,                 # 单个Agent超时时间
    
    # === 日志配置 ===
    "log_level": "INFO",
    "log_file": "./logs/a_share_analysis.log",
    "log_rotation": "daily",
    "log_retention_days": 30,
    
    # === 调试配置 ===
    "debug_mode": False,
    "save_intermediate_results": True,    # 保存中间分析结果
    "verbose_logging": False,
    "performance_monitoring": True,
    
    # === 风险管理配置 ===
    "risk_analysis_enabled": True,
    "risk_factors": [
        "market_risk",        # 市场风险
        "industry_risk",      # 行业风险
        "company_risk",       # 公司风险
        "liquidity_risk",     # 流动性风险
        "valuation_risk"      # 估值风险
    ],
    "risk_threshold": {
        "low": 30,
        "medium": 60,
        "high": 100
    },
    
    # === 合规配置 ===
    "compliance_checks": True,
    "disclaimer_required": True,
    "investment_advice_warning": True,
    "data_usage_tracking": True,
    
    # === 输出配置 ===
    "output_dir": "./results/a_share_analysis",
    "save_raw_data": False,               # 是否保存原始数据
    "save_analysis_logs": True,           # 是否保存分析日志
    "export_formats": ["json", "csv", "excel"], # 数据导出格式
}


# 分析深度对应的配置
ANALYSIS_DEPTH_CONFIG = {
    "basic": {
        "financial_analysis_periods": 3,
        "peer_comparison_count": 3,
        "valuation_methods": ["pe_ratio", "pb_ratio"],
        "technical_indicators": ["ma_20", "rsi"],
        "max_report_length": 3000,
    },
    "standard": {
        "financial_analysis_periods": 5,
        "peer_comparison_count": 5,
        "valuation_methods": ["pe_ratio", "pb_ratio", "ps_ratio", "dcf_model"],
        "technical_indicators": ["ma_20", "ma_50", "rsi", "macd"],
        "max_report_length": 6000,
    },
    "comprehensive": {
        "financial_analysis_periods": 7,
        "peer_comparison_count": 8,
        "valuation_methods": ["pe_ratio", "pb_ratio", "ps_ratio", "dcf_model", "dividend_model"],
        "technical_indicators": ["ma_20", "ma_50", "rsi", "macd", "bollinger_bands"],
        "max_report_length": 10000,
    }
}


def get_analysis_config(depth: str = "standard") -> dict:
    """
    根据分析深度获取对应配置
    
    Args:
        depth: 分析深度 (basic/standard/comprehensive)
        
    Returns:
        深度特定的配置字典
    """
    base_config = A_SHARE_DEFAULT_CONFIG.copy()
    if depth in ANALYSIS_DEPTH_CONFIG:
        base_config.update(ANALYSIS_DEPTH_CONFIG[depth])
    return base_config


# 行业配置
INDUSTRY_CONFIG = {
    "shenwan_levels": {
        1: "一级行业",
        2: "二级行业", 
        3: "三级行业"
    },
    "major_industries": [
        "801010",  # 农林牧渔
        "801020",  # 采掘
        "801030",  # 化工
        "801040",  # 钢铁
        "801050",  # 有色金属
        "801080",  # 电子
        "801110",  # 家用电器
        "801120",  # 食品饮料
        "801130",  # 纺织服装
        "801140",  # 轻工制造
        "801150",  # 医药生物
        "801160",  # 公用事业
        "801170",  # 交通运输
        "801180",  # 房地产
        "801200",  # 商业贸易
        "801210",  # 休闲服务
        "801230",  # 综合
        "801710",  # 建筑材料
        "801720",  # 建筑装饰
        "801730",  # 电气设备
        "801740",  # 国防军工
        "801750",  # 计算机
        "801760",  # 传媒
        "801770",  # 通信
        "801780",  # 银行
        "801790",  # 非银金融
        "801880",  # 汽车
        "801890",  # 机械设备
    ]
}


# 数据源配置
DATA_SOURCE_CONFIG = {
    "primary_sources": [
        "a_share_api",    # A股数据API
        "mcp_service",    # MCP金融工具
    ],
    "fallback_sources": [
        "cached_data",    # 缓存数据
        "manual_input",   # 手动输入
    ],
    "data_validation_rules": {
        "financial_data": ["required_fields", "data_range", "logical_consistency"],
        "market_data": ["price_range", "volume_range", "date_sequence"],
        "industry_data": ["industry_code_format", "data_completeness"],
    }
}