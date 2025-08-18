"""
A股分析多Agent图结构

基于LangGraph框架的A股投资分析多Agent工作流系统，
整合财务分析、行业分析、估值分析和信息整合四个专业Agent。
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from ..utils.state_models import StockAnalysisState, AnalysisStage, AnalysisDepth
from ..config.a_share_config import A_SHARE_DEFAULT_CONFIG
from ..utils.llm_utils import LLMManager
from .setup import (
    create_analysis_graph, 
    add_graph_edges, 
    create_conditional_edges,
    setup_graph_logging,
    validate_graph_config,
    _validate_stock_code
)


logger = logging.getLogger(__name__)


class AShareAnalysisGraph:
    """
    A股分析多Agent图类
    
    管理整个A股投资分析工作流，协调各个专业Agent的执行顺序，
    确保分析流程的完整性和结果的一致性。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, debug: bool = False):
        """
        初始化A股分析图
        
        Args:
            config: 配置字典，默认使用A_SHARE_DEFAULT_CONFIG
            debug: 是否启用调试模式
        """
        self.config = config or A_SHARE_DEFAULT_CONFIG.copy()
        self.debug = debug
        
        # 设置日志级别
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        # 初始化LLM管理器
        self.llm_manager = LLMManager(self.config)
        
        # 获取LLM实例
        self.deep_think_llm = self.llm_manager.get_llm(self.config.get("deep_think_llm", "o4-mini"))
        self.quick_think_llm = self.llm_manager.get_llm(self.config.get("quick_think_llm", "gpt-4o-mini"))
        
        # 工具集（暂时为空，后续可扩展）
        self.toolkit = []
        
        # 创建检查点保存器
        self.checkpointer = MemorySaver()
        
        # 初始化图结构
        self.graph = None
        self.compiled_graph = None
        
        # 创建图
        self._create_graph()
        
        logger.info("AShareAnalysisGraph initialized successfully")
    
    def _create_graph(self):
        """创建并配置LangGraph"""
        try:
            # 设置日志
            setup_graph_logging(self.config)
            
            # 验证配置
            validation_result = validate_graph_config(self.config)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid configuration: {validation_result['errors']}")
            
            if validation_result["warnings"]:
                for warning in validation_result["warnings"]:
                    logger.warning(warning)
            
            # 创建基础图结构
            workflow = create_analysis_graph(self.config, self.llm_manager, self.toolkit)
            
            # 添加边连接
            workflow = add_graph_edges(workflow, self.config)
            
            # 添加条件边（如果启用）
            if self.config.get("enable_conditional_edges", False):
                workflow = create_conditional_edges(workflow, self.config)
            
            # 编译图
            self.graph = workflow
            self.compiled_graph = workflow.compile(checkpointer=self.checkpointer)
            
            logger.info("Graph created and compiled successfully")
            
        except Exception as e:
            logger.error(f"Error creating graph: {str(e)}")
            raise
    
    def analyze_stock(self, stock_code: str, 
                     stock_name: Optional[str] = None,
                     analysis_depth: AnalysisDepth = AnalysisDepth.COMPREHENSIVE,
                     analysis_date: Optional[str] = None) -> Tuple[StockAnalysisState, str]:
        """
        分析指定股票
        
        Args:
            stock_code: 股票代码（如"000001"）
            stock_name: 股票名称（可选）
            analysis_depth: 分析深度
            analysis_date: 分析日期，默认当前日期
            
        Returns:
            (最终状态, 综合分析报告)
        """
        try:
            logger.info(f"Starting analysis for stock {stock_code}")
            
            # 准备初始状态
            if not analysis_date:
                analysis_date = datetime.now().strftime("%Y-%m-%d")
            
            initial_state = {
                "stock_code": stock_code,
                "stock_name": stock_name or stock_code,
                "analysis_date": analysis_date,
                "analysis_depth": analysis_depth,
                "analysis_stage": [AnalysisStage.INIT],
                "messages": [],
                "financial_analysis_report": "",
                "industry_analysis_report": "",
                "valuation_analysis_report": "",
                "comprehensive_analysis_report": "",
                "financial_data": {},
                "industry_data": {},
                "valuation_data": {},
                "integration_data": {},
                "key_financial_metrics": {},
                "key_industry_metrics": {},
                "market_signals": {},
                "technical_indicators": {},
                "competitive_position": {},
                "comprehensive_score": 0,
                "investment_recommendation": "",
                "final_conclusion": "",
                "data_sources": [],
                "analysis_completed": False,
                "last_updated": datetime.now().isoformat()
            }
            
            # 执行图工作流
            thread_config = {"configurable": {"thread_id": f"analysis_{stock_code}_{analysis_date}"}}
            
            final_state = None
            for state in self.compiled_graph.stream(initial_state, config=thread_config):
                final_state = state
                if self.debug:
                    logger.debug(f"Current state: {state}")
            
            if final_state is None:
                raise Exception("Graph execution failed - no final state")
            
            # 获取最终的综合报告
            comprehensive_report = ""
            for node_name, node_state in final_state.items():
                if node_name == "information_integration":
                    comprehensive_report = node_state.get("comprehensive_analysis_report", "")
                    break
            
            if not comprehensive_report:
                # 如果没有生成综合报告，创建一个简单的汇总
                financial_report = final_state.get("financial_analysis", {}).get("financial_analysis_report", "")
                industry_report = final_state.get("industry_analysis", {}).get("industry_analysis_report", "")
                valuation_report = final_state.get("valuation_analysis", {}).get("valuation_analysis_report", "")
                
                comprehensive_report = f"""
# {stock_name or stock_code} 综合分析报告

## 分析概要
分析日期：{analysis_date}
分析深度：{analysis_depth.value}

## 财务分析
{financial_report if financial_report else "财务分析数据不可用"}

## 行业分析  
{industry_report if industry_report else "行业分析数据不可用"}

## 估值分析
{valuation_report if valuation_report else "估值分析数据不可用"}

## 综合结论
基于以上多维度分析，该股票的投资价值需要进一步评估。
                """
            
            logger.info(f"Analysis completed for stock {stock_code}")
            
            return final_state, comprehensive_report
            
        except Exception as e:
            logger.error(f"Error analyzing stock {stock_code}: {str(e)}")
            raise
    
    def get_analysis_status(self, stock_code: str, analysis_date: str) -> Dict[str, Any]:
        """
        获取分析状态
        
        Args:
            stock_code: 股票代码
            analysis_date: 分析日期
            
        Returns:
            分析状态信息
        """
        try:
            thread_id = f"analysis_{stock_code}_{analysis_date}"
            thread_config = {"configurable": {"thread_id": thread_id}}
            
            # 获取当前状态
            current_state = self.compiled_graph.get_state(config=thread_config)
            
            if current_state is None:
                return {"status": "not_found", "message": "Analysis not found"}
            
            values = current_state.values
            next_steps = current_state.next
            
            return {
                "status": "found",
                "analysis_stage": values.get("analysis_stage", "unknown"),
                "analysis_completed": values.get("analysis_completed", False),
                "comprehensive_score": values.get("comprehensive_score", 0),
                "investment_recommendation": values.get("investment_recommendation", ""),
                "next_steps": list(next_steps) if next_steps else [],
                "last_updated": values.get("last_updated", "")
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def list_available_analyses(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的分析
        
        Returns:
            分析列表
        """
        try:
            # 这里需要实现获取所有分析的逻辑
            # 由于使用MemorySaver，这个功能有限
            logger.info("Listing available analyses")
            return []
        except Exception as e:
            logger.error(f"Error listing analyses: {str(e)}")
            return []
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        更新配置
        
        Args:
            new_config: 新的配置字典
        """
        try:
            self.config.update(new_config)
            
            # 重新初始化LLM管理器
            self.llm_manager = LLMManager(self.config)
            self.deep_think_llm = self.llm_manager.get_llm(self.config.get("deep_think_llm", "o4-mini"))
            self.quick_think_llm = self.llm_manager.get_llm(self.config.get("quick_think_llm", "gpt-4o-mini"))
            
            # 重新创建图
            self._create_graph()
            
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            raise
    
    def get_supported_models(self) -> List[str]:
        """
        获取支持的模型列表
        
        Returns:
            支持的模型名称列表
        """
        return self.llm_manager.get_available_models()
    
    def validate_stock_code(self, stock_code: str) -> bool:
        """
        验证股票代码格式
        
        Args:
            stock_code: 股票代码
            
        Returns:
            是否为有效的股票代码
        """
        return _validate_stock_code(stock_code)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 清理资源
        pass