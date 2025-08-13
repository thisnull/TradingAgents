## 实现计划

### 阶段1：数据与工具
- 新增 `a_stock_utils.py`：
  - 财务三表与指标：`stock_profit_sheet_by_report_em`、`stock_balance_sheet_by_report_em`、`stock_cash_flow_sheet_by_report_em`、`stock_financial_analysis_indicator`
  - 分红：`stock_history_dividend`
  - 股东结构：`stock_main_stock_holder`、`stock_circulate_stock_holder`、`stock_zh_a_gdhs`、`stock_restricted_release_summary_em`
  - 行业估值：`sw_index_third_info`、全市场估值样本：`stock_a_indicator_lg`
  - 估值时序：从指标中解析 PE(TTM)/ROE(%)，构造 PR=PE/ROE 时序表

### 阶段2：Agent 节点
- 核心财务：`create_core_financials_agent`
- 行业对比：`create_industry_competition_agent`
- 估值信号：`create_valuation_signal_agent`
- 信息整合：`create_a_stock_report_aggregator`

### 阶段3：编排
- 新建 `AStockGraph`，顺序执行四节点，产出 `a_stock_final_report`

### 阶段4：CLI 与文档
- CLI 新增 `analyze-ashare` 命令
- 文档：设计说明与使用说明

## 系统设计

### 数据流
- 节点内部先拉取数据（AkShare），再由 LLM 结构化总结，保留数据表与来源

### 状态
- 复用现有 `Propagator` 的 `state_schema`，新增输出键：
  - `a_core_financials`
  - `a_industry_competition`
  - `a_valuation_signal`
  - `a_stock_final_report`

### 依赖与资源
- 依赖：`akshare`、`pandas`
- LLM Provider：遵循 `DEFAULT_CONFIG` 与 `.env`（自定义 endpoint 与本地 Ollama 均已兼容）
- 不新增数据库，直接以即时查询为主（后续可接入缓存）

## 输出规范
- 报告采用金字塔结构，先结论后论据
- 每节必须含表格与“数据来源”
- 估值部分包含 PR=PE/ROE 序列


