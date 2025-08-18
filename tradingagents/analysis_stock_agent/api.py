"""
A股分析系统 Python API 接口

提供简单易用的Python API接口，方便在其他Python程序中集成A股分析功能。

使用示例:
    from tradingagents.analysis_stock_agent.api import StockAnalysisAPI
    
    # 创建API实例
    api = StockAnalysisAPI(debug=True)
    
    # 分析单个股票
    result = api.analyze("002594")
    print(result.report)
    
    # 批量分析
    results = api.batch_analyze(["002594", "000001", "600036"])
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, NamedTuple
from dataclasses import dataclass

from .graph.a_share_analysis_graph import AShareAnalysisGraph
from .config.a_share_config import A_SHARE_DEFAULT_CONFIG
from .utils.state_models import AnalysisDepth
from .main import setup_logging, validate_stock_code, save_analysis_report


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    stock_code: str
    success: bool
    report: str = ""
    final_state: Optional[Dict[str, Any]] = None
    error_message: str = ""
    analysis_time: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class StockAnalysisAPI:
    """
    A股分析系统 Python API 类
    
    提供简单易用的接口来分析A股股票，支持单个分析和批量分析。
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 debug: bool = False,
                 log_file: Optional[str] = None):
        """
        初始化API实例
        
        Args:
            config: 自定义配置字典
            debug: 是否启用调试模式
            log_file: 日志文件路径
        """
        self.config = config or A_SHARE_DEFAULT_CONFIG.copy()
        self.debug = debug
        
        # 配置日志
        setup_logging(debug=debug, log_file=log_file)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("StockAnalysisAPI 初始化完成")
    
    def analyze(self, 
                stock_code: str,
                analysis_depth: AnalysisDepth = AnalysisDepth.COMPREHENSIVE,
                save_report: bool = False,
                output_dir: str = "results") -> AnalysisResult:
        """
        分析单个股票
        
        Args:
            stock_code: 股票代码
            analysis_depth: 分析深度
            save_report: 是否保存报告到文件
            output_dir: 报告保存目录
            
        Returns:
            分析结果对象
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"开始分析股票: {stock_code}")
            
            # 验证股票代码
            if not validate_stock_code(stock_code):
                error_msg = f"无效的股票代码: {stock_code}"
                self.logger.error(error_msg)
                return AnalysisResult(
                    stock_code=stock_code,
                    success=False,
                    error_message=error_msg
                )
            
            # 创建分析图实例并执行分析
            with AShareAnalysisGraph(config=self.config, debug=self.debug) as graph:
                final_state, comprehensive_report = graph.analyze_stock(
                    stock_code=stock_code,
                    analysis_depth=analysis_depth
                )
            
            # 计算分析耗时
            analysis_time = (datetime.now() - start_time).total_seconds()
            
            # 保存报告（如果需要）
            report_path = ""
            if save_report:
                report_path = save_analysis_report(
                    stock_code=stock_code,
                    report=comprehensive_report,
                    output_dir=output_dir
                )
                self.logger.info(f"报告已保存至: {report_path}")
            
            self.logger.info(f"股票 {stock_code} 分析完成，耗时 {analysis_time:.2f}秒")
            
            return AnalysisResult(
                stock_code=stock_code,
                success=True,
                report=comprehensive_report,
                final_state=final_state,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            analysis_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"分析股票 {stock_code} 时发生错误: {str(e)}"
            
            self.logger.error(error_msg)
            self.logger.error(f"错误详情: {traceback.format_exc()}")
            
            return AnalysisResult(
                stock_code=stock_code,
                success=False,
                error_message=error_msg,
                analysis_time=analysis_time
            )
    
    def batch_analyze(self,
                     stock_codes: List[str],
                     analysis_depth: AnalysisDepth = AnalysisDepth.COMPREHENSIVE,
                     save_reports: bool = False,
                     output_dir: str = "results",
                     max_failures: int = 3) -> List[AnalysisResult]:
        """
        批量分析多个股票
        
        Args:
            stock_codes: 股票代码列表
            analysis_depth: 分析深度
            save_reports: 是否保存报告到文件
            output_dir: 报告保存目录
            max_failures: 最大失败数，超过则停止分析
            
        Returns:
            分析结果列表
        """
        self.logger.info(f"开始批量分析 {len(stock_codes)} 只股票")
        
        results = []
        failure_count = 0
        
        for i, stock_code in enumerate(stock_codes, 1):
            self.logger.info(f"正在分析第 {i}/{len(stock_codes)} 只股票: {stock_code}")
            
            result = self.analyze(
                stock_code=stock_code,
                analysis_depth=analysis_depth,
                save_report=save_reports,
                output_dir=output_dir
            )
            
            results.append(result)
            
            if not result.success:
                failure_count += 1
                if failure_count >= max_failures:
                    self.logger.warning(f"失败次数 ({failure_count}) 达到上限 ({max_failures})，停止批量分析")
                    break
            
            # 显示进度
            success_count = sum(1 for r in results if r.success)
            self.logger.info(f"进度: {i}/{len(stock_codes)}, 成功: {success_count}, 失败: {failure_count}")
        
        total_success = sum(1 for r in results if r.success)
        total_failure = len(results) - total_success
        
        self.logger.info(f"批量分析完成: 总计 {len(results)}, 成功 {total_success}, 失败 {total_failure}")
        
        return results
    
    def get_analysis_summary(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        获取分析结果摘要信息
        
        Args:
            result: 分析结果对象
            
        Returns:
            摘要信息字典
        """
        summary = {
            "stock_code": result.stock_code,
            "success": result.success,
            "timestamp": result.timestamp,
            "analysis_time": result.analysis_time
        }
        
        if result.success and result.final_state:
            # 提取关键指标
            for key, value in result.final_state.items():
                if key == "information_integration" and isinstance(value, dict):
                    summary.update({
                        "comprehensive_score": value.get("comprehensive_score", 0),
                        "investment_recommendation": value.get("investment_recommendation", ""),
                        "final_conclusion": value.get("final_conclusion", "")
                    })
                    break
        
        if not result.success:
            summary["error_message"] = result.error_message
        
        return summary
    
    def export_batch_results(self,
                           results: List[AnalysisResult],
                           output_path: str = "batch_analysis_summary.json") -> str:
        """
        导出批量分析结果摘要
        
        Args:
            results: 分析结果列表
            output_path: 输出文件路径
            
        Returns:
            导出文件路径
        """
        import json
        
        summary_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_stocks": len(results),
            "successful_analyses": sum(1 for r in results if r.success),
            "failed_analyses": sum(1 for r in results if not r.success),
            "results": [self.get_analysis_summary(result) for result in results]
        }
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"批量分析摘要已导出至: {output_path}")
        return output_path


# 便利函数
def quick_analyze(stock_code: str, debug: bool = False) -> AnalysisResult:
    """
    快速分析单个股票的便利函数
    
    Args:
        stock_code: 股票代码
        debug: 是否启用调试模式
        
    Returns:
        分析结果对象
    """
    api = StockAnalysisAPI(debug=debug)
    return api.analyze(stock_code)


def analyze_portfolio(stock_codes: List[str], 
                     save_reports: bool = True,
                     debug: bool = False) -> List[AnalysisResult]:
    """
    分析投资组合的便利函数
    
    Args:
        stock_codes: 股票代码列表
        save_reports: 是否保存报告
        debug: 是否启用调试模式
        
    Returns:
        分析结果列表
    """
    api = StockAnalysisAPI(debug=debug)
    return api.batch_analyze(stock_codes, save_reports=save_reports)


# 示例用法
if __name__ == "__main__":
    # 示例1: 快速分析
    print("=== 快速分析示例 ===")
    result = quick_analyze("002594", debug=True)
    if result.success:
        print(f"分析成功，报告长度: {len(result.report)} 字符")
        print(f"分析耗时: {result.analysis_time:.2f}秒")
    else:
        print(f"分析失败: {result.error_message}")
    
    # 示例2: 使用API类
    print("\n=== API类使用示例 ===")
    api = StockAnalysisAPI(debug=True)
    result = api.analyze("000001", save_report=True)
    summary = api.get_analysis_summary(result)
    print("分析摘要:", summary)
    
    # 示例3: 批量分析（这里注释掉，避免实际执行）
    # print("\n=== 批量分析示例 ===")
    # portfolio = ["002594", "000001", "600036"]
    # results = analyze_portfolio(portfolio, save_reports=True, debug=True)
    # api.export_batch_results(results)