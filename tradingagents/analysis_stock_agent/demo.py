#!/usr/bin/env python3
"""
A股分析系统演示脚本

展示如何使用入口方法进行股票分析。
包含命令行和Python API两种使用方式的完整示例。
"""

import os
import sys
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))


def demo_command_line():
    """演示命令行接口使用方法"""
    print("="*60)
    print("🖥️  命令行接口演示")
    print("="*60)
    
    print("\n📝 基本用法:")
    print("python -m tradingagents.analysis_stock_agent.main 002594")
    
    print("\n📝 启用调试模式:")
    print("python -m tradingagents.analysis_stock_agent.main 002594 --debug")
    
    print("\n📝 指定分析深度:")
    print("python -m tradingagents.analysis_stock_agent.main 000001 --depth comprehensive")
    
    print("\n📝 自定义输出目录:")
    print("python -m tradingagents.analysis_stock_agent.main 600036 --output ./my_reports")
    
    print("\n📝 保存日志到文件:")
    print("python -m tradingagents.analysis_stock_agent.main 000858 --log analysis.log --debug")
    
    print("\n💡 支持的股票代码示例:")
    stock_examples = [
        ("002594", "比亚迪"),
        ("000001", "平安银行"),
        ("600036", "招商银行"), 
        ("000858", "五粮液"),
        ("600519", "贵州茅台")
    ]
    
    for code, name in stock_examples:
        print(f"   {code} - {name}")


def demo_python_api():
    """演示Python API使用方法"""
    print("\n" + "="*60)
    print("🐍 Python API接口演示") 
    print("="*60)
    
    print("\n📝 方式1: 使用便利函数（最简单）")
    print("""
from tradingagents.analysis_stock_agent.api import quick_analyze

# 快速分析单个股票
result = quick_analyze("002594", debug=True)
if result.success:
    print("✅ 分析成功！")
    print(f"报告长度: {len(result.report)} 字符")
    print(f"分析耗时: {result.analysis_time:.2f}秒")
else:
    print(f"❌ 分析失败: {result.error_message}")
""")
    
    print("\n📝 方式2: 使用API类（更多控制）")
    print("""
from tradingagents.analysis_stock_agent.api import StockAnalysisAPI

# 创建API实例
api = StockAnalysisAPI(debug=True)

# 分析单个股票并保存报告
result = api.analyze("002594", save_report=True)
if result.success:
    print(result.report[:200] + "...")
    
    # 获取分析摘要
    summary = api.get_analysis_summary(result)
    print(f"投资建议: {summary.get('investment_recommendation', 'N/A')}")
""")
    
    print("\n📝 方式3: 批量分析投资组合")
    print("""
from tradingagents.analysis_stock_agent.api import analyze_portfolio

# 分析投资组合
portfolio = ["002594", "000001", "600036", "000858"]
results = analyze_portfolio(portfolio, save_reports=True, debug=True)

# 打印每只股票的投资建议
api = StockAnalysisAPI()
for result in results:
    if result.success:
        summary = api.get_analysis_summary(result)
        print(f"{result.stock_code}: {summary.get('investment_recommendation', 'N/A')}")

# 导出批量分析摘要
api.export_batch_results(results, "portfolio_analysis.json")
""")


def demo_advanced_usage():
    """演示高级用法"""
    print("\n" + "="*60)
    print("🚀 高级用法演示")
    print("="*60)
    
    print("\n📝 自定义配置:")
    print("""
# 创建自定义配置
custom_config = {
    "deep_think_llm": "gemini-2.5-pro",
    "quick_think_llm": "gemini-2.5-flash",
    "max_debate_rounds": 2,
    "analysis_timeout": 300,
    "a_share_api_url": "http://your-api-server.com/api/v1"
}

api = StockAnalysisAPI(config=custom_config, debug=True)
result = api.analyze("002594")
""")
    
    print("\n📝 错误处理:")
    print("""
try:
    result = api.analyze("INVALID_CODE")
    if not result.success:
        print(f"分析失败: {result.error_message}")
except Exception as e:
    print(f"系统错误: {e}")
""")
    
    print("\n📝 性能监控:")
    print("""
import time
start_time = time.time()

result = api.analyze("002594")

print(f"API调用耗时: {result.analysis_time:.2f}秒")
print(f"总体耗时: {time.time() - start_time:.2f}秒")
""")


def demo_environment_setup():
    """演示环境配置"""
    print("\n" + "="*60)
    print("⚙️  环境配置指南")
    print("="*60)
    
    print("\n📝 1. 激活conda环境:")
    print("conda activate tradingagents")
    
    print("\n📝 2. 设置必需的环境变量:")
    print("export GOOGLE_API_KEY=$YOUR_GOOGLE_API_KEY")
    print("export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY  # 可选")
    
    print("\n📝 3. 验证安装:")
    print("""
python -c "
from tradingagents.analysis_stock_agent.api import quick_analyze
print('✅ 模块导入成功')
"
""")
    
    print("\n📝 4. 测试基本功能:")
    print("python -m tradingagents.analysis_stock_agent.main --help")
    
    print("\n🔧 常见问题排查:")
    problems = [
        ("模块导入错误", "确保已激活tradingagents环境"),
        ("API密钥错误", "检查GOOGLE_API_KEY环境变量设置"),
        ("网络连接失败", "检查网络连接和防火墙设置"),
        ("权限错误", "确保输出目录有写入权限")
    ]
    
    for problem, solution in problems:
        print(f"   ❌ {problem} → ✅ {solution}")


def check_environment():
    """检查当前环境配置"""
    print("\n" + "="*60)
    print("🔍 环境检查")
    print("="*60)
    
    # 检查环境变量
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    print(f"\n🔑 GOOGLE_API_KEY: {'✅ 已设置' if api_key else '❌ 未设置'}")
    print(f"🔑 FINNHUB_API_KEY: {'✅ 已设置' if finnhub_key else '⚠️ 可选，建议设置'}")
    
    # 检查模块导入
    try:
        from tradingagents.analysis_stock_agent.api import StockAnalysisAPI
        print("📦 模块导入: ✅ 正常")
    except ImportError as e:
        print(f"📦 模块导入: ❌ 失败 - {e}")
        return
    
    # 检查conda环境
    conda_env = os.getenv('CONDA_DEFAULT_ENV')
    print(f"🐍 Conda环境: {conda_env if conda_env else '❌ 未检测到'}")
    
    # 检查输出目录权限
    try:
        test_dir = Path("results")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test_permission.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("📁 输出权限: ✅ 正常")
    except Exception as e:
        print(f"📁 输出权限: ❌ 失败 - {e}")
    
    # 总结
    if api_key:
        print("\n🎉 环境配置完成，可以开始使用！")
        print("\n🚀 快速开始:")
        print("python -m tradingagents.analysis_stock_agent.main 002594 --debug")
    else:
        print("\n⚠️  请设置GOOGLE_API_KEY环境变量后再使用")


def main():
    """主演示函数"""
    print("🔍 A股投资分析系统入口方法演示")
    print("="*60)
    
    # 环境检查
    check_environment()
    
    # 演示各种用法
    demo_environment_setup()
    demo_command_line()
    demo_python_api()
    demo_advanced_usage()
    
    print("\n" + "="*60)
    print("📚 更多信息请查看:")
    print("   - README.md: 完整使用指南")
    print("   - main.py: 命令行入口实现")
    print("   - api.py: Python API接口实现")
    print("="*60)


if __name__ == "__main__":
    main()