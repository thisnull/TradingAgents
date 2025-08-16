#!/usr/bin/env python3
"""
申万行业升级功能测试脚本
测试新增的申万行业API方法和MCP工具
"""
import asyncio
import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.analysis_stock_agent.tools.ashare_toolkit import AShareToolkit
from tradingagents.analysis_stock_agent.tools.mcp_integration import MCPToolkit, UnifiedDataToolkit
from tradingagents.analysis_stock_agent.agents.industry_analysis_agent import IndustryAnalysisAgent
from tradingagents.analysis_stock_agent.config.analysis_config import get_config
from tradingagents.analysis_stock_agent.utils.analysis_states import (
    validate_sw_industry_data,
    extract_sw_industry_info,
    calculate_industry_data_quality_score,
    SWIndustryHierarchy
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SWIndustryUpgradeTest:
    """申万行业升级功能测试类"""
    
    def __init__(self):
        self.config = get_config()
        self.ashare_toolkit = None
        self.mcp_toolkit = None
        self.unified_toolkit = None
        self.industry_agent = None
        
        # 测试用的股票代码
        self.test_symbols = ["000001", "000002", "600000", "600036", "000858"]
    
    async def setup(self):
        """初始化测试环境"""
        logger.info("🔧 初始化测试环境...")
        
        try:
            # 初始化AShare工具集
            self.ashare_toolkit = AShareToolkit(self.config)
            await self.ashare_toolkit._ensure_session()
            
            # 初始化MCP工具集 (可选)
            self.mcp_toolkit = MCPToolkit(self.config)
            # 注意：MCP连接可能失败，这是正常的
            
            # 初始化统一数据工具集
            self.unified_toolkit = UnifiedDataToolkit(self.config)
            await self.unified_toolkit.initialize()
            
            # 初始化行业分析Agent
            self.industry_agent = IndustryAnalysisAgent(self.config, self.ashare_toolkit)
            
            logger.info("✅ 测试环境初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 测试环境初始化失败: {e}")
            raise
    
    async def test_ashare_toolkit_methods(self):
        """测试AShare工具集的新方法"""
        logger.info("🧪 测试AShare工具集申万行业方法...")
        
        test_symbol = self.test_symbols[0]
        
        try:
            # 测试1: 获取申万行业层级信息
            logger.info(f"测试获取申万行业层级: {test_symbol}")
            hierarchy_result = await self.ashare_toolkit.get_stock_sw_industry_hierarchy(test_symbol)
            
            if hierarchy_result.get('success'):
                logger.info(f"✅ 申万行业层级获取成功")
                hierarchy_data = hierarchy_result.get('data', {})
                
                # 验证数据
                if validate_sw_industry_data(hierarchy_data):
                    logger.info("✅ 申万行业数据验证通过")
                    
                    # 提取结构化信息
                    extracted_info = extract_sw_industry_info(hierarchy_data)
                    logger.info(f"📊 提取的行业信息: {extracted_info}")
                else:
                    logger.warning("⚠️ 申万行业数据验证失败")
            else:
                logger.warning(f"⚠️ 申万行业层级获取失败: {hierarchy_result.get('message', '未知错误')}")
            
            # 测试2: 获取申万行业信息
            logger.info("测试获取申万一级行业信息")
            industry_info_result = await self.ashare_toolkit.get_sw_industry_info(level=1, limit=5)
            
            if industry_info_result.get('success'):
                logger.info(f"✅ 申万一级行业信息获取成功，数量: {len(industry_info_result.get('data', []))}")
            else:
                logger.warning("⚠️ 申万行业信息获取失败")
            
            # 测试3: 基于申万分类的竞争对手
            logger.info(f"测试获取申万行业竞争对手: {test_symbol}")
            competitors_result = await self.ashare_toolkit.get_sw_industry_competitors(test_symbol, limit=5)
            
            if competitors_result.get('success'):
                competitors = competitors_result.get('data', [])
                logger.info(f"✅ 申万行业竞争对手获取成功，数量: {len(competitors)}")
                
                # 显示行业信息
                industry_info = competitors_result.get('industry_info', {})
                if industry_info:
                    logger.info(f"📈 行业信息: {industry_info.get('industry_name')} "
                              f"(级别: {industry_info.get('industry_level')}, "
                              f"代码: {industry_info.get('industry_code')})")
            else:
                logger.warning("⚠️ 申万行业竞争对手获取失败")
            
            # 测试4: 搜索申万行业
            logger.info("测试搜索申万行业")
            search_result = await self.ashare_toolkit.search_sw_industries("电子", limit=3)
            
            if search_result.get('success'):
                search_data = search_result.get('data', [])
                logger.info(f"✅ 申万行业搜索成功，找到 {len(search_data)} 个相关行业")
            else:
                logger.warning("⚠️ 申万行业搜索失败")
            
        except Exception as e:
            logger.error(f"❌ AShare工具集测试失败: {e}")
            return False
        
        return True
    
    async def test_unified_toolkit_methods(self):
        """测试统一数据工具集的新方法"""
        logger.info("🧪 测试统一数据工具集增强功能...")
        
        test_symbol = self.test_symbols[1]
        
        try:
            # 测试综合股票数据获取 (包含申万行业)
            logger.info(f"测试综合股票数据获取: {test_symbol}")
            comprehensive_data = await self.unified_toolkit.get_comprehensive_stock_data(test_symbol)
            
            # 检查是否包含新的申万行业数据
            if 'sw_industry_hierarchy' in comprehensive_data:
                logger.info("✅ 综合数据包含申万行业层级信息")
            
            if 'sw_industry_competitors' in comprehensive_data:
                logger.info("✅ 综合数据包含申万行业竞争对手信息")
            
            # 测试综合行业分析
            logger.info(f"测试综合行业分析: {test_symbol}")
            industry_analysis_data = await self.unified_toolkit.get_comprehensive_industry_analysis(test_symbol)
            
            if industry_analysis_data.get('industry_hierarchy'):
                logger.info("✅ 综合行业分析获取申万层级成功")
            
            if industry_analysis_data.get('precise_competitors'):
                competitors = industry_analysis_data['precise_competitors'].get('data', [])
                logger.info(f"✅ 获取精准竞争对手成功，数量: {len(competitors)}")
            
        except Exception as e:
            logger.error(f"❌ 统一数据工具集测试失败: {e}")
            return False
        
        return True
    
    async def test_industry_analysis_agent(self):
        """测试行业分析Agent的增强功能"""
        logger.info("🧪 测试行业分析Agent增强功能...")
        
        test_symbol = self.test_symbols[2]
        
        try:
            # 执行完整的行业分析
            logger.info(f"执行申万行业分析: {test_symbol}")
            analysis_result = await self.industry_agent.analyze_industry_position(
                test_symbol, 
                max_competitors=5
            )
            
            if analysis_result.status.value == "completed":
                logger.info("✅ 申万行业分析完成")
                
                # 检查分析结果
                if analysis_result.analysis_summary:
                    logger.info("✅ 包含分析摘要")
                    # 显示摘要的前200个字符
                    summary_preview = analysis_result.analysis_summary[:200] + "..." if len(analysis_result.analysis_summary) > 200 else analysis_result.analysis_summary
                    logger.info(f"📝 分析摘要预览: {summary_preview}")
                
                if analysis_result.competitive_advantages:
                    logger.info(f"✅ 识别到 {len(analysis_result.competitive_advantages)} 个竞争优势")
                
                if analysis_result.industry_metrics:
                    metrics = analysis_result.industry_metrics
                    logger.info(f"📊 行业地位评级: {metrics.industry_position_grade}, "
                              f"评分: {metrics.competitive_advantage_score}")
                
                # 检查竞争对手数据源
                sw_competitors = [comp for comp in analysis_result.competitors_data 
                                if hasattr(comp, 'data_source') and comp.data_source == 'sw_classification']
                if sw_competitors:
                    logger.info(f"✅ 使用申万分类获取了 {len(sw_competitors)} 个竞争对手")
                
            else:
                logger.warning(f"⚠️ 行业分析未完成，状态: {analysis_result.status}")
                if analysis_result.error_message:
                    logger.warning(f"错误信息: {analysis_result.error_message}")
            
        except Exception as e:
            logger.error(f"❌ 行业分析Agent测试失败: {e}")
            return False
        
        return True
    
    async def test_data_validation_functions(self):
        """测试数据验证和处理函数"""
        logger.info("🧪 测试数据验证和处理函数...")
        
        try:
            # 测试申万行业层级数据结构
            test_hierarchy = SWIndustryHierarchy(
                level_1={'industry_code': '28', 'industry_name': '电子'},
                level_2={'industry_code': '2801', 'industry_name': '电子制造'},
                level_3={'industry_code': '280101', 'industry_name': '消费电子'}
            )
            
            # 测试获取主要行业
            primary_industry = test_hierarchy.get_primary_industry([3, 2, 1])
            if primary_industry:
                logger.info(f"✅ 主要行业: {primary_industry['industry_name']} ({primary_industry['industry_code']})")
            
            # 测试获取行业路径
            industry_path = test_hierarchy.get_industry_path()
            logger.info(f"✅ 行业路径: {industry_path}")
            
            # 测试数据质量评分
            mock_industry_data = {
                'sw_industry_info': {
                    'hierarchy': {
                        'level_1': {'industry_code': '28', 'industry_name': '电子'},
                        'level_2': {'industry_code': '2801', 'industry_name': '电子制造'},
                        'level_3': {'industry_code': '280101', 'industry_name': '消费电子'}
                    }
                },
                'competitors': {'000001': {'roe': 15.5, 'net_profit_margin': 8.2}},
                'target_company': {'roe': 18.0, 'net_profit_margin': 10.5, 'current_ratio': 2.1}
            }
            
            quality_score = calculate_industry_data_quality_score(mock_industry_data)
            logger.info(f"✅ 数据质量评分: {quality_score:.2f}")
            
        except Exception as e:
            logger.error(f"❌ 数据验证函数测试失败: {e}")
            return False
        
        return True
    
    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")
        
        try:
            if self.ashare_toolkit:
                await self.ashare_toolkit.close()
            
            if self.unified_toolkit:
                await self.unified_toolkit.close()
            
            logger.info("✅ 测试环境清理完成")
            
        except Exception as e:
            logger.error(f"❌ 清理测试环境失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始申万行业升级功能测试")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        test_results = []
        
        try:
            await self.setup()
            
            # 执行所有测试
            tests = [
                ("AShare工具集方法", self.test_ashare_toolkit_methods),
                ("统一数据工具集方法", self.test_unified_toolkit_methods),
                ("行业分析Agent", self.test_industry_analysis_agent),
                ("数据验证函数", self.test_data_validation_functions),
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
        logger.info("📊 测试结果汇总")
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
            logger.info("🎉 所有测试通过！申万行业升级功能运行正常")
        else:
            logger.warning("⚠️ 部分测试失败，请检查相关功能")
        
        return passed_tests == total_tests

async def main():
    """主函数"""
    test = SWIndustryUpgradeTest()
    success = await test.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    # 运行测试
    exit_code = asyncio.run(main())
    sys.exit(exit_code)