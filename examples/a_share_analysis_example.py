"""
A股分析系统使用示例

演示如何使用A股投资分析多Agent系统进行股票分析
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.analysis_stock_agent import (
    AShareAnalysisGraph,
    A_SHARE_DEFAULT_CONFIG,
    AnalysisDepth
)


def basic_usage_example():
    """基础使用示例"""
    print("="*60)
    print("📊 基础使用示例")
    print("="*60)
    
    # 创建配置
    config = A_SHARE_DEFAULT_CONFIG.copy()
    
    # 设置必要的API密钥（示例）
    config["openai_api_key"] = os.getenv("OPENAI_API_KEY", "your_key_here")
    config["a_share_api_key"] = os.getenv("A_SHARE_API_KEY", "your_key_here")
    
    # 创建分析图实例
    try:
        with AShareAnalysisGraph(config=config, debug=True) as graph:
            print("✓ 分析图创建成功")
            
            # 验证股票代码
            stock_code = "000001"
            if graph.validate_stock_code(stock_code):
                print(f"✓ 股票代码 {stock_code} 验证通过")
            else:
                print(f"❌ 股票代码 {stock_code} 格式无效")
                return
            
            # 执行分析
            print(f"🚀 开始分析股票 {stock_code}")
            
            final_state, comprehensive_report = graph.analyze_stock(
                stock_code=stock_code,
                stock_name="平安银行",
                analysis_depth=AnalysisDepth.BASIC
            )
            
            print("✓ 分析完成")
            print(f"📊 综合评分: {final_state.get('comprehensive_score', 'N/A')}")
            print(f"💡 投资建议: {final_state.get('investment_recommendation', 'N/A')}")
            
            # 保存报告
            report_file = f"analysis_report_{stock_code}_{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(comprehensive_report)
            print(f"📄 分析报告已保存: {report_file}")
            
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")


def advanced_usage_example():
    """高级使用示例"""
    print("\n" + "="*60)
    print("🎯 高级使用示例")
    print("="*60)
    
    # 自定义配置
    custom_config = A_SHARE_DEFAULT_CONFIG.copy()
    custom_config.update({
        "deep_think_llm": "gpt-4o",  # 使用更强的模型
        "analysis_execution_mode": "serial",  # 串行执行分析
        "enable_preprocessing": True,  # 启用预处理
        "enable_postprocessing": True,  # 启用后处理
        "log_level": "DEBUG"  # 详细日志
    })
    
    try:
        with AShareAnalysisGraph(config=custom_config, debug=True) as graph:
            print("✓ 高级分析图创建成功")
            
            # 批量分析多只股票
            stock_codes = ["000001", "000002", "600000"]
            results = {}
            
            for stock_code in stock_codes:
                if not graph.validate_stock_code(stock_code):
                    print(f"⚠ 跳过无效股票代码: {stock_code}")
                    continue
                
                print(f"🔍 分析股票: {stock_code}")
                
                try:
                    final_state, report = graph.analyze_stock(
                        stock_code=stock_code,
                        analysis_depth=AnalysisDepth.COMPREHENSIVE
                    )
                    
                    results[stock_code] = {
                        "score": final_state.get("comprehensive_score", 0),
                        "recommendation": final_state.get("investment_recommendation", ""),
                        "stage": final_state.get("analysis_stage", "")
                    }
                    
                    print(f"  ✓ 评分: {results[stock_code]['score']}")
                    print(f"  ✓ 建议: {results[stock_code]['recommendation']}")
                    
                except Exception as e:
                    print(f"  ❌ 分析失败: {e}")
                    results[stock_code] = {"error": str(e)}
            
            # 输出汇总结果
            print("\n📈 批量分析结果汇总:")
            for code, result in results.items():
                if "error" not in result:
                    print(f"  {code}: {result['score']}分 ({result['recommendation']})")
                else:
                    print(f"  {code}: 分析失败 - {result['error']}")
            
    except Exception as e:
        print(f"❌ 高级分析过程中出现错误: {e}")


def configuration_example():
    """配置示例"""
    print("\n" + "="*60)
    print("⚙️ 配置示例")
    print("="*60)
    
    # 展示如何创建自定义配置
    custom_config = {
        # LLM配置
        "deep_think_llm": "o4-mini",
        "quick_think_llm": "gpt-4o-mini",
        
        # API配置
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_base_url": "https://oned.lvtu.in/v1",  # 自定义OpenAI端点
        "a_share_api_url": "http://localhost:8000/api/v1",
        "a_share_api_key": os.getenv("A_SHARE_API_KEY"),
        
        # 分析配置
        "analysis_execution_mode": "parallel",
        "enable_preprocessing": True,
        "enable_postprocessing": True,
        "max_retries": 2,
        
        # 估值参数
        "default_wacc": 9.0,
        "default_terminal_growth": 3.0,
        
        # MCP工具
        "mcp_tools_enabled": True,
        "mcp_server_url": "http://localhost:3000",
        
        # 日志配置
        "log_level": "INFO",
        "debug_mode": False
    }
    
    print("📋 自定义配置示例:")
    for key, value in custom_config.items():
        if "key" in key.lower():
            value = "***" if value else "未设置"
        print(f"  {key}: {value}")
    
    try:
        # 使用自定义配置创建图
        graph = AShareAnalysisGraph(config=custom_config)
        
        # 展示可用模型
        models = graph.get_supported_models()
        print(f"\n🤖 支持的模型 ({len(models)}个):")
        for model in models[:5]:  # 只显示前5个
            print(f"  • {model}")
        if len(models) > 5:
            print(f"  ... 还有 {len(models) - 5} 个模型")
        
        print("✓ 配置验证成功")
        
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")


def integration_example():
    """集成示例"""
    print("\n" + "="*60)
    print("🔗 集成示例")
    print("="*60)
    
    # 展示如何在其他项目中集成
    integration_code = '''
# 在你的项目中集成A股分析系统

from tradingagents.analysis_stock_agent import AShareAnalysisGraph, A_SHARE_DEFAULT_CONFIG

class MyTradingSystem:
    def __init__(self):
        # 初始化A股分析系统
        self.config = A_SHARE_DEFAULT_CONFIG.copy()
        self.config["openai_api_key"] = "your_key"
        self.analysis_graph = AShareAnalysisGraph(self.config)
    
    def analyze_portfolio(self, stock_codes):
        """分析投资组合"""
        results = {}
        
        for code in stock_codes:
            try:
                state, report = self.analysis_graph.analyze_stock(code)
                results[code] = {
                    "score": state.get("comprehensive_score", 0),
                    "recommendation": state.get("investment_recommendation", ""),
                    "report": report
                }
            except Exception as e:
                results[code] = {"error": str(e)}
        
        return results
    
    def get_buy_signals(self, stock_codes, min_score=80):
        """获取买入信号"""
        portfolio_analysis = self.analyze_portfolio(stock_codes)
        buy_signals = []
        
        for code, analysis in portfolio_analysis.items():
            if "error" not in analysis:
                score = analysis["score"]
                recommendation = analysis["recommendation"]
                
                if score >= min_score and recommendation in ["买入", "强烈买入"]:
                    buy_signals.append({
                        "code": code,
                        "score": score,
                        "recommendation": recommendation
                    })
        
        return sorted(buy_signals, key=lambda x: x["score"], reverse=True)

# 使用示例
trading_system = MyTradingSystem()
signals = trading_system.get_buy_signals(["000001", "000002", "600000"])
print("买入信号:", signals)
    '''
    
    print("💡 集成代码示例:")
    print(integration_code)


def main():
    """主函数"""
    print("🎯 A股投资分析多Agent系统 - 使用示例")
    print("版本: 1.0.0")
    print("作者: TradingAgents Team")
    
    try:
        # 基础使用示例
        basic_usage_example()
        
        # 高级使用示例
        advanced_usage_example()
        
        # 配置示例
        configuration_example()
        
        # 集成示例
        integration_example()
        
        print("\n🎉 所有示例演示完成!")
        print("\n💡 提示:")
        print("  1. 请确保设置正确的API密钥")
        print("  2. 可以通过CLI工具快速使用: python a_share_cli.py analyze 000001")
        print("  3. 支持多种分析深度: basic, standard, comprehensive")
        print("  4. 查看完整文档: docs/README.md")
        
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()