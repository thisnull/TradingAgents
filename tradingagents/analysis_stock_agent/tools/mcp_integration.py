"""
MCP服务集成模块
集成A股数据MCP服务，提供17个专业分析工具
"""
import asyncio
import websockets
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..utils.analysis_states import DataSource

logger = logging.getLogger(__name__)

class MCPError(Exception):
    """MCP服务相关错误"""
    pass

class MCPToolkit:
    """MCP服务工具集"""
    
    def __init__(self, config: Dict[str, Any]):
        self.endpoint = config.get('mcp_endpoint')
        self.api_key = config.get('mcp_api_key')
        self.enabled = config.get('use_mcp_service', False)
        self.timeout = config.get('request_timeout', 120)
        
        # 连接状态
        self.websocket = None
        self.is_connected = False
        self.available_tools = {}
        
        # 消息队列
        self.pending_requests = {}
        
    async def connect(self) -> bool:
        """建立MCP连接"""
        if not self.enabled or not self.endpoint:
            logger.info("MCP服务未启用或未配置endpoint")
            return False
        
        try:
            # 准备连接头部
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # 建立WebSocket连接
            self.websocket = await websockets.connect(
                self.endpoint,
                extra_headers=headers,
                ping_interval=30,
                ping_timeout=10
            )
            
            # 执行MCP初始化握手
            await self._initialize_connection()
            
            # 获取可用工具列表
            await self._discover_tools()
            
            self.is_connected = True
            logger.info(f"MCP连接成功，可用工具: {len(self.available_tools)}个")
            return True
            
        except Exception as e:
            logger.error(f"MCP连接失败: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """断开MCP连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.is_connected = False
        logger.info("MCP连接已断开")
    
    async def _initialize_connection(self):
        """执行MCP初始化握手"""
        init_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "analysis_stock_agent",
                    "version": "1.0.0"
                }
            }
        }
        
        await self.websocket.send(json.dumps(init_request))
        response = await self.websocket.recv()
        
        init_response = json.loads(response)
        if 'error' in init_response:
            raise MCPError(f"MCP初始化失败: {init_response['error']}")
        
        logger.debug("MCP初始化成功")
    
    async def _discover_tools(self):
        """发现可用的MCP工具"""
        tools_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list"
        }
        
        await self.websocket.send(json.dumps(tools_request))
        response = await self.websocket.recv()
        
        tools_response = json.loads(response)
        if 'error' in tools_response:
            raise MCPError(f"获取工具列表失败: {tools_response['error']}")
        
        # 解析工具列表
        tools = tools_response.get('result', {}).get('tools', [])
        for tool in tools:
            tool_name = tool.get('name')
            if tool_name:
                self.available_tools[tool_name] = tool
        
        logger.debug(f"发现MCP工具: {list(self.available_tools.keys())}")
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        if not self.is_connected:
            await self.connect()
        
        if tool_name not in self.available_tools:
            raise MCPError(f"工具 {tool_name} 不可用")
        
        request_id = str(uuid.uuid4())
        tool_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            await self.websocket.send(json.dumps(tool_request))
            
            # 等待响应
            response = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=self.timeout
            )
            
            tool_response = json.loads(response)
            
            if 'error' in tool_response:
                raise MCPError(f"工具调用失败: {tool_response['error']}")
            
            return tool_response.get('result', {})
            
        except asyncio.TimeoutError:
            raise MCPError(f"工具调用超时: {tool_name}")
        except Exception as e:
            raise MCPError(f"工具调用异常 {tool_name}: {str(e)}")
    
    # A股分析专用工具方法
    
    async def get_stock_detail(self, symbol: str) -> Dict[str, Any]:
        """获取股票详情 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            result = await self._call_tool('get_stock_detail', {'symbol': symbol})
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP股票详情工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP获取股票详情失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_financial_reports_mcp(self, symbol: str, report_type: str = "annual") -> Dict[str, Any]:
        """获取财务报告 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {
                'symbol': symbol,
                'report_type': report_type,
                'limit': 5
            }
            
            result = await self._call_tool('get_financial_reports', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP财务报告工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP获取财务报告失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def calculate_financial_ratios_mcp(self, symbol: str, year: int = None) -> Dict[str, Any]:
        """计算财务比率 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {'symbol': symbol}
            if year:
                arguments['year'] = year
            
            result = await self._call_tool('calculate_financial_ratios', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP财务比率工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP计算财务比率失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_financial_summary_mcp(self, symbols: List[str]) -> Dict[str, Any]:
        """获取财务摘要 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {
                'symbols': symbols,
                'limit': 20
            }
            
            result = await self._call_tool('get_financial_summary', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP财务摘要工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP获取财务摘要失败 {symbols}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_daily_quotes_mcp(self, symbol: str, start_date: str = None, 
                                 end_date: str = None) -> Dict[str, Any]:
        """获取日线行情 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {
                'symbol': symbol,
                'limit': 20
            }
            if start_date:
                arguments['start_date'] = start_date
            if end_date:
                arguments['end_date'] = end_date
            
            result = await self._call_tool('get_daily_quotes', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP日线行情工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP获取日线行情失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def calculate_technical_indicators_mcp(self, symbol: str, 
                                               indicator: str = "ma",
                                               period: int = 20) -> Dict[str, Any]:
        """计算技术指标 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {
                'symbol': symbol,
                'indicator': indicator,
                'period': period
            }
            
            result = await self._call_tool('calculate_technical_indicators', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP技术指标工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP计算技术指标失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_market_trend_mcp(self, symbol: str, period: str = "1m") -> Dict[str, Any]:
        """分析市场趋势 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {
                'symbol': symbol,
                'period': period,
                'indicators': ['trend', 'volatility']
            }
            
            result = await self._call_tool('analyze_market_trend', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP市场趋势工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP分析市场趋势失败 {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_indices_mcp(self, index_codes: List[str] = None) -> Dict[str, Any]:
        """获取指数信息 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {}
            if index_codes:
                arguments['index_codes'] = index_codes
            
            result = await self._call_tool('get_indices', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP指数信息工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP获取指数信息失败: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_index_constituents_mcp(self, index_code: str) -> Dict[str, Any]:
        """获取指数成分股 (MCP工具)"""
        if not self.enabled:
            return {'success': False, 'message': 'MCP服务未启用'}
        
        try:
            arguments = {
                'index_code': index_code,
                'limit': 50
            }
            
            result = await self._call_tool('get_index_constituents', arguments)
            
            return {
                'success': True,
                'data': result.get('content', [{}])[0].get('text', ''),
                'data_source': DataSource(
                    name="MCP指数成分股工具",
                    endpoint=self.endpoint,
                    version="2024-11-05"
                )
            }
        except Exception as e:
            logger.error(f"MCP获取指数成分股失败 {index_code}: {e}")
            return {'success': False, 'error': str(e)}
    
    def is_available(self) -> bool:
        """检查MCP服务是否可用"""
        return self.enabled and self.is_connected
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return list(self.available_tools.keys())

# 工具函数
async def create_mcp_toolkit(config: Dict[str, Any]) -> MCPToolkit:
    """创建MCP工具集实例"""
    toolkit = MCPToolkit(config)
    
    # 尝试连接，如果失败也不抛出异常
    try:
        await toolkit.connect()
    except Exception as e:
        logger.warning(f"MCP连接失败，将使用备选数据源: {e}")
    
    return toolkit

# 统一数据获取接口
class UnifiedDataToolkit:
    """统一数据工具集 - 结合A股API和MCP服务"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ashare_toolkit = None
        self.mcp_toolkit = None
        
    async def initialize(self):
        """初始化工具集"""
        from .ashare_toolkit import create_ashare_toolkit
        
        # 初始化A股API工具集 (主要数据源)
        self.ashare_toolkit = await create_ashare_toolkit(self.config)
        
        # 初始化MCP工具集 (可选数据源)
        self.mcp_toolkit = await create_mcp_toolkit(self.config)
    
    async def close(self):
        """关闭所有连接"""
        if self.ashare_toolkit:
            await self.ashare_toolkit.close()
        if self.mcp_toolkit:
            await self.mcp_toolkit.disconnect()
    
    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        """获取股票的综合数据 (结合多个数据源)"""
        results = {}
        
        # 从A股API获取数据 (主要)
        try:
            results['basic_info'] = await self.ashare_toolkit.get_stock_basic_info(symbol)
            results['financial_reports'] = await self.ashare_toolkit.get_financial_reports(symbol)
            results['financial_ratios'] = await self.ashare_toolkit.get_financial_ratios(symbol)
            results['daily_quotes'] = await self.ashare_toolkit.get_daily_quotes(symbol, limit=30)
        except Exception as e:
            logger.error(f"A股API获取数据失败: {e}")
        
        # 从MCP服务获取补充数据 (可选)
        if self.mcp_toolkit and self.mcp_toolkit.is_available():
            try:
                results['mcp_stock_detail'] = await self.mcp_toolkit.get_stock_detail(symbol)
                results['mcp_technical_indicators'] = await self.mcp_toolkit.calculate_technical_indicators_mcp(symbol)
            except Exception as e:
                logger.warning(f"MCP服务获取数据失败: {e}")
        
        return results