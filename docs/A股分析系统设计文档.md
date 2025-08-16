# A股投资分析多Agent系统

> 基于LangGraph框架的专业A股投资分析多Agent系统，整合财务分析、行业分析、估值分析和信息整合四个专业Agent，为投资者提供全面的股票分析报告。

## 🎯 系统概述

本系统采用多Agent协作架构，模拟真实投资机构的分析流程，为A股投资者提供专业级的股票分析服务。系统集成了财务分析、行业对比、估值建模、市场信号解读等多个维度，生成综合性投资建议。

### 核心特性

- ✅ **多Agent协作**: 4个专业Agent分工合作，确保分析的全面性和专业性
- ✅ **智能工作流**: 基于LangGraph的可视化工作流编排
- ✅ **多维度分析**: 财务、行业、估值、市场信号全覆盖
- ✅ **灵活配置**: 支持多种LLM模型和分析深度
- ✅ **API集成**: 整合A股数据API和MCP金融工具
- ✅ **专业报告**: 金字塔原理结构化报告输出
- ✅ **CLI工具**: 便捷的命令行操作界面

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        A股分析多Agent系统                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   财务分析Agent   │  │   行业分析Agent   │  │   估值分析Agent   │    │
│  │                │  │                │  │                │    │
│  │ • 盈利能力分析    │  │ • 行业地位分析    │  │ • DCF估值模型    │    │
│  │ • 偿债能力分析    │  │ • 竞争优势评估    │  │ • 相对估值分析    │    │
│  │ • 运营能力分析    │  │ • 行业前景判断    │  │ • 技术信号分析    │    │
│  │ • 现金流分析     │  │ • 申万行业分类    │  │ • 市场情绪指标    │    │
│  │ • 成长性分析     │  │ • 同业对比分析    │  │ • 资金流向分析    │    │
│  │ • 股东回报分析    │  │ • 护城河评估     │  │ • 催化剂识别     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│           │                     │                     │           │
│           └─────────────────────┼─────────────────────┘           │
│                                 │                                 │
│                  ┌─────────────────────────────┐                  │
│                  │      信息整合Agent           │                  │
│                  │                            │                  │
│                  │ • 一致性分析和冲突识别        │                  │
│                  │ • 权重分配和综合评分        │                  │
│                  │ • 投资建议制定             │                  │
│                  │ • 风险因素综合评估          │                  │
│                  │ • 策略执行指导             │                  │
│                  │ • 综合分析报告生成          │                  │
│                  └─────────────────────────────┘                  │
├─────────────────────────────────────────────────────────────────┤
│                          支撑层                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  LLM管理器   │  │  数据工具层   │  │  计算工具层   │  │  状态管理  │  │
│  │            │  │            │  │            │  │          │  │
│  │ • OpenAI   │  │ • A股API   │  │ • 财务计算   │  │ • 状态模型 │  │
│  │ • Claude   │  │ • MCP工具  │  │ • 技术分析   │  │ • 流程控制 │  │
│  │ • Ollama   │  │ • 行业数据  │  │ • 估值模型   │  │ • 错误处理 │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent职责分工

#### 1. 财务指标分析Agent
- **核心职能**: 深度财务分析和健康度评估
- **分析维度**: 盈利能力、偿债能力、运营能力、现金流、成长性、股东回报
- **输出成果**: 财务健康度评分(1-100分)、财务分析报告
- **关键工具**: 财务比率计算、财务健康度评分、财务报告生成

#### 2. 行业对比与竞争优势分析Agent  
- **核心职能**: 行业地位评估和竞争力分析
- **分析维度**: 申万行业分类、同业对比、竞争格局、市场地位、护城河深度
- **输出成果**: 行业竞争力评分(1-100分)、行业分析报告
- **关键工具**: 行业数据获取、同业对比分析、竞争优势评估

#### 3. 估值与市场信号分析Agent
- **核心职能**: 估值建模和市场信号解读
- **分析维度**: DCF估值、相对估值、技术分析、市场情绪、资金流向
- **输出成果**: 估值合理性评分(1-100分)、目标价位、估值分析报告
- **关键工具**: DCF模型、相对估值计算、技术指标分析、市场情绪分析

#### 4. 信息整合Agent
- **核心职能**: 综合分析和投资决策
- **分析维度**: 一致性分析、权重分配、风险评估、投资策略制定
- **输出成果**: 综合投资评分(1-100分)、投资建议、综合分析报告
- **关键工具**: 结果整合、一致性分析、综合评分、策略制定

## 📁 项目结构

```
TradingAgents/
├── tradingagents/
│   └── analysis_stock_agent/           # A股分析模块
│       ├── __init__.py                 # 模块入口
│       ├── agents/                     # Agent实现
│       │   ├── financial_analyst.py   # 财务分析Agent
│       │   ├── industry_analyst.py    # 行业分析Agent
│       │   ├── valuation_analyst.py   # 估值分析Agent
│       │   └── information_integrator.py # 信息整合Agent
│       ├── graph/                      # 图结构和工作流
│       │   ├── a_share_analysis_graph.py # 主图类
│       │   └── setup.py                # 图初始化配置
│       ├── utils/                      # 工具模块
│       │   ├── state_models.py         # 状态模型定义
│       │   ├── data_tools.py           # 数据获取工具
│       │   ├── calculation_utils.py    # 计算工具
│       │   ├── mcp_tools.py           # MCP工具集成
│       │   └── llm_utils.py           # LLM管理器
│       ├── prompts/                    # 提示词模板
│       │   ├── financial_prompts.py   # 财务分析提示词
│       │   ├── industry_prompts.py    # 行业分析提示词
│       │   ├── valuation_prompts.py   # 估值分析提示词
│       │   └── integration_prompts.py # 信息整合提示词
│       ├── config/                     # 配置文件
│       │   └── a_share_config.py      # 默认配置
│       └── cli/                        # 命令行工具
│           └── a_share_cli.py         # CLI入口
├── examples/                          # 使用示例
│   └── a_share_analysis_example.py   # 完整使用示例
├── tests/                             # 测试文件
│   └── test_a_share_analysis.py      # 基本功能测试
└── docs/                              # 文档
    └── README.md                      # 系统文档(本文件)
```

## 🚀 快速开始

### 环境要求

- Python 3.9+
- 相关依赖包 (见requirements.txt)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository_url>
cd TradingAgents
```

2. **创建虚拟环境**
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 必需的API密钥
export OPENAI_API_KEY="your_openai_api_key"
export A_SHARE_API_KEY="your_a_share_api_key"

# 可选的配置
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 或自定义端点
export A_SHARE_API_URL="http://localhost:8000/api/v1"
```

5. **验证安装**
```bash
python tests/test_a_share_analysis.py
```

### 快速使用

#### 方式1: CLI工具 (推荐)

```bash
# 分析单只股票
python tradingagents/analysis_stock_agent/cli/a_share_cli.py analyze 000001 --name "平安银行"

# 指定分析深度
python tradingagents/analysis_stock_agent/cli/a_share_cli.py analyze 000001 --depth comprehensive

# 输出到文件
python tradingagents/analysis_stock_agent/cli/a_share_cli.py analyze 000001 --output report.md

# 验证股票代码
python tradingagents/analysis_stock_agent/cli/a_share_cli.py validate 000001

# 查看支持的模型
python tradingagents/analysis_stock_agent/cli/a_share_cli.py list-models

# 生成配置文件模板
python tradingagents/analysis_stock_agent/cli/a_share_cli.py generate-config
```

#### 方式2: Python API

```python
from tradingagents.analysis_stock_agent import AShareAnalysisGraph, AnalysisDepth

# 创建分析图
config = {
    "openai_api_key": "your_key",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini"
}

with AShareAnalysisGraph(config=config) as graph:
    # 执行分析
    final_state, report = graph.analyze_stock(
        stock_code="000001",
        stock_name="平安银行", 
        analysis_depth=AnalysisDepth.COMPREHENSIVE
    )
    
    # 获取结果
    score = final_state.get("comprehensive_score", 0)
    recommendation = final_state.get("investment_recommendation", "")
    
    print(f"综合评分: {score}/100")
    print(f"投资建议: {recommendation}")
    print(f"分析报告:\n{report}")
```

#### 方式3: 批量分析

```python
# 批量分析多只股票
stock_codes = ["000001", "000002", "600000", "600036"]
results = {}

with AShareAnalysisGraph(config=config) as graph:
    for code in stock_codes:
        try:
            state, report = graph.analyze_stock(code)
            results[code] = {
                "score": state.get("comprehensive_score", 0),
                "recommendation": state.get("investment_recommendation", ""),
                "report": report
            }
        except Exception as e:
            results[code] = {"error": str(e)}

# 输出排序结果
sorted_stocks = sorted(
    [(code, data) for code, data in results.items() if "error" not in data],
    key=lambda x: x[1]["score"], 
    reverse=True
)

for code, data in sorted_stocks:
    print(f"{code}: {data['score']}分 ({data['recommendation']})")
```

## ⚙️ 配置说明

### 配置文件结构

系统使用JSON格式的配置文件，主要配置项包括：

```json
{
  "deep_think_llm": "o4-mini",
  "quick_think_llm": "gpt-4o-mini",
  "openai_api_key": "your_openai_api_key",
  "openai_base_url": "https://api.openai.com/v1",
  "a_share_api_url": "http://localhost:8000/api/v1",
  "a_share_api_key": "your_a_share_api_key",
  "mcp_tools_enabled": true,
  "analysis_execution_mode": "parallel",
  "enable_preprocessing": false,
  "enable_postprocessing": false,
  "default_wacc": 8.5,
  "default_terminal_growth": 2.5,
  "log_level": "INFO"
}
```

### 关键配置说明

#### LLM配置
- `deep_think_llm`: 主要推理模型，用于复杂分析任务
- `quick_think_llm`: 快速响应模型，用于简单任务
- 支持的模型: `gpt-4o`, `gpt-4o-mini`, `o4-mini`, `claude-3-opus`, `claude-3-sonnet`

#### API配置
- `openai_base_url`: OpenAI API端点，支持自定义代理
- `a_share_api_url`: A股数据API地址
- `mcp_tools_enabled`: 是否启用MCP金融工具

#### 分析配置
- `analysis_execution_mode`: `parallel`(并行) 或 `serial`(串行)
- `enable_preprocessing`: 是否启用预处理
- `enable_postprocessing`: 是否启用后处理

#### 估值参数
- `default_wacc`: 默认加权平均成本(%)
- `default_terminal_growth`: 默认永续增长率(%)

### 生成配置文件

```bash
# 生成默认配置文件
python tradingagents/analysis_stock_agent/cli/a_share_cli.py generate-config --output my_config.json

# 使用自定义配置
python tradingagents/analysis_stock_agent/cli/a_share_cli.py analyze 000001 --config my_config.json
```

## 📊 分析深度说明

系统支持三种分析深度，适应不同的使用场景：

### 基础分析 (Basic)
- **适用场景**: 快速筛选、初步评估
- **分析内容**: 核心财务指标、基本行业地位、简单估值
- **分析时间**: 30-60秒
- **报告长度**: 1-2页

### 标准分析 (Standard)  
- **适用场景**: 常规投资决策、定期跟踪
- **分析内容**: 完整财务分析、详细行业对比、多种估值方法
- **分析时间**: 2-3分钟
- **报告长度**: 3-5页

### 综合分析 (Comprehensive)
- **适用场景**: 重要投资决策、深度研究
- **分析内容**: 全面多维分析、敏感性分析、情景分析
- **分析时间**: 5-10分钟  
- **报告长度**: 8-15页

## 🎯 使用场景

### 个人投资者
- **股票筛选**: 批量分析候选股票，识别投资机会
- **投资决策**: 全面分析目标股票，制定投资策略
- **持仓跟踪**: 定期分析持仓股票，调整投资组合

### 专业投资机构
- **研究报告**: 生成专业级股票研究报告
- **风控分析**: 评估投资组合风险，优化配置
- **客户服务**: 为客户提供数据驱动的投资建议

### 金融科技公司
- **产品集成**: 将分析能力集成到现有金融产品
- **API服务**: 为其他开发者提供股票分析API
- **智能投顾**: 构建基于AI的智能投资顾问

## 🔧 开发指南

### 自定义Agent

系统采用模块化设计，支持自定义Agent：

```python
from langchain_core.tools import tool
from tradingagents.analysis_stock_agent.utils.state_models import AnalysisStage

def create_custom_analyst(llm, toolkit, config):
    """创建自定义分析Agent"""
    
    @tool
    def custom_analysis_tool(stock_code: str) -> dict:
        """自定义分析工具"""
        # 实现自定义分析逻辑
        return {"result": "custom analysis"}
    
    def custom_analyst_node(state):
        """自定义分析节点"""
        # 实现分析逻辑
        return {
            **state,
            "custom_analysis_report": "Custom analysis result",
            "analysis_stage": AnalysisStage.CUSTOM_ANALYSIS
        }
    
    return custom_analyst_node
```

### 扩展数据源

添加新的数据源API：

```python
from tradingagents.analysis_stock_agent.utils.data_tools import AShareDataTools

class CustomDataTools(AShareDataTools):
    """自定义数据工具"""
    
    def get_custom_data(self, stock_code: str):
        """获取自定义数据"""
        # 实现自定义数据获取逻辑
        pass
```

### 自定义计算模型

扩展计算工具：

```python
from tradingagents.analysis_stock_agent.utils.calculation_utils import ValuationCalculator

class CustomValuationCalculator(ValuationCalculator):
    """自定义估值计算器"""
    
    @staticmethod
    def custom_valuation_model(financial_data: dict) -> float:
        """自定义估值模型"""
        # 实现自定义估值逻辑
        pass
```

## 🧪 测试和调试

### 运行测试

```bash
# 运行全部测试
python tests/test_a_share_analysis.py

# 运行特定测试
python -m unittest tests.test_a_share_analysis.TestAShareAnalysisSystem.test_stock_code_validation

# 调试模式
python tests/test_a_share_analysis.py --debug
```

### 调试技巧

1. **启用调试模式**
```python
graph = AShareAnalysisGraph(config=config, debug=True)
```

2. **查看中间状态**
```python
# 获取分析状态
status = graph.get_analysis_status("000001", "2024-01-01")
print(status)
```

3. **日志配置**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 性能优化

### 并行处理
- 三个分析Agent并行执行，提高分析效率
- 支持批量分析多只股票

### 缓存机制
- LLM实例缓存，避免重复创建
- 数据API结果缓存，减少网络请求

### 配置优化
- 选择合适的LLM模型平衡速度和质量
- 调整分析深度适应不同场景需求

## 🔒 安全和隐私

### API密钥管理
- 环境变量存储，避免硬编码
- 支持配置文件独立管理
- 敏感信息自动脱敏

### 数据安全
- 本地处理，数据不存储在外部服务器
- 支持私有部署，保护商业机密
- API调用加密传输

## 🚨 故障排除

### 常见问题

#### 1. API密钥错误
```
错误: Authentication failed
解决: 检查OPENAI_API_KEY和A_SHARE_API_KEY环境变量
```

#### 2. 网络连接问题
```
错误: Connection timeout
解决: 检查网络连接，或配置代理服务器
```

#### 3. 模型不支持
```
错误: Model not supported
解决: 检查LLM配置，确保使用支持的模型
```

#### 4. 内存不足
```
错误: Out of memory
解决: 降低分析深度或减少并行分析数量
```

### 日志分析

启用详细日志进行问题诊断：

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🛠️ 部署指南

### 本地开发部署

1. **开发环境搭建**
```bash
# 克隆代码
git clone <repository>
cd TradingAgents

# 创建开发环境
conda create -n dev python=3.13
conda activate dev
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

2. **配置开发环境**
```bash
# 复制环境变量模板
cp .env.example .env
# 编辑.env文件，设置API密钥
```

3. **运行开发服务器**
```bash
# 启动Jupyter Notebook
jupyter notebook examples/

# 或运行示例
python examples/a_share_analysis_example.py
```

### 生产环境部署

#### Docker部署 (推荐)

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["python", "-m", "tradingagents.analysis_stock_agent.api.server"]
```

```bash
# 构建镜像
docker build -t trading-agents .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e A_SHARE_API_KEY=your_key \
  --name trading-agents \
  trading-agents
```

#### 云服务部署

**AWS ECS部署**
```yaml
# ecs-task-definition.json
{
  "family": "trading-agents",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "trading-agents",
      "image": "your-repo/trading-agents:latest",
      "portMappings": [
        {
          "containerPort": 8000
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your_key"
        }
      ]
    }
  ]
}
```

**Azure Container Instances部署**
```bash
az container create \
  --resource-group myResourceGroup \
  --name trading-agents \
  --image your-repo/trading-agents:latest \
  --ports 8000 \
  --environment-variables \
    OPENAI_API_KEY=your_key \
    A_SHARE_API_KEY=your_key
```

### 性能监控

#### 应用监控
```python
# 添加监控中间件
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

#### 系统监控
```bash
# 使用Prometheus + Grafana
# 监控CPU、内存、API调用次数等指标
```

## 📋 API参考

### 核心类

#### AShareAnalysisGraph
主要的分析图类，协调整个分析流程。

```python
class AShareAnalysisGraph:
    def __init__(self, config: Dict = None, debug: bool = False)
    def analyze_stock(self, stock_code: str, stock_name: str = None, 
                     analysis_depth: AnalysisDepth = AnalysisDepth.COMPREHENSIVE) -> Tuple[Dict, str]
    def get_analysis_status(self, stock_code: str, analysis_date: str) -> Dict
    def validate_stock_code(self, stock_code: str) -> bool
    def get_supported_models(self) -> List[str]
```

#### AnalysisDepth
分析深度枚举。

```python
class AnalysisDepth(Enum):
    BASIC = "basic"
    STANDARD = "standard" 
    COMPREHENSIVE = "comprehensive"
```

#### AnalysisStage
分析阶段枚举。

```python
class AnalysisStage(Enum):
    INITIALIZATION = "initialization"
    FINANCIAL_ANALYSIS = "financial_analysis"
    INDUSTRY_ANALYSIS = "industry_analysis"
    VALUATION_ANALYSIS = "valuation_analysis"
    INTEGRATION = "integration"
    COMPLETED = "completed"
    ERROR = "error"
```

### 配置选项

完整的配置选项说明：

```python
A_SHARE_DEFAULT_CONFIG = {
    # LLM配置
    "deep_think_llm": "o4-mini",           # 主要推理模型
    "quick_think_llm": "gpt-4o-mini",      # 快速响应模型
    
    # API配置  
    "openai_api_key": None,                # OpenAI API密钥
    "openai_base_url": "https://api.openai.com/v1",  # OpenAI API端点
    "a_share_api_url": "http://localhost:8000/api/v1",  # A股数据API
    "a_share_api_key": None,               # A股数据API密钥
    "a_share_api_timeout": 30,             # API超时时间(秒)
    "a_share_api_retry_times": 3,          # API重试次数
    
    # MCP工具配置
    "mcp_tools_enabled": True,             # 是否启用MCP工具
    "mcp_server_url": "http://localhost:3000",  # MCP服务器地址
    
    # 分析配置
    "analysis_execution_mode": "parallel", # 执行模式: parallel/serial
    "enable_preprocessing": False,          # 是否启用预处理
    "enable_postprocessing": False,         # 是否启用后处理
    "enable_conditional_edges": False,      # 是否启用条件边
    "enable_retry_logic": False,           # 是否启用重试逻辑
    "max_retries": 3,                      # 最大重试次数
    
    # 估值模型参数
    "default_wacc": 8.5,                   # 默认加权平均成本(%)
    "default_terminal_growth": 2.5,        # 默认永续增长率(%)
    
    # 日志配置
    "log_level": "INFO",                   # 日志级别
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "debug_mode": False                    # 调试模式
}
```

## 🤝 贡献指南

### 开发流程

1. **Fork项目**
2. **创建功能分支**: `git checkout -b feature/new-feature`
3. **提交更改**: `git commit -m 'Add new feature'`
4. **推送分支**: `git push origin feature/new-feature`
5. **创建Pull Request**

### 代码规范

- 遵循PEP 8代码风格
- 添加类型注释
- 编写单元测试
- 更新文档

### 测试要求

- 单元测试覆盖率 > 80%
- 所有测试必须通过
- 代码审查通过

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- LangGraph框架提供了强大的多Agent编排能力
- OpenAI为系统提供了高质量的LLM支持
- A股数据API提供商为系统提供了实时数据支持
- 所有贡献者和测试用户的宝贵反馈

## 📞 联系我们

- **项目维护者**: TradingAgents Team
- **邮箱**: trading.agents@example.com
- **项目地址**: https://github.com/your-org/TradingAgents
- **文档地址**: https://trading-agents.readthedocs.io
- **问题反馈**: https://github.com/your-org/TradingAgents/issues

---

**⚠️ 免责声明**: 本系统仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。使用本系统进行投资决策的风险由用户自行承担。