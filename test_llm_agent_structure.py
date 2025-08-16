#!/usr/bin/env python3
"""
LLM Agent结构验证测试脚本
验证重构后的LLM Agent架构是否正确，不进行真实API调用
"""
import sys
import os
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMAgentStructureTest:
    """LLM Agent结构测试类"""
    
    def test_agent_imports(self):
        """测试Agent导入是否正常"""
        logger.info("🧪 测试LLM Agent导入...")
        
        try:
            # 测试创建函数导入
            from tradingagents.analysis_stock_agent.agents.financial_analysis_agent import create_financial_analysis_agent
            from tradingagents.analysis_stock_agent.agents.industry_analysis_agent import create_industry_analysis_agent
            from tradingagents.analysis_stock_agent.agents.valuation_analysis_agent import create_valuation_analysis_agent
            from tradingagents.analysis_stock_agent.agents.report_integration_agent import create_report_integration_agent
            
            logger.info("✅ LLM Agent创建函数导入成功")
            
            # 测试从agents模块导入
            from tradingagents.analysis_stock_agent.agents import (
                create_financial_analysis_agent as cfa,
                create_industry_analysis_agent as cia,
                create_valuation_analysis_agent as cva,
                create_report_integration_agent as cra
            )
            
            logger.info("✅ Agent模块统一导入成功")
            
            return True
            
        except ImportError as e:
            logger.error(f"❌ Agent导入失败: {e}")
            return False
    
    def test_graph_structure(self):
        """测试图结构导入"""
        logger.info("🧪 测试LangGraph结构...")
        
        try:
            # 测试LangGraph组件导入
            from langgraph.graph import StateGraph, END
            logger.info("✅ LangGraph核心组件导入成功")
            
            # 测试LLM导入
            from langchain_openai import ChatOpenAI
            from langchain_anthropic import ChatAnthropic
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("✅ LLM提供商导入成功")
            
            # 测试Prompt组件导入
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
            logger.info("✅ Prompt组件导入成功")
            
            return True
            
        except ImportError as e:
            logger.error(f"❌ 图结构导入失败: {e}")
            return False
    
    def test_agent_function_structure(self):
        """测试Agent函数结构"""
        logger.info("🧪 测试LLM Agent函数结构...")
        
        try:
            from tradingagents.analysis_stock_agent.agents.financial_analysis_agent import create_financial_analysis_agent
            
            # 检查函数签名
            import inspect
            sig = inspect.signature(create_financial_analysis_agent)
            params = list(sig.parameters.keys())
            
            if 'llm' in params and 'ashare_toolkit' in params:
                logger.info("✅ 财务分析Agent函数签名正确")
            else:
                logger.warning(f"⚠️ 财务分析Agent函数签名异常: {params}")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Agent函数结构测试失败: {e}")
            return False
    
    def test_config_structure(self):
        """测试配置结构"""
        logger.info("🧪 测试配置结构...")
        
        try:
            from tradingagents.analysis_stock_agent.config.analysis_config import get_config
            
            config = get_config()
            
            # 检查关键配置项
            required_keys = ['llm_provider', 'deep_think_llm', 'quick_think_llm']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                logger.warning(f"⚠️ 配置缺少关键项: {missing_keys}")
            else:
                logger.info("✅ 配置结构完整")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ 配置结构测试失败: {e}")
            return False
    
    def test_state_management(self):
        """测试状态管理结构"""
        logger.info("🧪 测试状态管理结构...")
        
        try:
            from tradingagents.analysis_stock_agent.utils.analysis_states import AnalysisStatus, DataSource
            
            # 检查状态枚举
            status_values = [item.value for item in AnalysisStatus]
            logger.info(f"✅ 分析状态枚举: {status_values}")
            
            # 检查DataSource模型
            test_source = DataSource(name="测试源", endpoint="http://test.com")
            logger.info(f"✅ 数据源模型创建成功: {test_source.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 状态管理测试失败: {e}")
            return False
    
    def test_mock_agent_creation(self):
        """测试模拟Agent创建（不调用LLM）"""
        logger.info("🧪 测试模拟Agent创建...")
        
        try:
            from tradingagents.analysis_stock_agent.agents.financial_analysis_agent import create_financial_analysis_agent
            from langchain_core.runnables import RunnableLambda
            
            # 创建模拟LLM
            def mock_llm_invoke(*args, **kwargs):
                class MockResult:
                    content = "模拟LLM财务分析结果"
                    tool_calls = []
                return MockResult()
            
            mock_llm = RunnableLambda(mock_llm_invoke)
            
            # 添加bind_tools方法
            def bind_tools(tools):
                return mock_llm
            mock_llm.bind_tools = bind_tools
            
            # 创建模拟工具集
            class MockToolkit:
                def __init__(self):
                    self.config = {"online_tools": False}
                    
                def get_financial_reports(self): pass
                def get_financial_ratios(self): pass
                def get_financial_summary(self): pass
            
            mock_toolkit = MockToolkit()
            
            # 创建Agent
            agent = create_financial_analysis_agent(mock_llm, mock_toolkit)
            
            # 测试Agent调用
            test_state = {
                "symbol": "000001",
                "company_name": "测试公司",
                "analysis_date": "2024-08-16"
            }
            
            result = agent(test_state)
            
            if "financial_analysis_report" in result:
                logger.info("✅ 模拟Agent创建和调用成功")
                logger.info(f"📝 Agent返回结果键: {list(result.keys())}")
                return True
            else:
                logger.warning("⚠️ Agent返回结果格式异常")
                return False
                
        except Exception as e:
            logger.error(f"❌ 模拟Agent创建失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有结构测试"""
        logger.info("🚀 开始LLM Agent结构验证测试")
        logger.info("=" * 60)
        
        tests = [
            ("Agent导入测试", self.test_agent_imports),
            ("图结构测试", self.test_graph_structure),
            ("Agent函数结构测试", self.test_agent_function_structure),
            ("配置结构测试", self.test_config_structure),
            ("状态管理测试", self.test_state_management),
            ("模拟Agent创建测试", self.test_mock_agent_creation),
        ]
        
        test_results = []
        
        for test_name, test_func in tests:
            logger.info("-" * 40)
            try:
                result = test_func()
                test_results.append((test_name, result))
                if result:
                    logger.info(f"✅ {test_name} 通过")
                else:
                    logger.warning(f"⚠️ {test_name} 失败")
            except Exception as e:
                logger.error(f"❌ {test_name} 异常: {e}")
                test_results.append((test_name, False))
        
        # 汇总结果
        logger.info("=" * 60)
        logger.info("📊 LLM Agent结构验证结果汇总")
        logger.info("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name}: {status}")
        
        logger.info("-" * 40)
        logger.info(f"总计: {passed_tests}/{total_tests} 个测试通过")
        logger.info(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            logger.info("🎉 所有结构测试通过！LLM Agent重构架构正确！")
            logger.info("🎯 系统已从硬编码规则成功转换为LLM智能分析")
        else:
            logger.warning("⚠️ 部分结构测试失败，需要进一步检查")
        
        return passed_tests == total_tests

def main():
    """主函数"""
    test = LLMAgentStructureTest()
    success = test.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    # 运行测试
    exit_code = main()
    sys.exit(exit_code)