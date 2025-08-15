"""
A股分析系统配置模块
基于TradingAgents的DEFAULT_CONFIG扩展，专门用于A股分析
"""
import os
from typing import Dict, Any

# 基础配置继承自TradingAgents
ANALYSIS_CONFIG: Dict[str, Any] = {
    # 项目基础配置
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
    "results_dir": os.getenv("ANALYSIS_RESULTS_DIR", "./results/analysis"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        "dataflows/data_cache",
    ),
    
    # LLM配置 - 使用用户提供的自定义endpoint
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",          # 深度分析使用
    "quick_think_llm": "gpt-4o-mini",    # 快速处理使用
    "backend_url": "https://oned.lvtu.in",  # 用户自定义endpoint
    "local_llm_url": "http://localhost:10000",  # 本地Ollama备选
    
    # A股数据源配置
    "ashare_api_url": "http://localhost:8000/api/v1",
    "use_ashare_api": True,
    "ashare_cache_ttl": 3600,  # 1小时缓存
    
    # MCP服务配置 (可选)
    "mcp_endpoint": "ws://your-server.com:8001",
    "mcp_api_key": os.getenv("MCP_API_KEY"),
    "use_mcp_service": False,  # 默认关闭，A股API优先
    
    # 分析参数配置
    "analysis_period": "3years",  # 分析时间范围
    "industry_comparison_count": 10,  # 行业对比公司数量
    "technical_indicators": ["ma", "rsi", "macd"],  # 技术指标
    "financial_metrics": [
        "revenue_growth", "profit_growth", "roe", "roa",
        "debt_ratio", "current_ratio", "gross_margin", "net_margin"
    ],
    
    # 报告配置
    "report_format": "markdown",
    "include_charts": False,  # 暂不支持图表
    "language": "zh-CN",
    "use_pyramid_principle": True,  # 使用金字塔原理
    
    # 评分权重配置
    "scoring_weights": {
        "financial_quality": 0.4,     # 财务质量 40%
        "competitive_advantage": 0.3,  # 竞争优势 30%
        "valuation_level": 0.3        # 估值水平 30%
    },
    
    # 性能配置
    "max_concurrent_analysis": 5,    # 最大并发分析数
    "request_timeout": 120,          # 请求超时时间(秒)
    "max_retry_attempts": 3,         # 最大重试次数
    "cache_enabled": True,
    "cache_ttl": 3600,              # 默认缓存时间(秒)
    
    # 调试和日志配置
    "debug_mode": False,
    "log_level": "INFO",
    "log_file": "./logs/analysis.log",
    "enable_performance_monitoring": True,
    
    # 数据质量配置
    "min_data_completeness": 0.8,   # 最小数据完整度要求
    "enable_data_validation": True,
    "enable_anomaly_detection": True,
    
    # 安全配置
    "enable_input_validation": True,
    "sanitize_user_input": True,
    "max_symbol_length": 6,
    "allowed_symbol_pattern": r"^[0-9]{6}$",  # A股6位数字代码
}

# 环境变量覆盖配置
def load_config_from_env() -> Dict[str, Any]:
    """从环境变量加载配置覆盖"""
    config = ANALYSIS_CONFIG.copy()
    
    # LLM配置
    if os.getenv("LLM_PROVIDER"):
        config["llm_provider"] = os.getenv("LLM_PROVIDER")
    if os.getenv("DEEP_THINK_LLM"):
        config["deep_think_llm"] = os.getenv("DEEP_THINK_LLM")
    if os.getenv("QUICK_THINK_LLM"):
        config["quick_think_llm"] = os.getenv("QUICK_THINK_LLM")
    if os.getenv("LLM_BACKEND_URL"):
        config["backend_url"] = os.getenv("LLM_BACKEND_URL")
    
    # 数据源配置
    if os.getenv("ASHARE_API_URL"):
        config["ashare_api_url"] = os.getenv("ASHARE_API_URL")
    if os.getenv("MCP_ENDPOINT"):
        config["mcp_endpoint"] = os.getenv("MCP_ENDPOINT")
    if os.getenv("MCP_API_KEY"):
        config["mcp_api_key"] = os.getenv("MCP_API_KEY")
    
    # 性能配置
    if os.getenv("MAX_CONCURRENT_ANALYSIS"):
        config["max_concurrent_analysis"] = int(os.getenv("MAX_CONCURRENT_ANALYSIS"))
    if os.getenv("REQUEST_TIMEOUT"):
        config["request_timeout"] = int(os.getenv("REQUEST_TIMEOUT"))
    
    # 调试配置
    if os.getenv("DEBUG_MODE"):
        config["debug_mode"] = os.getenv("DEBUG_MODE").lower() == "true"
    if os.getenv("LOG_LEVEL"):
        config["log_level"] = os.getenv("LOG_LEVEL")
    
    return config

# 配置验证
def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置的有效性"""
    required_fields = [
        "llm_provider", "deep_think_llm", "quick_think_llm", 
        "backend_url", "ashare_api_url"
    ]
    
    for field in required_fields:
        if not config.get(field):
            raise ValueError(f"必需的配置项缺失: {field}")
    
    # 验证LLM provider
    if config["llm_provider"] not in ["openai", "anthropic", "google", "ollama"]:
        raise ValueError(f"不支持的LLM provider: {config['llm_provider']}")
    
    # 验证URL格式
    import re
    url_pattern = r"^https?://.+"
    if not re.match(url_pattern, config["backend_url"]):
        raise ValueError(f"无效的LLM backend URL: {config['backend_url']}")
    
    if not re.match(url_pattern, config["ashare_api_url"]):
        raise ValueError(f"无效的A股API URL: {config['ashare_api_url']}")
    
    return True

# 获取运行时配置
def get_config() -> Dict[str, Any]:
    """获取运行时配置"""
    config = load_config_from_env()
    validate_config(config)
    return config

# 默认导出
DEFAULT_ANALYSIS_CONFIG = ANALYSIS_CONFIG