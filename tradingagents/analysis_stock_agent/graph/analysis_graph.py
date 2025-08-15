"""
A股分析系统主控制器
使用LangGraph协调4个分析Agent的执行流程
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from ..config.analysis_config import ANALYSIS_CONFIG
from ..utils.analysis_states import (
    AnalysisState, 
    AnalysisResult,
    AnalysisStatus,
    create_analysis_state
)
from ..tools.ashare_toolkit import create_ashare_toolkit
from ..tools.mcp_integration import create_mcp_toolkit, UnifiedDataToolkit
from ..agents.financial_analysis_agent import create_financial_analysis_agent
from ..agents.industry_analysis_agent import create_industry_analysis_agent
from ..agents.valuation_analysis_agent import create_valuation_analysis_agent
from ..agents.report_integration_agent import create_report_integration_agent

logger = logging.getLogger(__name__)

class AShareAnalysisSystem:
    """A股分析系统主控制器"""
    
    def __init__(self, config: Dict[str, Any] = None, debug: bool = False):
        """
        初始化A股分析系统
        
        Args:
            config: 配置字典，默认使用ANALYSIS_CONFIG
            debug: 是否启用调试模式
        """
        self.config = config or ANALYSIS_CONFIG.copy()
        self.debug = debug
        
        # 工具集
        self.data_toolkit = None
        
        # 分析Agent
        self.financial_agent = None
        self.industry_agent = None
        self.valuation_agent = None
        self.integration_agent = None
        
        # LangGraph工作流
        self.workflow = None
        
        # 初始化状态
        self._initialized = False
    
    async def initialize(self):
        """初始化系统组件"""
        if self._initialized:
            return
        
        try:
            logger.info("正在初始化A股分析系统...")
            
            # 1. 初始化数据工具集
            await self._initialize_data_toolkit()
            
            # 2. 初始化分析Agent
            await self._initialize_agents()
            
            # 3. 构建LangGraph工作流
            self._build_workflow()
            
            self._initialized = True
            logger.info("A股分析系统初始化完成")
            
        except Exception as e:
            logger.error(f"A股分析系统初始化失败: {e}")
            raise
    
    async def _initialize_data_toolkit(self):
        """初始化数据工具集"""
        try:
            # 创建统一数据工具集
            self.data_toolkit = UnifiedDataToolkit(self.config)
            await self.data_toolkit.initialize()
            
            logger.info("数据工具集初始化完成")
            
        except Exception as e:
            logger.error(f"数据工具集初始化失败: {e}")
            raise
    
    async def _initialize_agents(self):
        """初始化分析Agent"""
        try:
            # 获取A股工具集用于Agent
            ashare_toolkit = self.data_toolkit.ashare_toolkit
            
            # 创建分析Agent
            self.financial_agent = await create_financial_analysis_agent(
                self.config, ashare_toolkit
            )
            
            self.industry_agent = await create_industry_analysis_agent(
                self.config, ashare_toolkit
            )
            
            self.valuation_agent = await create_valuation_analysis_agent(
                self.config, ashare_toolkit
            )
            
            self.integration_agent = await create_report_integration_agent(
                self.config
            )
            
            logger.info("分析Agent初始化完成")
            
        except Exception as e:
            logger.error(f"分析Agent初始化失败: {e}")
            raise
    
    def _build_workflow(self):
        """构建LangGraph工作流"""
        try:
            # 创建状态图
            workflow = StateGraph(AnalysisState)
            
            # 添加节点
            workflow.add_node("financial_analysis", self._financial_analysis_node)
            workflow.add_node("industry_analysis", self._industry_analysis_node)
            workflow.add_node("valuation_analysis", self._valuation_analysis_node)
            workflow.add_node("integration", self._integration_node)
            
            # 定义边 - 并行执行前3个分析，然后整合
            workflow.set_entry_point("financial_analysis")
            
            # 并行执行3个分析Agent
            workflow.add_edge("financial_analysis", "industry_analysis")
            workflow.add_edge("financial_analysis", "valuation_analysis")
            
            # 等待所有分析完成后进行整合
            workflow.add_edge("industry_analysis", "integration")
            workflow.add_edge("valuation_analysis", "integration")
            
            # 整合完成后结束
            workflow.add_edge("integration", END)
            
            # 编译工作流
            self.workflow = workflow.compile()
            
            logger.info("LangGraph工作流构建完成")
            
        except Exception as e:
            logger.error(f"LangGraph工作流构建失败: {e}")
            raise
    
    async def _financial_analysis_node(self, state: AnalysisState) -> Dict[str, Any]:
        """财务分析节点"""
        try:
            logger.info(f"开始财务分析: {state.stock_symbol}")
            
            financial_result = await self.financial_agent.analyze_financial_performance(
                state.stock_symbol
            )
            
            return {
                "financial_analysis": financial_result
            }
            
        except Exception as e:
            logger.error(f"财务分析节点执行失败: {e}")
            return {
                "financial_analysis": None,
                "errors": state.errors + [f"财务分析失败: {str(e)}"]
            }
    
    async def _industry_analysis_node(self, state: AnalysisState) -> Dict[str, Any]:
        """行业分析节点"""
        try:
            logger.info(f"开始行业分析: {state.stock_symbol}")
            
            industry_result = await self.industry_agent.analyze_industry_position(
                state.stock_symbol
            )
            
            return {
                "industry_analysis": industry_result
            }
            
        except Exception as e:
            logger.error(f"行业分析节点执行失败: {e}")
            return {
                "industry_analysis": None,
                "errors": state.errors + [f"行业分析失败: {str(e)}"]
            }
    
    async def _valuation_analysis_node(self, state: AnalysisState) -> Dict[str, Any]:
        """估值分析节点"""
        try:
            logger.info(f"开始估值分析: {state.stock_symbol}")
            
            valuation_result = await self.valuation_agent.analyze_valuation(
                state.stock_symbol
            )
            
            return {
                "valuation_analysis": valuation_result
            }
            
        except Exception as e:
            logger.error(f"估值分析节点执行失败: {e}")
            return {
                "valuation_analysis": None,
                "errors": state.errors + [f"估值分析失败: {str(e)}"]
            }
    
    async def _integration_node(self, state: AnalysisState) -> Dict[str, Any]:
        """报告整合节点"""
        try:
            logger.info(f"开始报告整合: {state.stock_symbol}")
            
            # 检查前面的分析是否都成功完成
            if not all([
                state.financial_analysis,
                state.industry_analysis, 
                state.valuation_analysis
            ]):
                logger.warning("部分分析模块失败，将使用可用数据进行整合")
            
            # 执行整合分析
            integrated_result = await self.integration_agent.integrate_analysis_results(
                state.stock_symbol,
                state.financial_analysis,
                state.industry_analysis,
                state.valuation_analysis
            )
            
            return {
                "final_result": integrated_result
            }
            
        except Exception as e:
            logger.error(f"报告整合节点执行失败: {e}")
            return {
                "final_result": None,
                "errors": state.errors + [f"报告整合失败: {str(e)}"]
            }
    
    async def analyze_stock(self, symbol: str, 
                          analysis_options: Dict[str, Any] = None) -> AnalysisResult:
        """
        分析股票
        
        Args:
            symbol: 股票代码 (6位数字)
            analysis_options: 分析选项
        
        Returns:
            AnalysisResult: 分析结果
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # 验证输入
            from ..utils.data_validator import validate_analysis_input
            is_valid, errors = validate_analysis_input(symbol)
            
            if not is_valid:
                logger.error(f"输入验证失败: {errors}")
                return AnalysisResult(
                    symbol=symbol,
                    status=AnalysisStatus.FAILED,
                    error_message=f"输入验证失败: {'; '.join(errors)}"
                )
            
            # 创建初始状态
            initial_state = create_analysis_state(
                stock_symbol=symbol,
                analysis_options=analysis_options or {}
            )
            
            logger.info(f"开始分析股票: {symbol}")
            
            # 执行工作流
            final_state = await self.workflow.ainvoke(initial_state)
            
            # 返回最终结果
            if final_state.get("final_result"):
                logger.info(f"股票分析完成: {symbol}")
                return final_state["final_result"]
            else:
                # 如果整合失败，尝试返回部分结果
                partial_result = AnalysisResult(
                    symbol=symbol,
                    status=AnalysisStatus.PARTIAL,
                    financial_analysis=final_state.get("financial_analysis"),
                    industry_analysis=final_state.get("industry_analysis"),
                    valuation_analysis=final_state.get("valuation_analysis"),
                    error_message="部分分析模块失败"
                )
                
                logger.warning(f"股票分析部分完成: {symbol}")
                return partial_result
            
        except Exception as e:
            logger.error(f"股票分析失败 {symbol}: {e}")
            return AnalysisResult(
                symbol=symbol,
                status=AnalysisStatus.FAILED,
                error_message=f"分析过程异常: {str(e)}"
            )
    
    async def batch_analyze_stocks(self, symbols: List[str],
                                 max_concurrent: int = 3) -> Dict[str, AnalysisResult]:
        """
        批量分析股票
        
        Args:
            symbols: 股票代码列表
            max_concurrent: 最大并发数
        
        Returns:
            Dict[str, AnalysisResult]: 分析结果字典
        """
        if not self._initialized:
            await self.initialize()
        
        results = {}
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_single(symbol: str):
            async with semaphore:
                try:
                    result = await self.analyze_stock(symbol)
                    return symbol, result
                except Exception as e:
                    logger.error(f"批量分析中股票{symbol}失败: {e}")
                    return symbol, AnalysisResult(
                        symbol=symbol,
                        status=AnalysisStatus.FAILED,
                        error_message=f"批量分析异常: {str(e)}"
                    )
        
        # 并发执行所有分析
        tasks = [analyze_single(symbol) for symbol in symbols]
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        for result in completed_results:
            if isinstance(result, Exception):
                logger.error(f"批量分析时发生异常: {result}")
                continue
            
            symbol, analysis_result = result
            results[symbol] = analysis_result
        
        logger.info(f"批量分析完成，成功分析{len(results)}只股票")
        return results
    
    async def close(self):
        """关闭系统资源"""
        try:
            if self.data_toolkit:
                await self.data_toolkit.close()
            
            logger.info("A股分析系统资源已释放")
            
        except Exception as e:
            logger.error(f"释放系统资源时出错: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "system_name": "AShareAnalysisSystem",
            "version": "1.0.0",
            "initialized": self._initialized,
            "config": {
                "backend_url": self.config.get("backend_url"),
                "ashare_api_url": self.config.get("ashare_api_url"),
                "use_mcp_service": self.config.get("use_mcp_service", False)
            },
            "agents": {
                "financial_agent": self.financial_agent is not None,
                "industry_agent": self.industry_agent is not None,
                "valuation_agent": self.valuation_agent is not None,
                "integration_agent": self.integration_agent is not None
            }
        }

# 工具函数
async def create_analysis_system(config: Dict[str, Any] = None, 
                               debug: bool = False) -> AShareAnalysisSystem:
    """
    创建A股分析系统实例
    
    Args:
        config: 配置字典
        debug: 是否启用调试模式
    
    Returns:
        AShareAnalysisSystem: 分析系统实例
    """
    system = AShareAnalysisSystem(config, debug)
    await system.initialize()
    return system