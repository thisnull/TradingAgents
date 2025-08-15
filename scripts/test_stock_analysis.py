#!/usr/bin/env python
"""
A股分析系统测试脚本
用于测试Multi-Agent股票分析系统的功能
"""

import sys
import os
import logging
from pathlib import Path
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tradingagents.analysis_stock_agent import (
    StockAnalysisGraph,
    StockAnalysisConfig,
    AStockToolkit
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_stock_analysis.log')
    ]
)

logger = logging.getLogger(__name__)

def test_data_toolkit():
    """测试数据工具包"""
    print("\n" + "="*50)
    print("测试数据工具包")
    print("="*50)
    
    config = {
        "cache_dir": "./cache",
        "cache_enabled": True,
        "cache_ttl": 3600
    }
    
    toolkit = AStockToolkit(config)
    
    # 测试股票：贵州茅台
    test_stock = "600519"
    
    try:
        # 测试获取股票信息
        print(f"\n1. 获取股票信息 {test_stock}:")
        stock_info = toolkit.get_stock_info(test_stock)
        print(f"   股票名称: {stock_info.get('股票名称')}")
        
        # 测试获取财务指标
        print(f"\n2. 获取财务指标:")
        indicators = toolkit.get_financial_indicators(test_stock)
        if indicators and not indicators.get("error"):
            for key, value in list(indicators.items())[:3]:
                print(f"   {key}: {value}")
        
        # 测试获取估值数据
        print(f"\n3. 获取估值数据:")
        valuation = toolkit.get_stock_valuation(test_stock)
        if valuation and not valuation.get("error"):
            print(f"   PE: {valuation.get('PE_动态')}")
            print(f"   PB: {valuation.get('PB')}")
            print(f"   总市值: {valuation.get('总市值')}")
        
        print("\n✅ 数据工具包测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据工具包测试失败: {e}")
        logger.error(f"数据工具包测试失败: {e}", exc_info=True)
        return False

def test_single_stock_analysis():
    """测试单只股票分析"""
    print("\n" + "="*50)
    print("测试单只股票分析")
    print("="*50)
    
    # 创建配置
    config = StockAnalysisConfig(
        llm_provider="openai",
        cache_enabled=True,
        report_format="markdown"
    )
    
    # 检查API密钥
    if not config.api_key:
        print("⚠️  警告: 未设置OPENAI_API_KEY环境变量")
        print("请设置: export OPENAI_API_KEY='your_api_key'")
        return False
    
    try:
        # 创建分析图
        analysis_graph = StockAnalysisGraph(config)
        
        # 分析贵州茅台
        stock_code = "600519"
        print(f"\n开始分析股票: {stock_code}")
        
        # 执行分析
        result = analysis_graph.analyze(
            stock_code=stock_code,
            save_report=True
        )
        
        # 打印分析摘要
        if result and not result.get("error"):
            print("\n分析结果摘要:")
            summary = analysis_graph.get_analysis_summary(result)
            for key, value in summary.items():
                print(f"  {key}: {value}")
            
            # 打印报告路径
            if result.get("report_path"):
                print(f"\n📄 报告已保存: {result['report_path']}")
            
            print("\n✅ 股票分析测试通过")
            return True
        else:
            print(f"\n❌ 股票分析失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 股票分析测试失败: {e}")
        logger.error(f"股票分析测试失败: {e}", exc_info=True)
        return False

def test_batch_analysis():
    """测试批量股票分析"""
    print("\n" + "="*50)
    print("测试批量股票分析")
    print("="*50)
    
    # 测试股票列表
    stock_codes = [
        "000858",  # 五粮液
        "000002",  # 万科A
        "002415",  # 海康威视
    ]
    
    # 创建配置
    config = StockAnalysisConfig(
        llm_provider="openai",
        cache_enabled=True,
        report_format="markdown"
    )
    
    # 检查API密钥
    if not config.api_key:
        print("⚠️  警告: 未设置OPENAI_API_KEY环境变量")
        return False
    
    try:
        # 创建分析图
        analysis_graph = StockAnalysisGraph(config)
        
        print(f"\n批量分析股票: {stock_codes}")
        
        # 执行批量分析
        results = analysis_graph.batch_analyze(stock_codes)
        
        # 打印结果
        success_count = 0
        for stock_code, result in results.items():
            if result and not result.get("error"):
                print(f"\n✅ {stock_code} 分析成功")
                print(f"   投资评级: {result.get('investment_rating')}")
                print(f"   目标价格: {result.get('target_price')}")
                success_count += 1
            else:
                print(f"\n❌ {stock_code} 分析失败: {result.get('error')}")
        
        print(f"\n批量分析完成: {success_count}/{len(stock_codes)} 成功")
        return success_count == len(stock_codes)
        
    except Exception as e:
        print(f"\n❌ 批量分析测试失败: {e}")
        logger.error(f"批量分析测试失败: {e}", exc_info=True)
        return False

def test_agent_components():
    """测试各个Agent组件"""
    print("\n" + "="*50)
    print("测试Agent组件")
    print("="*50)
    
    from tradingagents.analysis_stock_agent.agents import (
        FinancialAnalystAgent,
        IndustryAnalystAgent,
        ValuationAnalystAgent,
        ReportIntegrationAgent
    )
    
    # 创建配置
    config = StockAnalysisConfig()
    
    # 检查API密钥
    if not config.api_key:
        print("⚠️  警告: 未设置OPENAI_API_KEY环境变量")
        return False
    
    try:
        # 初始化LLM
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=config.quick_think_llm,
            base_url=config.backend_url,
            api_key=config.api_key
        )
        
        # 初始化工具包
        toolkit = AStockToolkit(config.to_dict())
        
        # 测试财务分析Agent
        print("\n1. 测试财务分析Agent:")
        financial_agent = FinancialAnalystAgent(llm, toolkit)
        print("   ✅ 财务分析Agent创建成功")
        
        # 测试行业分析Agent
        print("\n2. 测试行业分析Agent:")
        industry_agent = IndustryAnalystAgent(llm, toolkit)
        print("   ✅ 行业分析Agent创建成功")
        
        # 测试估值分析Agent
        print("\n3. 测试估值分析Agent:")
        valuation_agent = ValuationAnalystAgent(llm, toolkit)
        print("   ✅ 估值分析Agent创建成功")
        
        # 测试报告整合Agent
        print("\n4. 测试报告整合Agent:")
        report_agent = ReportIntegrationAgent(llm, config.to_dict())
        print("   ✅ 报告整合Agent创建成功")
        
        print("\n✅ 所有Agent组件测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent组件测试失败: {e}")
        logger.error(f"Agent组件测试失败: {e}", exc_info=True)
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("A股分析Multi-Agent System 测试")
    print("="*60)
    
    # 测试结果统计
    results = {}
    
    # 1. 测试数据工具包
    results["数据工具包"] = test_data_toolkit()
    
    # 2. 测试Agent组件
    results["Agent组件"] = test_agent_components()
    
    # 3. 测试单只股票分析（需要完整的API配置）
    if os.getenv("OPENAI_API_KEY"):
        results["单股分析"] = test_single_stock_analysis()
        
        # 4. 测试批量分析（可选）
        # results["批量分析"] = test_batch_analysis()
    else:
        print("\n⚠️  跳过需要API的测试，请设置OPENAI_API_KEY环境变量")
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    # 返回测试是否全部通过
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
