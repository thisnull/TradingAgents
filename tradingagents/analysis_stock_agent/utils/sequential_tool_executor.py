#!/usr/bin/env python3
"""
Sequential Tool Execution Framework

解决LLM一次只调用一个工具的问题，通过程序化的方式按顺序执行所有必需的工具，
然后让LLM基于所有工具结果生成完整的分析报告。
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolExecutionStep:
    """工具执行步骤定义"""
    def __init__(self, tool_name: str, description: str, required_args: Optional[Dict] = None, 
                 dependency: Optional[str] = None, param_mapping: Optional[Dict[str, str]] = None):
        self.tool_name = tool_name
        self.description = description
        self.required_args = required_args or {}
        self.dependency = dependency  # 依赖的前一步工具名
        self.param_mapping = param_mapping or {}  # 参数映射：{目标参数名: 源数据键}

class SequentialToolExecutor:
    """序列化工具执行器"""
    
    def __init__(self, tools: List[Any], debug: bool = False):
        """
        初始化执行器
        
        Args:
            tools: 可用工具列表
            debug: 是否开启调试模式
        """
        self.tools = {tool.name: tool for tool in tools}
        self.debug = debug
        self.execution_results = {}
        
    def execute_tool_sequence(self, 
                            execution_steps: List[ToolExecutionStep],
                            stock_code: str,
                            stock_name: str,
                            context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        按顺序执行工具序列
        
        Args:
            execution_steps: 执行步骤列表
            stock_code: 股票代码
            stock_name: 股票名称
            context: 额外上下文信息
            
        Returns:
            包含所有工具执行结果的字典
        """
        results = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "execution_time": datetime.now().isoformat(),
            "steps": [],
            "tool_results": {},
            "errors": [],
            "success": True
        }
        
        if self.debug:
            logger.info(f"开始序列化执行 {len(execution_steps)} 个工具步骤")
        
        # 按顺序执行每个步骤
        for i, step in enumerate(execution_steps):
            if self.debug:
                logger.info(f"执行步骤 {i+1}/{len(execution_steps)}: {step.description}")
            
            try:
                # 准备工具参数
                tool_args = self._prepare_tool_args(step, results, context)
                
                # 执行工具
                tool_result = self._execute_single_tool(step.tool_name, tool_args)
                
                # 记录结果
                step_result = {
                    "step_number": i + 1,
                    "tool_name": step.tool_name,
                    "description": step.description,
                    "success": True,
                    "result": tool_result,
                    "execution_time": datetime.now().isoformat()
                }
                
                results["steps"].append(step_result)
                results["tool_results"][step.tool_name] = tool_result
                
                if self.debug:
                    logger.info(f"步骤 {i+1} 执行成功: {step.tool_name}")
                    
            except Exception as e:
                error_msg = f"步骤 {i+1} 执行失败 ({step.tool_name}): {str(e)}"
                logger.error(error_msg)
                
                # 记录错误
                step_result = {
                    "step_number": i + 1,
                    "tool_name": step.tool_name,
                    "description": step.description,
                    "success": False,
                    "error": str(e),
                    "execution_time": datetime.now().isoformat()
                }
                
                results["steps"].append(step_result)
                results["errors"].append(error_msg)
                results["success"] = False
                
                # 根据错误策略决定是否继续
                if self._should_continue_on_error(step, e):
                    if self.debug:
                        logger.warning(f"忽略错误，继续执行下一步")
                    continue
                else:
                    if self.debug:
                        logger.error(f"关键错误，停止执行")
                    break
        
        return results
    
    def _prepare_tool_args(self, step: ToolExecutionStep, results: Dict, context: Optional[Dict]) -> Dict:
        """准备工具参数"""
        args = {
            "stock_code": results["stock_code"],
            "stock_name": results["stock_name"]
        }
        
        # 添加必需参数
        args.update(step.required_args)
        
        # 添加上下文信息
        if context:
            args.update(context)
        
        # 如果有依赖，处理参数映射
        if step.dependency and step.dependency in results["tool_results"]:
            dependency_result = results["tool_results"][step.dependency]
            
            # 使用参数映射
            if step.param_mapping:
                for target_param, source_key in step.param_mapping.items():
                    if source_key == "__full_result__":
                        # 使用完整结果
                        args[target_param] = dependency_result
                    elif source_key == "__all_results__":
                        # 聚合所有工具结果
                        args[target_param] = {
                            "financial_data": results["tool_results"].get("get_financial_data", {}),
                            "financial_ratios": results["tool_results"].get("calculate_financial_ratios", {}),
                            "health_score": results["tool_results"].get("calculate_financial_health_score", {}),
                            "stock_code": results["stock_code"],
                            "stock_name": results["stock_name"]
                        }
                    elif isinstance(dependency_result, dict) and source_key in dependency_result:
                        # 使用特定键值
                        args[target_param] = dependency_result[source_key]
                    else:
                        # 默认使用完整结果
                        args[target_param] = dependency_result
            else:
                # 默认行为：使用通用参数名
                args["previous_result"] = dependency_result
                args[f"{step.dependency}_result"] = dependency_result
        
        # 为特定工具添加默认参数
        if step.tool_name == "get_financial_data":
            args.setdefault("years", 3)
        elif step.tool_name == "get_industry_comparison":
            args.setdefault("comparison_years", 2)
        elif step.tool_name == "calculate_valuation_metrics":
            args.setdefault("method", "dcf")
        
        return args
    
    def _execute_single_tool(self, tool_name: str, tool_args: Dict) -> Any:
        """执行单个工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 {tool_name} 未找到")
        
        tool = self.tools[tool_name]
        
        if self.debug:
            logger.debug(f"调用工具 {tool_name}，参数: {list(tool_args.keys())}")
        
        # 执行工具
        result = tool.invoke(tool_args)
        
        if self.debug:
            result_preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            logger.debug(f"工具 {tool_name} 返回结果: {result_preview}")
        
        return result
    
    def _should_continue_on_error(self, step: ToolExecutionStep, error: Exception) -> bool:
        """判断是否在错误时继续执行"""
        # 对于某些非关键步骤，可以继续执行
        non_critical_tools = ["get_market_sentiment", "get_news_analysis"]
        
        if step.tool_name in non_critical_tools:
            return True
        
        # 对于网络错误，可以尝试继续
        if "network" in str(error).lower() or "timeout" in str(error).lower():
            return True
        
        # 默认停止执行
        return False
    
    def generate_tool_results_summary(self, results: Dict) -> str:
        """生成工具执行结果摘要"""
        if not results["success"]:
            return f"工具执行失败，错误: {'; '.join(results['errors'])}"
        
        summary_parts = []
        summary_parts.append(f"成功执行 {len(results['steps'])} 个分析步骤")
        
        for step in results["steps"]:
            if step["success"]:
                summary_parts.append(f"✅ {step['description']}")
            else:
                summary_parts.append(f"❌ {step['description']} (失败)")
        
        return "\n".join(summary_parts)


# 预定义的执行序列

# 财务分析Agent执行序列
FINANCIAL_ANALYSIS_SEQUENCE = [
    ToolExecutionStep("get_financial_data", "获取财务数据", {"years": 3}),
    ToolExecutionStep("calculate_financial_ratios", "计算财务比率", 
                     dependency="get_financial_data", 
                     param_mapping={"financial_data": "__full_result__"}),
    ToolExecutionStep("calculate_financial_health_score", "计算财务健康度评分", 
                     dependency="calculate_financial_ratios",
                     param_mapping={
                         "ratios": "__full_result__",
                         "financial_data": "get_financial_data.__full_result__"
                     }),
    ToolExecutionStep("prepare_analysis_data_for_llm", "准备LLM分析数据", 
                     dependency="calculate_financial_health_score",
                     param_mapping={"analysis_data": "__all_results__"})
]

# 行业分析Agent执行序列
INDUSTRY_ANALYSIS_SEQUENCE = [
    ToolExecutionStep("get_industry_data", "获取行业数据"),
    ToolExecutionStep("get_industry_comparison", "获取行业对比数据", {"comparison_years": 2}),
    ToolExecutionStep("analyze_competitive_position", "分析竞争地位", dependency="get_industry_comparison"),
    ToolExecutionStep("identify_industry_trends", "识别行业趋势", dependency="get_industry_data"),
    ToolExecutionStep("assess_industry_risks", "评估行业风险", dependency="analyze_competitive_position"),
    ToolExecutionStep("generate_industry_analysis_report", "生成行业分析报告", dependency="assess_industry_risks")
]

# 估值分析Agent执行序列
VALUATION_ANALYSIS_SEQUENCE = [
    ToolExecutionStep("get_market_data", "获取市场数据"),
    ToolExecutionStep("calculate_valuation_metrics", "计算估值指标", {"method": "dcf"}),
    ToolExecutionStep("perform_relative_valuation", "执行相对估值分析", dependency="calculate_valuation_metrics"),
    ToolExecutionStep("analyze_technical_indicators", "分析技术指标", dependency="get_market_data"),
    ToolExecutionStep("calculate_intrinsic_value", "计算内在价值", dependency="perform_relative_valuation"),
    ToolExecutionStep("assess_valuation_risk", "评估估值风险", dependency="calculate_intrinsic_value"),
    ToolExecutionStep("generate_valuation_analysis_report", "生成估值分析报告", dependency="assess_valuation_risk")
]

# 信息整合Agent执行序列
INTEGRATION_ANALYSIS_SEQUENCE = [
    ToolExecutionStep("collect_analysis_results", "收集分析结果"),
    ToolExecutionStep("analyze_consistency", "分析一致性", dependency="collect_analysis_results"),
    ToolExecutionStep("calculate_comprehensive_score", "计算综合评分", dependency="analyze_consistency"),
    ToolExecutionStep("identify_risks_and_catalysts", "识别风险和催化剂", dependency="calculate_comprehensive_score"),
    ToolExecutionStep("develop_investment_strategy", "制定投资策略", dependency="identify_risks_and_catalysts"),
    ToolExecutionStep("generate_comprehensive_report", "生成综合报告", dependency="develop_investment_strategy")
]