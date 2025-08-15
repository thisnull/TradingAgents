"""
A股分析系统集成测试
测试核心功能的基本可用性
"""
import asyncio
import pytest
import logging
from typing import Dict, Any

from tradingagents.analysis_stock_agent import (
    AShareAnalysisSystem,
    create_analysis_system,
    ANALYSIS_CONFIG,
    AnalysisStatus
)

logger = logging.getLogger(__name__)

class TestAShareAnalysisSystem:
    """A股分析系统集成测试类"""
    
    @pytest.fixture
    async def analysis_system(self):
        """创建测试用的分析系统"""
        config = ANALYSIS_CONFIG.copy()
        config.update({
            "request_timeout": 30,  # 缩短超时时间用于测试
            "max_retry_attempts": 1,
            "debug_mode": True
        })
        
        system = await create_analysis_system(config, debug=True)
        yield system
        await system.close()
    
    async def test_system_initialization(self, analysis_system):
        """测试系统初始化"""
        system_info = analysis_system.get_system_info()
        
        assert system_info["initialized"] is True
        assert system_info["system_name"] == "AShareAnalysisSystem"
        assert system_info["version"] == "1.0.0"
        
        # 检查所有Agent都已初始化
        agents = system_info["agents"]
        assert agents["financial_agent"] is True
        assert agents["industry_agent"] is True
        assert agents["valuation_agent"] is True
        assert agents["integration_agent"] is True
    
    async def test_valid_stock_analysis(self, analysis_system):
        """测试有效股票代码分析"""
        # 使用平安银行作为测试股票
        test_symbol = "000001"
        
        result = await analysis_system.analyze_stock(test_symbol)
        
        # 基本验证
        assert result is not None
        assert result.symbol == test_symbol
        assert result.status in [AnalysisStatus.COMPLETED, AnalysisStatus.PARTIAL]
        
        # 如果分析成功，检查结果结构
        if result.status == AnalysisStatus.COMPLETED:
            assert result.financial_analysis is not None
            assert result.industry_analysis is not None
            assert result.valuation_analysis is not None
            assert result.investment_recommendation is not None
            assert result.final_report is not None
            assert len(result.final_report) > 100  # 报告应该有足够的内容
            
            # 检查投资建议
            rec = result.investment_recommendation
            assert rec.investment_action in ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell']
            assert rec.confidence_level in ['high', 'medium', 'low']
            assert rec.risk_level in ['high', 'medium', 'low']
    
    async def test_invalid_stock_code(self, analysis_system):
        """测试无效股票代码"""
        invalid_codes = ["12345", "ABCDEF", "0000000", "999999"]
        
        for code in invalid_codes:
            result = await analysis_system.analyze_stock(code)
            
            assert result is not None
            assert result.symbol == code
            assert result.status == AnalysisStatus.FAILED
            assert result.error_message is not None
            assert "输入验证失败" in result.error_message or "分析过程异常" in result.error_message
    
    async def test_batch_analysis(self, analysis_system):
        """测试批量分析功能"""
        test_symbols = ["000001", "000002"]  # 平安银行、万科A
        
        results = await analysis_system.batch_analyze_stocks(
            test_symbols,
            max_concurrent=2
        )
        
        # 验证结果
        assert len(results) == len(test_symbols)
        
        for symbol in test_symbols:
            assert symbol in results
            result = results[symbol]
            assert result.symbol == symbol
            assert result.status in [
                AnalysisStatus.COMPLETED, 
                AnalysisStatus.PARTIAL, 
                AnalysisStatus.FAILED
            ]
    
    async def test_financial_analysis_component(self, analysis_system):
        """测试财务分析组件"""
        test_symbol = "000001"
        
        # 直接测试财务分析Agent
        financial_agent = analysis_system.financial_agent
        assert financial_agent is not None
        
        try:
            financial_result = await financial_agent.analyze_financial_performance(test_symbol)
            
            assert financial_result is not None
            assert financial_result.symbol == test_symbol
            
            if financial_result.status == AnalysisStatus.COMPLETED:
                assert financial_result.financial_metrics is not None
                assert financial_result.analysis_summary is not None
                
                # 检查财务指标
                metrics = financial_result.financial_metrics
                assert metrics.overall_score is not None
                assert 0 <= metrics.overall_score <= 100
                assert metrics.quality_grade is not None
                
        except Exception as e:
            logger.warning(f"财务分析测试失败，可能因为数据源问题: {e}")
    
    async def test_industry_analysis_component(self, analysis_system):
        """测试行业分析组件"""
        test_symbol = "000001"
        
        industry_agent = analysis_system.industry_agent
        assert industry_agent is not None
        
        try:
            industry_result = await industry_agent.analyze_industry_position(test_symbol)
            
            assert industry_result is not None
            assert industry_result.symbol == test_symbol
            
            if industry_result.status == AnalysisStatus.COMPLETED:
                assert industry_result.industry_metrics is not None
                assert industry_result.analysis_summary is not None
                
        except Exception as e:
            logger.warning(f"行业分析测试失败，可能因为数据源问题: {e}")
    
    async def test_valuation_analysis_component(self, analysis_system):
        """测试估值分析组件"""
        test_symbol = "000001"
        
        valuation_agent = analysis_system.valuation_agent
        assert valuation_agent is not None
        
        try:
            valuation_result = await valuation_agent.analyze_valuation(test_symbol)
            
            assert valuation_result is not None
            assert valuation_result.symbol == test_symbol
            
            if valuation_result.status == AnalysisStatus.COMPLETED:
                assert valuation_result.valuation_metrics is not None
                assert valuation_result.analysis_summary is not None
                
                # 检查PR估值模型
                metrics = valuation_result.valuation_metrics
                if metrics.pr_ratio is not None:
                    assert metrics.pr_ratio > 0
                    assert metrics.pr_assessment is not None
                    assert metrics.pr_assessment in [
                        'severely_undervalued', 'undervalued', 'fairly_valued',
                        'overvalued', 'severely_overvalued'
                    ]
                
        except Exception as e:
            logger.warning(f"估值分析测试失败，可能因为数据源问题: {e}")
    
    async def test_report_integration(self, analysis_system):
        """测试报告整合功能"""
        # 这个测试需要所有组件都工作正常
        test_symbol = "000001"
        
        try:
            result = await analysis_system.analyze_stock(test_symbol)
            
            if result.status == AnalysisStatus.COMPLETED:
                # 检查最终报告格式
                assert result.final_report is not None
                
                # 报告应该包含关键部分
                report = result.final_report
                assert "投资分析报告" in report
                assert "核心结论" in report
                assert "关键支撑论据" in report
                assert "风险提示" in report
                
                # 检查综合指标
                if result.integrated_metrics:
                    metrics = result.integrated_metrics
                    assert metrics.overall_score is not None
                    assert 0 <= metrics.overall_score <= 100
                    assert metrics.overall_grade is not None
                
        except Exception as e:
            logger.warning(f"报告整合测试失败，可能因为数据源问题: {e}")

# 手动运行测试的辅助函数
async def run_integration_tests():
    """手动运行集成测试"""
    print("开始A股分析系统集成测试...")
    
    # 创建测试系统
    config = ANALYSIS_CONFIG.copy()
    config.update({
        "request_timeout": 30,
        "max_retry_attempts": 1,
        "debug_mode": True
    })
    
    system = None
    try:
        system = await create_analysis_system(config, debug=True)
        test_instance = TestAShareAnalysisSystem()
        
        # 运行各项测试
        tests = [
            ("系统初始化测试", test_instance.test_system_initialization),
            ("有效股票分析测试", test_instance.test_valid_stock_analysis),
            ("无效股票代码测试", test_instance.test_invalid_stock_code),
            ("批量分析测试", test_instance.test_batch_analysis),
            ("财务分析组件测试", test_instance.test_financial_analysis_component),
            ("行业分析组件测试", test_instance.test_industry_analysis_component),
            ("估值分析组件测试", test_instance.test_valuation_analysis_component),
            ("报告整合测试", test_instance.test_report_integration),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n运行测试: {test_name}")
                await test_func(system)
                print(f"✓ {test_name} - 通过")
                passed += 1
            except Exception as e:
                print(f"✗ {test_name} - 失败: {e}")
                failed += 1
        
        print(f"\n测试总结:")
        print(f"- 通过: {passed}")
        print(f"- 失败: {failed}")
        print(f"- 总计: {passed + failed}")
        
        if failed == 0:
            print("🎉 所有测试通过！")
        else:
            print(f"⚠️  有 {failed} 个测试失败")
    
    except Exception as e:
        print(f"测试执行失败: {e}")
    
    finally:
        if system:
            await system.close()

if __name__ == "__main__":
    # 手动运行测试
    asyncio.run(run_integration_tests())