## A股多智能体分析系统（analysis_stock_agent）

### 目标
- 针对单个A股公司，形成自动化分析报告：
  - 核心财务指标分析（营收/净利/ROE/资产负债/现金流/股东回报）
  - 行业对比与竞争优势分析（同业三大指标横向比较）
  - 估值与市场信号（股权结构、限售解禁、股东户数、PR=PE/ROE 时序）
  - 金字塔结构整合报告：先结论、后论据、附数据表与来源

### 技术选型（与本项目一致）
- LLM编排：LangGraph
- LLM接入：遵循 `DEFAULT_CONFIG`，支持自定义 OpenAI 兼容 endpoint 与本地 Ollama
- 数据源：AkShare（东方财富/巨潮等）

### 代码结构
- `tradingagents/dataflows/a_stock_utils.py`：A股数据抓取与组装（财务三表、指标、分红、股东结构、行业估值、PR=PE/ROE 计算）
- `tradingagents/agents/analysis_stock_agent/agents.py`：
  - `create_core_financials_agent`
  - `create_industry_competition_agent`
  - `create_valuation_signal_agent`
  - `create_a_stock_report_aggregator`
- `tradingagents/graph/a_stock_graph.py`：工作流编排，顺序执行四个节点
- CLI：`cli/main.py` 新增 `analyze-ashare` 命令

### 运行
```bash
uv run python -m cli.main analyze-ashare --symbol 600519 --analysis-date 2025-06-30
```

### 输出
- 终端展示完整 Markdown 报告
- 报告每节均包含数据表与“数据来源”标注（AKShare 接口名）

### 资源需求
- Python 依赖（已在项目 requirements.txt 中包含 akshare）
- LLM Provider：配置 `.env` 或 `DEFAULT_CONFIG` 中的 `llm_provider`/`backend_url`/模型名
- 可选：本地 Ollama 作为小模型供应（项目已支持）

### 备注
- 工具保持“单一成熟方案”：AkShare；避免同时集成多套同类数据源
- 若需 Docker 化运行，请另见《AnalysisStockAgent_Docker部署.md》


