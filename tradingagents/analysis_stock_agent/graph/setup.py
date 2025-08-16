"""
图初始化和设置模块

负责A股分析图的初始化、节点配置、边设置等核心功能。
"""

import logging
from typing import Dict, Any, Optional, Callable
from langgraph.graph import StateGraph, START, END

from ..agents.financial_analyst import create_financial_analyst
from ..agents.industry_analyst import create_industry_analyst  
from ..agents.valuation_analyst import create_valuation_analyst
from ..agents.information_integrator import create_information_integrator

from ..utils.state_models import StockAnalysisState, AnalysisStage
from ..utils.llm_utils import LLMManager

logger = logging.getLogger(__name__)


def create_analysis_graph(config: Dict[str, Any], 
                         llm_manager: LLMManager,
                         toolkit: Optional[list] = None) -> StateGraph:
    """
    创建A股分析图
    
    Args:
        config: 配置字典
        llm_manager: LLM管理器实例
        toolkit: 工具集（可选）
        
    Returns:
        配置完成的StateGraph实例
    """
    try:
        logger.info("Creating A-share analysis graph")
        
        # 获取LLM实例
        deep_think_llm = llm_manager.get_llm(config.get("deep_think_llm", "o4-mini"))
        quick_think_llm = llm_manager.get_llm(config.get("quick_think_llm", "gpt-4o-mini"))
        
        # 创建状态图
        workflow = StateGraph(StockAnalysisState)
        
        # 创建各个Agent节点函数
        financial_analyst = create_financial_analyst(deep_think_llm, toolkit or [], config)
        industry_analyst = create_industry_analyst(deep_think_llm, toolkit or [], config)
        valuation_analyst = create_valuation_analyst(deep_think_llm, toolkit or [], config)
        information_integrator = create_information_integrator(deep_think_llm, toolkit or [], config)
        
        # 添加节点到图中
        workflow.add_node("financial_analysis", financial_analyst)
        workflow.add_node("industry_analysis", industry_analyst)
        workflow.add_node("valuation_analysis", valuation_analyst)
        workflow.add_node("information_integration", information_integrator)
        
        # 添加可选的预处理和后处理节点
        if config.get("enable_preprocessing", False):
            preprocessing_node = create_preprocessing_node(config)
            workflow.add_node("preprocessing", preprocessing_node)
        
        if config.get("enable_postprocessing", False):
            postprocessing_node = create_postprocessing_node(config)
            workflow.add_node("postprocessing", postprocessing_node)
        
        logger.info("Graph nodes created successfully")
        return workflow
        
    except Exception as e:
        logger.error(f"Error creating analysis graph: {str(e)}")
        raise


def add_graph_edges(workflow: StateGraph, config: Dict[str, Any]) -> StateGraph:
    """
    添加图的边连接
    
    Args:
        workflow: StateGraph实例
        config: 配置字典
        
    Returns:
        配置完边的StateGraph实例
    """
    try:
        logger.info("Adding graph edges")
        
        # 获取分析执行模式
        analysis_mode = config.get("analysis_execution_mode", "parallel")
        
        if config.get("enable_preprocessing", False):
            # 预处理模式：START -> preprocessing -> 分析节点
            workflow.add_edge(START, "preprocessing")
            
            if analysis_mode == "parallel":
                # 并行执行三个分析
                workflow.add_edge("preprocessing", "financial_analysis")
                workflow.add_edge("preprocessing", "industry_analysis")
                workflow.add_edge("preprocessing", "valuation_analysis")
            else:
                # 串行执行：财务 -> 行业 -> 估值
                workflow.add_edge("preprocessing", "financial_analysis")
                workflow.add_edge("financial_analysis", "industry_analysis")
                workflow.add_edge("industry_analysis", "valuation_analysis")
        else:
            # 直接从START开始
            if analysis_mode == "parallel":
                workflow.add_edge(START, "financial_analysis")
                workflow.add_edge(START, "industry_analysis")
                workflow.add_edge(START, "valuation_analysis")
            else:
                workflow.add_edge(START, "financial_analysis")
                workflow.add_edge("financial_analysis", "industry_analysis")
                workflow.add_edge("industry_analysis", "valuation_analysis")
        
        # 所有分析完成后进入信息整合
        workflow.add_edge("financial_analysis", "information_integration")
        workflow.add_edge("industry_analysis", "information_integration")
        workflow.add_edge("valuation_analysis", "information_integration")
        
        # 信息整合后的流程
        if config.get("enable_postprocessing", False):
            workflow.add_edge("information_integration", "postprocessing")
            workflow.add_edge("postprocessing", END)
        else:
            workflow.add_edge("information_integration", END)
        
        logger.info("Graph edges added successfully")
        return workflow
        
    except Exception as e:
        logger.error(f"Error adding graph edges: {str(e)}")
        raise


def create_preprocessing_node(config: Dict[str, Any]) -> Callable:
    """
    创建预处理节点
    
    Args:
        config: 配置字典
        
    Returns:
        预处理节点函数
    """
    def preprocessing_node(state: StockAnalysisState) -> StockAnalysisState:
        """
        预处理节点：验证输入、初始化数据等
        """
        try:
            logger.info("Running preprocessing")
            
            stock_code = state.get("stock_code", "")
            if not stock_code:
                raise ValueError("Stock code is required")
            
            # 验证股票代码格式
            if not _validate_stock_code(stock_code):
                raise ValueError(f"Invalid stock code format: {stock_code}")
            
            # 更新状态
            updated_state = state.copy()
            updated_state["analysis_stage"] = AnalysisStage.PREPROCESSING
            updated_state["data_sources"] = updated_state.get("data_sources", []) + ["预处理模块"]
            
            logger.info("Preprocessing completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}")
            return {
                **state,
                "analysis_stage": AnalysisStage.ERROR,
                "error_message": str(e)
            }
    
    return preprocessing_node


def create_postprocessing_node(config: Dict[str, Any]) -> Callable:
    """
    创建后处理节点
    
    Args:
        config: 配置字典
        
    Returns:
        后处理节点函数
    """
    def postprocessing_node(state: StockAnalysisState) -> StockAnalysisState:
        """
        后处理节点：最终验证、格式化输出等
        """
        try:
            logger.info("Running postprocessing")
            
            # 验证分析完整性
            required_reports = [
                "financial_analysis_report",
                "industry_analysis_report", 
                "valuation_analysis_report",
                "comprehensive_analysis_report"
            ]
            
            missing_reports = []
            for report in required_reports:
                if not state.get(report):
                    missing_reports.append(report)
            
            if missing_reports:
                logger.warning(f"Missing reports: {missing_reports}")
            
            # 更新最终状态
            updated_state = state.copy()
            updated_state["analysis_stage"] = AnalysisStage.COMPLETED
            updated_state["analysis_completed"] = True
            updated_state["data_sources"] = updated_state.get("data_sources", []) + ["后处理模块"]
            
            # 计算完整性得分
            completeness_score = (len(required_reports) - len(missing_reports)) / len(required_reports) * 100
            updated_state["analysis_completeness"] = completeness_score
            
            logger.info("Postprocessing completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Error in postprocessing: {str(e)}")
            return {
                **state,
                "analysis_stage": AnalysisStage.ERROR,
                "error_message": str(e)
            }
    
    return postprocessing_node


def create_conditional_edges(workflow: StateGraph, config: Dict[str, Any]) -> StateGraph:
    """
    添加条件边（如果需要）
    
    Args:
        workflow: StateGraph实例
        config: 配置字典
        
    Returns:
        添加条件边后的StateGraph实例
    """
    try:
        logger.info("Adding conditional edges")
        
        # 这里可以添加条件逻辑，比如：
        # - 根据分析结果决定是否需要额外分析
        # - 根据错误状态决定重试逻辑
        # - 根据配置决定分析深度
        
        def should_retry_analysis(state: StockAnalysisState) -> str:
            """决定是否需要重试分析"""
            error_count = state.get("error_count", 0)
            max_retries = config.get("max_retries", 3)
            
            if error_count < max_retries and state.get("analysis_stage") == AnalysisStage.ERROR:
                return "retry"
            else:
                return "continue"
        
        # 示例：添加错误处理的条件边
        if config.get("enable_retry_logic", False):
            workflow.add_conditional_edges(
                "information_integration",
                should_retry_analysis,
                {
                    "retry": "financial_analysis",  # 重试时回到财务分析
                    "continue": END
                }
            )
        
        logger.info("Conditional edges added successfully")
        return workflow
        
    except Exception as e:
        logger.error(f"Error adding conditional edges: {str(e)}")
        raise


def _validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        stock_code: 股票代码
        
    Returns:
        是否为有效格式
    """
    if not stock_code:
        return False
    
    # 移除可能的后缀
    code = stock_code.split('.')[0]
    
    # 检查长度和格式
    if len(code) != 6 or not code.isdigit():
        return False
    
    # 检查市场前缀
    valid_prefixes = [
        '000', '001', '002', '003',  # 深圳主板、中小板
        '300',  # 创业板
        '600', '601', '603', '605',  # 上海主板
        '688',  # 科创板
        '430', '831', '832', '833', '834', '835', '836', '837', '838', '839'  # 新三板
    ]
    
    return any(code.startswith(p) for p in valid_prefixes)


def setup_graph_logging(config: Dict[str, Any]):
    """
    设置图的日志配置
    
    Args:
        config: 配置字典
    """
    log_level = config.get("log_level", "INFO")
    log_format = config.get("log_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format
    )
    
    # 设置特定模块的日志级别
    if config.get("debug_mode", False):
        logging.getLogger("tradingagents.analysis_stock_agent").setLevel(logging.DEBUG)


def validate_graph_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证图配置
    
    Args:
        config: 配置字典
        
    Returns:
        验证结果和错误信息
    """
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # 检查必需的配置项
    required_configs = [
        "deep_think_llm",
        "quick_think_llm",
        "a_share_api_url"
    ]
    
    for req_config in required_configs:
        if req_config not in config:
            validation_results["errors"].append(f"Missing required config: {req_config}")
            validation_results["valid"] = False
    
    # 检查API密钥
    if not config.get("openai_api_key") and not config.get("OPENAI_API_KEY"):
        validation_results["warnings"].append("OpenAI API key not configured")
    
    if not config.get("a_share_api_key"):
        validation_results["warnings"].append("A-share API key not configured")
    
    # 检查模型配置
    supported_models = ["gpt-4o", "gpt-4o-mini", "o4-mini", "o1", "claude-3-opus", "claude-3-sonnet"]
    
    for model_key in ["deep_think_llm", "quick_think_llm"]:
        model = config.get(model_key)
        if model and model not in supported_models:
            validation_results["warnings"].append(f"Unsupported model in {model_key}: {model}")
    
    return validation_results