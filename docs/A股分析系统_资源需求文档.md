# A股分析Multi-Agent System 资源需求文档

## 一、概述

本文档详细说明A股分析Multi-Agent System所需的各类资源，包括数据源、工具库、LLM服务、基础设施等，为系统部署和运行提供完整的资源清单。

## 二、数据源需求

### 2.1 主要数据源：AKShare

#### 安装方式
```bash
pip install akshare --upgrade
```

#### 主要使用接口

| 功能模块 | 接口名称 | 用途说明 | 数据示例 |
|---------|---------|---------|---------|
| **财务数据** | | | |
| 资产负债表 | `stock_balance_sheet_by_report_em` | 获取按报告期的资产负债表 | 总资产、负债、净资产等 |
| 利润表 | `stock_profit_sheet_by_report_em` | 获取按报告期的利润表 | 营收、净利润、毛利率等 |
| 现金流量表 | `stock_cash_flow_sheet_by_report_em` | 获取按报告期的现金流量表 | 经营/投资/筹资现金流 |
| 财务指标 | `stock_financial_analysis_indicator` | 获取主要财务指标 | ROE、ROA、资产负债率等 |
| **行业数据** | | | |
| 行业分类 | `stock_industry_category_cninfo` | 获取股票行业分类 | 申万一级/二级/三级行业 |
| 行业PE/PB | `stock_industry_pe_ratio_cninfo` | 获取行业市盈率数据 | 行业平均PE、PB |
| 行业成分股 | `sw_index_third_cons` | 获取申万行业成分股 | 同行业公司列表 |
| **股东数据** | | | |
| 股东人数 | `stock_zh_a_gdhs` | 获取股东人数变化 | 股东总数及变化趋势 |
| 十大股东 | `stock_circulate_stock_holder` | 获取十大流通股东 | 主要股东及持股比例 |
| 股东增减持 | `stock_dzjy_sctj` | 获取大宗交易数据 | 重要股东增减持情况 |
| **市场数据** | | | |
| 实时行情 | `stock_zh_a_spot_em` | 获取A股实时行情 | 股价、成交量、涨跌幅等 |
| 历史行情 | `stock_zh_a_hist` | 获取历史K线数据 | OHLCV数据 |
| 分红数据 | `stock_dividend_cninfo` | 获取历史分红数据 | 分红金额、股息率等 |

#### 数据更新频率
- 实时数据：1分钟更新
- 日线数据：每日收盘后更新
- 财务数据：季报/年报发布后更新

### 2.2 备选数据源：Tushare Pro（可选）

#### 安装与配置
```bash
pip install tushare
```

```python
import tushare as ts
# 需要在tushare.pro注册获取token
ts.set_token('your_token_here')
pro = ts.pro_api()
```

#### 使用场景
- 数据验证和交叉检验
- 获取更详细的财务数据
- 特殊数据需求（如：业绩预告、机构调研等）

### 2.3 数据缓存策略

```python
CACHE_CONFIG = {
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "ttl": {
            "realtime": 60,        # 实时数据缓存1分钟
            "daily": 3600,         # 日线数据缓存1小时
            "financial": 86400,    # 财务数据缓存1天
        }
    },
    "local_file": {
        "path": "./data_cache",
        "format": "parquet",       # 使用parquet格式存储
        "compression": "snappy"
    }
}
```

## 三、LLM资源需求

### 3.1 模型选择方案

#### 方案一：OpenAI API兼容接口（推荐）
```python
LLM_CONFIG = {
    "provider": "openai",
    "models": {
        "deep_thinking": {
            "model": "gpt-4o",           # 深度分析模型
            "temperature": 0.7,
            "max_tokens": 4096
        },
        "quick_thinking": {
            "model": "gpt-4o-mini",      # 快速响应模型
            "temperature": 0.5,
            "max_tokens": 2048
        }
    },
    "endpoint": "https://api.openai.com/v1",  # 或自定义endpoint
    "api_key": "YOUR_API_KEY"
}
```

#### 方案二：本地Ollama部署（成本优化）
```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull qwen2.5:14b  # 用于深度思考
ollama pull qwen2.5:7b   # 用于快速分析
```

```python
OLLAMA_CONFIG = {
    "provider": "ollama",
    "models": {
        "deep_thinking": "qwen2.5:14b",
        "quick_thinking": "qwen2.5:7b"
    },
    "base_url": "http://localhost:11434/v1"
}
```

#### 方案三：混合部署（平衡成本与效果）
```python
HYBRID_CONFIG = {
    "report_integration": "gpt-4o",         # 云端强模型
    "financial_analysis": "ollama/qwen2.5:7b",  # 本地模型
    "industry_analysis": "ollama/qwen2.5:7b",   # 本地模型
    "valuation_analysis": "ollama/qwen2.5:7b"   # 本地模型
}
```

### 3.2 模型资源估算

| 模型类型 | 调用频率 | 单次Token | 月度Token估算 | 预估成本 |
|---------|---------|-----------|--------------|----------|
| 深度思考模型 | 1次/分析 | ~3000 | 30万 | $15-30 |
| 快速响应模型 | 3次/分析 | ~1500 | 45万 | $5-10 |
| **合计** | - | - | **75万** | **$20-40/月** |

*注：基于每天10个股票分析任务估算*

## 四、工具库依赖

### 4.1 核心依赖

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.9"

# 数据获取
akshare = "^1.13.0"
tushare = "^1.4.0"  # 可选

# LLM框架
langchain = "^0.2.0"
langchain-openai = "^0.1.0"
langchain-community = "^0.2.0"
langgraph = "^0.1.0"

# 数据处理
pandas = "^2.2.0"
numpy = "^1.26.0"
scipy = "^1.12.0"

# 向量数据库
chromadb = "^0.4.0"  # 或 faiss-cpu
sentence-transformers = "^2.3.0"

# Web框架（API服务）
fastapi = "^0.110.0"
uvicorn = "^0.27.0"
pydantic = "^2.5.0"

# 工具库
python-dotenv = "^1.0.0"
loguru = "^0.7.0"
tenacity = "^8.2.0"  # 重试机制
cachetools = "^5.3.0"  # 缓存

# 报告生成
jinja2 = "^3.1.0"
markdown = "^3.5.0"
weasyprint = "^61.0"  # PDF生成（可选）
```

### 4.2 开发工具

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.1.0"
black = "^24.0.0"
ruff = "^0.2.0"
mypy = "^1.8.0"
ipython = "^8.20.0"
jupyter = "^1.0.0"
```

## 五、基础设施需求

### 5.1 硬件需求

#### 最小配置（开发环境）
- CPU: 4核
- 内存: 8GB
- 存储: 50GB SSD
- 网络: 稳定的互联网连接

#### 推荐配置（生产环境）
- CPU: 8核+
- 内存: 16GB+
- 存储: 100GB+ SSD
- GPU: 可选（如使用本地LLM）

### 5.2 容器化部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 主服务
  analysis-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=${LLM_PROVIDER}
      - BACKEND_URL=${BACKEND_URL}
      - API_KEY=${API_KEY}
    volumes:
      - ./cache:/app/cache
      - ./results:/app/results
    depends_on:
      - redis
      - chroma
    
  # 缓存服务
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      
  # 向量数据库
  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8090:8000"
    volumes:
      - chroma_data:/chroma/chroma
      
  # Ollama服务（可选）
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # 需要GPU

volumes:
  redis_data:
  chroma_data:
  ollama_data:
```

## 六、外部服务依赖

### 6.1 必需服务

| 服务名称 | 用途 | 获取方式 | 费用 |
|---------|------|---------|------|
| LLM API | AI模型调用 | OpenAI/自定义endpoint | 按使用量计费 |
| AKShare | A股数据 | 开源免费 | 免费 |

### 6.2 可选服务

| 服务名称 | 用途 | 获取方式 | 费用 |
|---------|------|---------|------|
| Tushare Pro | 数据补充 | tushare.pro注册 | 积分制 |
| 搜索API | 实时资讯 | Serper/Google | 按调用计费 |
| 监控服务 | 系统监控 | Prometheus/Grafana | 开源免费 |

## 七、环境配置

### 7.1 环境变量配置

```bash
# .env文件
# LLM配置
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 数据源配置
TUSHARE_TOKEN=your_tushare_token  # 可选
DATA_CACHE_DIR=./data_cache

# 系统配置
LOG_LEVEL=INFO
MAX_WORKERS=4
REQUEST_TIMEOUT=30

# 数据库配置
REDIS_URL=redis://localhost:6379/0
CHROMA_HOST=localhost
CHROMA_PORT=8090

# API服务配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

### 7.2 配置文件

```yaml
# config.yaml
analysis:
  max_concurrent_tasks: 5
  cache_ttl: 3600
  retry_times: 3
  
data_sources:
  primary: akshare
  fallback: tushare
  
models:
  deep_thinking:
    provider: openai
    model: gpt-4o
    temperature: 0.7
    max_tokens: 4096
    
  quick_thinking:
    provider: openai
    model: gpt-4o-mini
    temperature: 0.5
    max_tokens: 2048
    
reporting:
  format: markdown
  include_charts: true
  language: zh_CN
```

## 八、部署检查清单

### 8.1 环境准备
- [ ] Python 3.9+ 已安装
- [ ] Docker & Docker Compose 已安装（可选）
- [ ] Git 已安装

### 8.2 依赖安装
- [ ] 所有Python包已安装
- [ ] AKShare正常工作
- [ ] LLM API可访问

### 8.3 配置完成
- [ ] .env文件已配置
- [ ] config.yaml已配置
- [ ] 数据目录已创建

### 8.4 服务启动
- [ ] Redis服务运行中
- [ ] 向量数据库运行中
- [ ] API服务可访问

## 九、成本预算

### 9.1 月度成本估算（生产环境）

| 项目 | 规格 | 单价 | 数量 | 月度费用 |
|------|------|------|------|---------|
| 云服务器 | 8核16G | $100/月 | 1 | $100 |
| LLM API | GPT-4 | $0.03/1K tokens | ~1M tokens | $30 |
| 存储 | 100GB SSD | $10/月 | 1 | $10 |
| 带宽 | 100Mbps | $20/月 | 1 | $20 |
| **合计** | - | - | - | **$160/月** |

### 9.2 成本优化建议

1. **使用本地模型**：部署Ollama可节省70%+ LLM成本
2. **数据缓存**：合理缓存可减少50%+ API调用
3. **批量处理**：批量分析可提高资源利用率
4. **按需扩容**：使用云服务的弹性扩容能力

## 十、备份与恢复

### 10.1 数据备份策略

```python
BACKUP_CONFIG = {
    "schedule": "0 2 * * *",  # 每天凌晨2点
    "retention": 30,          # 保留30天
    "targets": [
        "redis_snapshot",
        "vector_db_export",
        "analysis_reports"
    ],
    "storage": "s3://your-bucket/backups/"
}
```

### 10.2 灾难恢复计划

- **RPO (Recovery Point Objective)**: 24小时
- **RTO (Recovery Time Objective)**: 4小时
- **备份验证**: 每周自动验证备份完整性

## 十一、监控指标

### 11.1 系统监控

```python
METRICS = {
    "system": [
        "cpu_usage",
        "memory_usage",
        "disk_io",
        "network_throughput"
    ],
    "application": [
        "request_rate",
        "response_time",
        "error_rate",
        "cache_hit_rate"
    ],
    "business": [
        "analysis_completed",
        "report_generated",
        "data_freshness",
        "user_satisfaction"
    ]
}
```

### 11.2 告警规则

| 指标 | 阈值 | 级别 | 响应措施 |
|------|------|------|---------|
| CPU使用率 | >80% | 警告 | 检查负载 |
| 内存使用率 | >90% | 严重 | 立即扩容 |
| API错误率 | >1% | 警告 | 检查日志 |
| 响应时间 | >5s | 警告 | 优化查询 |

## 十二、安全要求

### 12.1 访问控制
- API密钥管理
- 角色权限控制
- 审计日志记录

### 12.2 数据安全
- 传输加密（HTTPS）
- 存储加密（AES-256）
- 敏感信息脱敏

### 12.3 合规要求
- 数据使用符合相关法规
- 用户隐私保护
- 定期安全审计

---

*本文档版本：1.0*
*更新日期：2024*
*维护者：A股分析系统团队*
