"""
信息整合Agent独立测试

测试information_integrator.py的独立功能，绕过LangGraph
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.analysis_stock_agent.utils.agent_test_framework import create_test_framework
from tradingagents.analysis_stock_agent.agents.information_integrator import create_information_integrator
from tradingagents.analysis_stock_agent.config.a_share_config import A_SHARE_DEFAULT_CONFIG


def test_information_integrator_isolated():
    """独立测试信息整合Agent"""
    print("🧪 信息整合Agent独立测试")
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
        
        # 创建信息整合Agent
        integrator_node = create_information_integrator(
            llm=deep_think_llm,
            toolkit=[],  # 空工具集测试
            config=A_SHARE_DEFAULT_CONFIG
        )
        print("✅ 信息整合Agent创建成功")
        
        # 创建包含前置分析结果的测试状态
        test_state = framework.create_mock_state(
            stock_code="002594",
            stock_name="比亚迪"
        )
        
        # 模拟前置分析结果
        test_state.update({
            "financial_analysis_report": "比亚迪（002594）财务分析报告：财务健康度评分85分，ROE为18.5%，净利率12.3%，公司盈利能力强劲，现金流稳定。",
            "industry_analysis_report": "比亚迪（002594）行业分析报告：在新能源汽车行业中处于领先地位，市场份额20%，技术优势明显，行业竞争力评分90分。",
            "valuation_analysis_report": "比亚迪（002594）估值分析报告：基于DCF模型估值合理，PE比率15倍，相比行业均值具有估值优势，目标价位120元。",
            "financial_data": {
                "latest_report": {
                    "roe": 18.5,
                    "net_profit_margin": 12.3,
                    "total_revenue": 150000000000
                }
            },
            "industry_data": {
                "industry_ranking": {"market_share": 20, "rank": 1},
                "competitive_position": "领先"
            },
            "key_financial_metrics": {"roe": 18.5, "roa": 8.2},
            "key_industry_metrics": {"market_share": 20, "industry_score": 90}
        })
        
        print(f"\n📊 测试数据:")
        print(f"  股票代码: {test_state['stock_code']}")
        print(f"  股票名称: {test_state['stock_name']}")
        print(f"  财务分析: {'✅ 已提供' if test_state.get('financial_analysis_report') else '❌ 缺失'}")
        print(f"  行业分析: {'✅ 已提供' if test_state.get('industry_analysis_report') else '❌ 缺失'}")
        print(f"  估值分析: {'✅ 已提供' if test_state.get('valuation_analysis_report') else '❌ 缺失'}")
        
        # 运行Agent测试
        result = framework.run_agent_test(
            agent_name="信息整合Agent",
            agent_function=integrator_node,
            mock_state=test_state
        )
        
        # 详细分析结果
        if result["success"]:
            agent_result = result["result"]
            
            print(f"\n🔍 详细结果分析:")
            
            # 检查必要字段
            required_fields = [
                "messages", 
                "comprehensive_analysis_report",
                "comprehensive_score",
                "investment_recommendation",
                "integration_data",
                "final_conclusion",
                "data_sources",
                "analysis_completed",
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
                    
            # 检查综合分析报告
            if "comprehensive_analysis_report" in agent_result:
                report = agent_result["comprehensive_analysis_report"]
                print(f"  📄 综合分析报告长度: {len(str(report))} 字符")
                if len(str(report)) > 100:
                    print(f"  📄 报告预览: {str(report)[:150]}...")
                    
            # 检查综合评分
            if "comprehensive_score" in agent_result:
                score = agent_result["comprehensive_score"]
                print(f"  📊 综合评分: {score}")
                print(f"  📊 评分类型: {type(score)}")
                if isinstance(score, (int, float)):
                    print(f"  📊 评分合理性: {'✅ 合理' if 0 <= score <= 100 else '❌ 超出范围'}")
                    
            # 检查投资建议
            if "investment_recommendation" in agent_result:
                recommendation = agent_result["investment_recommendation"]
                print(f"  💡 投资建议: {recommendation}")
                
                valid_recommendations = ["强烈买入", "买入", "增持", "持有", "减持", "卖出", "观望"]
                is_valid = any(rec in str(recommendation) for rec in valid_recommendations)
                print(f"  💡 建议有效性: {'✅ 有效' if is_valid else '❌ 无效'}")
                
            # 检查最终结论
            if "final_conclusion" in agent_result:
                conclusion = agent_result["final_conclusion"]
                print(f"  🎯 最终结论长度: {len(str(conclusion))} 字符")
                if len(str(conclusion)) > 50:
                    print(f"  🎯 结论预览: {str(conclusion)[:100]}...")
                    
            # 检查数据源
            if "data_sources" in agent_result:
                sources = agent_result["data_sources"]
                print(f"  📚 数据源数量: {len(sources) if sources else 0}")
                if sources:
                    print(f"  📚 数据源列表: {sources}")
                    
            # 检查分析完成状态
            if "analysis_completed" in agent_result:
                completed = agent_result["analysis_completed"]
                print(f"  ✅ 分析完成状态: {completed}")
                    
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


def test_integrator_with_missing_data():
    """测试缺失前置分析数据的情况"""
    print("\n🔍 测试缺失前置分析数据情况")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过缺失数据测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建信息整合Agent
        integrator_node = create_information_integrator(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        print("✅ 信息整合Agent创建成功")
        
        # 测试不同的缺失数据情况
        test_scenarios = [
            {
                "name": "完全空白状态",
                "state": framework.create_mock_state("002594", "比亚迪")
            },
            {
                "name": "仅有财务分析",
                "state": {
                    **framework.create_mock_state("002594", "比亚迪"),
                    "financial_analysis_report": "简单财务分析报告"
                }
            },
            {
                "name": "缺失估值分析",
                "state": {
                    **framework.create_mock_state("002594", "比亚迪"),
                    "financial_analysis_report": "财务分析报告",
                    "industry_analysis_report": "行业分析报告"
                }
            },
            {
                "name": "空股票代码",
                "state": {
                    **framework.create_mock_state("", ""),
                    "financial_analysis_report": "财务分析报告"
                }
            }
        ]
        
        test_results = []
        
        for scenario in test_scenarios:
            print(f"\n📋 测试场景: {scenario['name']}")
            
            result = framework.run_agent_test(
                agent_name=f"信息整合Agent - {scenario['name']}",
                agent_function=integrator_node,
                mock_state=scenario["state"]
            )
            
            test_results.append(result)
            
            # 分析特定场景的结果
            if result["success"]:
                agent_result = result["result"]
                
                # 检查错误处理
                if "comprehensive_analysis_report" in agent_result:
                    report = str(agent_result["comprehensive_analysis_report"])
                    
                    error_indicators = ["错误", "失败", "缺少", "无法", "error"]
                    has_error_handling = any(indicator in report for indicator in error_indicators)
                    
                    print(f"  🔍 错误处理: {'✅ 检测到' if has_error_handling else '⚠️  未检测到'}")
                    
        # 打印测试总结
        framework.print_test_summary(test_results)
        
        # 分析成功率
        success_count = sum(1 for r in test_results if r["success"])
        success_rate = success_count / len(test_results) * 100
        
        print(f"\n📊 缺失数据处理成功率: {success_rate:.1f}% ({success_count}/{len(test_results)})")
        
        return success_rate >= 50  # 至少50%成功率认为基本可用
        
    except Exception as e:
        print(f"\n❌ 缺失数据测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integrator_comprehensive():
    """综合测试信息整合Agent的完整功能"""
    print("\n🎯 综合测试信息整合Agent功能")
    print("=" * 60)
    
    framework = create_test_framework(debug=True)
    
    if not framework.llm_manager:
        print("❌ 无法初始化LLM管理器，跳过综合测试")
        return False
        
    try:
        # 获取LLM实例
        deep_think_llm = framework.get_test_llm("gemini-2.5-pro")
        
        # 创建信息整合Agent
        integrator_node = create_information_integrator(
            llm=deep_think_llm,
            toolkit=[],
            config=A_SHARE_DEFAULT_CONFIG
        )
        
        # 创建完整的测试状态
        comprehensive_state = framework.create_mock_state("002594", "比亚迪")
        comprehensive_state.update({
            # 完整的前置分析结果
            "financial_analysis_report": """
            比亚迪（002594）财务指标分析报告：
            - 财务健康度评分：88/100分（优秀）
            - ROE：18.5%，ROA：8.2%，净利率：12.3%
            - 盈利能力强劲，现金流稳定，负债率适中
            - 成长性良好，收入同比增长25%
            """,
            "industry_analysis_report": """
            比亚迪（002594）行业对比与竞争优势分析报告：
            - 行业竞争力评分：92/100分（极强）
            - 新能源汽车行业领导者，市场份额20%
            - 技术优势明显，电池技术行业领先
            - 竞争护城河深厚，品牌影响力强
            """,
            "valuation_analysis_report": """
            比亚迪（002594）估值分析与市场信号解读报告：
            - 估值综合评分：78/100分（较为合理）
            - DCF估值：目标价位120元，安全边际15%
            - PE比率：15倍，相比行业均值具有估值优势
            - 技术分析：多头排列，MACD金叉
            """,
            "financial_data": {
                "latest_report": {
                    "roe": 18.5,
                    "roa": 8.2,
                    "net_profit_margin": 12.3,
                    "total_revenue": 150000000000,
                    "net_profit": 18450000000
                }
            },
            "industry_data": {
                "market_share": 20,
                "industry_rank": 1,
                "competitive_advantages": ["技术领先", "品牌优势", "成本控制"]
            },
            "key_financial_metrics": {
                "roe": 18.5,
                "roa": 8.2,
                "net_profit_margin": 12.3,
                "debt_ratio": 45.2
            },
            "key_industry_metrics": {
                "market_share": 20,
                "industry_score": 92,
                "competitive_rank": 1
            }
        })
        
        print("🔧 运行综合整合测试...")
        
        result = framework.run_agent_test(
            agent_name="信息整合Agent - 综合测试",
            agent_function=integrator_node,
            mock_state=comprehensive_state
        )
        
        if result["success"]:
            agent_result = result["result"]
            
            # 深度分析整合质量
            print(f"\n🔍 整合质量分析:")
            
            # 分析综合报告的完整性
            if "comprehensive_analysis_report" in agent_result:
                report = str(agent_result["comprehensive_analysis_report"])
                
                # 检查报告结构
                report_sections = ["摘要", "分析", "结论", "建议", "评分", "风险"]
                found_sections = [sec for sec in report_sections if sec in report]
                print(f"  📄 报告结构完整性: {len(found_sections)}/{len(report_sections)}")
                
                # 检查数据整合
                data_integration = ["财务", "行业", "估值", "比亚迪", "002594"]
                found_data = [data for data in data_integration if data in report]
                print(f"  📊 数据整合度: {len(found_data)}/{len(data_integration)}")
                
                # 检查报告长度和质量
                print(f"  📏 报告长度: {len(report)} 字符")
                print(f"  📏 报告质量: {'✅ 详细' if len(report) > 500 else '⚠️  简略' if len(report) > 100 else '❌ 过简'}")
                
            # 检查评分合理性
            if "comprehensive_score" in agent_result:
                score = agent_result["comprehensive_score"]
                print(f"  📊 综合评分: {score}")
                
                # 基于输入数据验证评分合理性
                expected_score_range = (75, 95)  # 基于良好的财务和行业数据
                is_reasonable = expected_score_range[0] <= score <= expected_score_range[1]
                print(f"  📊 评分合理性: {'✅ 合理' if is_reasonable else '⚠️  可能偏离'}")
                
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
    print("🚀 开始信息整合Agent独立测试")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 基础功能测试
    basic_test_passed = test_information_integrator_isolated()
    
    # 缺失数据处理测试
    missing_data_test_passed = test_integrator_with_missing_data()
    
    # 综合功能测试
    comprehensive_test_passed = test_integrator_comprehensive()
    
    # 总结
    print(f"\n{'='*60}")
    print("🎯 信息整合Agent测试总结")
    print(f"{'='*60}")
    print(f"📋 基础功能测试: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    print(f"🔍 缺失数据处理: {'✅ 通过' if missing_data_test_passed else '❌ 失败'}")
    print(f"🎯 综合功能测试: {'✅ 通过' if comprehensive_test_passed else '❌ 失败'}")
    
    overall_success = basic_test_passed and missing_data_test_passed and comprehensive_test_passed
    print(f"🎉 总体结果: {'✅ 信息整合Agent工作正常' if overall_success else '❌ 信息整合Agent存在问题'}")
    
    if not overall_success:
        print(f"\n🔧 建议调试步骤:")
        print(f"1. 检查Gemini API配置和网络连接")
        print(f"2. 验证整合逻辑的正确性")
        print(f"3. 检查评分计算算法")
        print(f"4. 验证投资建议生成逻辑")
        print(f"5. 检查Agent返回值结构完整性")
        
    print(f"{'='*60}")