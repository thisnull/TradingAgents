#!/usr/bin/env python3
"""
TradingAgents 快速测试脚本
快速验证系统是否可以正常工作
"""

import os
import sys
from datetime import datetime, timedelta

# 加载.env文件
def load_env_file():
    """加载.env文件中的环境变量"""
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ 已加载 .env 文件")
    else:
        print("⚠️  未找到 .env 文件，使用系统环境变量")

# 在导入其他模块前先加载环境变量
load_env_file()

def quick_test():
    """快速测试TradingAgents系统"""
    print("🚀 TradingAgents 快速测试开始...")
    
    # 1. 检查环境变量
    print("\n1️⃣ 检查环境变量...")
    required_vars = ["OPENAI_API_KEY", "TRADINGAGENTS_BACKEND_URL"]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: 未设置")
            if var == "OPENAI_API_KEY":
                print("   💡 提示: 使用自定义endpoint时，仍需要设置OPENAI_API_KEY作为认证密钥")
                print("        这是LangChain ChatOpenAI客户端的要求，请在.env文件中设置您的API密钥")
            return False
    
    # 2. 测试导入
    print("\n2️⃣ 测试模块导入...")
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        print("   ✅ 核心模块导入成功")
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        return False
    
    # 3. 测试配置加载
    print("\n3️⃣ 测试配置加载...")
    try:
        print(f"   ✅ LLM Provider: {DEFAULT_CONFIG['llm_provider']}")
        print(f"   ✅ Backend URL: {DEFAULT_CONFIG['backend_url']}")
        print(f"   ✅ Deep Think Model: {DEFAULT_CONFIG['deep_think_llm']}")
        print(f"   ✅ Quick Think Model: {DEFAULT_CONFIG['quick_think_llm']}")
    except Exception as e:
        print(f"   ❌ 配置加载失败: {e}")
        return False
    
    # 4. 测试系统初始化
    print("\n4️⃣ 测试系统初始化...")
    try:
        # 创建简化配置以加快测试
        test_config = DEFAULT_CONFIG.copy()
        test_config["max_debate_rounds"] = 1
        test_config["max_risk_discuss_rounds"] = 1
        
        ta = TradingAgentsGraph(debug=False, config=test_config)
        print("   ✅ TradingAgents 初始化成功")
    except Exception as e:
        print(f"   ❌ 系统初始化失败: {e}")
        return False
    
    # 5. 测试LLM连接（可选）
    print("\n5️⃣ 测试LLM连接（快速）...")
    try:
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model=DEFAULT_CONFIG["quick_think_llm"],
            base_url=DEFAULT_CONFIG["backend_url"],
            temperature=0.1
        )
        
        response = llm.invoke("请回复'测试成功'")
        if response and hasattr(response, 'content'):
            print(f"   ✅ LLM响应: {response.content[:50]}...")
        else:
            print("   ⚠️  LLM响应格式异常")
            
    except Exception as e:
        print(f"   ❌ LLM连接失败: {e}")
        return False
    
    print("\n🎉 快速测试完成！系统基本配置正确。")
    print("\n如需完整测试，请运行: python test_system.py")
    return True

def run_mini_analysis():
    """运行一个最小化的分析流程测试"""
    print("\n🧪 运行最小化分析测试...")
    print("⚠️  注意：这将产生实际的API调用费用")
    
    response = input("是否继续？(y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("跳过分析测试")
        return True
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 最小化配置
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = 1
        config["max_risk_discuss_rounds"] = 1
        config["online_tools"] = True
        
        print("   正在初始化TradingAgents...")
        ta = TradingAgentsGraph(debug=True, config=config)
        
        print("   正在运行AAPL股票分析...")
        test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        _, decision = ta.propagate("AAPL", test_date)
        
        if decision:
            print(f"   ✅ 分析完成！")
            print(f"   决策摘要: {decision[:150]}...")
            return True
        else:
            print("   ❌ 分析失败，未获得决策")
            return False
            
    except Exception as e:
        print(f"   ❌ 分析测试失败: {e}")
        return False

if __name__ == "__main__":
    if quick_test():
        # 询问是否运行分析测试
        print("\n" + "="*50)
        run_mini_analysis()
        print("\n🚀 TradingAgents 已准备就绪！")
        print("您可以开始使用:")
        print("- CLI模式: python -m cli.main")
        print("- Python API: python main.py")
    else:
        print("\n❌ 系统配置有问题，请检查配置后重试")
        sys.exit(1)