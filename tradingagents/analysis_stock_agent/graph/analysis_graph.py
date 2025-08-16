"""
A股分析系统主控制器 - 基于LLM Agent的智能分析框架
使用LangGraph协调4个LLM专业分析Agent的执行流程
"""
import logging
from typing import Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config.analysis_config import get_config
from ..tools.ashare_toolkit import AShareToolkit
from ..agents.financial_analysis_agent import create_financial_analysis_agent
from ..agents.industry_analysis_agent import create_industry_analysis_agent
from ..agents.valuation_analysis_agent import create_valuation_analysis_agent
from ..agents.report_integration_agent import create_report_integration_agent

logger = logging.getLogger(__name__)


class AShareAnalysisSystem:
    """A股分析系统主控制器 - 基于LLM Agent的智能分析框架"""
    
    def __init__(self, config: Dict[str, Any] = None, debug: bool = False):
        """
        初始化A股分析系统
        
        Args:
            config: 配置字典，默认使用分析配置
            debug: 是否启用调试模式
        """
        self.config = config or get_config()
        self.debug = debug
        
        # 初始化LLM
        self._initialize_llms()
        
        # 初始化数据工具集
        self.ashare_toolkit = AShareToolkit(self.config)
        
        # 初始化LLM Agent
        self._initialize_agents()
        
        # 构建分析图
        self.analysis_graph = self._build_analysis_graph()
        
        logger.info("A股LLM分析系统初始化完成")
    
    def _initialize_llms(self):
        """初始化大语言模型"""
        provider = self.config.get("llm_provider", "openai").lower()
        base_url = self.config.get("backend_url")
        
        if provider == "openai" or provider == "ollama" or provider == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config.get("deep_think_llm", "gpt-4o"),
                base_url=base_url
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config.get("quick_think_llm", "gpt-4o-mini"),
                base_url=base_url
            )
        elif provider == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(
                model=self.config.get("deep_think_llm", "claude-3-5-sonnet-20241022"),
                base_url=base_url
            )
            self.quick_thinking_llm = ChatAnthropic(
                model=self.config.get("quick_think_llm", "claude-3-5-haiku-20241022"),
                base_url=base_url
            )
        elif provider == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config.get("deep_think_llm", "gemini-pro")
            )
            self.quick_thinking_llm = ChatGoogleGenerativeAI(
                model=self.config.get("quick_think_llm", "gemini-pro")
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
        
        logger.info(f"LLM初始化完成 - 提供商: {provider}")
    
    def _initialize_agents(self):
        """初始化LLM分析Agent"""
        # 财务分析Agent (使用深度思考LLM)
        self.financial_agent = create_financial_analysis_agent(
            self.deep_thinking_llm, 
            self.ashare_toolkit
        )
        
        # 行业分析Agent (使用深度思考LLM)
        self.industry_agent = create_industry_analysis_agent(
            self.deep_thinking_llm,
            self.ashare_toolkit
        )
        
        # 估值分析Agent (使用深度思考LLM)
        self.valuation_agent = create_valuation_analysis_agent(
            self.deep_thinking_llm,
            self.ashare_toolkit
        )
        
        # 报告整合Agent (使用深度思考LLM)
        self.integration_agent = create_report_integration_agent(
            self.deep_thinking_llm
        )
        
        logger.info("LLM分析Agent初始化完成")
    
    def _build_analysis_graph(self):
        """构建LangGraph分析流程"""
        # 定义状态结构
        class AnalysisState(dict):
            symbol: str
            company_name: str
            analysis_date: str
            financial_analysis_report: str
            industry_analysis_report: str
            valuation_analysis_report: str
            comprehensive_analysis_report: str
            analysis_status: str
        
        # 创建状态图
        workflow = StateGraph(AnalysisState)
        
        # 添加分析节点
        workflow.add_node("financial_analysis", self.financial_agent)
        workflow.add_node("industry_analysis", self.industry_agent)
        workflow.add_node("valuation_analysis", self.valuation_agent)
        workflow.add_node("report_integration", self.integration_agent)
        
        # 定义执行流程
        workflow.set_entry_point("financial_analysis")
        
        # 串行执行专业分析
        workflow.add_edge("financial_analysis", "industry_analysis")
        workflow.add_edge("industry_analysis", "valuation_analysis")
        workflow.add_edge("valuation_analysis", "report_integration")
        workflow.add_edge("report_integration", END)
        
        # 编译图
        return workflow.compile()
    
    async def analyze_stock(self, symbol: str, company_name: str = None) -> Dict[str, Any]:
        """
        对指定股票进行全面分析
        
        Args:
            symbol: 股票代码（6位数字）
            company_name: 公司名称（可选）
        
        Returns:
            分析结果字典
        """
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            raise ValueError("股票代码必须是6位数字")
        
        logger.info(f"开始分析股票: {symbol} ({company_name or ''})")
        
        try:
            # 初始化分析状态
            initial_state = {
                "symbol": symbol,
                "company_name": company_name or symbol,
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "financial_analysis_report": "",
                "industry_analysis_report": "",
                "valuation_analysis_report": "",
                "comprehensive_analysis_report": "",
                "analysis_status": "started"
            }
            
            # 执行分析流程
            final_state = self.analysis_graph.invoke(initial_state)
            
            # 返回分析结果
            return {
                "success": True,
                "symbol": symbol,
                "company_name": company_name,
                "analysis_date": final_state.get("analysis_date"),
                "financial_report": final_state.get("financial_analysis_report", ""),
                "industry_report": final_state.get("industry_analysis_report", ""),
                "valuation_report": final_state.get("valuation_analysis_report", ""),
                "comprehensive_report": final_state.get("comprehensive_analysis_report", ""),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"股票分析失败 {symbol}: {e}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e),
                "status": "failed"
            }
    
    async def close(self):
        """关闭系统资源"""
        if hasattr(self.ashare_toolkit, 'close'):
            await self.ashare_toolkit.close()
        logger.info("A股分析系统资源已关闭")


# 工具函数
async def create_ashare_analysis_system(config: Dict[str, Any] = None, debug: bool = False):
    """创建A股分析系统实例"""
    return AShareAnalysisSystem(config, debug)


# 主入口函数
async def analyze_ashare_stock(symbol: str, company_name: str = None, 
                              config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    快速分析A股股票的便捷函数
    
    Args:
        symbol: 股票代码
        company_name: 公司名称
        config: 配置选项
    
    Returns:
        分析结果
    """
    system = AShareAnalysisSystem(config)
    try:
        return await system.analyze_stock(symbol, company_name)
    finally:
        await system.close()


if __name__ == "__main__":
    # 示例用法
    import asyncio
    
    async def main():
        # 测试分析平安银行
        result = await analyze_ashare_stock("000001", "平安银行")
        
        if result["success"]:
            print("=== 财务分析 ===")
            print(result["financial_report"][:200] + "...")
            print("\n=== 行业分析 ===")
            print(result["industry_report"][:200] + "...")
            print("\n=== 估值分析 ===")
            print(result["valuation_report"][:200] + "...")
            print("\n=== 综合报告 ===")
            print(result["comprehensive_report"][:300] + "...")
        else:
            print(f"分析失败: {result['error']}")
    
    # asyncio.run(main())