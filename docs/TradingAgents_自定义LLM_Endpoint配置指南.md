# TradingAgents自定义LLM Endpoint配置指南

## 概述

TradingAgents项目设计得非常灵活，**天然支持多种LLM提供商和自定义endpoint**，并不仅限于OpenAI官方API。项目通过配置化的方式，允许用户轻松切换不同的模型服务。

## 支持的LLM提供商

项目目前支持以下LLM提供商：

| 提供商 | 标识符 | 说明 | 典型用例 |
|--------|-------|------|----------|
| **OpenAI** | `openai` | 官方OpenAI API | GPT-4、GPT-3.5等模型 |
| **Ollama** | `ollama` | 本地LLM部署方案 | 私有化部署、成本控制 |
| **OpenRouter** | `openrouter` | 多模型API聚合服务 | 统一接口访问多种模型 |
| **Anthropic** | `anthropic` | Claude系列模型 | 高质量对话和分析能力 |
| **Google** | `google` | Gemini系列模型 | Google的多模态模型 |

## 核心配置参数

在`tradingagents/default_config.py`中，关键的LLM配置参数包括：

```python
DEFAULT_CONFIG = {
    # LLM基础设置
    "llm_provider": "openai",                    # LLM提供商标识
    "backend_url": "https://api.openai.com/v1", # API端点URL
    "deep_think_llm": "o4-mini",                 # 深度思考模型（用于复杂推理）
    "quick_think_llm": "gpt-4o-mini",           # 快速响应模型（用于简单任务）
}
```

## 自定义Endpoint配置方法

### 方法1：代码配置（推荐）

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 创建自定义配置
config = DEFAULT_CONFIG.copy()

# 配置自定义endpoint
config["llm_provider"] = "openai"  # 选择兼容的提供商类型
config["backend_url"] = "https://your-custom-endpoint.com/v1"  # 您的自定义API地址
config["deep_think_llm"] = "your-model-name"    # 深度思考模型名称
config["quick_think_llm"] = "your-model-name"   # 快速响应模型名称

# 初始化TradingAgents
ta = TradingAgentsGraph(debug=True, config=config)
```

### 方法2：环境变量配置

```bash
# 设置环境变量
export TRADINGAGENTS_LLM_PROVIDER="openai"
export TRADINGAGENTS_BACKEND_URL="https://your-api.com/v1"
export TRADINGAGENTS_DEEP_THINK_LLM="your-model"
export TRADINGAGENTS_QUICK_THINK_LLM="your-model"
```

## 常见自定义Endpoint配置示例

### 1. 使用Ollama本地部署

```python
# Ollama本地部署配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "ollama"
config["backend_url"] = "http://localhost:11434/v1"
config["deep_think_llm"] = "qwen2.5:14b"      # 大模型用于深度分析
config["quick_think_llm"] = "qwen2.5:7b"      # 小模型用于快速响应

ta = TradingAgentsGraph(debug=True, config=config)
```

### 2. 使用OpenRouter聚合服务

```python
# OpenRouter配置 - 统一接口访问多种模型
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openrouter"
config["backend_url"] = "https://openrouter.ai/api/v1"
config["deep_think_llm"] = "anthropic/claude-3.5-sonnet"  # 高质量推理
config["quick_think_llm"] = "openai/gpt-4o-mini"          # 快速响应

# 需要设置OpenRouter API密钥
import os
os.environ["OPENAI_API_KEY"] = "your-openrouter-api-key"

ta = TradingAgentsGraph(debug=True, config=config)
```

### 3. 使用私有部署API（vLLM/TGI/FastChat等）

```python
# 私有API服务配置（兼容OpenAI格式）
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"  # 使用OpenAI兼容格式
config["backend_url"] = "https://your-private-api.com/v1"
config["deep_think_llm"] = "custom-finance-model-large"
config["quick_think_llm"] = "custom-finance-model-small"

ta = TradingAgentsGraph(debug=True, config=config)
```

### 4. 使用Anthropic Claude

```python
# Anthropic Claude配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "anthropic"
config["backend_url"] = "https://api.anthropic.com"
config["deep_think_llm"] = "claude-3-5-sonnet-20241022"
config["quick_think_llm"] = "claude-3-haiku-20240307"

# 需要设置Anthropic API密钥
import os
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"

ta = TradingAgentsGraph(debug=True, config=config)
```

### 5. 使用Google Gemini

```python
# Google Gemini配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["backend_url"] = "https://generativelanguage.googleapis.com/v1"
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash"

# 需要设置Google API密钥
import os
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"

ta = TradingAgentsGraph(debug=True, config=config)
```

## 核心实现机制

项目通过以下代码实现灵活的endpoint支持：

```python
# 位置: tradingagents/graph/trading_graph.py
class TradingAgentsGraph:
    def __init__(self, config):
        # 根据配置选择对应的LLM客户端
        if self.config["llm_provider"].lower() == "openai" or \
           self.config["llm_provider"] == "ollama" or \
           self.config["llm_provider"] == "openrouter":
            # 使用ChatOpenAI客户端，支持自定义base_url
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config["deep_think_llm"], 
                base_url=self.config["backend_url"]  # 关键：支持自定义endpoint
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config["quick_think_llm"], 
                base_url=self.config["backend_url"]
            )
            
        elif self.config["llm_provider"].lower() == "anthropic":
            # Anthropic Claude客户端
            self.deep_thinking_llm = ChatAnthropic(
                model=self.config["deep_think_llm"], 
                base_url=self.config["backend_url"]
            )
            
        elif self.config["llm_provider"].lower() == "google":
            # Google Gemini客户端
            self.deep_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config["deep_think_llm"]
            )
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
```

## 模型选择建议

### 深度思考模型 vs 快速响应模型

TradingAgents采用**双模型架构**：

- **深度思考模型** (`deep_think_llm`)：用于复杂的分析任务
  - 研究经理的投资总结
  - 风险经理的最终决策
  - 复杂的市场分析和推理

- **快速响应模型** (`quick_think_llm`)：用于简单的响应任务  
  - 各类分析师的报告生成
  - 研究员的辩论发言
  - 数据处理和格式化

### 推荐配置组合

**成本优化配置：**
```python
config["deep_think_llm"] = "gpt-4o-mini"    # 平衡性能和成本
config["quick_think_llm"] = "gpt-4o-mini"   # 统一使用轻量模型
```

**性能优先配置：**
```python
config["deep_think_llm"] = "o1-preview"     # 最强推理能力
config["quick_think_llm"] = "gpt-4o"        # 高质量快速响应
```

**本地化配置：**
```python
config["deep_think_llm"] = "qwen2.5:32b"    # 本地大模型
config["quick_think_llm"] = "qwen2.5:14b"   # 本地中等模型
```

## API兼容性要求

### OpenAI格式兼容

大多数自定义endpoint需要兼容OpenAI的API格式：

```bash
# 请求格式示例
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "model": "your-model-name",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7
}
```

### 必需的API端点

确保您的自定义endpoint支持以下功能：
- `/v1/chat/completions` - 聊天完成API
- 支持 `messages` 格式的对话历史
- 支持 `tools` 参数（如果使用工具调用功能）
- 返回标准的响应格式

## 环境变量配置

不同LLM提供商需要设置对应的API密钥：

```bash
# OpenAI / OpenRouter / Ollama / 自定义OpenAI兼容API
export OPENAI_API_KEY="your-api-key"

# Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-key"

# Google Gemini
export GOOGLE_API_KEY="your-google-key"

# FinnHub (金融数据，必需)
export FINNHUB_API_KEY="your-finnhub-key"
```

## 故障排查

### 常见问题及解决方案

**1. 连接超时或拒绝连接**
```python
# 检查endpoint地址是否正确
import requests
response = requests.get("https://your-endpoint.com/v1/models")
print(response.status_code)
```

**2. 认证失败**
```python
# 验证API密钥是否正确设置
import os
print("API Key:", os.getenv("OPENAI_API_KEY", "未设置"))
```

**3. 模型不存在**
```python
# 获取可用模型列表
curl -H "Authorization: Bearer your-api-key" \
     https://your-endpoint.com/v1/models
```

**4. 调试连接问题**
```python
# 启用详细日志
config["debug"] = True
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 性能优化建议

### 1. 模型选择策略
- **开发阶段**：使用轻量模型降低成本和延迟
- **生产阶段**：深度思考任务使用高性能模型，快速任务使用效率模型

### 2. 网络优化
- 选择地理位置较近的API服务器
- 考虑使用CDN或代理服务加速访问
- 合理设置超时和重试机制

### 3. 成本控制
```python
# 减少辩论轮数以降低API调用次数
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1

# 使用缓存数据而非实时数据
config["online_tools"] = False
```

## 总结

TradingAgents的LLM配置设计非常灵活和开放，支持几乎所有主流的LLM服务提供商和自定义endpoint。通过简单的配置修改，您可以：

1. **本地化部署** - 使用Ollama等本地方案保护数据隐私
2. **成本优化** - 选择性价比更高的模型服务
3. **性能定制** - 针对不同任务使用最适合的模型
4. **供应商多样化** - 避免单一依赖，提高服务可靠性

无论您是想使用自建的模型服务，还是切换到其他商业API，TradingAgents都能轻松适配，为您的金融AI应用提供最大的灵活性。