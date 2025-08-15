"""
A股数据API工具集
集成A股数据同步服务API，提供财务数据获取能力
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
from ..utils.data_validator import DataFormatter, DataQualityChecker
from ..utils.analysis_states import DataSource

logger = logging.getLogger(__name__)

class AShareAPIError(Exception):
    """A股API相关错误"""
    pass

class AShareToolkit:
    """A股数据API工具集"""
    
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('ashare_api_url', 'http://localhost:8000/api/v1')
        self.timeout = config.get('request_timeout', 120)
        self.max_retries = config.get('max_retry_attempts', 3)
        self.cache_ttl = config.get('ashare_cache_ttl', 3600)
        
        # 创建HTTP会话
        self.session = None
        self._session_created = False
        
    async def _ensure_session(self):
        """确保HTTP会话已创建"""
        if not self._session_created:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            self._session_created = True
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self._session_created = False
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发起API请求"""
        await self._ensure_session()
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 检查API响应格式
                        if not data.get('success', False):
                            error_msg = data.get('message', '未知API错误')
                            raise AShareAPIError(f"API返回错误: {error_msg}")
                        
                        return data
                    else:
                        error_text = await response.text()
                        raise AShareAPIError(f"HTTP {response.status}: {error_text}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"请求超时，第{attempt + 1}次尝试: {url}")
                if attempt == self.max_retries - 1:
                    raise AShareAPIError(f"请求超时，已重试{self.max_retries}次")
                await asyncio.sleep(2 ** attempt)  # 指数退避
                
            except aiohttp.ClientError as e:
                logger.warning(f"网络错误，第{attempt + 1}次尝试: {e}")
                if attempt == self.max_retries - 1:
                    raise AShareAPIError(f"网络错误: {str(e)}")
                await asyncio.sleep(2 ** attempt)
    
    async def get_stock_basic_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基础信息"""
        try:
            endpoint = f"/market/{symbol}"
            response = await self._make_request(endpoint)
            
            if 'data' in response:
                # 清理和格式化数据
                raw_data = response['data']
                cleaned_data = {
                    'symbol': raw_data.get('symbol'),
                    'name': raw_data.get('name'),
                    'market': raw_data.get('market'),
                    'exchange': raw_data.get('exchange'),
                    'industry': raw_data.get('industry'),
                    'listing_date': raw_data.get('listing_date'),
                    'total_shares': raw_data.get('total_shares'),
                    'float_shares': raw_data.get('float_shares'),
                    'status': raw_data.get('status'),
                    'data_source': raw_data.get('data_source', 'ashare_api'),
                    'last_sync': raw_data.get('last_sync')
                }
                
                return {
                    'success': True,
                    'data': cleaned_data,
                    'data_source': DataSource(
                        name="A股数据API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                raise AShareAPIError("API响应中缺少data字段")
                
        except Exception as e:
            logger.error(f"获取股票基础信息失败 {symbol}: {e}")
            raise AShareAPIError(f"获取股票基础信息失败: {str(e)}")
    
    async def get_financial_reports(self, symbol: str, report_type: str = "A", 
                                  start_date: str = None, end_date: str = None,
                                  limit: int = 5) -> Dict[str, Any]:
        """获取财务报表数据"""
        try:
            endpoint = "/financial/reports"
            params = {
                'symbols': symbol,
                'limit': limit
            }
            
            if report_type:
                params['report_type'] = report_type
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = await self._make_request(endpoint, params)
            
            if 'data' in response:
                reports = response['data']
                
                # 处理和验证财务数据
                processed_reports = []
                for report in reports:
                    cleaned_report = DataFormatter.clean_financial_data(report)
                    
                    # 计算数据质量评分
                    quality_score = DataQualityChecker.calculate_data_quality_score(cleaned_report)
                    cleaned_report['data_quality_score'] = quality_score
                    
                    processed_reports.append(cleaned_report)
                
                return {
                    'success': True,
                    'data': processed_reports,
                    'total_count': response.get('pagination', {}).get('total', len(processed_reports)),
                    'data_source': DataSource(
                        name="A股财务报表API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                raise AShareAPIError("API响应中缺少data字段")
                
        except Exception as e:
            logger.error(f"获取财务报表失败 {symbol}: {e}")
            raise AShareAPIError(f"获取财务报表失败: {str(e)}")
    
    async def get_latest_financial_reports(self, symbols: List[str], 
                                         report_type: str = "A") -> Dict[str, Any]:
        """获取最新财务报表"""
        try:
            endpoint = "/financial/reports/latest"
            params = {
                'symbols': ','.join(symbols) if isinstance(symbols, list) else symbols,
                'report_type': report_type,
                'limit': 100
            }
            
            response = await self._make_request(endpoint, params)
            
            if 'data' in response:
                reports = response['data']
                
                # 按股票代码分组处理
                grouped_reports = {}
                for report in reports:
                    symbol = report.get('symbol')
                    if symbol:
                        cleaned_report = DataFormatter.clean_financial_data(report)
                        quality_score = DataQualityChecker.calculate_data_quality_score(cleaned_report)
                        cleaned_report['data_quality_score'] = quality_score
                        grouped_reports[symbol] = cleaned_report
                
                return {
                    'success': True,
                    'data': grouped_reports,
                    'data_source': DataSource(
                        name="A股最新财报API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                raise AShareAPIError("API响应中缺少data字段")
                
        except Exception as e:
            logger.error(f"获取最新财务报表失败 {symbols}: {e}")
            raise AShareAPIError(f"获取最新财务报表失败: {str(e)}")
    
    async def get_financial_ratios(self, symbol: str, 
                                 report_date: str = None) -> Dict[str, Any]:
        """获取财务比率数据"""
        try:
            endpoint = "/financial/ratios"
            params = {'symbols': symbol}
            
            if report_date:
                params['report_date'] = report_date
            
            response = await self._make_request(endpoint, params)
            
            if 'data' in response and response['data']:
                # 取第一条记录 (最新的)
                ratio_data = response['data'][0] if response['data'] else {}
                
                # 清理和验证比率数据
                cleaned_ratios = {
                    'symbol': ratio_data.get('symbol'),
                    'report_date': ratio_data.get('report_date'),
                    'gross_profit_margin': ratio_data.get('gross_profit_margin'),
                    'net_profit_margin': ratio_data.get('net_profit_margin'),
                    'roe': ratio_data.get('roe'),
                    'roa': ratio_data.get('roa'),
                    'debt_to_asset_ratio': ratio_data.get('debt_to_asset_ratio'),
                    'current_ratio': ratio_data.get('current_ratio'),
                    'quick_ratio': ratio_data.get('quick_ratio'),
                    'eps': ratio_data.get('eps'),
                    'bps': ratio_data.get('bps'),
                    'ocfps': ratio_data.get('ocfps')
                }
                
                return {
                    'success': True,
                    'data': cleaned_ratios,
                    'data_source': DataSource(
                        name="A股财务比率API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                # 如果没有数据，返回空结果而不是错误
                return {
                    'success': True,
                    'data': {},
                    'message': f"暂无{symbol}的财务比率数据",
                    'data_source': DataSource(
                        name="A股财务比率API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
                
        except Exception as e:
            logger.error(f"获取财务比率失败 {symbol}: {e}")
            raise AShareAPIError(f"获取财务比率失败: {str(e)}")
    
    async def get_financial_summary(self, symbol: str, years: int = 3) -> Dict[str, Any]:
        """获取财务摘要信息"""
        try:
            endpoint = f"/financial/summary/{symbol}"
            params = {'years': years}
            
            response = await self._make_request(endpoint, params)
            
            if 'data' in response:
                summary_data = response['data']
                
                return {
                    'success': True,
                    'data': summary_data,
                    'data_source': DataSource(
                        name="A股财务摘要API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                raise AShareAPIError("API响应中缺少data字段")
                
        except Exception as e:
            logger.error(f"获取财务摘要失败 {symbol}: {e}")
            raise AShareAPIError(f"获取财务摘要失败: {str(e)}")
    
    async def get_daily_quotes(self, symbol: str, start_date: str = None, 
                             end_date: str = None, limit: int = 100) -> Dict[str, Any]:
        """获取日线行情数据"""
        try:
            endpoint = "/market/quotes/daily"
            params = {
                'symbols': symbol,
                'limit': limit
            }
            
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = await self._make_request(endpoint, params)
            
            if 'data' in response:
                quotes_data = response['data']
                
                return {
                    'success': True,
                    'data': quotes_data,
                    'total_count': response.get('pagination', {}).get('total', len(quotes_data)),
                    'data_source': DataSource(
                        name="A股行情数据API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                # 行情数据可能为空，这是正常情况
                return {
                    'success': True,
                    'data': [],
                    'message': f"暂无{symbol}的行情数据",
                    'data_source': DataSource(
                        name="A股行情数据API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
                
        except Exception as e:
            logger.error(f"获取行情数据失败 {symbol}: {e}")
            raise AShareAPIError(f"获取行情数据失败: {str(e)}")
    
    async def get_industry_stocks(self, industry: str, limit: int = 20) -> Dict[str, Any]:
        """获取同行业股票列表"""
        try:
            endpoint = "/market/basic"
            params = {
                'limit': limit,
                'offset': 0
            }
            
            response = await self._make_request(endpoint, params)
            
            if 'data' in response:
                all_stocks = response['data']
                
                # 筛选同行业股票
                industry_stocks = []
                for stock in all_stocks:
                    if stock.get('industry') and industry in stock.get('industry', ''):
                        industry_stocks.append({
                            'symbol': stock.get('symbol'),
                            'name': stock.get('name'),
                            'industry': stock.get('industry'),
                            'market': stock.get('market'),
                            'total_shares': stock.get('total_shares')
                        })
                
                return {
                    'success': True,
                    'data': industry_stocks[:limit],  # 限制返回数量
                    'total_count': len(industry_stocks),
                    'data_source': DataSource(
                        name="A股股票列表API",
                        endpoint=endpoint,
                        version="v1.1.0"
                    )
                }
            else:
                raise AShareAPIError("API响应中缺少data字段")
                
        except Exception as e:
            logger.error(f"获取行业股票列表失败 {industry}: {e}")
            raise AShareAPIError(f"获取行业股票列表失败: {str(e)}")
    
    async def batch_get_financial_ratios(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """批量获取财务比率"""
        results = {}
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(5)  # 最多5个并发请求
        
        async def get_single_ratio(symbol: str):
            async with semaphore:
                try:
                    result = await self.get_financial_ratios(symbol)
                    return symbol, result
                except Exception as e:
                    logger.warning(f"获取{symbol}财务比率失败: {e}")
                    return symbol, {'success': False, 'error': str(e)}
        
        # 并发执行所有请求
        tasks = [get_single_ratio(symbol) for symbol in symbols]
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        for result in completed_results:
            if isinstance(result, Exception):
                logger.error(f"批量获取财务比率时发生异常: {result}")
                continue
            
            symbol, data = result
            if data.get('success'):
                results[symbol] = data.get('data', {})
            else:
                results[symbol] = {}
        
        return results
    
    async def initialize_stock_data(self, symbol: str, start_date: str = None,
                                  end_date: str = None, force_update: bool = False) -> Dict[str, Any]:
        """初始化股票数据"""
        try:
            endpoint = f"/initialization/stocks/{symbol}/initialize"
            
            # 准备请求数据
            request_data = {
                'symbol': symbol,
                'start_date': start_date or '1970-01-01',
                'end_date': end_date or datetime.now().strftime('%Y-%m-%d'),
                'force_update': force_update
            }
            
            async with self.session.post(f"{self.base_url}{endpoint}", 
                                       json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'success': True,
                        'data': data,
                        'data_source': DataSource(
                            name="A股数据初始化API",
                            endpoint=endpoint,
                            version="v1.1.0"
                        )
                    }
                else:
                    error_text = await response.text()
                    raise AShareAPIError(f"初始化失败 HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"初始化股票数据失败 {symbol}: {e}")
            raise AShareAPIError(f"初始化股票数据失败: {str(e)}")
    
    async def get_initialization_status(self, request_id: str) -> Dict[str, Any]:
        """查询数据初始化状态"""
        try:
            endpoint = f"/initialization/status/{request_id}"
            response = await self._make_request(endpoint)
            
            return {
                'success': True,
                'data': response,
                'data_source': DataSource(
                    name="A股数据初始化状态API",
                    endpoint=endpoint,
                    version="v1.1.0"
                )
            }
                
        except Exception as e:
            logger.error(f"查询初始化状态失败 {request_id}: {e}")
            raise AShareAPIError(f"查询初始化状态失败: {str(e)}")

# 工具函数
async def create_ashare_toolkit(config: Dict[str, Any]) -> AShareToolkit:
    """创建A股数据工具集实例"""
    toolkit = AShareToolkit(config)
    await toolkit._ensure_session()
    return toolkit