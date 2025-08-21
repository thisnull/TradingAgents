# LangChain + Gemini 多轮链式工具调用 Demo

这个demo展示了如何使用 **Gemini + LangChain** 实现**多轮链式工具调用**。Agent 每次只调用一个工具，但由 **AgentExecutor** 在外层循环，把工具返回的结果塞回对话，再决定是否继续调用下一个工具，直到模型给出最终答案。

## 功能特性

- ✅ **多轮链式工具调用**：Agent可以连续调用多个工具来完成复杂任务
- ✅ **智能决策**：每步只调用一个工具，根据结果决定下一步
- ✅ **完整观测性**：详细显示每一步的工具调用过程
- ✅ **错误处理**：包含输入校验和错误恢复机制
- ✅ **可扩展**：易于添加新的工具函数

## 包含的工具

1. **用户档案查询** (`get_user_profile`): 根据用户ID查询用户信息
2. **安全计算器** (`calculator`): 支持基本算术运算
3. **天气查询** (`weather_is_good_for_cycling`): 查询某城市某天是否适合骑行

## 环境要求

- Python 3.8+
- Google API Key (用于Gemini模型)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Google API Key：
```
GOOGLE_API_KEY=your_actual_api_key_here
```

> 获取 Google API Key：访问 [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. 运行Demo

```bash
python langchain_gemini_demo.py
```

## Demo示例

### 示例1：复杂链式调用

输入：
```
用户ID是 42。请先查他的姓名和所在城市；
再判断他所在城市'明天'是否适合骑行；
然后计算 (12*3+5)/7 的结果；
最后把姓名、城市、是否适合骑行、以及计算结果整理成一句中文话回复我。
```

Agent执行流程：
1. 调用 `get_user_profile("42")` → 获取用户信息
2. 调用 `weather_is_good_for_cycling("Singapore", "tomorrow")` → 查询天气
3. 调用 `calculator("(12*3+5)/7")` → 计算结果
4. 整合信息并给出最终答案

### 示例2：简单工具调用

输入：
```
请帮我计算 (100 - 25) * 2 + 15 的结果
```

Agent执行流程：
1. 调用 `calculator("(100 - 25) * 2 + 15")` → 直接计算
2. 返回结果

### 示例3：双工具链式调用

输入：
```
用户ID是7，请查询他的信息，然后告诉我他所在城市后天是否适合骑行。
```

Agent执行流程：
1. 调用 `get_user_profile("7")` → 获取用户信息
2. 调用 `weather_is_good_for_cycling("Beijing", "the_day_after")` → 查询天气
3. 整合并返回答案

## 核心架构

### Agent配置

```python
# 系统提示
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个可以使用工具的助手。你可以按步骤调用多个不同工具..."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Agent执行器
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,                      # 显示调试信息
    handle_parsing_errors=True,        # 错误处理
    max_iterations=8,                  # 最大迭代次数
    return_intermediate_steps=True,    # 返回中间步骤
)
```

### 工具定义

使用 `@tool` 装饰器定义工具：

```python
@tool
def get_user_profile(user_id: str) -> str:
    """Return user's profile. Input: user_id (str)."""
    # 工具实现...
```

## 扩展指南

### 添加新工具

1. 使用 `@tool` 装饰器定义新函数
2. 添加清晰的文档字符串
3. 将工具添加到 `tools` 列表中

```python
@tool
def new_tool(param: str) -> str:
    """工具描述. Input: param (str)."""
    # 工具实现
    return result
```

### 自定义Prompt

修改系统提示来改变Agent的行为：

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你的自定义系统提示..."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
```

## 故障排除

### 常见问题

1. **API Key错误**
   - 确保 `.env` 文件中的 `GOOGLE_API_KEY` 正确配置
   - 检查API Key是否有效且有足够配额

2. **网络连接问题**
   - 确保网络可以访问Google AI服务
   - 考虑代理设置

3. **依赖包问题**
   - 确保使用正确的Python版本 (3.8+)
   - 重新安装依赖：`pip install -r requirements.txt`

### 调试模式

Demo默认开启了详细日志（`verbose=True`），会显示：
- 每一步的工具调用
- 工具参数
- 工具返回结果
- Agent的思考过程

## 参考资料

- [LangChain 官方文档](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [LangChain Agent 教程](https://python.langchain.com/docs/modules/agents/)
