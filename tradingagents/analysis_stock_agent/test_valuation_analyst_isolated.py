"""
估值分析Agent独立测试

测试valuation_analyst.py的独立功能，绕过LangGraph
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.analysis_stock_agent.utils.agent_test_framework import create_test_framework
from tradingagents.analysis_stock_agent.agents.valuation_analyst import create_valuation_analyst
from tradingagents.analysis_stock_agent.config.a_share_config import A_SHARE_DEFAULT_CONFIG


def test_valuation_analyst_isolated():
    """独立测试估值分析Agent"""
    print("🧪 估值分析Agent独立测试")
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
        
        # 创建估值分析Agent
        valuation_analyst_node = create_valuation_analyst(
            llm=deep_think_llm,
            toolkit=[],  # 空工具集测试
            config=A_SHARE_DEFAULT_CONFIG
        )
        print("✅ 估值分析Agent创建成功")
        
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
            agent_name="估值分析Agent",
            agent_function=valuation_analyst_node,
            mock_state=test_state
        )
        
        # 详细分析结果
        if result["success"]:
            agent_result = result["result"]
            
            print(f"\n🔍 详细结果分析:")
            
            # 检查必要字段
            required_fields = [
                "messages", 
                "valuation_analysis_report",
                "valuation_metrics",
                "key_valuation_metrics",
                "market_signals",
                "technical_indicators",
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
                    
            # 检查估值分析报告
            if "valuation_analysis_report" in agent_result:
                report = agent_result["valuation_analysis_report"]
                print(f"  📄 估值分析报告长度: {len(str(report))} 字符")
                if len(str(report)) > 50:
                    print(f"  📄 报告预览: {str(report)[:100]}...")
                    
            # 检查估值指标
            if "valuation_metrics" in agent_result:
                metrics = agent_result["valuation_metrics"]
                print(f"  💰 估值指标类型: {type(metrics)}")
                if isinstance(metrics, dict):
                    print(f"  💰 估值指标字段: {list(metrics.keys())}")
                    
            # 检查市场信号
            if "market_signals" in agent_result:
                signals = agent_result["market_signals"]
                print(f"  📊 市场信号类型: {type(signals)}")
                if isinstance(signals, dict):
                    print(f"  📊 市场信号字段: {list(signals.keys())}")
                    
            # 检查技术指标
            if "technical_indicators" in agent_result:
                indicators = agent_result["technical_indicators"]
                print(f"  📈 技术指标类型: {type(indicators)}")
                if isinstance(indicators, dict):
                    print(f"  📈 技术指标字段: {list(indicators.keys())}")
                    
            # 检查数据源
            if "data_sources" in agent_result:
                sources = agent_result["data_sources"]
                print(f"  📚 数据源数量: {len(sources) if sources else 0}")
                if sources:
                    print(f"  📚 数据源列表: {sources}")
                    
            # 保存分析报告（如果是有效股票代码且有实质内容）
            if (test_state['stock_code'] and test_state['stock_code'] != "INVALID" and 
                "valuation_analysis_report" in agent_result):
                
                try:
                    report_path = framework.save_analysis_report(
                        agent_name="估值分析Agent",
                        stock_code=test_state['stock_code'],
                        agent_result=agent_result
                    )
                    if report_path:
                        print(f"  📄 详细分析报告已保存: {report_path}")
                except Exception as e:
                    print(f"  ⚠️  保存报告失败: {str(e)}")
                    
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


def test_valuation_analyst_different_scenarios():
    """测试不同估值场景的股票分析"""
    print("\n💰 测试不同估值场景股票分析")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过估值场景测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建估值分析Agent
        valuation_analyst_node = create_valuation_analyst(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        print("✅ 估值分析Agent创建成功")
        
        # 测试不同类型的股票
        test_stocks = [
            {
                "scenario": "高成长科技股",
                "stock_code": "002594",
                "stock_name": "比亚迪"
            },
            {
                "scenario": "传统金融股",
                "stock_code": "000001", 
                "stock_name": "平安银行"
            },
            {
                "scenario": "地产龙头股",
                "stock_code": "000002",
                "stock_name": "万科A"
            },
            {
                "scenario": "空代码测试",
                "stock_code": "",
                "stock_name": "测试公司"
            }
        ]
        
        test_results = []
        
        for stock in test_stocks:
            print(f"\n📋 测试场景: {stock['scenario']}")
            
            test_state = framework.create_mock_state(
                stock_code=stock["stock_code"],
                stock_name=stock["stock_name"]
            )
            
            result = framework.run_agent_test(
                agent_name=f"估值分析Agent - {stock['scenario']}",
                agent_function=valuation_analyst_node,
                mock_state=test_state
            )
            
            test_results.append(result)
            
            # 保存分析报告（如果测试成功且有分析报告）
            if (result["success"] and stock["stock_code"] and 
                stock["stock_code"] not in ["", "INVALID"]):
                agent_result = result["result"]
                if "valuation_analysis_report" in agent_result:
                    try:
                        report_path = framework.save_analysis_report(
                            agent_name=f"估值分析Agent-{stock['scenario']}",
                            stock_code=stock["stock_code"],
                            agent_result=agent_result
                        )
                        if report_path:
                            print(f"  📄 {stock['scenario']}分析报告已保存: {report_path}")
                    except Exception as e:
                        print(f"  ⚠️  保存{stock['scenario']}报告失败: {str(e)}")
            
            # 检查特定的估值分析结果
            if result["success"]:
                agent_result = result["result"]
                
                # 分析估值特定信息
                if "valuation_analysis_report" in agent_result:
                    report = str(agent_result["valuation_analysis_report"])
                    
                    valuation_keywords = ["估值", "DCF", "PE", "PB", "目标价", "折现"]
                    found_keywords = [kw for kw in valuation_keywords if kw in report]
                    
                    print(f"  🔍 估值关键词覆盖: {len(found_keywords)}/{len(valuation_keywords)}")
                    print(f"  🔍 包含关键词: {found_keywords}")
                    
        # 打印测试总结
        framework.print_test_summary(test_results)
        
        # 分析成功率
        success_count = sum(1 for r in test_results if r["success"])
        success_rate = success_count / len(test_results) * 100
        
        print(f"\n📊 估值分析Agent成功率: {success_rate:.1f}% ({success_count}/{len(test_results)})")
        
        return success_rate >= 50  # 至少50%成功率认为基本可用
        
    except Exception as e:
        print(f"\n❌ 估值场景测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_valuation_analyst_tools():
    """测试估值分析Agent的工具调用"""
    print("\n🔧 测试估值分析Agent工具调用")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过工具测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建估值分析Agent
        valuation_analyst_node = create_valuation_analyst(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        # 测试状态
        test_state = framework.create_mock_state(
            stock_code="002594",
            stock_name="比亚迪"
        )
        
        print("🔧 运行估值工具调用测试...")
        
        result = framework.run_agent_test(
            agent_name="估值分析Agent - 工具测试",
            agent_function=valuation_analyst_node,
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
                    
            # 检查估值相关数据是否产生
            valuation_data_fields = [
                "valuation_metrics", "key_valuation_metrics", 
                "market_signals", "technical_indicators"
            ]
            
            for field in valuation_data_fields:
                if field in agent_result and agent_result[field]:
                    print(f"  💰 {field}: 数据已生成")
                else:
                    print(f"  ⚠️  {field}: 数据缺失")
                    
            return True
        else:
            print(f"❌ 工具测试失败: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 工具测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_valuation_comprehensive():
    """综合测试估值分析Agent的完整功能"""
    print("\n🎯 综合测试估值分析Agent功能")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过综合测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建估值分析Agent
        valuation_analyst_node = create_valuation_analyst(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        # 创建包含前置财务数据的测试状态
        comprehensive_state = framework.create_mock_state("002594", "比亚迪")
        comprehensive_state.update({
            # 模拟财务数据用于估值计算
            "financial_data": {
                "latest_report": {
                    "net_profit": 18450000000,  # 净利润
                    "total_revenue": 150000000000,  # 营业收入
                    "total_assets": 200000000000,  # 总资产
                    "total_equity": 120000000000,  # 净资产
                    "free_cash_flow": 15000000000,  # 自由现金流
                    "roe": 18.5,
                    "roa": 8.2,
                    "pe_ratio": 15.0,
                    "pb_ratio": 1.8
                },
                "historical_growth": {
                    "revenue_growth_3y": 25.5,  # 3年收入增长率
                    "profit_growth_3y": 30.2,   # 3年净利润增长率
                    "roe_avg_3y": 17.8          # 3年平均ROE
                }
            },
            "market_data": {
                "current_price": 108.50,
                "market_cap": 250000000000,  # 市值
                "volume": 85000000,
                "turnover_rate": 3.2
            }
        })
        
        print("🔧 运行综合估值测试...")
        
        result = framework.run_agent_test(
            agent_name="估值分析Agent - 综合测试",
            agent_function=valuation_analyst_node,
            mock_state=comprehensive_state
        )
        
        if result["success"]:
            agent_result = result["result"]
            
            # 深度分析估值质量
            print(f"\n🔍 估值质量分析:")
            
            # 分析估值报告的完整性
            if "valuation_analysis_report" in agent_result:
                report = str(agent_result["valuation_analysis_report"])
                
                # 检查报告结构
                valuation_sections = ["DCF", "相对估值", "技术分析", "目标价", "风险", "建议"]
                found_sections = [sec for sec in valuation_sections if sec in report]
                print(f"  📄 估值报告结构: {len(found_sections)}/{len(valuation_sections)}")
                
                # 检查估值方法
                valuation_methods = ["DCF", "PE", "PB", "PEG", "EV/EBITDA"]
                found_methods = [method for method in valuation_methods if method in report]
                print(f"  💰 估值方法覆盖: {len(found_methods)}/{len(valuation_methods)}")
                
                # 检查报告长度和质量
                print(f"  📏 报告长度: {len(report)} 字符")
                print(f"  📏 报告质量: {'✅ 详细' if len(report) > 500 else '⚠️  简略' if len(report) > 100 else '❌ 过简'}")
                
            # 检查关键估值指标
            if "key_valuation_metrics" in agent_result:
                metrics = agent_result["key_valuation_metrics"]
                print(f"  💰 关键估值指标: {metrics}")
                
                # 验证是否包含核心估值指标
                core_metrics = ["target_price", "dcf_value", "pe_value", "pb_value"]
                found_metrics = [m for m in core_metrics if m in metrics]
                print(f"  💰 核心指标完整性: {len(found_metrics)}/{len(core_metrics)}")
                
            # 保存综合测试分析报告
            if "valuation_analysis_report" in agent_result:
                try:
                    report_path = framework.save_analysis_report(
                        agent_name="估值分析Agent-综合测试",
                        stock_code="002594",
                        agent_result=agent_result
                    )
                    if report_path:
                        print(f"  📄 综合测试详细报告已保存: {report_path}")
                except Exception as e:
                    print(f"  ⚠️  保存综合测试报告失败: {str(e)}")
                
            return True
        else:
            print(f"❌ 综合测试失败: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 综合测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 开始估值分析Agent独立测试")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 基础功能测试
    basic_test_passed = test_valuation_analyst_isolated()
    
    # 不同估值场景测试
    scenario_test_passed = test_valuation_analyst_different_scenarios()
    
    # 工具调用测试
    tools_test_passed = test_valuation_analyst_tools()
    
    # 综合功能测试
    comprehensive_test_passed = test_valuation_comprehensive()
    
    # 总结
    print(f"\n{'='*60}")
    print("🎯 估值分析Agent测试总结")
    print(f"{'='*60}")
    print(f"📋 基础功能测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    print(f"💰 估值场景测试: {'✅ 通过' if scenario_test_passed else '❌ 失败'}")
    print(f"🔧 工具调用测试: {'✅ 通过' if tools_test_passed else '❌ 失败'}")
    print(f"🎯 综合功能测试: {'✅ 通过' if comprehensive_test_passed else '❌ 失败'}")
    
    overall_success = basic_test_passed and scenario_test_passed and tools_test_passed and comprehensive_test_passed
    print(f"🎉 总体结果: {'✅ 估值分析Agent工作正常' if overall_success else '❌ 估值分析Agent存在问题'}")
    
    if not overall_success:
        print(f"\n🔧 建议调试步骤:")
        print(f"1. 检查Gemini API配置和网络连接")
        print(f"2. 验证估值计算工具的实现")
        print(f"3. 检查技术指标数据获取功能")
        print(f"4. 分析DCF和相对估值模型准确性")
        print(f"5. 检查Agent返回值结构完整性")
        
    print(f"{'='*60}")