# A股分析Multi-Agent System 部署指南

## 一、环境准备

### 1.1 系统要求

**最小配置**
- 操作系统：Linux/macOS/Windows
- Python版本：3.9+
- 内存：8GB RAM
- 存储：10GB可用空间
- 网络：稳定的互联网连接

**推荐配置**
- 操作系统：Ubuntu 22.04 LTS / macOS 13+
- Python版本：3.10+
- 内存：16GB+ RAM
- 存储：50GB+ SSD
- 网络：100Mbps+带宽

### 1.2 Python环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 升级pip
pip install --upgrade pip
```

## 二、安装步骤

### 2.1 克隆项目

```bash
# 克隆项目仓库
git clone https://github.com/your-repo/TradingAgents.git
cd TradingAgents
```

### 2.2 安装依赖

```bash
# 安装A股分析系统依赖
pip install -r tradingagents/analysis_stock_agent/requirements.txt

# 验证安装
python -c "import akshare; import langchain; print('依赖安装成功')"
```

### 2.3 配置环境变量

创建`.env`文件：

```bash
# .env
# LLM配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 或自定义endpoint

# 数据源配置（可选）
TUSHARE_TOKEN=your_tushare_token  # 如果使用Tushare

# 系统配置
LOG_LEVEL=INFO
DATA_CACHE_DIR=./cache
RESULTS_DIR=./results
```

## 三、LLM配置方案

### 方案1：使用OpenAI API

```python
# 配置OpenAI
export OPENAI_API_KEY="sk-..."

# 在代码中使用
config = StockAnalysisConfig(
    llm_provider="openai",
    deep_think_llm="gpt-4o",
    quick_think_llm="gpt-4o-mini"
)
```

### 方案2：使用自定义Endpoint

许多国内服务商提供OpenAI兼容接口：

```python
# 配置自定义endpoint
export OPENAI_API_KEY="your_api_key"
export OPENAI_BASE_URL="https://your-provider.com/v1"

config = StockAnalysisConfig(
    llm_provider="openai",
    backend_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 方案3：使用本地Ollama（成本优化）

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull qwen2.5:14b  # 深度思考模型
ollama pull qwen2.5:7b   # 快速分析模型

# 启动Ollama服务
ollama serve
```

修改配置使用Ollama：

```python
config = StockAnalysisConfig(
    llm_provider="openai",  # Ollama兼容OpenAI接口
    backend_url="http://localhost:11434/v1",
    deep_think_llm="qwen2.5:14b",
    quick_think_llm="qwen2.5:7b",
    api_key="ollama"  # Ollama不需要真实API key
)
```

## 四、Docker部署（推荐）

### 4.1 构建Docker镜像

创建`Dockerfile`：

```dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY tradingagents/analysis_stock_agent /app/analysis_stock_agent
COPY tradingagents/analysis_stock_agent/requirements.txt /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口（如果需要API服务）
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "analysis_stock_agent"]
```

### 4.2 使用Docker Compose

创建`docker-compose.yml`：

```yaml
version: '3.8'

services:
  # 主服务
  stock-analysis:
    build: .
    container_name: stock-analysis
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL}
      - LOG_LEVEL=INFO
    volumes:
      - ./cache:/app/cache
      - ./results:/app/results
      - ./logs:/app/logs
    networks:
      - analysis-network
    restart: unless-stopped

  # Redis缓存（可选）
  redis:
    image: redis:7-alpine
    container_name: stock-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - analysis-network
    restart: unless-stopped

  # Ollama服务（可选，本地LLM）
  ollama:
    image: ollama/ollama:latest
    container_name: stock-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - analysis-network
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # 需要GPU

networks:
  analysis-network:
    driver: bridge

volumes:
  redis_data:
  ollama_data:
```

### 4.3 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f stock-analysis

# 停止服务
docker-compose down
```

## 五、快速验证

### 5.1 测试数据获取

```python
# test_data.py
import akshare as ak

# 测试获取股票数据
df = ak.stock_zh_a_spot_em()
print(f"获取到 {len(df)} 只股票数据")

# 测试获取财务数据
financial = ak.stock_financial_analysis_indicator(
    symbol="600519",
    indicator="按年度"
)
print(f"获取到贵州茅台 {len(financial)} 条财务数据")
```

### 5.2 测试系统功能

```bash
# 运行测试脚本
python scripts/test_stock_analysis.py

# 运行示例
python scripts/example_usage.py
```

### 5.3 分析第一只股票

```python
from tradingagents.analysis_stock_agent import (
    StockAnalysisGraph,
    StockAnalysisConfig
)

# 创建分析系统
config = StockAnalysisConfig()
analyzer = StockAnalysisGraph(config)

# 分析贵州茅台
result = analyzer.analyze("600519")
print(f"分析完成: {result['investment_rating']}")
```

## 六、生产环境部署

### 6.1 使用Gunicorn + FastAPI（API服务）

```python
# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tradingagents.analysis_stock_agent import StockAnalysisGraph

app = FastAPI(title="A股分析API")
analyzer = StockAnalysisGraph()

class AnalysisRequest(BaseModel):
    stock_code: str
    save_report: bool = True

@app.post("/analyze")
async def analyze_stock(request: AnalysisRequest):
    try:
        result = analyzer.analyze(
            stock_code=request.stock_code,
            save_report=request.save_report
        )
        return {
            "status": "success",
            "data": analyzer.get_analysis_summary(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

启动服务：

```bash
# 安装依赖
pip install fastapi uvicorn gunicorn

# 开发环境
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# 生产环境
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6.2 使用Nginx反向代理

```nginx
# /etc/nginx/sites-available/stock-analysis
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /app/static;
    }
}
```

### 6.3 使用Supervisor进程管理

```ini
# /etc/supervisor/conf.d/stock-analysis.conf
[program:stock-analysis]
command=/app/venv/bin/gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/stock-analysis/app.log
environment=PATH="/app/venv/bin",OPENAI_API_KEY="your_key"
```

## 七、监控与维护

### 7.1 日志管理

```python
# 配置日志
import logging
from loguru import logger

# 配置文件轮转
logger.add(
    "logs/stock_analysis_{time}.log",
    rotation="500 MB",
    retention="30 days",
    level="INFO"
)
```

### 7.2 性能监控

```bash
# 使用Prometheus + Grafana
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

### 7.3 定期维护任务

```bash
# 创建定时任务
crontab -e

# 每天凌晨2点清理缓存
0 2 * * * /app/venv/bin/python /app/scripts/clean_cache.py

# 每周日备份分析报告
0 3 * * 0 tar -czf /backup/reports_$(date +\%Y\%m\%d).tar.gz /app/results/

# 每月1号清理过期日志
0 4 1 * * find /var/log/stock-analysis/ -mtime +30 -delete
```

## 八、故障排查

### 8.1 常见问题

**问题1：API连接失败**
```bash
# 检查网络连接
curl https://api.openai.com/v1/models

# 检查API密钥
echo $OPENAI_API_KEY
```

**问题2：数据获取失败**
```python
# 测试AKShare
import akshare as ak
try:
    df = ak.stock_info_a_code_name()
    print("AKShare正常")
except Exception as e:
    print(f"AKShare异常: {e}")
```

**问题3：内存不足**
```bash
# 检查内存使用
free -h

# 调整Docker内存限制
docker update --memory="2g" stock-analysis
```

### 8.2 性能优化

1. **启用缓存**
```python
config = StockAnalysisConfig(
    cache_enabled=True,
    cache_ttl=7200  # 2小时缓存
)
```

2. **使用本地模型**
```bash
# 部署本地Ollama减少API调用
ollama pull qwen2.5:7b
```

3. **批量处理**
```python
# 批量分析提高效率
results = analyzer.batch_analyze(stock_codes)
```

## 九、安全建议

1. **API密钥管理**
   - 使用环境变量存储敏感信息
   - 定期轮换API密钥
   - 使用密钥管理服务（如AWS Secrets Manager）

2. **访问控制**
   - 限制API访问IP
   - 实施速率限制
   - 使用认证中间件

3. **数据安全**
   - 加密存储敏感数据
   - 定期备份重要数据
   - 遵守数据隐私法规

## 十、升级指南

```bash
# 备份当前版本
cp -r /app /app_backup_$(date +%Y%m%d)

# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
supervisorctl restart stock-analysis
```

---

*如有问题，请参考项目文档或提交Issue*
