"""
A股分析工作流图
基于LangGraph实现的Multi-Agent工作流编排
"""

import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from ..agents import (
    FinancialAnalystAgent,
    IndustryAnalystAgent,
    ValuationAnalystAgent,
    ReportIntegrationAgent,
    StockAnalysisState,
)
from ..tools import AStockToolkit, DataCache
from ..config import StockAnalysisConfig

logger = logging.getLogger(__name__)

class StockAnalysisGraph:
    """A股分析工作流图"""
    
    def __init__(self, config: Optional[StockAnalysisConfig] = None):
        """
        初始化工作流图
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or StockAnalysisConfig()
        
        # 初始化LLM
        self._init_llms()
        
        # 初始化工具包
        self._init_toolkit()
        
        # 初始化Agents
        self._init_agents()
        
        # 构建工作流图
        self._build_graph()
        
        # 初始化缓存
        self.cache = DataCache(
            cache_dir=str(self.config.cache_dir),
            default_ttl=self.config.cache_ttl
        )
        
        logger.info("A股分析工作流图初始化完成")
    
    def _init_llms(self):
        """初始化语言模型"""
        if self.config.llm_provider.lower() == "openai":
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config.deep_think_llm,
                base_url=self.config.backend_url,
                api_key=self.config.api_key,
                temperature=0.7,
                max_tokens=4096
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config.quick_think_llm,
                base_url=self.config.backend_url,
                api_key=self.config.api_key,
                temperature=0.5,
                max_tokens=2048
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {self.config.llm_provider}")
        
        logger.info(f"LLM初始化完成: {self.config.llm_provider}")
    
    def _init_toolkit(self):
        """初始化数据工具包"""
        self.toolkit = AStockToolkit(self.config.to_dict())
        logger.info("数据工具包初始化完成")
    
    def _init_agents(self):
        """初始化各个Agent"""
        # 使用快速响应模型的专业分析Agent
        self.financial_agent = FinancialAnalystAgent(
            self.quick_thinking_llm,
            self.toolkit
        )
        self.industry_agent = IndustryAnalystAgent(
            self.quick_thinking_llm,
            self.toolkit
        )
        self.valuation_agent = ValuationAnalystAgent(
            self.quick_thinking_llm,
            self.toolkit
        )
        
        # 使用深度思考模型的报告整合Agent
        self.report_agent = ReportIntegrationAgent(
            self.deep_thinking_llm,
            self.config.to_dict()
        )
        
        logger.info("所有Agent初始化完成")
    
    def _build_graph(self):
        """构建工作流图"""
        # 创建状态图
        workflow = StateGraph(StockAnalysisState)
        
        # 添加节点
        workflow.add_node("data_collection", self.data_collection_node)
        workflow.add_node("financial_analysis", self.financial_analysis_node)
        workflow.add_node("industry_analysis", self.industry_analysis_node)
        workflow.add_node("valuation_analysis", self.valuation_analysis_node)
        workflow.add_node("report_integration", self.report_integration_node)
        
        # 定义工作流
        workflow.add_edge(START, "data_collection")
        
        # 并行分析（三个分析可以同时进行）
        workflow.add_edge("data_collection", "financial_analysis")
        workflow.add_edge("data_collection", "industry_analysis")
        workflow.add_edge("data_collection", "valuation_analysis")
        
        # 汇聚到报告整合
        workflow.add_edge("financial_analysis", "report_integration")
        workflow.add_edge("industry_analysis", "report_integration")
        workflow.add_edge("valuation_analysis", "report_integration")
        
        # 结束
        workflow.add_edge("report_integration", END)
        
        # 编译图
        memory = MemorySaver()
        self.graph = workflow.compile(checkpointer=memory)
        
        logger.info("工作流图构建完成")
    
    def data_collection_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """数据收集节点"""
        stock_code = state.get("stock_code")
        logger.info(f"开始收集 {stock_code} 的基础数据")
        
        try:
            # 获取股票基本信息
            stock_info = self.toolkit.get_stock_info(stock_code)
            company_name = stock_info.get("股票名称", stock_code)
            
            # 初始化分析日期
            analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
            
            return {
                "company_name": company_name,
                "analysis_date": analysis_date,
                "messages": [{"role": "system", "content": f"开始分析 {company_name}({stock_code})"}]
            }
            
        except Exception as e:
            logger.error(f"数据收集失败: {e}")
            return {
                "company_name": stock_code,
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "error_messages": [str(e)]
            }
    
    def financial_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """财务分析节点"""
        start_time = time.time()
        result = self.financial_agent.analyze(state)
        elapsed_time = time.time() - start_time
        logger.info(f"财务分析完成，耗时: {elapsed_time:.2f}秒")
        return result
    
    def industry_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """行业分析节点"""
        start_time = time.time()
        result = self.industry_agent.analyze(state)
        elapsed_time = time.time() - start_time
        logger.info(f"行业分析完成，耗时: {elapsed_time:.2f}秒")
        return result
    
    def valuation_analysis_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """估值分析节点"""
        start_time = time.time()
        result = self.valuation_agent.analyze(state)
        elapsed_time = time.time() - start_time
        logger.info(f"估值分析完成，耗时: {elapsed_time:.2f}秒")
        return result
    
    def report_integration_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """报告整合节点"""
        start_time = time.time()
        result = self.report_agent.generate_report(state)
        elapsed_time = time.time() - start_time
        logger.info(f"报告整合完成，耗时: {elapsed_time:.2f}秒")
        
        # 添加总耗时
        result["analysis_duration"] = elapsed_time
        
        return result
    
    def analyze(
        self,
        stock_code: str,
        analysis_date: Optional[str] = None,
        save_report: bool = True
    ) -> Dict[str, Any]:
        """
        执行股票分析
        
        Args:
            stock_code: 股票代码（6位数字）
            analysis_date: 分析日期，默认为今天
            save_report: 是否保存报告到文件
            
        Returns:
            包含分析结果的字典
        """
        # 记录开始时间
        start_time = time.time()
        
        # 验证股票代码
        if not stock_code or len(stock_code) != 6:
            raise ValueError(f"无效的股票代码: {stock_code}，应为6位数字")
        
        # 初始化状态
        initial_state = {
            "stock_code": stock_code,
            "analysis_date": analysis_date or datetime.now().strftime("%Y-%m-%d"),
            "messages": [],
            "error_messages": [],
        }
        
        logger.info(f"开始分析股票: {stock_code}")
        
        try:
            # 执行工作流
            config = {"configurable": {"thread_id": f"analysis_{stock_code}_{start_time}"}}
            final_state = self.graph.invoke(initial_state, config)
            
            # 计算总耗时
            total_duration = time.time() - start_time
            final_state["analysis_duration"] = total_duration
            
            logger.info(f"股票分析完成: {stock_code}，总耗时: {total_duration:.2f}秒")
            
            # 保存报告
            if save_report and final_state.get("final_report"):
                output_path = self.save_report(final_state)
                final_state["report_path"] = output_path
            
            return final_state
            
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return {
                "stock_code": stock_code,
                "error": str(e),
                "analysis_duration": time.time() - start_time
            }
    
    def save_report(self, state: Dict[str, Any]) -> str:
        """
        保存分析报告
        
        Args:
            state: 包含报告的状态
            
        Returns:
            报告文件路径
        """
        stock_code = state.get("stock_code", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 构建文件路径
        report_dir = self.config.results_dir / stock_code
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"analysis_report_{timestamp}.md"
        
        try:
            # 保存Markdown报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(state.get("final_report", ""))
            
            # 保存元数据
            metadata = {
                "stock_code": stock_code,
                "company_name": state.get("company_name", ""),
                "analysis_date": state.get("analysis_date", ""),
                "analysis_duration": state.get("analysis_duration", 0),
                "investment_rating": state.get("investment_rating", ""),
                "target_price": state.get("target_price", 0),
                "confidence_score": state.get("confidence_score", 0),
                "data_quality_score": state.get("data_quality_score", 0),
                "key_risks": state.get("key_risks", []),
                "key_opportunities": state.get("key_opportunities", []),
            }
            
            metadata_path = report_dir / f"analysis_metadata_{timestamp}.json"
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"报告已保存: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return ""
    
    def batch_analyze(
        self,
        stock_codes: list,
        analysis_date: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            analysis_date: 分析日期
            
        Returns:
            各股票分析结果的字典
        """
        results = {}
        
        for stock_code in stock_codes:
            logger.info(f"批量分析进度: {stock_codes.index(stock_code) + 1}/{len(stock_codes)}")
            
            try:
                result = self.analyze(stock_code, analysis_date)
                results[stock_code] = result
                
                # 避免请求过快
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"分析 {stock_code} 失败: {e}")
                results[stock_code] = {"error": str(e)}
        
        return results
    
    def get_analysis_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取分析摘要
        
        Args:
            state: 分析结果状态
            
        Returns:
            摘要信息字典
        """
        return {
            "股票代码": state.get("stock_code"),
            "公司名称": state.get("company_name"),
            "分析日期": state.get("analysis_date"),
            "投资评级": state.get("investment_rating"),
            "目标价格": state.get("target_price"),
            "财务评分": state.get("financial_score"),
            "行业地位": state.get("industry_position"),
            "估值水平": state.get("valuation_level"),
            "主要风险": state.get("key_risks", []),
            "主要机会": state.get("key_opportunities", []),
            "置信度": state.get("confidence_score"),
            "数据质量": state.get("data_quality_score"),
        }
