# A股分析Multi-Agent系统技术设计规范

## 🎯 技术设计概述

### 设计目标
构建一个高可靠、高性能、易扩展的A股公司投资价值分析系统，基于TradingAgents成熟架构，集成A股数据API和MCP服务。

### 技术原则
- **模块化设计**：组件间低耦合，高内聚
- **异步优先**：提升系统响应性能
- **数据驱动**：所有分析基于真实数据
- **可观测性**：完整的日志和监控机制

---

## 🏗️ 核心技术架构

### 1. 技术栈选择

#### 核心框架
```python
# 基础依赖
- Python 3.13+
- LangChain 0.2+
- LangGraph 0.2+
- FastAPI 0.100+ (用于API接口)
- Pydantic 2.0+ (数据验证)
- asyncio (异步处理)

# 数据处理
- pandas 2.0+ (数据分析)
- numpy 1.24+ (数值计算)
- aiohttp 3.8+ (异步HTTP客户端)

# 存储和缓存
- Redis 7.0+ (缓存)
- SQLite 3.40+ (本地存储)

# 监控和日志
- structlog (结构化日志)
- prometheus-client (监控指标)
```

#### LLM集成
```python
# 支持的LLM提供商
- OpenAI GPT-4o/GPT-4o-mini
- 自定义OpenAPI endpoint (https://oned.lvtu.in)
- Ollama本地模型 (http://localhost:10000)
- Anthropic Claude (可选)
```

### 2. 系统架构分层

#### Layer 1: 接口层 (Interface Layer)
```python
# API接口设计
@router.post("/analyze/stock/{symbol}")
async def analyze_stock(
    symbol: str,
    config: Optional[AnalysisConfig] = None
) -> AnalysisResult:
    """分析单只股票的投资价值"""
    
@router.post("/analyze/batch")
async def batch_analyze(
    symbols: list[str],
    config: Optional[AnalysisConfig] = None
) -> list[AnalysisResult]:
    """批量分析多只股票"""

@router.get("/analysis/history/{symbol}")
async def get_analysis_history(symbol: str) -> list[AnalysisResult]:
    """获取历史分析记录"""
```

#### Layer 2: 业务逻辑层 (Business Logic Layer)
```python
# 核心服务组件
class AnalysisService:
    def __init__(self, config: AnalysisConfig):
        self.financial_agent = FinancialAnalysisAgent(config)
        self.industry_agent = IndustryAnalysisAgent(config)
        self.valuation_agent = ValuationAnalysisAgent(config)
        self.integration_agent = ReportIntegrationAgent(config)
        
    async def execute_analysis(self, symbol: str) -> AnalysisResult:
        # 工作流编排逻辑
        pass
```

#### Layer 3: Agent层 (Agent Layer)
```python
# Agent基类设计
class BaseAnalysisAgent:
    def __init__(self, llm, tools, memory):
        self.llm = llm
        self.tools = tools
        self.memory = memory
        
    async def analyze(self, state: AnalysisState) -> AnalysisState:
        # 标准分析流程
        pass
        
    def validate_input(self, state: AnalysisState) -> bool:
        # 输入验证
        pass
        
    def format_output(self, result: dict) -> str:
        # 输出格式化
        pass
```

#### Layer 4: 数据层 (Data Layer)
```python
# 数据访问接口
class DataAccessLayer:
    def __init__(self):
        self.ashare_client = AShareAPIClient()
        self.mcp_client = MCPClient()
        self.cache = RedisCache()
        
    async def get_financial_data(self, symbol: str) -> dict:
        # 数据获取和缓存逻辑
        pass
```

---

## 🔧 详细组件设计

### 1. 状态管理设计

#### AnalysisState结构
```python
from typing import Annotated, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AnalysisState(BaseModel):
    """分析状态的完整定义"""
    
    # 基础信息
    stock_symbol: str = Field(..., description="6位股票代码")
    company_name: Optional[str] = Field(None, description="公司名称")
    analysis_date: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(..., description="请求唯一标识")
    
    # 数据状态
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    processed_data: Dict[str, Any] = Field(default_factory=dict)
    
    # 分析状态
    financial_analysis: Optional['FinancialAnalysisResult'] = None
    industry_analysis: Optional['IndustryAnalysisResult'] = None
    valuation_analysis: Optional['ValuationAnalysisResult'] = None
    
    # 评分结果
    financial_score: Optional[float] = Field(None, ge=0, le=10)
    competition_score: Optional[float] = Field(None, ge=0, le=10)
    valuation_score: Optional[float] = Field(None, ge=0, le=10)
    comprehensive_score: Optional[float] = Field(None, ge=0, le=10)
    
    # 最终输出
    final_report: Optional[str] = None
    investment_recommendation: Optional[str] = None
    target_price: Optional[float] = Field(None, gt=0)
    
    # 元数据
    data_sources: List[str] = Field(default_factory=list)
    processing_time: Optional[float] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
```

#### 子状态定义
```python
class FinancialAnalysisResult(BaseModel):
    """财务分析结果"""
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None
    roe_current: Optional[float] = None
    roe_trend: Optional[str] = None
    debt_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    cash_flow_score: Optional[float] = None
    dividend_yield: Optional[float] = None
    financial_health_rating: Optional[str] = None
    key_insights: List[str] = Field(default_factory=list)

class IndustryAnalysisResult(BaseModel):
    """行业分析结果"""
    industry_name: Optional[str] = None
    industry_growth_rate: Optional[float] = None
    market_position: Optional[int] = None
    peer_comparison: Dict[str, float] = Field(default_factory=dict)
    competitive_advantages: List[str] = Field(default_factory=list)
    market_share: Optional[float] = None
    industry_outlook: Optional[str] = None

class ValuationAnalysisResult(BaseModel):
    """估值分析结果"""
    current_pe: Optional[float] = None
    current_pb: Optional[float] = None
    pr_ratio: Optional[float] = None
    valuation_level: Optional[str] = None
    technical_signals: Dict[str, str] = Field(default_factory=dict)
    ownership_changes: List[Dict] = Field(default_factory=list)
    market_sentiment: Optional[str] = None
```

### 2. Agent详细设计

#### 财务分析Agent
```python
class FinancialAnalysisAgent:
    """核心财务指标分析Agent"""
    
    def __init__(self, llm, toolkit, config):
        self.llm = llm
        self.toolkit = toolkit
        self.config = config
        self.prompt_template = self._load_financial_prompt()
    
    async def analyze(self, state: AnalysisState) -> AnalysisState:
        """执行财务分析"""
        try:
            # 1. 数据收集
            financial_data = await self._collect_financial_data(state.stock_symbol)
            
            # 2. 数据处理
            processed_data = self._process_financial_data(financial_data)
            
            # 3. LLM分析
            analysis_result = await self._llm_analysis(processed_data)
            
            # 4. 结果验证和评分
            validated_result = self._validate_and_score(analysis_result)
            
            # 5. 更新状态
            state.financial_analysis = validated_result
            state.financial_score = validated_result.financial_health_rating
            state.data_sources.extend(self._get_data_sources())
            
            return state
            
        except Exception as e:
            state.errors.append(f"财务分析失败: {str(e)}")
            return state
    
    async def _collect_financial_data(self, symbol: str) -> dict:
        """收集财务数据"""
        data = {}
        
        # 从A股API获取财务报表
        financial_reports = await self.toolkit.get_financial_reports(symbol)
        data['financial_reports'] = financial_reports
        
        # 获取财务比率
        financial_ratios = await self.toolkit.get_financial_ratios(symbol)
        data['financial_ratios'] = financial_ratios
        
        # 获取最新财务摘要
        financial_summary = await self.toolkit.get_financial_summary([symbol])
        data['financial_summary'] = financial_summary
        
        return data
    
    def _process_financial_data(self, raw_data: dict) -> dict:
        """处理和清洗财务数据"""
        processed = {}
        
        # 计算增长率
        if 'financial_reports' in raw_data:
            processed['growth_metrics'] = self._calculate_growth_metrics(
                raw_data['financial_reports']
            )
        
        # 计算健康度指标
        if 'financial_ratios' in raw_data:
            processed['health_metrics'] = self._calculate_health_metrics(
                raw_data['financial_ratios']
            )
        
        return processed
    
    async def _llm_analysis(self, data: dict) -> FinancialAnalysisResult:
        """使用LLM进行深度分析"""
        prompt = self.prompt_template.format(
            financial_data=data,
            analysis_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        response = await self.llm.ainvoke([("human", prompt)])
        
        # 解析LLM输出为结构化结果
        return self._parse_llm_output(response.content)
    
    def _validate_and_score(self, result: FinancialAnalysisResult) -> FinancialAnalysisResult:
        """验证分析结果并计算评分"""
        # 数据合理性检查
        if result.roe_current and result.roe_current > 100:
            result.warnings.append("ROE异常高，请核实数据")
        
        # 计算综合财务健康评分
        score = self._calculate_financial_score(result)
        result.financial_health_rating = score
        
        return result
```

#### 行业分析Agent
```python
class IndustryAnalysisAgent:
    """行业对比与竞争优势分析Agent"""
    
    async def analyze(self, state: AnalysisState) -> AnalysisState:
        """执行行业分析"""
        try:
            # 1. 获取公司行业信息
            company_info = await self._get_company_industry(state.stock_symbol)
            
            # 2. 获取同行业公司数据
            peer_companies = await self._get_peer_companies(company_info.industry)
            
            # 3. 进行对比分析
            comparison_result = await self._compare_with_peers(
                state.stock_symbol, peer_companies
            )
            
            # 4. 识别竞争优势
            competitive_analysis = await self._analyze_competitive_position(
                state.stock_symbol, comparison_result
            )
            
            # 5. 更新状态
            state.industry_analysis = competitive_analysis
            state.competition_score = competitive_analysis.competitive_score
            
            return state
            
        except Exception as e:
            state.errors.append(f"行业分析失败: {str(e)}")
            return state
    
    async def _get_peer_companies(self, industry: str) -> List[str]:
        """获取同行业公司列表"""
        # 使用A股API获取同行业股票
        peer_stocks = await self.toolkit.get_stocks_by_industry(industry)
        
        # 筛选出市值和业务相似的公司
        filtered_peers = self._filter_comparable_companies(peer_stocks)
        
        return filtered_peers[:10]  # 取前10家作为对比
    
    async def _compare_with_peers(self, target_symbol: str, peers: List[str]) -> dict:
        """与同行业公司对比"""
        comparison_data = {}
        
        # 获取所有公司的关键指标
        all_symbols = [target_symbol] + peers
        financial_data = await self.toolkit.batch_get_financial_ratios(all_symbols)
        
        # 计算行业平均值和排名
        metrics = ['roe', 'gross_margin', 'net_margin', 'debt_ratio']
        for metric in metrics:
            values = [data.get(metric, 0) for data in financial_data.values()]
            target_value = financial_data[target_symbol].get(metric, 0)
            
            comparison_data[metric] = {
                'target_value': target_value,
                'industry_average': np.mean(values),
                'industry_median': np.median(values),
                'ranking': self._calculate_ranking(target_value, values),
                'percentile': self._calculate_percentile(target_value, values)
            }
        
        return comparison_data
```

#### 估值分析Agent
```python
class ValuationAnalysisAgent:
    """估值与市场信号分析Agent"""
    
    async def analyze(self, state: AnalysisState) -> AnalysisState:
        """执行估值分析"""
        try:
            # 1. 获取市场数据
            market_data = await self._get_market_data(state.stock_symbol)
            
            # 2. 计算PR估值
            pr_valuation = self._calculate_pr_valuation(
                market_data, state.financial_analysis
            )
            
            # 3. 技术指标分析
            technical_analysis = await self._analyze_technical_indicators(
                state.stock_symbol
            )
            
            # 4. 股权变动分析
            ownership_analysis = await self._analyze_ownership_changes(
                state.stock_symbol
            )
            
            # 5. 综合市场信号
            market_signals = self._synthesize_market_signals(
                pr_valuation, technical_analysis, ownership_analysis
            )
            
            # 6. 更新状态
            valuation_result = ValuationAnalysisResult(
                **pr_valuation,
                **technical_analysis,
                **ownership_analysis,
                **market_signals
            )
            
            state.valuation_analysis = valuation_result
            state.valuation_score = valuation_result.valuation_score
            
            return state
            
        except Exception as e:
            state.errors.append(f"估值分析失败: {str(e)}")
            return state
    
    def _calculate_pr_valuation(self, market_data: dict, financial_data: FinancialAnalysisResult) -> dict:
        """计算PR估值模型"""
        try:
            pe_ratio = market_data.get('pe_ratio')
            roe = financial_data.roe_current
            
            if pe_ratio and roe and roe > 0:
                pr_ratio = pe_ratio / roe
                
                # PR估值分类
                if pr_ratio < 1.0:
                    valuation_level = "低估"
                elif pr_ratio <= 1.5:
                    valuation_level = "合理"
                else:
                    valuation_level = "高估"
                
                return {
                    'current_pe': pe_ratio,
                    'pr_ratio': pr_ratio,
                    'valuation_level': valuation_level,
                    'pr_historical_avg': self._get_historical_pr(market_data),
                    'valuation_score': self._calculate_valuation_score(pr_ratio)
                }
            else:
                return {'error': '缺少必要的PE或ROE数据'}
                
        except Exception as e:
            return {'error': f'PR估值计算失败: {str(e)}'}
```

### 3. 数据层设计

#### A股数据工具集
```python
class AShareToolkit:
    """A股数据API工具集"""
    
    def __init__(self, config: dict):
        self.base_url = config.get('ashare_api_url', 'http://localhost:8000/api/v1')
        self.session = aiohttp.ClientSession()
        self.cache = RedisCache(config.get('redis_url'))
        
    async def get_financial_reports(self, symbol: str, **kwargs) -> dict:
        """获取财务报表数据"""
        cache_key = f"financial_reports:{symbol}:{kwargs}"
        
        # 尝试从缓存获取
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从API获取
        url = f"{self.base_url}/financial/reports"
        params = {'symbols': symbol, **kwargs}
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                # 缓存数据
                await self.cache.set(cache_key, data, expire=3600)  # 1小时缓存
                
                return data
            else:
                raise APIError(f"获取财务报表失败: {response.status}")
    
    async def batch_get_financial_ratios(self, symbols: List[str]) -> dict:
        """批量获取财务比率"""
        # 并发获取多个股票的数据
        tasks = [self.get_financial_ratios(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"获取{symbol}财务比率失败: {result}")
                data[symbol] = {}
            else:
                data[symbol] = result
        
        return data
```

#### MCP服务集成
```python
class MCPToolkit:
    """MCP服务工具集"""
    
    def __init__(self, config: dict):
        self.endpoint = config.get('mcp_endpoint')
        self.api_key = config.get('mcp_api_key')
        self.websocket = None
        self.tools = {}
        
    async def connect(self):
        """建立MCP连接"""
        try:
            self.websocket = await websockets.connect(
                self.endpoint,
                extra_headers={'Authorization': f'Bearer {self.api_key}'}
            )
            
            # 初始化握手
            await self._initialize_connection()
            
            # 获取可用工具列表
            self.tools = await self._list_tools()
            
        except Exception as e:
            logger.error(f"MCP连接失败: {e}")
            raise
    
    async def call_tool(self, tool_name: str, parameters: dict) -> str:
        """调用MCP工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具{tool_name}不可用")
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        
        return json.loads(response)
```

### 4. 工作流编排设计

#### LangGraph集成
```python
from langgraph.graph import StateGraph, END, START

def create_analysis_graph(config: AnalysisConfig) -> CompiledGraph:
    """创建分析工作流图"""
    
    # 初始化Agent
    financial_agent = FinancialAnalysisAgent(config)
    industry_agent = IndustryAnalysisAgent(config)
    valuation_agent = ValuationAnalysisAgent(config)
    integration_agent = ReportIntegrationAgent(config)
    
    # 创建状态图
    graph = StateGraph(AnalysisState)
    
    # 添加节点
    graph.add_node("validate_input", validate_input_node)
    graph.add_node("financial_analysis", financial_agent.analyze)
    graph.add_node("industry_analysis", industry_agent.analyze)
    graph.add_node("valuation_analysis", valuation_agent.analyze)
    graph.add_node("integration", integration_agent.analyze)
    graph.add_node("error_handling", error_handling_node)
    
    # 设置流程
    graph.add_edge(START, "validate_input")
    
    # 条件路由：验证通过则并行执行分析
    graph.add_conditional_edges(
        "validate_input",
        lambda state: "parallel_analysis" if not state.errors else "error_handling",
        {
            "parallel_analysis": ["financial_analysis", "industry_analysis", "valuation_analysis"],
            "error_handling": "error_handling"
        }
    )
    
    # 并行分析完成后进行整合
    graph.add_edge("financial_analysis", "integration")
    graph.add_edge("industry_analysis", "integration")
    graph.add_edge("valuation_analysis", "integration")
    
    # 结束节点
    graph.add_edge("integration", END)
    graph.add_edge("error_handling", END)
    
    return graph.compile()

# 并行执行优化
async def parallel_analysis_node(state: AnalysisState) -> AnalysisState:
    """并行执行三个分析Agent"""
    
    # 创建异步任务
    tasks = [
        financial_agent.analyze(state.copy()),
        industry_agent.analyze(state.copy()),
        valuation_agent.analyze(state.copy())
    ]
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 合并结果
    for result in results:
        if isinstance(result, Exception):
            state.errors.append(str(result))
        else:
            # 合并分析结果到主状态
            state = merge_analysis_states(state, result)
    
    return state
```

### 5. 缓存和性能优化

#### Redis缓存设计
```python
class RedisCache:
    """Redis缓存管理"""
    
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        
    async def get(self, key: str) -> Optional[dict]:
        """获取缓存数据"""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"缓存获取失败: {e}")
            return None
    
    async def set(self, key: str, value: dict, expire: int = 3600):
        """设置缓存数据"""
        try:
            await self.redis.setex(
                key, 
                expire, 
                json.dumps(value, ensure_ascii=False, default=str)
            )
        except Exception as e:
            logger.warning(f"缓存设置失败: {e}")
    
    async def delete_pattern(self, pattern: str):
        """删除匹配模式的缓存"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

#### 性能监控
```python
import time
from functools import wraps

def performance_monitor(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 记录性能指标
            logger.info(f"{func.__name__} 执行时间: {execution_time:.2f}秒")
            
            # 更新状态中的性能信息
            if hasattr(result, 'processing_time'):
                result.processing_time = execution_time
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败 (耗时{execution_time:.2f}秒): {e}")
            raise
    
    return wrapper
```

---

## 🔒 安全和错误处理

### 1. 输入验证
```python
class InputValidator:
    """输入数据验证"""
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> bool:
        """验证股票代码格式"""
        # A股代码格式: 6位数字
        pattern = r'^[0-9]{6}$'
        return bool(re.match(pattern, symbol))
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """验证日期范围"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return start <= end <= datetime.now()
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """清理输入文本"""
        # 移除潜在的恶意字符
        cleaned = re.sub(r'[<>"\';]', '', text)
        return cleaned.strip()
```

### 2. 错误处理策略
```python
class AnalysisError(Exception):
    """分析相关错误基类"""
    pass

class DataSourceError(AnalysisError):
    """数据源错误"""
    pass

class ValidationError(AnalysisError):
    """验证错误"""
    pass

class LLMError(AnalysisError):
    """LLM调用错误"""
    pass

# 错误处理装饰器
def error_handler(error_type: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except DataSourceError as e:
                logger.error(f"数据源错误 in {func.__name__}: {e}")
                # 尝试备用数据源
                return await fallback_handler(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"验证错误 in {func.__name__}: {e}")
                raise  # 验证错误需要立即停止
            except LLMError as e:
                logger.error(f"LLM错误 in {func.__name__}: {e}")
                # 降级到简化分析
                return await simplified_analysis(*args, **kwargs)
            except Exception as e:
                logger.error(f"未知错误 in {func.__name__}: {e}")
                raise AnalysisError(f"分析失败: {str(e)}")
        
        return wrapper
    return decorator
```

### 3. 数据质量保证
```python
class DataQualityChecker:
    """数据质量检查"""
    
    @staticmethod
    def check_financial_data_completeness(data: dict) -> float:
        """检查财务数据完整性"""
        required_fields = [
            'total_revenue', 'net_profit', 'total_assets', 
            'total_liabilities', 'roe', 'gross_margin'
        ]
        
        available_fields = sum(1 for field in required_fields if data.get(field) is not None)
        completeness = available_fields / len(required_fields)
        
        return completeness
    
    @staticmethod
    def detect_anomalies(data: dict) -> List[str]:
        """检测数据异常"""
        anomalies = []
        
        # 检查异常值
        if data.get('roe', 0) > 100:
            anomalies.append("ROE异常高 (>100%)")
        
        if data.get('debt_ratio', 0) > 200:
            anomalies.append("负债率异常高 (>200%)")
        
        if data.get('gross_margin', 0) < 0:
            anomalies.append("毛利率为负")
        
        return anomalies
```

---

## 📊 监控和日志

### 1. 结构化日志
```python
import structlog

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 使用示例
logger.info(
    "分析开始",
    stock_symbol="000001",
    analysis_type="comprehensive",
    request_id="req_123456"
)
```

### 2. 监控指标
```python
from prometheus_client import Counter, Histogram, Gauge

# 定义监控指标
analysis_requests_total = Counter(
    'analysis_requests_total',
    'Total number of analysis requests',
    ['stock_symbol', 'status']
)

analysis_duration_seconds = Histogram(
    'analysis_duration_seconds',
    'Time spent on analysis',
    ['analysis_type']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# 使用示例
@performance_monitor
async def analyze_stock(symbol: str):
    analysis_requests_total.labels(stock_symbol=symbol, status='started').inc()
    
    with analysis_duration_seconds.labels(analysis_type='comprehensive').time():
        try:
            result = await perform_analysis(symbol)
            analysis_requests_total.labels(stock_symbol=symbol, status='success').inc()
            return result
        except Exception as e:
            analysis_requests_total.labels(stock_symbol=symbol, status='error').inc()
            raise
```

---

## 🧪 测试策略

### 1. 单元测试
```python
import pytest
from unittest.mock import AsyncMock, patch

class TestFinancialAnalysisAgent:
    """财务分析Agent单元测试"""
    
    @pytest.fixture
    def agent(self):
        config = AnalysisConfig()
        return FinancialAnalysisAgent(config)
    
    @pytest.mark.asyncio
    async def test_analyze_success(self, agent):
        """测试正常分析流程"""
        # 准备测试数据
        test_state = AnalysisState(stock_symbol="000001")
        
        # Mock外部依赖
        with patch.object(agent, '_collect_financial_data') as mock_collect:
            mock_collect.return_value = self._get_mock_financial_data()
            
            result = await agent.analyze(test_state)
            
            assert result.financial_analysis is not None
            assert result.financial_score is not None
            assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_invalid_data(self, agent):
        """测试异常数据处理"""
        test_state = AnalysisState(stock_symbol="000001")
        
        with patch.object(agent, '_collect_financial_data') as mock_collect:
            mock_collect.side_effect = DataSourceError("API不可用")
            
            result = await agent.analyze(test_state)
            
            assert len(result.errors) > 0
            assert "财务分析失败" in result.errors[0]
```

### 2. 集成测试
```python
class TestAnalysisWorkflow:
    """完整工作流集成测试"""
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self):
        """测试完整分析流程"""
        system = AShareAnalysisSystem()
        
        result = await system.analyze_stock("000001")
        
        # 验证结果完整性
        assert result.final_report is not None
        assert result.investment_recommendation is not None
        assert result.comprehensive_score is not None
        assert len(result.data_sources) > 0
    
    @pytest.mark.asyncio
    async def test_batch_analysis(self):
        """测试批量分析"""
        system = AShareAnalysisSystem()
        symbols = ["000001", "000002", "600519"]
        
        results = await system.batch_analyze(symbols)
        
        assert len(results) == len(symbols)
        for result in results:
            assert result.final_report is not None
```

### 3. 性能测试
```python
import asyncio
import time

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_single_analysis_performance(self):
        """测试单股票分析性能"""
        system = AShareAnalysisSystem()
        
        start_time = time.time()
        result = await system.analyze_stock("000001")
        execution_time = time.time() - start_time
        
        # 性能目标：单次分析<2分钟
        assert execution_time < 120
        assert result.processing_time < 120
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self):
        """测试并发分析性能"""
        system = AShareAnalysisSystem()
        symbols = ["000001", "000002", "600519", "002594", "300750"]
        
        start_time = time.time()
        
        # 并发执行
        tasks = [system.analyze_stock(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        execution_time = time.time() - start_time
        
        # 并发性能目标：5个股票<5分钟
        assert execution_time < 300
        assert len(results) == len(symbols)
```

---

## 🚀 部署配置

### 1. Docker配置
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY tradingagents/ ./tradingagents/
COPY main.py .

# 设置环境变量
ENV PYTHONPATH=/app
ENV REDIS_URL=redis://redis:6379

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
```

### 2. docker-compose配置
```yaml
version: '3.8'

services:
  analysis-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - ASHARE_API_URL=http://ashare-api:8000/api/v1
      - LLM_ENDPOINT=https://oned.lvtu.in
    depends_on:
      - redis
      - ashare-api
    volumes:
      - ./logs:/app/logs
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  ashare-api:
    image: ashare-data:latest
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ashare
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ashare
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### 3. 环境配置
```bash
# .env文件
# LLM配置
LLM_PROVIDER=openai
DEEP_THINK_LLM=gpt-4o
QUICK_THINK_LLM=gpt-4o-mini
LLM_ENDPOINT=https://oned.lvtu.in
OPENAI_API_KEY=your_api_key

# A股数据API
ASHARE_API_URL=http://localhost:8000/api/v1

# MCP服务
MCP_ENDPOINT=ws://your-server.com:8001
MCP_API_KEY=your_mcp_key

# Redis缓存
REDIS_URL=redis://localhost:6379

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/analysis.log

# 性能配置
MAX_CONCURRENT_ANALYSIS=5
CACHE_TTL=3600
REQUEST_TIMEOUT=120
```

---

## ✅ 技术验收标准

### 1. 功能完整性
- [ ] 4个核心Agent全部实现
- [ ] A股数据API集成完成
- [ ] MCP服务集成完成
- [ ] 金字塔原理报告生成
- [ ] 投资建议生成逻辑

### 2. 性能指标
- [ ] 单股票分析 < 2分钟
- [ ] 并发处理 ≥ 5个股票
- [ ] 内存使用 < 500MB
- [ ] API响应时间 < 30秒
- [ ] 缓存命中率 > 80%

### 3. 质量标准
- [ ] 单元测试覆盖率 > 90%
- [ ] 集成测试通过率 100%
- [ ] 代码质量评分 > 8.0
- [ ] 文档完整性 > 95%
- [ ] 错误处理覆盖率 100%

### 4. 安全要求
- [ ] 输入验证机制完善
- [ ] 错误信息不暴露敏感数据
- [ ] API访问控制
- [ ] 数据传输加密
- [ ] 日志脱敏处理

---

**技术设计文档版本**：v1.0
**文档创建时间**：2025-08-15
**适用系统版本**：analysis_stock_agent v1.0
**下一步**：根据技术设计开始实现核心组件