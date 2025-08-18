# A股投资分析系统使用指南

## 快速开始

A股投资分析系统提供了多种使用方式，你可以选择最适合你的接口：

### 1. 命令行接口（推荐入门）

最简单的使用方式，直接在命令行输入股票代码即可获得分析报告：

```bash
# 基本用法
python -m tradingagents.analysis_stock_agent.main 002594

# 启用调试模式，查看详细日志
python -m tradingagents.analysis_stock_agent.main 002594 --debug

# 指定分析深度
python -m tradingagents.analysis_stock_agent.main 000001 --depth comprehensive

# 自定义输出目录
python -m tradingagents.analysis_stock_agent.main 600036 --output ./my_reports

# 保存日志到文件
python -m tradingagents.analysis_stock_agent.main 000858 --log analysis.log
```

#### 支持的股票代码示例：
- `002594` - 比亚迪
- `000001` - 平安银行  
- `600036` - 招商银行
- `000858` - 五粮液
- `600519` - 贵州茅台

#### 命令行参数说明：
- `stock_code`: 必需，6位数字的股票代码
- `--depth`: 分析深度，可选 `basic`、`standard`、`comprehensive`（默认）
- `--debug`: 启用调试模式，显示详细日志
- `--output`: 指定报告保存目录（默认：`results`）
- `--log`: 指定日志文件路径
- `--config`: 指定自定义配置文件（JSON格式）

### 2. Python API接口（推荐进阶）

在你的Python代码中直接调用分析功能：

```python
from tradingagents.analysis_stock_agent.api import StockAnalysisAPI, quick_analyze

# 方式1: 使用便利函数（最简单）
result = quick_analyze("002594", debug=True)
if result.success:
    print("分析成功！")
    print(f"报告长度: {len(result.report)} 字符")
    print(f"分析耗时: {result.analysis_time:.2f}秒")
else:
    print(f"分析失败: {result.error_message}")

# 方式2: 使用API类（更多控制）
api = StockAnalysisAPI(debug=True)

# 分析单个股票
result = api.analyze("002594", save_report=True)
print(result.report)

# 获取分析摘要
summary = api.get_analysis_summary(result)
print(summary)

# 批量分析
stock_list = ["002594", "000001", "600036"]
results = api.batch_analyze(stock_list, save_reports=True)

# 导出批量分析摘要
api.export_batch_results(results, "my_analysis_summary.json")
```

### 3. 高级用法

#### 自定义配置
```python
# 创建自定义配置
custom_config = {
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini", 
    "max_debate_rounds": 2,
    "analysis_timeout": 300,
    "a_share_api_url": "http://your-api-server.com/api/v1"
}

api = StockAnalysisAPI(config=custom_config, debug=True)
result = api.analyze("002594")
```

#### 投资组合分析
```python
from tradingagents.analysis_stock_agent.api import analyze_portfolio

# 分析整个投资组合
portfolio = ["002594", "000001", "600036", "000858", "600519"]
results = analyze_portfolio(portfolio, save_reports=True, debug=True)

# 打印每只股票的分析摘要
for result in results:
    if result.success:
        summary = api.get_analysis_summary(result)
        print(f"{result.stock_code}: {summary.get('investment_recommendation', 'N/A')}")
```

## 输出说明

### 分析报告结构
系统生成的分析报告采用金字塔原理结构，包含以下部分：

1. **执行摘要** - 投资建议和核心结论
2. **财务分析** - ROE、ROA、现金流等关键财务指标
3. **行业分析** - 行业地位、竞争优势、申万行业分类
4. **估值分析** - DCF估值、相对估值、技术指标
5. **风险分析** - 投资风险和催化剂识别
6. **数据来源** - 所有分析数据的来源追踪

### 日志输出
启用调试模式时，系统会输出详细的执行日志：

```
2024-01-15 10:30:15 - tradingagents.analysis_stock_agent.main - INFO - main.py:145 - 开始分析股票: 002594
2024-01-15 10:30:16 - tradingagents.analysis_stock_agent.graph.a_share_analysis_graph - INFO - a_share_analysis_graph.py:77 - AShareAnalysisGraph initialized successfully
2024-01-15 10:30:18 - tradingagents.analysis_stock_agent.agents.financial_analyst - INFO - financial_analyst.py:65 - Starting financial analysis for 002594
```

### 保存的文件
- **分析报告**: `results/A股分析报告_002594_20240115_103025.md`
- **日志文件**: `analysis.log` (如果指定了 --log 参数)
- **批量摘要**: `batch_analysis_summary.json` (批量分析时)

## 故障排查

### 常见问题

1. **股票代码无效**
   ```
   错误: 无效的股票代码: 002594SZ
   解决: 使用6位纯数字代码，如 002594
   ```

2. **API连接失败**
   ```
   错误: API request failed after 3 attempts
   解决: 检查网络连接和API服务器状态
   ```

3. **模块导入错误**
   ```
   错误: No module named 'langgraph'
   解决: 确保已激活 tradingagents conda环境
   ```

### 调试技巧

1. **始终使用 `--debug` 模式**进行问题排查
2. **保存日志到文件**便于后续分析：`--log debug.log`
3. **检查输出目录权限**确保可以写入报告文件
4. **验证环境配置**：
   ```bash
   conda activate tradingagents
   python -c "from tradingagents.analysis_stock_agent.api import quick_analyze; print('✅ 模块导入成功')"
   ```

## 环境要求

### 必需的环境变量
```bash
export GOOGLE_API_KEY=$YOUR_GOOGLE_API_KEY        # Google Gemini API密钥（必需）
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY      # 金融数据API密钥（推荐）
```

### API密钥获取
- **Google Gemini API**: 从 [Google AI Studio](https://ai.google.dev/) 获取免费API密钥
- **FinnHub API**: 从 [FinnHub.io](https://finnhub.io/) 获取金融数据API密钥（可选）

### 推荐配置
- Python 3.13+
- 16GB+ 内存（处理大量数据时）
- 稳定的网络连接（用于API调用）
- 足够的磁盘空间（保存分析报告）

## 技术架构

系统采用多Agent架构，包含4个专业Agent：

1. **财务分析Agent** - 核心财务指标分析
2. **行业分析Agent** - 行业对比与竞争优势分析  
3. **估值分析Agent** - 估值与市场信号分析
4. **信息整合Agent** - 综合分析和投资建议

每个Agent都配备了专业的金融分析工具，通过LangGraph框架协调工作，使用Google Gemini作为LLM Provider，最终产出高质量的投资分析报告。

### LLM配置
- **深度分析**: `gemini-2.5-pro` - 用于复杂的财务和投资分析
- **快速分析**: `gemini-2.5-flash` - 用于数据处理和快速响应  
- **报告生成**: `gemini-2.5-pro` - 用于最终分析报告生成

## 支持与反馈

如有问题或建议，请查看项目文档或联系开发团队。