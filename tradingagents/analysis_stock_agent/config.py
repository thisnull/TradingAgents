"""
配置管理模块
"""

import os
from typing import Dict, Any
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class StockAnalysisConfig:
    """A股分析系统配置"""
    
    # 项目路径配置
    project_dir: Path = field(default_factory=lambda: Path(__file__).parent)
    cache_dir: Path = field(default_factory=lambda: Path("./cache"))
    results_dir: Path = field(default_factory=lambda: Path("./results"))
    
    # LLM配置
    llm_provider: str = "openai"
    deep_think_llm: str = "gpt-4o"
    quick_think_llm: str = "gpt-4o-mini"
    backend_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # 数据源配置
    data_source: str = "akshare"  # akshare or tushare
    tushare_token: str = os.getenv("TUSHARE_TOKEN", "")
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存时间（秒）
    
    # 分析配置
    max_retry: int = 3
    timeout: int = 30
    concurrent_tasks: int = 3
    
    # 报告配置
    report_format: str = "markdown"  # markdown, html, pdf
    report_language: str = "zh_CN"
    include_charts: bool = True
    
    # Agent配置
    agent_config: Dict[str, Any] = field(default_factory=lambda: {
        "financial": {
            "metrics": ["ROE", "ROA", "净利率", "毛利率", "资产负债率"],
            "periods": 3,  # 分析最近3年数据
            "threshold": {
                "roe_min": 15,  # ROE最低要求15%
                "debt_ratio_max": 60,  # 资产负债率最高60%
            }
        },
        "industry": {
            "compare_top_n": 5,  # 对比行业前5名
            "metrics": ["市值", "营收", "净利润", "ROE", "PE"],
        },
        "valuation": {
            "pr_history_years": 5,  # PR值历史分析年限
            "pe_percentile_range": [10, 90],  # PE百分位区间
        },
        "report": {
            "sections": ["财务分析", "行业对比", "估值分析", "投资建议", "风险提示"],
            "max_length": 5000,  # 报告最大字数
        }
    })
    
    def __post_init__(self):
        """初始化后处理"""
        # 创建必要的目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 验证配置
        if not self.api_key and self.llm_provider == "openai":
            raise ValueError("OpenAI API key is required when using OpenAI provider")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "project_dir": str(self.project_dir),
            "cache_dir": str(self.cache_dir),
            "results_dir": str(self.results_dir),
            "llm_provider": self.llm_provider,
            "deep_think_llm": self.deep_think_llm,
            "quick_think_llm": self.quick_think_llm,
            "backend_url": self.backend_url,
            "data_source": self.data_source,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "report_format": self.report_format,
            "agent_config": self.agent_config,
        }

# 默认配置实例
DEFAULT_CONFIG = StockAnalysisConfig()
