#!/usr/bin/env python3
"""
LLM Agent重构验证测试脚本
测试重构后的基于LLM的智能分析Agent系统
"""
import asyncio
import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.analysis_stock_agent.graph.analysis_graph import AShareAnalysisSystem
from tradingagents.analysis_stock_agent.config.analysis_config import get_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMAgentSystemTest:
    """LLM Agent系统测试类"""
    
    def __init__(self):
        self.config = get_config()
        self.analysis_system = None
        
        # 测试用的股票代码
        self.test_symbols = [
            ("000001", "平安银行"),
            ("000002", "万科A"),
            ("600036", "招商银行")
        ]
    
    async def setup(self):
        """初始化测试环境"""
        logger.info("🔧 初始化LLM Agent测试环境...")
        
        try:
            # 初始化分析系统
            self.analysis_system = AShareAnalysisSystem(self.config, debug=True)
            logger.info("✅ LLM Agent分析系统初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 测试环境初始化失败: {e}")
            raise
    
    async def test_single_agent_execution(self):
        """测试单个Agent执行"""
        logger.info("🧪 测试单个LLM Agent执行...")
        
        test_symbol, test_name = self.test_symbols[0]
        
        try:
            # 测试财务分析Agent
            logger.info(f"测试财务分析Agent: {test_name} ({test_symbol})")
            
            # 创建测试状态
            test_state = {
                "symbol": test_symbol,
                "company_name": test_name,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 执行财务分析Agent
            financial_result = self.analysis_system.financial_agent(test_state)
            
            if financial_result.get("financial_analysis_report"):
                logger.info("✅ 财务分析Agent执行成功")
                logger.info(f"📊 财务分析报告预览: {financial_result['financial_analysis_report'][:200]}...")
            else:
                logger.warning("⚠️ 财务分析Agent未返回报告")
            
            # 测试行业分析Agent
            logger.info(f"测试行业分析Agent: {test_name} ({test_symbol})")
            industry_result = self.analysis_system.industry_agent(test_state)
            
            if industry_result.get("industry_analysis_report"):
                logger.info("✅ 行业分析Agent执行成功")
                logger.info(f"📈 行业分析报告预览: {industry_result['industry_analysis_report'][:200]}...")
            else:
                logger.warning("⚠️ 行业分析Agent未返回报告")
            
        except Exception as e:
            logger.error(f"❌ 单个Agent测试失败: {e}")
            return False
        
        return True
    
    async def test_complete_analysis_workflow(self):
        """测试完整的分析工作流"""
        logger.info("🧪 测试完整LLM Agent分析工作流...")
        
        test_symbol, test_name = self.test_symbols[1]
        
        try:
            # 执行完整分析
            logger.info(f"执行完整分析: {test_name} ({test_symbol})")
            result = await self.analysis_system.analyze_stock(test_symbol, test_name)
            
            if result.get("success"):
                logger.info("✅ 完整分析工作流执行成功")
                
                # 检查各部分报告
                reports = {
                    "财务分析": result.get("financial_report", ""),
                    "行业分析": result.get("industry_report", ""),
                    "估值分析": result.get("valuation_report", ""),
                    "综合报告": result.get("comprehensive_report", "")
                }
                
                for report_name, report_content in reports.items():
                    if report_content:
                        logger.info(f"✅ {report_name}报告生成成功")
                        logger.info(f"📝 {report_name}预览: {report_content[:150]}...")
                    else:
                        logger.warning(f"⚠️ {report_name}报告为空")
                
                return True
            else:
                logger.error(f"❌ 完整分析失败: {result.get('error', '未知错误')}")
                return False
            
        except Exception as e:
            logger.error(f"❌ 完整工作流测试失败: {e}")
            return False
    
    async def test_llm_integration_quality(self):
        """测试LLM集成质量"""
        logger.info("🧪 测试LLM集成和报告质量...")
        
        test_symbol, test_name = self.test_symbols[2]
        
        try:
            # 执行分析
            result = await self.analysis_system.analyze_stock(test_symbol, test_name)
            
            if not result.get("success"):
                logger.error("分析执行失败，无法测试质量")
                return False
            
            # 评估报告质量
            quality_checks = {
                "财务分析专业性": self._check_financial_analysis_quality(result.get("financial_report", "")),
                "行业分析深度": self._check_industry_analysis_quality(result.get("industry_report", "")),
                "估值分析逻辑": self._check_valuation_analysis_quality(result.get("valuation_report", "")),
                "综合报告完整性": self._check_comprehensive_report_quality(result.get("comprehensive_report", ""))
            }
            
            passed_checks = 0
            for check_name, passed in quality_checks.items():
                if passed:
                    logger.info(f"✅ {check_name}: 通过")
                    passed_checks += 1
                else:
                    logger.warning(f"⚠️ {check_name}: 需要改进")
            
            logger.info(f"📊 质量检查通过率: {passed_checks}/{len(quality_checks)} ({passed_checks/len(quality_checks)*100:.1f}%)")
            
            return passed_checks >= len(quality_checks) * 0.75  # 75%通过率
            
        except Exception as e:
            logger.error(f"❌ LLM集成质量测试失败: {e}")
            return False
    
    def _check_financial_analysis_quality(self, report: str) -> bool:
        """检查财务分析质量"""
        if len(report) < 100:
            return False
        
        key_indicators = ["ROE", "净利率", "财务", "盈利", "现金流", "分析"]
        return sum(1 for indicator in key_indicators if indicator in report) >= 3
    
    def _check_industry_analysis_quality(self, report: str) -> bool:
        """检查行业分析质量"""
        if len(report) < 100:
            return False
        
        key_indicators = ["行业", "竞争", "申万", "对手", "地位", "市场"]
        return sum(1 for indicator in key_indicators if indicator in report) >= 3
    
    def _check_valuation_analysis_quality(self, report: str) -> bool:
        """检查估值分析质量"""
        if len(report) < 100:
            return False
        
        key_indicators = ["估值", "PE", "PB", "价格", "投资", "时机"]
        return sum(1 for indicator in key_indicators if indicator in report) >= 3
    
    def _check_comprehensive_report_quality(self, report: str) -> bool:
        """检查综合报告质量"""
        if len(report) < 200:
            return False
        
        key_sections = ["投资", "建议", "风险", "优势", "评估", "结论"]
        return sum(1 for section in key_sections if section in report) >= 4
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")
        
        try:
            if self.analysis_system:
                await self.analysis_system.close()
            
            logger.info("✅ 测试环境清理完成")
            
        except Exception as e:
            logger.error(f"❌ 清理测试环境失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始LLM Agent系统重构验证测试")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        test_results = []
        
        try:
            await self.setup()
            
            # 执行所有测试
            tests = [
                ("单个Agent执行", self.test_single_agent_execution),
                ("完整分析工作流", self.test_complete_analysis_workflow),
                ("LLM集成质量", self.test_llm_integration_quality),
            ]
            
            for test_name, test_func in tests:
                logger.info("-" * 40)
                try:
                    result = await test_func()
                    test_results.append((test_name, result))
                    if result:
                        logger.info(f"✅ {test_name} 测试通过")
                    else:
                        logger.warning(f"⚠️ {test_name} 测试失败")
                except Exception as e:
                    logger.error(f"❌ {test_name} 测试异常: {e}")
                    test_results.append((test_name, False))
        
        finally:
            await self.cleanup()
        
        # 汇总测试结果
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("📊 LLM Agent重构验证结果汇总")
        logger.info("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name}: {status}")
        
        logger.info("-" * 40)
        logger.info(f"总计: {passed_tests}/{total_tests} 个测试通过")
        logger.info(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"测试耗时: {duration:.2f} 秒")
        
        if passed_tests == total_tests:
            logger.info("🎉 所有测试通过！LLM Agent重构成功！")
            logger.info("🎯 现在系统使用真正的LLM智能分析，而不是硬编码规则")
        else:
            logger.warning("⚠️ 部分测试失败，需要进一步优化LLM Agent")
        
        return passed_tests == total_tests

async def main():
    """主函数"""
    test = LLMAgentSystemTest()
    success = await test.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    # 运行测试
    exit_code = asyncio.run(main())
    sys.exit(exit_code)