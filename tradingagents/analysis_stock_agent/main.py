#!/usr/bin/env python3
"""
A股分析系统入口脚本

简单易用的入口方法，输入股票代码即可运行整个agents workflow生成分析文档。
支持详细日志输出，便于问题排查。

使用方法:
    python -m tradingagents.analysis_stock_agent.main 002594
    python -m tradingagents.analysis_stock_agent.main 000001 --depth comprehensive --debug
"""

import os
import sys
import argparse
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# 加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv未安装时的提示（仅在调试模式显示）
    pass

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.analysis_stock_agent.graph.a_share_analysis_graph import AShareAnalysisGraph
from tradingagents.analysis_stock_agent.config.a_share_config import A_SHARE_DEFAULT_CONFIG
from tradingagents.analysis_stock_agent.utils.state_models import AnalysisDepth


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    配置详细的日志输出
    
    Args:
        debug: 是否启用调试模式
        log_file: 日志文件路径（可选）
    """
    # 设置日志级别
    log_level = logging.DEBUG if debug else logging.INFO
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置特定模块的日志级别
    if debug:
        logging.getLogger('tradingagents.analysis_stock_agent').setLevel(logging.DEBUG)
        logging.getLogger('langgraph').setLevel(logging.INFO)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    else:
        logging.getLogger('tradingagents.analysis_stock_agent').setLevel(logging.INFO)
        logging.getLogger('langgraph').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        stock_code: 股票代码
        
    Returns:
        是否为有效的股票代码
    """
    if not stock_code:
        return False
    
    # 移除可能的前缀
    clean_code = stock_code.strip().upper()
    if clean_code.startswith('SH') or clean_code.startswith('SZ'):
        clean_code = clean_code[2:]
    
    # 检查长度和格式
    if len(clean_code) != 6:
        return False
        
    if not clean_code.isdigit():
        return False
    
    return True


def save_analysis_report(stock_code: str, report: str, output_dir: str = "results") -> str:
    """
    保存分析报告到文件
    
    Args:
        stock_code: 股票代码
        report: 分析报告内容
        output_dir: 输出目录
        
    Returns:
        保存的文件路径
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 验证输入参数
    if not report or not isinstance(report, str):
        logger.error(f"❌ 报告内容为空或非字符串类型: {type(report)}")
        raise ValueError("报告内容不能为空")
    
    if not stock_code:
        logger.error("❌ 股票代码为空")
        raise ValueError("股票代码不能为空")
    
    # 记录报告信息
    logger.info(f"📝 准备保存报告: 股票代码={stock_code}, 内容长度={len(report)}字符")
    
    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"A股分析报告_{stock_code}_{timestamp}.md"
    filepath = Path(output_dir) / filename
    
    try:
        # 保存报告 - 确保完整写入
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
            f.flush()  # 强制刷新缓冲区
        
        # 验证保存结果
        saved_size = filepath.stat().st_size
        logger.info(f"✅ 报告保存成功: {filepath}")
        logger.info(f"📊 文件大小: {saved_size} 字节 ({saved_size/1024:.2f} KB)")
        
        # 验证文件内容完整性
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        if len(saved_content) != len(report):
            logger.error(f"❌ 文件保存不完整！原始长度: {len(report)}, 保存长度: {len(saved_content)}")
            raise Exception("报告保存不完整")
        
        logger.info(f"✅ 文件完整性验证通过: {len(saved_content)}字符")
        
    except Exception as e:
        logger.error(f"❌ 保存报告失败: {str(e)}")
        raise Exception(f"保存报告失败: {str(e)}")
    
    return str(filepath)


def run_stock_analysis(stock_code: str, 
                      config: Optional[Dict[str, Any]] = None,
                      analysis_depth: AnalysisDepth = AnalysisDepth.COMPREHENSIVE,
                      debug: bool = False) -> tuple[Dict[str, Any], str]:
    """
    运行股票分析workflow
    
    Args:
        stock_code: 股票代码
        config: 配置字典（可选）
        analysis_depth: 分析深度
        debug: 是否启用调试模式
        
    Returns:
        (最终状态, 综合分析报告)
    """
    logger = logging.getLogger(__name__)
    logger.info(f"开始分析股票: {stock_code}")
    
    try:
        # 使用默认配置或自定义配置
        analysis_config = config or A_SHARE_DEFAULT_CONFIG.copy()
        
        # 创建分析图实例
        with AShareAnalysisGraph(config=analysis_config, debug=debug) as graph:
            logger.info("分析图初始化完成")
            
            # 执行分析
            final_state, comprehensive_report = graph.analyze_stock(
                stock_code=stock_code,
                analysis_depth=analysis_depth
            )
            
            logger.info(f"股票 {stock_code} 分析完成")
            return final_state, comprehensive_report
            
    except Exception as e:
        logger.error(f"分析股票 {stock_code} 时发生错误: {str(e)}")
        logger.error(f"错误详情: {traceback.format_exc()}")
        raise


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="A股投资分析多Agent系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s 002594                           # 分析比亚迪
  %(prog)s 000001 --debug                   # 启用调试模式分析平安银行  
  %(prog)s 600036 --depth standard          # 使用标准深度分析招商银行
  %(prog)s 000858 --output ./reports        # 指定输出目录
  %(prog)s 002415 --log analysis.log        # 保存日志到文件
        """
    )
    
    parser.add_argument(
        'stock_code',
        help='股票代码 (例如: 002594, 000001, 600036)'
    )
    
    parser.add_argument(
        '--depth',
        choices=['basic', 'standard', 'comprehensive'],
        default='comprehensive',
        help='分析深度 (默认: comprehensive)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式，输出详细日志'
    )
    
    parser.add_argument(
        '--output',
        default='results',
        help='输出目录 (默认: results)'
    )
    
    parser.add_argument(
        '--log',
        help='日志文件路径 (可选)'
    )
    
    parser.add_argument(
        '--config',
        help='自定义配置文件路径 (JSON格式，可选)'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    setup_logging(debug=args.debug, log_file=args.log)
    logger = logging.getLogger(__name__)
    
    try:
        # 验证股票代码
        if not validate_stock_code(args.stock_code):
            logger.error(f"无效的股票代码: {args.stock_code}")
            logger.error("股票代码应为6位数字，例如: 002594, 000001, 600036")
            sys.exit(1)
        
        # 解析分析深度
        depth_mapping = {
            'basic': AnalysisDepth.BASIC,
            'standard': AnalysisDepth.STANDARD,
            'comprehensive': AnalysisDepth.COMPREHENSIVE
        }
        analysis_depth = depth_mapping[args.depth]
        
        # 加载自定义配置（如果指定）
        config = None
        if args.config:
            import json
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"已加载自定义配置: {args.config}")
        
        # 显示分析开始信息
        print(f"\n{'='*60}")
        print(f"🔍 A股投资分析系统")
        print(f"📈 股票代码: {args.stock_code}")
        print(f"📊 分析深度: {args.depth}")
        print(f"🕒 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # 运行分析
        final_state, comprehensive_report = run_stock_analysis(
            stock_code=args.stock_code,
            config=config,
            analysis_depth=analysis_depth,
            debug=args.debug
        )
        
        # 保存分析报告
        report_path = save_analysis_report(
            stock_code=args.stock_code,
            report=comprehensive_report,
            output_dir=args.output
        )
        
        # 显示结果
        print(f"\n{'='*60}")
        print(f"✅ 分析完成!")
        print(f"📄 报告已保存至: {report_path}")
        print(f"🕒 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示关键信息摘要
        if isinstance(final_state, dict):
            summary_info = []
            for key, value in final_state.items():
                if key == "information_integration" and isinstance(value, dict):
                    if "comprehensive_score" in value:
                        summary_info.append(f"📊 综合评分: {value['comprehensive_score']}")
                    if "investment_recommendation" in value:
                        summary_info.append(f"💡 投资建议: {value['investment_recommendation']}")
            
            if summary_info:
                print("\n📋 分析摘要:")
                for info in summary_info:
                    print(f"   {info}")
        
        print(f"{'='*60}\n")
        
        # 如果调试模式，显示额外信息
        if args.debug:
            print("🔧 调试信息:")
            print(f"   最终状态键数量: {len(final_state) if isinstance(final_state, dict) else 'N/A'}")
            print(f"   报告长度: {len(comprehensive_report)} 字符")
            print()
        
        logger.info("分析流程全部完成")
        
    except KeyboardInterrupt:
        logger.warning("用户中断了分析过程")
        print("\n⚠️  分析已被用户中断")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"分析过程中发生未预期错误: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        print(f"\n❌ 分析失败: {str(e)}")
        
        if args.debug:
            print("\n🔧 详细错误信息:")
            print(traceback.format_exc())
        
        sys.exit(1)


if __name__ == "__main__":
    main()