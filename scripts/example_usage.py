#!/usr/bin/env python
"""
A股分析系统使用示例
展示如何使用Multi-Agent系统分析A股公司
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tradingagents.analysis_stock_agent import (
    StockAnalysisGraph,
    StockAnalysisConfig
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def example_basic_analysis():
    """基础分析示例"""
    print("\n" + "="*60)
    print("示例1: 基础股票分析")
    print("="*60)
    
    # 创建默认配置
    config = StockAnalysisConfig()
    
    # 创建分析系统
    analyzer = StockAnalysisGraph(config)
    
    # 分析贵州茅台
    stock_code = "600519"
    print(f"\n正在分析: {stock_code} (贵州茅台)")
    
    result = analyzer.analyze(
        stock_code=stock_code,
        save_report=True
    )
    
    # 打印结果
    if result and not result.get("error"):
        print("\n分析完成！")
        print(f"投资评级: {result.get('investment_rating')}")
        print(f"目标价格: {result.get('target_price')}元")
        print(f"财务评分: {result.get('financial_score')}/100")
        print(f"行业地位: {result.get('industry_position')}")
        print(f"估值水平: {result.get('valuation_level')}")
        
        if result.get('report_path'):
            print(f"\n详细报告已保存至: {result['report_path']}")
    else:
        print(f"分析失败: {result.get('error')}")

def example_custom_config():
    """自定义配置示例"""
    print("\n" + "="*60)
    print("示例2: 自定义配置分析")
    print("="*60)
    
    # 自定义配置
    config = StockAnalysisConfig(
        # LLM配置
        llm_provider="openai",
        deep_think_llm="gpt-4o",
        quick_think_llm="gpt-4o-mini",
        
        # 缓存配置
        cache_enabled=True,
        cache_ttl=7200,  # 2小时缓存
        
        # 报告配置
        report_format="markdown",
        report_language="zh_CN",
        
        # Agent配置
        agent_config={
            "financial": {
                "metrics": ["ROE", "ROA", "净利率", "毛利率"],
                "periods": 5,  # 分析5年数据
                "threshold": {
                    "roe_min": 20,  # ROE最低要求20%
                    "debt_ratio_max": 50,  # 资产负债率最高50%
                }
            },
            "industry": {
                "compare_top_n": 10,  # 对比行业前10名
            },
            "valuation": {
                "pr_history_years": 3,  # PR值历史分析3年
            }
        }
    )
    
    # 创建分析系统
    analyzer = StockAnalysisGraph(config)
    
    # 分析比亚迪
    stock_code = "002594"
    print(f"\n正在分析: {stock_code} (比亚迪)")
    
    result = analyzer.analyze(stock_code=stock_code)
    
    # 获取分析摘要
    summary = analyzer.get_analysis_summary(result)
    
    print("\n分析摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

def example_batch_analysis():
    """批量分析示例"""
    print("\n" + "="*60)
    print("示例3: 批量股票分析")
    print("="*60)
    
    # 股票列表（白酒、新能源、科技）
    stock_list = [
        "000858",  # 五粮液（白酒）
        "300750",  # 宁德时代（新能源）
        "000063",  # 中兴通讯（科技）
    ]
    
    config = StockAnalysisConfig()
    analyzer = StockAnalysisGraph(config)
    
    print(f"\n批量分析股票列表: {stock_list}")
    
    # 执行批量分析
    results = analyzer.batch_analyze(stock_list)
    
    # 整理结果
    print("\n" + "-"*60)
    print("批量分析结果汇总:")
    print("-"*60)
    
    for stock_code, result in results.items():
        if result and not result.get("error"):
            print(f"\n{stock_code} - {result.get('company_name', '')}:")
            print(f"  • 投资评级: {result.get('investment_rating')}")
            print(f"  • 目标价格: {result.get('target_price')}元")
            print(f"  • 财务评分: {result.get('financial_score')}/100")
            print(f"  • 主要风险: {', '.join(result.get('key_risks', []))}")
        else:
            print(f"\n{stock_code}: 分析失败 - {result.get('error')}")

def example_quick_screening():
    """快速筛选示例"""
    print("\n" + "="*60)
    print("示例4: 快速投资筛选")
    print("="*60)
    
    # 候选股票池
    candidates = [
        "600519",  # 贵州茅台
        "000002",  # 万科A
        "002415",  # 海康威视
        "300059",  # 东方财富
    ]
    
    config = StockAnalysisConfig()
    analyzer = StockAnalysisGraph(config)
    
    print("\n开始筛选优质投资标的...")
    
    # 分析并筛选
    recommended_stocks = []
    
    for stock_code in candidates:
        print(f"\n分析 {stock_code}...")
        result = analyzer.analyze(stock_code, save_report=False)
        
        if result and not result.get("error"):
            rating = result.get("investment_rating", "")
            score = result.get("financial_score", 0)
            
            # 筛选条件：评级为"推荐"以上，财务评分>70
            if rating in ["强烈推荐", "推荐"] and score > 70:
                recommended_stocks.append({
                    "code": stock_code,
                    "name": result.get("company_name"),
                    "rating": rating,
                    "score": score,
                    "target_price": result.get("target_price")
                })
    
    # 打印推荐结果
    print("\n" + "="*60)
    print("📊 投资推荐列表")
    print("="*60)
    
    if recommended_stocks:
        for stock in recommended_stocks:
            print(f"\n✅ {stock['name']}({stock['code']})")
            print(f"   评级: {stock['rating']}")
            print(f"   财务评分: {stock['score']}")
            print(f"   目标价: {stock['target_price']}元")
    else:
        print("\n暂无符合条件的推荐股票")

def example_focused_analysis():
    """专项分析示例"""
    print("\n" + "="*60)
    print("示例5: 专项深度分析")
    print("="*60)
    
    # 配置专项分析参数
    config = StockAnalysisConfig(
        agent_config={
            "financial": {
                "metrics": ["ROE", "ROIC", "自由现金流", "经营现金流"],
                "periods": 5,
                "threshold": {
                    "roe_min": 15,
                    "debt_ratio_max": 60,
                }
            },
            "report": {
                "sections": ["财务分析", "估值分析", "风险提示"],
                "max_length": 3000,
            }
        }
    )
    
    analyzer = StockAnalysisGraph(config)
    
    # 分析招商银行
    stock_code = "600036"
    print(f"\n执行专项分析: {stock_code} (招商银行)")
    
    result = analyzer.analyze(stock_code)
    
    # 详细展示财务指标
    if result and result.get("financial_metrics"):
        print("\n📈 核心财务指标:")
        for metric, value in result["financial_metrics"].items():
            if value:
                print(f"   • {metric}: {value}")
    
    # 展示风险提示
    if result and result.get("key_risks"):
        print("\n⚠️  风险提示:")
        for i, risk in enumerate(result["key_risks"], 1):
            print(f"   {i}. {risk}")

def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 A股分析Multi-Agent System 使用示例")
    print("="*70)
    
    # 检查环境配置
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  警告: 未检测到OPENAI_API_KEY环境变量")
        print("请设置: export OPENAI_API_KEY='your_api_key'")
        print("\n您可以:")
        print("1. 使用OpenAI官方API")
        print("2. 使用兼容OpenAI接口的自定义endpoint")
        print("3. 配置本地Ollama（需要修改配置）")
        return
    
    # 选择示例
    print("\n请选择要运行的示例:")
    print("1. 基础股票分析")
    print("2. 自定义配置分析")
    print("3. 批量股票分析")
    print("4. 快速投资筛选")
    print("5. 专项深度分析")
    print("0. 运行所有示例")
    
    choice = input("\n请输入选项 (0-5): ").strip()
    
    examples = {
        "1": example_basic_analysis,
        "2": example_custom_config,
        "3": example_batch_analysis,
        "4": example_quick_screening,
        "5": example_focused_analysis,
    }
    
    if choice == "0":
        # 运行所有示例
        for func in examples.values():
            try:
                func()
                input("\n按Enter继续下一个示例...")
            except Exception as e:
                print(f"\n示例运行失败: {e}")
    elif choice in examples:
        # 运行选择的示例
        try:
            examples[choice]()
        except Exception as e:
            print(f"\n示例运行失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n无效的选项")
    
    print("\n示例运行完成！")

if __name__ == "__main__":
    main()
