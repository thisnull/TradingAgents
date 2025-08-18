"""
行业分析Agent独立测试

测试industry_analyst.py的独立功能，绕过LangGraph
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.analysis_stock_agent.utils.agent_test_framework import create_test_framework
from tradingagents.analysis_stock_agent.agents.industry_analyst import create_industry_analyst
from tradingagents.analysis_stock_agent.config.a_share_config import A_SHARE_DEFAULT_CONFIG


def test_industry_analyst_isolated():
    """独立测试行业分析Agent"""
    print("🧪 行业分析Agent独立测试")
    print("=" * 60)
    
    # 创建测试框架
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，测试终止")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        print(f"✅ 获取深度思考LLM: {deep_think_llm}")
        
        # 创建行业分析Agent
        industry_analyst_node = create_industry_analyst(
            llm=deep_think_llm,
            toolkit=[],  # 空工具集测试
            config=A_SHARE_DEFAULT_CONFIG
        )
        print("✅ 行业分析Agent创建成功")
        
        # 创建测试状态
        test_state = framework.create_mock_state(
            stock_code="002594",
            stock_name="比亚迪"
        )
        
        print(f"\n📊 测试数据:")
        print(f"  股票代码: {test_state['stock_code']}")
        print(f"  股票名称: {test_state['stock_name']}")
        print(f"  分析日期: {test_state['analysis_date']}")
        
        # 运行Agent测试
        result = framework.run_agent_test(
            agent_name="行业分析Agent",
            agent_function=industry_analyst_node,
            mock_state=test_state
        )
        
        # 详细分析结果
        if result["success"]:
            agent_result = result["result"]
            
            print(f"\n🔍 详细结果分析:")
            
            # 检查必要字段
            required_fields = [
                "messages", 
                "industry_analysis_report",
                "industry_data",
                "key_industry_metrics",
                "competitive_position",
                "data_sources",
                "last_updated"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in agent_result:
                    missing_fields.append(field)
                else:
                    print(f"  ✅ {field}: 存在")
                    
            if missing_fields:
                print(f"  ❌ 缺失字段: {missing_fields}")
                
            # 检查messages结构
            if "messages" in agent_result and agent_result["messages"]:
                message = agent_result["messages"][0]
                print(f"  💬 消息类型: {type(message)}")
                if hasattr(message, 'content'):
                    print(f"  💬 消息内容长度: {len(message.content)} 字符")
                if hasattr(message, 'tool_calls'):
                    print(f"  🔧 工具调用: {len(message.tool_calls) if message.tool_calls else 0} 个")
                    
            # 检查分析报告
            if "industry_analysis_report" in agent_result:
                report = agent_result["industry_analysis_report"]
                print(f"  📄 行业分析报告长度: {len(str(report))} 字符")
                if len(str(report)) > 50:
                    print(f"  📄 报告预览: {str(report)[:100]}...")
                    
            # 检查行业数据
            if "industry_data" in agent_result:
                data = agent_result["industry_data"]
                print(f"  🏭 行业数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"  🏭 行业数据字段: {list(data.keys())}")
                    
            # 检查竞争地位
            if "competitive_position" in agent_result:
                position = agent_result["competitive_position"]
                print(f"  🥇 竞争地位类型: {type(position)}")
                if isinstance(position, dict):
                    print(f"  🥇 竞争地位字段: {list(position.keys())}")
                    
            # 检查数据源
            if "data_sources" in agent_result:
                sources = agent_result["data_sources"]
                print(f"  📚 数据源数量: {len(sources) if sources else 0}")
                if sources:
                    print(f"  📚 数据源列表: {sources}")
                    
            return True
        else:
            print(f"\n💥 测试失败原因:")
            print(f"  错误类型: {result.get('error_type', 'Unknown')}")
            print(f"  错误信息: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_industry_analyst_different_sectors():
    """测试不同行业的股票分析"""
    print("\n🏭 测试不同行业股票分析")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过行业测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建行业分析Agent
        industry_analyst_node = create_industry_analyst(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        print("✅ 行业分析Agent创建成功")
        
        # 测试不同行业的股票
        test_stocks = [
            {
                "name": "新能源汽车",
                "stock_code": "002594",
                "stock_name": "比亚迪"
            },
            {
                "name": "银行业",
                "stock_code": "000001", 
                "stock_name": "平安银行"
            },
            {
                "name": "科技股",
                "stock_code": "000002",
                "stock_name": "万科A"
            },
            {
                "name": "空代码测试",
                "stock_code": "",
                "stock_name": "测试公司"
            }
        ]
        
        test_results = []
        
        for stock in test_stocks:
            print(f"\n📋 测试行业: {stock['name']}")
            
            test_state = framework.create_mock_state(
                stock_code=stock["stock_code"],
                stock_name=stock["stock_name"]
            )
            
            result = framework.run_agent_test(
                agent_name=f"行业分析Agent - {stock['name']}",
                agent_function=industry_analyst_node,
                mock_state=test_state
            )
            
            test_results.append(result)
            
            # 检查特定的行业分析结果
            if result["success"]:
                agent_result = result["result"]
                
                # 分析行业特定信息
                if "industry_analysis_report" in agent_result:
                    report = str(agent_result["industry_analysis_report"])
                    
                    industry_keywords = ["行业", "竞争", "市场", "地位", "优势"]
                    found_keywords = [kw for kw in industry_keywords if kw in report]
                    
                    print(f"  🔍 行业关键词覆盖: {len(found_keywords)}/{len(industry_keywords)}")
                    print(f"  🔍 包含关键词: {found_keywords}")
                    
        # 打印测试总结
        framework.print_test_summary(test_results)
        
        # 分析成功率
        success_count = sum(1 for r in test_results if r["success"])
        success_rate = success_count / len(test_results) * 100
        
        print(f"\n📊 行业分析Agent成功率: {success_rate:.1f}% ({success_count}/{len(test_results)})")
        
        return success_rate >= 50  # 至少50%成功率认为基本可用
        
    except Exception as e:
        print(f"\n❌ 行业测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_industry_analyst_tools():
    """测试行业分析Agent的工具调用"""
    print("\n🔧 测试行业分析Agent工具调用")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过工具测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建行业分析Agent
        industry_analyst_node = create_industry_analyst(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        # 测试状态
        test_state = framework.create_mock_state(
            stock_code="002594",
            stock_name="比亚迪"
        )
        
        print("🔧 运行工具调用测试...")
        
        result = framework.run_agent_test(
            agent_name="行业分析Agent - 工具测试",
            agent_function=industry_analyst_node,
            mock_state=test_state
        )
        
        if result["success"]:
            agent_result = result["result"]
            
            # 检查是否有工具调用
            if "messages" in agent_result and agent_result["messages"]:
                message = agent_result["messages"][0]
                
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print(f"✅ 检测到工具调用: {len(message.tool_calls)} 个")
                    
                    for i, tool_call in enumerate(message.tool_calls):
                        print(f"  🔧 工具 {i+1}: {tool_call.get('name', 'Unknown')}")
                        if 'args' in tool_call:
                            print(f"    📝 参数: {tool_call['args']}")
                else:
                    print("⚠️  未检测到工具调用，Agent可能直接返回文本回复")
                    
            return True
        else:
            print(f"❌ 工具测试失败: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 工具测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 开始行业分析Agent独立测试")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 基础功能测试
    basic_test_passed = test_industry_analyst_isolated()
    
    # 不同行业测试
    sector_test_passed = test_industry_analyst_different_sectors()
    
    # 工具调用测试
    tools_test_passed = test_industry_analyst_tools()
    
    # 总结
    print(f"\n{'='*60}")
    print("🎯 行业分析Agent测试总结")
    print(f"{'='*60}")
    print(f"📋 基础功能测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    print(f"🏭 不同行业测试: {'✅ 通过' if sector_test_passed else '❌ 失败'}")
    print(f"🔧 工具调用测试: {'✅ 通过' if tools_test_passed else '❌ 失败'}")
    
    overall_success = basic_test_passed and sector_test_passed and tools_test_passed
    print(f"🎉 总体结果: {'✅ 行业分析Agent工作正常' if overall_success else '❌ 行业分析Agent存在问题'}")
    
    if not overall_success:
        print(f"\n🔧 建议调试步骤:")
        print(f"1. 检查Gemini API配置和网络连接")
        print(f"2. 验证行业数据获取工具的实现")
        print(f"3. 检查申万行业分类数据源")
        print(f"4. 分析同业对比功能的错误")
        print(f"5. 检查Agent返回值结构")
        
    print(f"{'='*60}")