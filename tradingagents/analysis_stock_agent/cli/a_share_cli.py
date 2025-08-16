"""
A股分析CLI入口

提供命令行接口来使用A股分析multi-agent系统
"""

import argparse
import sys
import json
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


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="A股投资分析多Agent系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python a_share_cli.py analyze 000001 --name "平安银行"
  python a_share_cli.py analyze 000001 --depth basic --config custom_config.json
  python a_share_cli.py list-models
  python a_share_cli.py validate 000001
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析指定股票')
    analyze_parser.add_argument('stock_code', help='股票代码（如000001）')
    analyze_parser.add_argument('--name', help='股票名称（可选）')
    analyze_parser.add_argument(
        '--depth', 
        choices=['basic', 'standard', 'comprehensive'],
        default='comprehensive',
        help='分析深度'
    )
    analyze_parser.add_argument('--config', help='配置文件路径（JSON格式）')
    analyze_parser.add_argument('--output', help='输出文件路径')
    analyze_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证股票代码')
    validate_parser.add_argument('stock_code', help='股票代码')
    
    # 列出模型命令
    list_models_parser = subparsers.add_parser('list-models', help='列出支持的模型')
    
    # 生成配置命令
    config_parser = subparsers.add_parser('generate-config', help='生成配置文件模板')
    config_parser.add_argument('--output', default='a_share_config.json', help='输出文件路径')
    
    return parser


def load_config(config_path: str = None) -> dict:
    """加载配置文件"""
    config = A_SHARE_DEFAULT_CONFIG.copy()
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                config.update(custom_config)
                print(f"✓ 已加载配置文件: {config_path}")
        except Exception as e:
            print(f"⚠ 加载配置文件失败: {e}")
            print("使用默认配置")
    
    return config


def analyze_stock(args):
    """执行股票分析"""
    print(f"🚀 开始分析股票: {args.stock_code}")
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 创建分析图
        with AShareAnalysisGraph(config=config, debug=args.debug) as graph:
            # 验证股票代码
            if not graph.validate_stock_code(args.stock_code):
                print(f"❌ 无效的股票代码: {args.stock_code}")
                return False
            
            # 设置分析深度
            depth_map = {
                'basic': AnalysisDepth.BASIC,
                'standard': AnalysisDepth.STANDARD,
                'comprehensive': AnalysisDepth.COMPREHENSIVE
            }
            analysis_depth = depth_map[args.depth]
            
            print(f"📊 分析深度: {args.depth}")
            print(f"📅 分析日期: {datetime.now().strftime('%Y-%m-%d')}")
            
            # 执行分析
            final_state, comprehensive_report = graph.analyze_stock(
                stock_code=args.stock_code,
                stock_name=args.name,
                analysis_depth=analysis_depth
            )
            
            # 输出结果
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(comprehensive_report)
                print(f"✓ 分析报告已保存到: {args.output}")
            else:
                print("\n" + "="*80)
                print("📈 分析报告")
                print("="*80)
                print(comprehensive_report)
            
            # 显示简要统计
            print(f"\n✓ 分析完成")
            print(f"📊 综合评分: {final_state.get('comprehensive_score', 'N/A')}")
            print(f"💡 投资建议: {final_state.get('investment_recommendation', 'N/A')}")
            
            return True
            
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False


def validate_stock_code(args):
    """验证股票代码"""
    try:
        graph = AShareAnalysisGraph()
        is_valid = graph.validate_stock_code(args.stock_code)
        
        if is_valid:
            print(f"✓ 股票代码 {args.stock_code} 格式有效")
        else:
            print(f"❌ 股票代码 {args.stock_code} 格式无效")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        return False


def list_models():
    """列出支持的模型"""
    try:
        graph = AShareAnalysisGraph()
        models = graph.get_supported_models()
        
        print("📋 支持的语言模型:")
        for model in models:
            print(f"  • {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return False


def generate_config(args):
    """生成配置文件模板"""
    try:
        config_template = {
            # LLM配置
            "deep_think_llm": "o4-mini",
            "quick_think_llm": "gpt-4o-mini",
            
            # API配置
            "openai_api_key": "your_openai_api_key_here",
            "openai_base_url": "https://api.openai.com/v1",
            "a_share_api_url": "http://localhost:8000/api/v1",
            "a_share_api_key": "your_a_share_api_key_here",
            
            # MCP工具配置
            "mcp_tools_enabled": True,
            "mcp_server_url": "http://localhost:3000",
            
            # 分析配置
            "analysis_execution_mode": "parallel",
            "enable_preprocessing": False,
            "enable_postprocessing": False,
            "enable_conditional_edges": False,
            "enable_retry_logic": False,
            "max_retries": 3,
            
            # 日志配置
            "log_level": "INFO",
            "debug_mode": False,
            
            # 估值模型参数
            "default_wacc": 8.5,
            "default_terminal_growth": 2.5,
            
            # 其他配置
            "a_share_api_timeout": 30,
            "a_share_api_retry_times": 3
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(config_template, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 配置文件模板已生成: {args.output}")
        print("💡 请编辑配置文件中的API密钥和其他参数")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成配置文件失败: {e}")
        return False


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🎯 A股投资分析多Agent系统")
    print("-" * 50)
    
    success = False
    
    if args.command == 'analyze':
        success = analyze_stock(args)
    elif args.command == 'validate':
        success = validate_stock_code(args)
    elif args.command == 'list-models':
        success = list_models()
    elif args.command == 'generate-config':
        success = generate_config(args)
    else:
        print(f"❌ 未知命令: {args.command}")
        parser.print_help()
    
    if success:
        print("\n🎉 操作完成!")
    else:
        print("\n💥 操作失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()