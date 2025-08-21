"""
LangChain + Gemini 多轮链式工具调用 Demo

这个demo展示了如何使用 Gemini + LangChain 实现多轮链式工具调用。
Agent 每次只调用一个工具，但由 AgentExecutor 在外层循环，把工具返回的结果塞回对话，
再决定是否继续调用下一个工具，直到模型给出最终答案。

依赖：
pip install "langchain>=0.2" "langchain-google-genai>=2.0.0" pydantic

环境变量：
export GOOGLE_API_KEY="你的_Gemini_Key"
或在 .env 文件中配置
"""

import os
from typing import Literal
from datetime import date
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ===== 1) 定义工具（@tool） =====

@tool
def get_user_profile(user_id: str) -> str:
    """Return user's profile. Input: user_id (str)."""
    # 假数据
    profiles = {
        "42": {"name": "Alice", "city": "Singapore"},
        "7":  {"name": "Bob", "city": "Beijing"},
        "123": {"name": "Charlie", "city": "Shanghai"},
        "999": {"name": "David", "city": "Shenzhen"},
    }
    p = profiles.get(user_id)
    return "NOT_FOUND" if p is None else f"name={p['name']}; city={p['city']}"

@tool
def calculator(expression: str) -> str:
    """Safe arithmetic calculator. Input: a math expression string with + - * / and parentheses."""
    allowed = set("0123456789+-*/(). ")
    if any(ch not in allowed for ch in expression):
        return "ERROR: unsupported characters"
    try:
        # eval 在受限字符集下进行，演示用途
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"ERROR: {e}"

@tool
def weather_is_good_for_cycling(city: str, day: Literal["today","tomorrow","the_day_after"]) -> str:
    """Return yes/no if weather is good for cycling in given city and day."""
    # 演示：简单规则
    good_map = {
        "Singapore": {"today": "yes", "tomorrow": "yes", "the_day_after": "no"},
        "Beijing":   {"today": "no",  "tomorrow": "yes", "the_day_after": "yes"},
        "Shanghai":  {"today": "yes", "tomorrow": "no",  "the_day_after": "yes"},
        "Shenzhen":  {"today": "yes", "tomorrow": "yes", "the_day_after": "yes"},
    }
    key = good_map.get(city, {})
    ans = key.get(day, "unknown")
    return ans

# ===== 2) 组装 Gemini + Tool Calling Agent =====

def create_agent():
    """创建并配置Agent"""
    
    # 检查API Key
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("请在.env文件中配置GOOGLE_API_KEY")
    
    # 初始化模型（Gemini 1.5 Pro 也可换成 flash）
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
    )

    tools = [get_user_profile, calculator, weather_is_good_for_cycling]

    # 系统提示：要求模型按目标分解步骤；若需要则多次调用不同工具
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "你是一个可以使用工具的助手。你可以按步骤调用多个不同工具来完成复杂任务；"
         "每一步只调用一个工具，拿到结果后再决定下一步。"
         "当你有了足够信息，请直接给出最终答案。"),
        ("human", "{input}"),
        # 可选：向模型展示中间状态的占位
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,                      # 打印中间过程（便于调试）
        handle_parsing_errors=True,        # 容错
        max_iterations=8,                  # 最多链 8 步
        return_intermediate_steps=True,    # 拿到中间工具调用记录
    )
    
    return executor

# ===== 3) 测试示例 =====

def test_chain_calling():
    """测试链式工具调用"""
    
    print("=== 初始化Agent ===")
    executor = create_agent()
    
    # 测试1：需要链式调用的复杂任务
    query1 = (
        "用户ID是 42。请先查他的姓名和所在城市；"
        "再判断他所在城市'明天'是否适合骑行；"
        "然后计算 (12*3+5)/7 的结果；"
        "最后把姓名、城市、是否适合骑行、以及计算结果整理成一句中文话回复我。"
    )
    
    print(f"\n=== 测试1：复杂链式调用 ===")
    print(f"Query: {query1}")
    print("\n" + "="*60)
    
    result1 = executor.invoke({"input": query1})
    
    print("\n=== 最终答案 ===")
    print(result1["output"])
    
    print("\n=== 中间工具调用（链式） ===")
    for i, step in enumerate(result1["intermediate_steps"], 1):
        action, observation = step
        print(f"\n步骤 {i}:")
        print(f"[TOOL] {action.tool}  <- args={action.tool_input}")
        print(f"[OBS]  {observation}")
    
    # 测试2：简单计算任务
    query2 = "请帮我计算 (100 - 25) * 2 + 15 的结果"
    
    print(f"\n\n=== 测试2：简单工具调用 ===")
    print(f"Query: {query2}")
    print("\n" + "="*60)
    
    result2 = executor.invoke({"input": query2})
    
    print("\n=== 最终答案 ===")
    print(result2["output"])
    
    # 测试3：用户档案查询 + 天气查询
    query3 = "用户ID是7，请查询他的信息，然后告诉我他所在城市后天是否适合骑行。"
    
    print(f"\n\n=== 测试3：双工具链式调用 ===")
    print(f"Query: {query3}")
    print("\n" + "="*60)
    
    result3 = executor.invoke({"input": query3})
    
    print("\n=== 最终答案 ===")
    print(result3["output"])
    
    print("\n=== 中间工具调用 ===")
    for i, step in enumerate(result3["intermediate_steps"], 1):
        action, observation = step
        print(f"\n步骤 {i}:")
        print(f"[TOOL] {action.tool}  <- args={action.tool_input}")
        print(f"[OBS]  {observation}")

def test_individual_tools():
    """测试各个工具的功能"""
    
    print("=== 测试各个工具功能 ===")
    
    # 测试用户档案查询 - 调用原始函数而不是工具对象
    print("\n1. 用户档案查询:")
    print(f"用户42: {get_user_profile.func('42')}")
    print(f"用户7: {get_user_profile.func('7')}")
    print(f"用户999: {get_user_profile.func('999')}")
    print(f"不存在用户: {get_user_profile.func('unknown')}")
    
    # 测试计算器
    print("\n2. 计算器:")
    print(f"(12*3+5)/7 = {calculator.func('(12*3+5)/7')}")
    print(f"100 + 200 = {calculator.func('100 + 200')}")
    print(f"无效表达式: {calculator.func('import os')}")
    
    # 测试天气查询
    print("\n3. 天气查询:")
    print(f"Singapore今天: {weather_is_good_for_cycling.func('Singapore', 'today')}")
    print(f"Beijing明天: {weather_is_good_for_cycling.func('Beijing', 'tomorrow')}")
    print(f"Shanghai后天: {weather_is_good_for_cycling.func('Shanghai', 'the_day_after')}")

if __name__ == "__main__":
    try:
        print("LangChain + Gemini 多轮链式工具调用 Demo")
        print("="*50)
        
        # 先测试各个工具
        # test_individual_tools()
        
        print("\n" + "="*50)
        
        # 再测试Agent链式调用
        test_chain_calling()
        
    except Exception as e:
        print(f"错误：{e}")
        print("\n请确保：")
        print("1. 已安装依赖：pip install langchain langchain-google-genai pydantic python-dotenv")
        print("2. 已在.env文件中配置GOOGLE_API_KEY")
        print("3. 网络连接正常")
