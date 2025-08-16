"""
A股分析Agent模块
提供A股市场综合分析能力的多Agent系统

主要功能：
- 财务分析：分析核心财务指标，评估财务质量
- 行业分析：分析行业地位和竞争优势
- 估值分析：使用PR=PE/ROE模型等评估估值水平
- 报告整合：使用金字塔原理生成投资分析报告

使用示例：
```python
from tradingagents.analysis_stock_agent import AShareAnalysisSystem, ANALYSIS_CONFIG

# 创建分析系统
config = ANALYSIS_CONFIG.copy()
system = await create_analysis_system(config, debug=True)

# 分析单只股票
result = await system.analyze_stock("000001")
print(result.final_report)

# 批量分析
results = await system.batch_analyze_stocks(["000001", "000002", "600036"])

# 释放资源
await system.close()
```
"""

from .graph.analysis_graph import (
    AShareAnalysisSystem,
    analyze_ashare_stock
)

from .utils.analysis_states import (
    AnalysisState,
    AnalysisResult,
    FinancialAnalysisResult,
    IndustryAnalysisResult, 
    ValuationAnalysisResult,
    InvestmentRecommendation,
    AnalysisStatus,
    DataSource,
    create_analysis_state
)

from .config.analysis_config import ANALYSIS_CONFIG

from .agents import (
    create_financial_analysis_agent,
    create_industry_analysis_agent,
    create_valuation_analysis_agent,
    create_report_integration_agent
)

from .tools import (
    AShareToolkit,
    MCPToolkit,
    UnifiedDataToolkit
)

__version__ = "1.0.0"
__author__ = "TradingAgents Team"

__all__ = [
    # 主要系统
    "AShareAnalysisSystem",
    "analyze_ashare_stock",
    
    # 状态和结果类
    "AnalysisState",
    "AnalysisResult", 
    "FinancialAnalysisResult",
    "IndustryAnalysisResult",
    "ValuationAnalysisResult",
    "InvestmentRecommendation",
    "AnalysisStatus",
    "DataSource",
    "create_analysis_state",
    
    # 配置
    "ANALYSIS_CONFIG",
    
    # Agent创建函数
    "create_financial_analysis_agent",
    "create_industry_analysis_agent", 
    "create_valuation_analysis_agent",
    "create_report_integration_agent",
    
    # 工具类
    "AShareToolkit",
    "MCPToolkit", 
    "UnifiedDataToolkit"
]