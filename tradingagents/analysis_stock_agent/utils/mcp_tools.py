"""
MCP服务工具集成模块

提供与A股数据MCP服务的集成，利用21个专业金融数据工具进行深度分析。
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


logger = logging.getLogger(__name__)


class MCPFinancialTools:
    """MCP金融工具集成类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mcp_url = config.get("mcp_service_url", "ws://localhost:8001")
        self.mcp_key = config.get("mcp_service_key", "")
        self.timeout = config.get("mcp_timeout", 30)
        self.enabled = config.get("mcp_tools_enabled", True)
        
        self.websocket = None
        self.request_id = 0
        
    async def connect(self) -> bool:
        """
        连接到MCP服务
        
        Returns:
            连接是否成功
        """
        if not self.enabled:
            logger.info("MCP tools are disabled")
            return False
            
        try:
            headers = {}
            if self.mcp_key:
                headers["Authorization"] = f"Bearer {self.mcp_key}"
                
            self.websocket = await websockets.connect(
                self.mcp_url,
                extra_headers=headers,
                timeout=self.timeout
            )
            
            # 发送初始化消息
            init_message = {
                "jsonrpc": "2.0",
                "id": self._get_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "a-share-analysis-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            await self.websocket.send(json.dumps(init_message))
            response = await self.websocket.recv()
            result = json.loads(response)
            
            if "error" not in result:
                logger.info("Successfully connected to MCP service")
                return True
            else:
                logger.error(f"MCP initialization failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP service: {str(e)}")
            return False
    
    async def disconnect(self):
        """断开MCP连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
    
    def _get_request_id(self) -> int:
        """获取请求ID"""
        self.request_id += 1
        return self.request_id
    
    async def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.websocket:
            raise Exception("MCP service not connected")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        try:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            result = json.loads(response)
            
            if "error" in result:
                logger.error(f"MCP tool call failed: {result['error']}")
                return {}
            
            return result.get("result", {})
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            return {}
    
    async def get_stock_detail(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票详细信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票详细信息
        """
        return await self._call_tool("get_stock_detail", {"symbol": symbol})
    
    async def get_financial_reports(self, symbol: str, 
                                  report_type: str = "annual",
                                  year: Optional[int] = None,
                                  limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取财务报告
        
        Args:
            symbol: 股票代码
            report_type: 报告类型
            year: 年度
            limit: 返回数量
            
        Returns:
            财务报告列表
        """
        params = {
            "symbol": symbol,
            "report_type": report_type,
            "limit": limit
        }
        if year:
            params["year"] = year
            
        result = await self._call_tool("get_financial_reports", params)
        return result.get("data", [])
    
    async def get_latest_financial_reports(self, symbols: List[str],
                                         report_type: str = "A") -> List[Dict[str, Any]]:
        """
        获取最新财务报告
        
        Args:
            symbols: 股票代码列表
            report_type: 报告类型
            
        Returns:
            最新财务报告列表
        """
        params = {
            "symbols": symbols,
            "report_type": report_type
        }
        
        result = await self._call_tool("get_latest_financial_reports", params)
        return result.get("data", [])
    
    async def calculate_financial_ratios(self, symbol: str, 
                                       year: Optional[int] = None,
                                       ratios: Optional[List[str]] = None) -> Dict[str, float]:
        """
        计算财务比率
        
        Args:
            symbol: 股票代码
            year: 计算年度
            ratios: 指定比率类型
            
        Returns:
            财务比率字典
        """
        params = {"symbol": symbol}
        if year:
            params["year"] = year
        if ratios:
            params["ratios"] = ratios
            
        result = await self._call_tool("calculate_financial_ratios", params)
        return result.get("ratios", {})
    
    async def get_daily_quotes(self, symbol: str,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取日线行情数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量
            
        Returns:
            日线行情列表
        """
        params = {
            "symbol": symbol,
            "limit": limit
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        result = await self._call_tool("get_daily_quotes", params)
        return result.get("data", [])
    
    async def calculate_technical_indicators(self, symbol: str,
                                           indicator: str,
                                           period: int = 20,
                                           start_date: Optional[str] = None,
                                           end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        计算技术指标
        
        Args:
            symbol: 股票代码
            indicator: 指标类型 (ma/ema/rsi/macd/bollinger)
            period: 计算周期
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            技术指标数据
        """
        params = {
            "symbol": symbol,
            "indicator": indicator,
            "period": period
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        result = await self._call_tool("calculate_technical_indicators", params)
        return result.get("data", {})
    
    async def get_sw_industry_info(self, level: int,
                                 industry_codes: Optional[List[str]] = None,
                                 status: str = "active") -> List[Dict[str, Any]]:
        """
        获取申万行业信息
        
        Args:
            level: 行业级别
            industry_codes: 行业代码列表
            status: 状态筛选
            
        Returns:
            申万行业信息列表
        """
        params = {
            "level": level,
            "status": status
        }
        if industry_codes:
            params["industry_codes"] = industry_codes
            
        result = await self._call_tool("get_sw_industry_info", params)
        return result.get("data", [])
    
    async def get_sw_industry_constituents(self, industry_codes: List[str],
                                         levels: Optional[List[int]] = None,
                                         status: str = "active") -> List[Dict[str, Any]]:
        """
        获取申万行业成分股
        
        Args:
            industry_codes: 行业代码列表
            levels: 行业级别列表
            status: 状态筛选
            
        Returns:
            行业成分股列表
        """
        params = {
            "industry_codes": industry_codes,
            "status": status
        }
        if levels:
            params["levels"] = levels
            
        result = await self._call_tool("get_sw_industry_constituents", params)
        return result.get("data", [])
    
    async def get_stock_industry_hierarchy(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票行业层级
        
        Args:
            symbol: 股票代码
            
        Returns:
            行业层级信息
        """
        result = await self._call_tool("get_stock_industry_hierarchy", {"symbol": symbol})
        return result.get("data", {})
    
    async def analyze_industry_constituents(self, industry_codes: Optional[List[str]] = None,
                                          levels: Optional[List[int]] = None,
                                          analysis_type: str = "summary") -> Dict[str, Any]:
        """
        分析行业成分股
        
        Args:
            industry_codes: 行业代码列表
            levels: 行业级别列表
            analysis_type: 分析类型
            
        Returns:
            行业成分股分析结果
        """
        params = {"analysis_type": analysis_type}
        if industry_codes:
            params["industry_codes"] = industry_codes
        if levels:
            params["levels"] = levels
            
        result = await self._call_tool("analyze_industry_constituents", params)
        return result.get("data", {})
    
    async def get_indices(self, index_codes: Optional[List[str]] = None,
                         market_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取指数信息
        
        Args:
            index_codes: 指数代码列表
            market_type: 市场类型
            
        Returns:
            指数信息列表
        """
        params = {}
        if index_codes:
            params["index_codes"] = index_codes
        if market_type:
            params["market_type"] = market_type
            
        result = await self._call_tool("get_indices", params)
        return result.get("data", [])
    
    async def get_index_constituents(self, index_code: str) -> List[Dict[str, Any]]:
        """
        获取指数成分股
        
        Args:
            index_code: 指数代码
            
        Returns:
            成分股列表
        """
        result = await self._call_tool("get_index_constituents", {"index_code": index_code})
        return result.get("data", [])
    
    async def analyze_market_trend(self, symbol: str,
                                 period: str = "1m",
                                 indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        分析市场趋势
        
        Args:
            symbol: 股票代码或指数代码
            period: 分析周期
            indicators: 分析维度
            
        Returns:
            市场趋势分析结果
        """
        params = {
            "symbol": symbol,
            "period": period
        }
        if indicators:
            params["indicators"] = indicators
            
        result = await self._call_tool("analyze_market_trend", params)
        return result.get("data", {})


class MCPToolsWrapper:
    """MCP工具同步包装器，用于在非异步环境中使用"""
    
    def __init__(self, config: Dict[str, Any]):
        self.mcp_tools = MCPFinancialTools(config)
        self.loop = None
        
    def _run_async(self, coro):
        """运行异步函数"""
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果在已运行的循环中，创建新的任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 如果没有事件循环，创建新的
            return asyncio.run(coro)
    
    async def _connect_and_execute(self, coro):
        """连接并执行异步操作"""
        try:
            await self.mcp_tools.connect()
            result = await coro
            return result
        finally:
            await self.mcp_tools.disconnect()
    
    def get_stock_detail(self, symbol: str) -> Dict[str, Any]:
        """同步获取股票详细信息"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.get_stock_detail(symbol))
        )
    
    def get_financial_reports(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        """同步获取财务报告"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.get_financial_reports(symbol, **kwargs))
        )
    
    def calculate_financial_ratios(self, symbol: str, **kwargs) -> Dict[str, float]:
        """同步计算财务比率"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.calculate_financial_ratios(symbol, **kwargs))
        )
    
    def get_daily_quotes(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        """同步获取日线行情"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.get_daily_quotes(symbol, **kwargs))
        )
    
    def calculate_technical_indicators(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """同步计算技术指标"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.calculate_technical_indicators(symbol, **kwargs))
        )
    
    def get_industry_info(self, level: int, **kwargs) -> List[Dict[str, Any]]:
        """同步获取行业信息"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.get_sw_industry_info(level, **kwargs))
        )
    
    def get_industry_constituents(self, industry_codes: List[str], **kwargs) -> List[Dict[str, Any]]:
        """同步获取行业成分股"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.get_sw_industry_constituents(industry_codes, **kwargs))
        )
    
    def get_stock_industry_hierarchy(self, symbol: str) -> Dict[str, Any]:
        """同步获取股票行业层级"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.get_stock_industry_hierarchy(symbol))
        )
    
    def analyze_market_trend(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """同步分析市场趋势"""
        return self._run_async(
            self._connect_and_execute(self.mcp_tools.analyze_market_trend(symbol, **kwargs))
        )