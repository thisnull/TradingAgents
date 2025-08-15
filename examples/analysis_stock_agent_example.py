"""
A股分析系统使用示例
演示如何使用analysis_stock_agent模块进行股票分析
"""
import asyncio
import logging
import os
from typing import Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入分析系统
try:
    from tradingagents.analysis_stock_agent import (
        AShareAnalysisSystem,
        create_analysis_system,
        ANALYSIS_CONFIG
    )
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已正确安装TradingAgents并配置Python路径")
    exit(1)

async def example_single_stock_analysis():
    """示例1：单只股票分析"""
    print("\n" + "="*60)
    print("示例1：单只股票分析")
    print("="*60)
    
    # 配置系统
    config = ANALYSIS_CONFIG.copy()
    
    # 可以根据需要修改配置
    config.update({
        "debug_mode": True,
        "max_retry_attempts": 2,
        "request_timeout": 60
    })
    
    # 创建分析系统
    system = None
    try:
        logger.info("正在创建A股分析系统...")
        system = await create_analysis_system(config, debug=True)
        
        # 分析平安银行 (000001)
        stock_symbol = "000001"
        logger.info(f"开始分析股票: {stock_symbol}")
        
        result = await system.analyze_stock(stock_symbol)
        
        # 打印分析结果
        print(f"\n分析结果状态: {result.status}")
        
        if result.final_report:
            print("\n最终分析报告:")
            print("-" * 50)
            print(result.final_report)
        
        if result.investment_recommendation:
            print(f"\n投资建议:")
            rec = result.investment_recommendation
            print(f"- 推荐行动: {rec.investment_action}")
            print(f"- 持有期建议: {rec.holding_period}")
            print(f"- 仓位建议: {rec.position_size_suggestion}")
            print(f"- 置信度: {rec.confidence_level}")
            print(f"- 风险等级: {rec.risk_level}")
            
            if rec.key_reasons:
                print(f"- 关键理由:")
                for reason in rec.key_reasons:
                    print(f"  • {reason}")
        
        if result.key_insights:
            print(f"\n关键洞察:")
            for insight in result.key_insights[:5]:
                print(f"- {insight}")
        
        if result.risk_factors:
            print(f"\n风险因素:")
            for risk in result.risk_factors[:5]:
                print(f"- {risk}")
        
        # 打印系统信息
        system_info = system.get_system_info()
        print(f"\n系统信息:")
        print(f"- 系统版本: {system_info['version']}")
        print(f"- 初始化状态: {system_info['initialized']}")
        print(f"- Agent状态: {system_info['agents']}")
        
    except Exception as e:
        logger.error(f"单只股票分析失败: {e}")
        print(f"分析失败: {e}")
    
    finally:
        if system:
            await system.close()
            logger.info("系统资源已释放")

async def example_batch_analysis():
    """示例2：批量股票分析"""
    print("\n" + "="*60)
    print("示例2：批量股票分析")
    print("="*60)
    
    # 创建分析系统
    system = None
    try:
        config = ANALYSIS_CONFIG.copy()
        system = await create_analysis_system(config, debug=True)
        
        # 分析多只股票
        stock_symbols = ["000001", "000002", "600036"]  # 平安银行、万科A、招商银行
        logger.info(f"开始批量分析股票: {stock_symbols}")
        
        results = await system.batch_analyze_stocks(
            stock_symbols,
            max_concurrent=2  # 限制并发数
        )
        
        # 打印批量分析结果
        print(f"\n批量分析完成，共分析 {len(results)} 只股票:")
        print("-" * 50)
        
        for symbol, result in results.items():
            print(f"\n股票 {symbol}:")
            print(f"  状态: {result.status}")
            
            if result.investment_recommendation:
                rec = result.investment_recommendation
                print(f"  投资建议: {rec.investment_action}")
                print(f"  置信度: {rec.confidence_level}")
            
            if result.integrated_metrics:
                metrics = result.integrated_metrics
                print(f"  综合评分: {metrics.overall_score:.1f}/100")
                print(f"  综合评级: {metrics.overall_grade}")
            
            if result.error_message:
                print(f"  错误信息: {result.error_message}")
        
        # 生成对比分析
        print(f"\n对比分析:")
        print("-" * 50)
        
        successful_results = {k: v for k, v in results.items() 
                            if v.status.value in ['completed', 'partial']}
        
        if successful_results:
            # 按综合评分排序
            sorted_stocks = sorted(
                successful_results.items(),
                key=lambda x: x[1].integrated_metrics.overall_score if x[1].integrated_metrics else 0,
                reverse=True
            )
            
            print("按综合评分排序:")
            for i, (symbol, result) in enumerate(sorted_stocks, 1):
                if result.integrated_metrics:
                    score = result.integrated_metrics.overall_score
                    grade = result.integrated_metrics.overall_grade
                    action = result.investment_recommendation.investment_action if result.investment_recommendation else "N/A"
                    print(f"  {i}. {symbol}: {score:.1f}分 ({grade}) - {action}")
    
    except Exception as e:
        logger.error(f"批量股票分析失败: {e}")
        print(f"批量分析失败: {e}")
    
    finally:
        if system:
            await system.close()
            logger.info("系统资源已释放")

async def example_custom_config():
    """示例3：自定义配置"""
    print("\n" + "="*60)
    print("示例3：自定义配置示例")
    print("="*60)
    
    # 自定义配置
    custom_config = ANALYSIS_CONFIG.copy()
    custom_config.update({
        # 调整分析权重
        "integration_weights": {
            "financial_analysis": 0.50,  # 增加财务分析权重
            "industry_analysis": 0.25,   # 减少行业分析权重
            "valuation_analysis": 0.25   # 减少估值分析权重
        },
        
        # 调整评分权重
        "scoring_weights": {
            "financial_quality": 0.5,    # 增加财务质量权重
            "competitive_advantage": 0.2,
            "valuation_level": 0.3
        },
        
        # 修改超时设置
        "request_timeout": 90,
        "max_retry_attempts": 3,
        
        # 启用调试模式
        "debug_mode": True
    })
    
    print("使用自定义配置:")
    print(f"- 财务分析权重: {custom_config['integration_weights']['financial_analysis']}")
    print(f"- 行业分析权重: {custom_config['integration_weights']['industry_analysis']}")
    print(f"- 估值分析权重: {custom_config['integration_weights']['valuation_analysis']}")
    
    # 使用自定义配置创建系统
    system = None
    try:
        system = await create_analysis_system(custom_config, debug=True)
        
        # 分析股票
        result = await system.analyze_stock("000001")
        
        print(f"\n使用自定义配置的分析结果:")
        if result.integrated_metrics:
            print(f"- 综合评分: {result.integrated_metrics.overall_score:.1f}/100")
            print(f"- 综合评级: {result.integrated_metrics.overall_grade}")
            print(f"- 财务评分: {result.integrated_metrics.financial_score:.1f}/100")
            print(f"- 行业评分: {result.integrated_metrics.industry_score:.1f}/100")
            print(f"- 估值评分: {result.integrated_metrics.valuation_score:.1f}/100")
    
    except Exception as e:
        logger.error(f"自定义配置分析失败: {e}")
        print(f"自定义配置分析失败: {e}")
    
    finally:
        if system:
            await system.close()

async def example_error_handling():
    """示例4：错误处理"""
    print("\n" + "="*60)
    print("示例4：错误处理示例")
    print("="*60)
    
    system = None
    try:
        config = ANALYSIS_CONFIG.copy()
        system = await create_analysis_system(config, debug=True)
        
        # 测试无效股票代码
        invalid_symbols = ["12345", "ABCDEF", "0000000"]
        
        print("测试无效股票代码:")
        for symbol in invalid_symbols:
            print(f"\n尝试分析无效代码: {symbol}")
            result = await system.analyze_stock(symbol)
            print(f"- 状态: {result.status}")
            print(f"- 错误信息: {result.error_message}")
        
        # 测试网络超时等错误的处理
        print(f"\n测试错误恢复机制:")
        print("系统会自动重试失败的请求...")
        
    except Exception as e:
        logger.error(f"错误处理示例失败: {e}")
        print(f"错误处理示例失败: {e}")
    
    finally:
        if system:
            await system.close()

async def main():
    """主函数"""
    print("A股分析系统示例程序")
    print("=" * 60)
    
    # 检查环境变量
    print("环境检查:")
    required_vars = ["FINNHUB_API_KEY", "OPENAI_API_KEY"]
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * 8}{value[-4:]}")
        else:
            print(f"✗ {var}: 未设置")
    
    try:
        # 运行所有示例
        await example_single_stock_analysis()
        await example_batch_analysis() 
        await example_custom_config()
        await example_error_handling()
        
        print("\n" + "="*60)
        print("所有示例执行完成！")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        logger.error(f"示例程序执行失败: {e}")
        print(f"示例程序执行失败: {e}")

if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())