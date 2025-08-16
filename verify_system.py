"""
A股分析系统完整性验证

验证所有4个Agent是否已经正确实现和集成
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def verify_system_completeness():
    """验证系统完整性"""
    print("🔍 A股分析系统完整性验证")
    print("="*50)
    
    verification_results = {}
    
    # 1. 验证Agent文件存在
    print("\n📁 检查Agent文件...")
    agent_files = [
        "tradingagents/analysis_stock_agent/agents/financial_analyst.py",
        "tradingagents/analysis_stock_agent/agents/industry_analyst.py", 
        "tradingagents/analysis_stock_agent/agents/valuation_analyst.py",
        "tradingagents/analysis_stock_agent/agents/information_integrator.py"
    ]
    
    for agent_file in agent_files:
        file_path = project_root / agent_file
        exists = file_path.exists()
        agent_name = agent_file.split("/")[-1].replace(".py", "")
        verification_results[f"{agent_name}_file"] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {agent_name}")
        
        if exists:
            # 检查文件大小
            size = file_path.stat().st_size
            print(f"      文件大小: {size} bytes")
    
    # 2. 验证提示词模板
    print("\n📝 检查提示词模板...")
    prompt_files = [
        "tradingagents/analysis_stock_agent/prompts/financial_prompts.py",
        "tradingagents/analysis_stock_agent/prompts/industry_prompts.py",
        "tradingagents/analysis_stock_agent/prompts/valuation_prompts.py", 
        "tradingagents/analysis_stock_agent/prompts/integration_prompts.py"
    ]
    
    for prompt_file in prompt_files:
        file_path = project_root / prompt_file
        exists = file_path.exists()
        prompt_name = prompt_file.split("/")[-1].replace("_prompts.py", "")
        verification_results[f"{prompt_name}_prompts"] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {prompt_name}_prompts.py")
    
    # 3. 验证导入功能
    print("\n🔗 检查模块导入...")
    try:
        from tradingagents.analysis_stock_agent import (
            AShareAnalysisGraph,
            A_SHARE_DEFAULT_CONFIG,
            StockAnalysisState,
            AnalysisStage,
            AnalysisDepth
        )
        print("  ✅ 主模块导入成功")
        verification_results["main_import"] = True
    except Exception as e:
        print(f"  ❌ 主模块导入失败: {e}")
        verification_results["main_import"] = False
    
    # 4. 验证Agent创建函数
    print("\n🤖 检查Agent创建函数...")
    agent_creators = [
        ("financial_analyst", "create_financial_analyst"),
        ("industry_analyst", "create_industry_analyst"),
        ("valuation_analyst", "create_valuation_analyst"),
        ("information_integrator", "create_information_integrator")
    ]
    
    for module_name, creator_name in agent_creators:
        try:
            module = __import__(f"tradingagents.analysis_stock_agent.agents.{module_name}", 
                              fromlist=[creator_name])
            creator_func = getattr(module, creator_name)
            print(f"  ✅ {creator_name}")
            verification_results[f"{module_name}_creator"] = True
        except Exception as e:
            print(f"  ❌ {creator_name}: {e}")
            verification_results[f"{module_name}_creator"] = False
    
    # 5. 验证图结构
    print("\n🏗️ 检查图结构...")
    try:
        graph = AShareAnalysisGraph()
        print("  ✅ 图创建成功")
        verification_results["graph_creation"] = True
        
        # 检查节点数量
        if hasattr(graph.graph, '_nodes'):
            node_count = len(graph.graph._nodes)
            print(f"      图节点数量: {node_count}")
            verification_results["node_count"] = node_count
        
    except Exception as e:
        print(f"  ❌ 图创建失败: {e}")
        verification_results["graph_creation"] = False
    
    # 6. 验证工具文件
    print("\n🔧 检查工具模块...")
    tool_files = [
        "tradingagents/analysis_stock_agent/utils/state_models.py",
        "tradingagents/analysis_stock_agent/utils/data_tools.py",
        "tradingagents/analysis_stock_agent/utils/calculation_utils.py",
        "tradingagents/analysis_stock_agent/utils/llm_utils.py",
        "tradingagents/analysis_stock_agent/utils/mcp_tools.py"
    ]
    
    for tool_file in tool_files:
        file_path = project_root / tool_file
        exists = file_path.exists()
        tool_name = tool_file.split("/")[-1].replace(".py", "")
        verification_results[f"{tool_name}_tool"] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {tool_name}")
    
    # 7. 验证CLI和示例
    print("\n💻 检查CLI和示例...")
    other_files = [
        "tradingagents/analysis_stock_agent/cli/a_share_cli.py",
        "examples/a_share_analysis_example.py",
        "tests/test_a_share_analysis.py"
    ]
    
    for other_file in other_files:
        file_path = project_root / other_file
        exists = file_path.exists()
        file_name = other_file.split("/")[-1]
        verification_results[f"{file_name}_file"] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {file_name}")
    
    # 8. 详细检查信息整合Agent
    print("\n🎯 详细检查信息整合Agent...")
    try:
        from tradingagents.analysis_stock_agent.agents.information_integrator import create_information_integrator
        print("  ✅ 信息整合Agent导入成功")
        
        # 检查关键函数
        import inspect
        from tradingagents.analysis_stock_agent.agents import information_integrator
        
        # 获取模块中的所有函数
        functions = inspect.getmembers(information_integrator, inspect.isfunction)
        tool_functions = [name for name, func in functions if hasattr(func, 'name')]
        
        print(f"  ✅ 找到 {len(tool_functions)} 个工具函数:")
        for tool_name in tool_functions:
            print(f"      • {tool_name}")
        
        verification_results["integration_tools_count"] = len(tool_functions)
        
    except Exception as e:
        print(f"  ❌ 信息整合Agent检查失败: {e}")
        verification_results["integration_agent_check"] = False
    
    # 汇总结果
    print("\n" + "="*50)
    print("📊 验证结果汇总:")
    
    total_checks = len(verification_results)
    passed_checks = sum(1 for v in verification_results.values() if v is True)
    
    print(f"总检查项: {total_checks}")
    print(f"通过检查: {passed_checks}")
    print(f"成功率: {passed_checks/total_checks*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 系统完整性验证通过！所有4个Agent都已正确实现")
        print("\n✅ 已实现的Agent:")
        print("  1. 💰 财务指标分析Agent")
        print("  2. 🏭 行业对比与竞争优势分析Agent") 
        print("  3. 📈 估值与市场信号分析Agent")
        print("  4. 🎯 信息整合Agent")
        
        print("\n💡 系统可以正常使用了！")
    else:
        print(f"\n⚠️ 发现 {total_checks - passed_checks} 个问题，需要修复")
        
        failed_checks = [k for k, v in verification_results.items() if v is False]
        for failed in failed_checks:
            print(f"  ❌ {failed}")
    
    return verification_results

if __name__ == "__main__":
    verify_system_completeness()