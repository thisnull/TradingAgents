# TradingAgents自定义LLM配置完整指南

## 📋 快速配置步骤

### 1. 创建环境变量文件

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用您喜欢的编辑器
```

### 2. 配置您的.env文件

根据您的endpoint，修改以下核心配置：

```bash
# 基础LLM服务配置
TRADINGAGENTS_LLM_PROVIDER=openai
TRADINGAGENTS_BACKEND_URL=https://your-custom-endpoint.com/v1
OPENAI_API_KEY=your_custom_api_key_here

# 模型选择（推荐配置）
TRADINGAGENTS_DEEP_THINK_LLM=deepseek-r1
TRADINGAGENTS_QUICK_THINK_LLM=gemini-2.5-flash
```

### 3. 使用配置运行

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 现在默认配置会自动读取.env文件
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG)
_, decision = ta.propagate("NVDA", "2024-05-10")
print(f"交易决策: {decision}")
```

## 🎯 模型选择方案详解

### 方案1: 性能优先（推荐）

```bash
TRADINGAGENTS_DEEP_THINK_LLM=deepseek-r1
TRADINGAGENTS_QUICK_THINK_LLM=gemini-2.5-flash
```

**适用场景**: 生产环境，追求最佳决策质量
**优势**: 
- deepseek-r1具备最强的推理能力，适合复杂的投资决策
- gemini-2.5-flash响应速度快，处理分析任务高效

### 方案2: 成本平衡

```bash
TRADINGAGENTS_DEEP_THINK_LLM=qwen3-235b-a22b  
TRADINGAGENTS_QUICK_THINK_LLM=gemini-2.5-flash
```

**适用场景**: 预算有限但需要良好性能
**优势**:
- qwen3-235b-a22b大参数量模型，推理能力强
- 中文理解能力优秀，适合中文用户

### 方案3: Google生态

```bash
TRADINGAGENTS_DEEP_THINK_LLM=gemini-2.5-pro
TRADINGAGENTS_QUICK_THINK_LLM=gemini-2.5-flash
```

**适用场景**: 偏好Google模型或已有Google生态
**优势**:
- 模型来源统一，兼容性好
- gemini-2.5-pro是Google最强模型

## 🔧 代码修改说明

### 修改的核心文件

我已经修改了 `tradingagents/default_config.py` 文件，添加了环境变量支持：

```python
# 修改前
"deep_think_llm": "o4-mini",
"quick_think_llm": "gpt-4o-mini", 
"backend_url": "https://api.openai.com/v1",

# 修改后 - 支持环境变量
"deep_think_llm": os.getenv("TRADINGAGENTS_DEEP_THINK_LLM", "deepseek-r1"),
"quick_think_llm": os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", "gemini-2.5-flash"),
"backend_url": os.getenv("TRADINGAGENTS_BACKEND_URL", "https://api.openai.com/v1"),
```

### 支持的环境变量列表

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `TRADINGAGENTS_LLM_PROVIDER` | openai | LLM提供商类型 |
| `TRADINGAGENTS_BACKEND_URL` | https://api.openai.com/v1 | API端点URL |
| `TRADINGAGENTS_DEEP_THINK_LLM` | deepseek-r1 | 深度思考模型 |
| `TRADINGAGENTS_QUICK_THINK_LLM` | gemini-2.5-flash | 快速响应模型 |
| `OPENAI_API_KEY` | 无 | API认证密钥 |

## 💡 使用示例

### 基础使用

```python
# 直接使用默认配置(会自动读取.env)
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG)
_, decision = ta.propagate("AAPL", "2024-12-01")
```

### 动态覆盖配置

```python
# 如果需要临时覆盖某些设置
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gemini-2.5-pro"  # 临时使用不同模型

ta = TradingAgentsGraph(debug=True, config=config)
```

### 不同场景的完整配置

**开发测试场景**:
```bash
# .env文件
TRADINGAGENTS_BACKEND_URL=http://localhost:8000/v1  # 本地测试服务
TRADINGAGENTS_DEEP_THINK_LLM=gemini-2.5-flash      # 使用轻量模型节省成本
TRADINGAGENTS_QUICK_THINK_LLM=gemini-2.5-flash
TRADINGAGENTS_MAX_DEBATE_ROUNDS=1                    # 减少API调用
```

**生产环境场景**:
```bash
# .env文件  
TRADINGAGENTS_BACKEND_URL=https://your-production-api.com/v1
TRADINGAGENTS_DEEP_THINK_LLM=deepseek-r1           # 最强推理能力
TRADINGAGENTS_QUICK_THINK_LLM=gemini-2.5-flash     # 高效处理
TRADINGAGENTS_MAX_DEBATE_ROUNDS=3                   # 更充分的讨论
TRADINGAGENTS_MAX_RISK_DISCUSS_ROUNDS=2
```

## 🚀 启动验证

### 验证配置是否生效

```python
from tradingagents.default_config import DEFAULT_CONFIG
import pprint

print("当前配置:")
pprint.pprint({
    "llm_provider": DEFAULT_CONFIG["llm_provider"],
    "backend_url": DEFAULT_CONFIG["backend_url"], 
    "deep_think_llm": DEFAULT_CONFIG["deep_think_llm"],
    "quick_think_llm": DEFAULT_CONFIG["quick_think_llm"],
})
```

### 测试API连接

```python
import os
import requests

# 测试您的endpoint是否可访问
backend_url = os.getenv("TRADINGAGENTS_BACKEND_URL")
api_key = os.getenv("OPENAI_API_KEY")

headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(f"{backend_url}/models", headers=headers)

if response.status_code == 200:
    print("✅ API连接成功")
    print("可用模型:", [model["id"] for model in response.json()["data"]])
else:
    print("❌ API连接失败:", response.status_code, response.text)
```

## 🔍 故障排查

### 常见问题解决

**1. 环境变量未生效**
```bash
# 确认环境变量是否加载
python -c "import os; print('Backend URL:', os.getenv('TRADINGAGENTS_BACKEND_URL'))"
```

**2. 模型名称错误**
```bash
# 检查您的endpoint支持的模型列表
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     $TRADINGAGENTS_BACKEND_URL/models
```

**3. API认证失败**
```bash
# 验证API Key是否正确
echo "API Key: $OPENAI_API_KEY"
```

## 📝 最佳实践

### 1. 环境隔离
```bash
# 不同环境使用不同的.env文件
cp .env.example .env.development
cp .env.example .env.production
```

### 2. 安全配置
```bash
# 确保.env文件不被git追踪
echo ".env" >> .gitignore
```

### 3. 性能监控
```python
# 在config中启用debug模式监控模型调用
config = DEFAULT_CONFIG.copy()
config["debug"] = True
```

通过以上配置，您现在可以无缝地使用自定义endpoint和您选择的模型运行TradingAgents了！