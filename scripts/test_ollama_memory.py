#!/usr/bin/env python3
"""
测试TradingAgents使用Ollama embedding的配置
"""

import sys
import os
sys.path.append('.')

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
        print("⚠️  未找到 .env 文件")

# 加载环境变量
load_env_file()

try:
    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.agents.utils.memory import FinancialSituationMemory
    
    print("✅ 成功导入TradingAgents模块")
    
    # 显示当前配置
    print(f"\n🔧 当前配置:")
    print(f"   主LLM Backend: {DEFAULT_CONFIG['backend_url']}")
    print(f"   深度思考模型: {DEFAULT_CONFIG['deep_think_llm']}")
    print(f"   快速响应模型: {DEFAULT_CONFIG['quick_think_llm']}")
    print(f"   Embedding Backend: {DEFAULT_CONFIG['embedding_backend_url']}")
    print(f"   Embedding模型: {DEFAULT_CONFIG['embedding_model']}")
    
    # 测试Memory系统
    print(f"\n🧠 测试记忆系统...")
    
    # 创建Memory实例
    memory = FinancialSituationMemory("test_memory", DEFAULT_CONFIG)
    print("✅ 成功创建FinancialSituationMemory实例")
    
    # 测试embedding功能
    test_text = "股市今天表现良好，科技股上涨3%"
    print(f"🔍 测试文本: {test_text}")
    
    embedding = memory.get_embedding(test_text)
    print(f"✅ 成功获取embedding向量，维度: {len(embedding)}")
    
    # 测试存储和检索
    print(f"\n💾 测试存储和检索功能...")
    
    # 添加一些测试数据
    test_data = [
        ("科技股表现强劲，市场情绪乐观", "建议增加科技股配置，但要注意风险控制"),
        ("通胀压力上升，央行可能加息", "建议减少债券配置，增加抗通胀资产"),
    ]
    
    memory.add_situations(test_data)
    print("✅ 成功添加测试数据到记忆系统")
    
    # 查询相似情况
    query = "今天科技板块涨势不错"
    results = memory.get_memories(query, n_matches=1)
    
    print(f"🔍 查询: {query}")
    print(f"✅ 找到相似情况: {results[0]['matched_situation']}")
    print(f"📊 相似度得分: {results[0]['similarity_score']:.3f}")
    print(f"💡 建议: {results[0]['recommendation']}")
    
    print(f"\n🎉 所有测试通过！TradingAgents现在使用Ollama提供embedding服务")
    
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保您在TradingAgents项目目录中运行此脚本")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    print("请检查Ollama是否正在运行以及配置是否正确")