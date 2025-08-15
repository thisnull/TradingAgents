# A股分析Multi-Agent System

## 📋 项目简介

A股分析Multi-Agent System是一个专门针对A股市场的智能投资分析系统。通过多个专业化Agent的协作，系统能够从财务、行业、估值等多个维度对A股上市公司进行全面分析，并生成专业的投资分析报告。

## 🌟 核心功能

- **财务健康分析**：深度分析公司财务报表，评估盈利能力、成长性和财务风险
- **行业地位评估**：对比同行业公司，识别竞争优势和市场地位
- **估值水平判断**：基于PE、PB、PR等指标评估估值合理性
- **智能报告生成**：基于金字塔原理生成结构化的投资分析报告
- **批量分析支持**：支持同时分析多只股票，提高研究效率

## 🏗️ 系统架构

```
A股分析系统
├── 数据收集层（AKShare）
├── 分析Agent层
│   ├── 财务分析Agent
│   ├── 行业分析Agent
│   └── 估值分析Agent
├── 报告整合层
└── 输出层（Markdown/PDF）
```

## 🚀 快速开始

### 安装依赖

```bash
# 安装必要的Python包
pip install akshare langchain langchain-openai langgraph pandas numpy

# 或使用requirements文件
pip install -r requirements.txt
```

### 环境配置

```bash
# 设置OpenAI API密钥（或兼容的endpoint）
export OPENAI_API_KEY="your_api_key_here"

# 可选：设置自定义endpoint
export OPENAI_BASE_URL="https://your-custom-endpoint.com/v1"
```

### 基础使用

```python
from tradingagents.analysis_stock_agent import StockAnalysisGraph, StockAnalysisConfig

# 创建配置
config = StockAnalysisConfig()

# 创建分析系统
analyzer = StockAnalysisGraph(config)

# 分析单只股票
result = analyzer.analyze(
    stock_code="600519",  # 贵州茅台
    save_report=True
)

# 查看结果
print(f"投资评级: {result['investment_rating']}")
print(f"目标价格: {result['target_price']}")
print(f"报告路径: {result['report_path']}")
```

## 📊 使用示例

### 1. 基础分析

```python
# 分析贵州茅台
result = analyzer.analyze("600519")

# 获取分析摘要
summary = analyzer.get_analysis_summary(result)
print(summary)
```

### 2. 批量分析

```python
# 批量分析多只股票
stock_codes = ["000858", "002415", "300750"]
results = analyzer.batch_analyze(stock_codes)

for code, result in results.items():
    print(f"{code}: {result['investment_rating']}")
```

### 3. 自定义配置

```python
# 自定义分析配置
config = StockAnalysisConfig(
    # LLM配置
    deep_think_llm="gpt-4o",
    quick_think_llm="gpt-4o-mini",
    
    # Agent配置
    agent_config={
        "financial": {
            "metrics": ["ROE", "ROA", "净利率"],
            "periods": 5,  # 分析5年数据
            "threshold": {
                "roe_min": 20,  # ROE最低20%
            }
        }
    }
)

analyzer = StockAnalysisGraph(config)
```

## 📝 分析报告示例

生成的报告包含以下内容：

```markdown
# 贵州茅台(600519) 投资分析报告

## 一、投资结论
**投资评级**：推荐
**目标价格**：2100.00元（潜在涨幅：15%）
**核心逻辑**：公司是白酒行业龙头，具有强大的品牌护城河和定价权

## 二、核心投资要点
### 2.1 财务表现优异
- ROE：28.5%，显著高于行业平均
- 营收CAGR：12.3%，保持稳健增长
- 现金流充裕，财务风险低

### 2.2 行业地位领先
- 高端白酒市场份额第一
- 品牌价值和定价权无可比拟
- 产能扩张有序推进

### 2.3 估值水平合理
- PE：35倍，处于历史中位
- PR值：1.2，估值相对合理
...
```

## 🛠️ 配置选项

### LLM配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| llm_provider | LLM提供商 | "openai" |
| deep_think_llm | 深度思考模型 | "gpt-4o" |
| quick_think_llm | 快速响应模型 | "gpt-4o-mini" |
| backend_url | API端点 | "https://api.openai.com/v1" |

### 数据源配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| data_source | 数据源 | "akshare" |
| cache_enabled | 启用缓存 | True |
| cache_ttl | 缓存时间(秒) | 3600 |

### Agent配置

通过`agent_config`参数可以自定义各Agent的行为：

```python
agent_config = {
    "financial": {
        "metrics": ["ROE", "ROA", "净利率", "毛利率"],
        "periods": 3,  # 分析年数
        "threshold": {
            "roe_min": 15,
            "debt_ratio_max": 60,
        }
    },
    "industry": {
        "compare_top_n": 5,  # 对比前N名
    },
    "valuation": {
        "pr_history_years": 5,
    }
}
```

## 🧪 测试

运行测试脚本：

```bash
# 运行完整测试
python scripts/test_stock_analysis.py

# 运行使用示例
python scripts/example_usage.py
```

## 📁 项目结构

```
analysis_stock_agent/
├── agents/              # Agent实现
│   ├── financial_analyst.py
│   ├── industry_analyst.py
│   ├── valuation_analyst.py
│   └── report_integration.py
├── tools/               # 数据工具
│   ├── akshare_toolkit.py
│   └── data_cache.py
├── graph/               # 工作流编排
│   └── stock_analysis_graph.py
├── config.py           # 配置管理
└── README.md           # 本文档
```

## 🔧 扩展开发

### 添加新的分析维度

```python
# 创建新的Agent
class TechnicalAnalystAgent:
    def analyze(self, state):
        # 实现技术分析逻辑
        return updated_state

# 在工作流中添加节点
workflow.add_node("technical_analysis", technical_node)
```

### 集成新的数据源

```python
# 扩展数据工具包
class ExtendedToolkit(AStockToolkit):
    def get_custom_data(self, stock_code):
        # 实现自定义数据获取
        return data
```

## ⚠️ 注意事项

1. **API限制**：请注意LLM API的调用限制和费用
2. **数据时效**：财务数据可能有延迟，请关注数据更新时间
3. **投资风险**：本系统仅供参考，不构成投资建议
4. **合规要求**：使用时请遵守相关法律法规

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

本项目采用MIT许可证

## 📮 联系方式

如有问题或建议，请通过以下方式联系：
- Issue: GitHub Issues
- Email: your-email@example.com

---

*免责声明：本系统生成的分析报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。*
