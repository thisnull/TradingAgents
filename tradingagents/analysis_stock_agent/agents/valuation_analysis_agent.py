"""
估值分析Agent
分析股票估值水平和市场信号，包括PR=PE/ROE估值模型
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from ..tools.ashare_toolkit import AShareToolkit, AShareAPIError
from ..utils.analysis_states import (
    ValuationAnalysisResult,
    AnalysisStatus,
    DataSource
)
from ..utils.data_validator import DataValidator, DataQualityChecker

logger = logging.getLogger(__name__)

@dataclass
class ValuationMetrics:
    """估值分析指标数据结构"""
    # 基础估值指标
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    pcf_ratio: Optional[float] = None
    
    # PR估值模型 (PR = PE/ROE)
    pr_ratio: Optional[float] = None
    pr_assessment: Optional[str] = None
    
    # 相对估值指标
    industry_avg_pe: Optional[float] = None
    pe_relative_to_industry: Optional[float] = None
    historical_pe_percentile: Optional[float] = None
    
    # 市场信号指标
    trading_volume_trend: Optional[str] = None
    price_momentum: Optional[float] = None
    volatility_level: Optional[str] = None
    
    # 股东结构指标
    institutional_ownership: Optional[float] = None
    ownership_concentration: Optional[float] = None
    recent_ownership_changes: Optional[List[Dict]] = None
    
    # 综合估值评分
    valuation_score: Optional[float] = None
    valuation_grade: Optional[str] = None
    investment_timing: Optional[str] = None

@dataclass
class MarketSignal:
    """市场信号数据结构"""
    signal_type: str
    signal_strength: str  # 'strong', 'moderate', 'weak'
    description: str
    impact: str  # 'positive', 'negative', 'neutral'

class ValuationAnalysisAgent:
    """估值分析Agent - 分析股票估值水平和市场信号"""
    
    def __init__(self, config: Dict[str, Any], ashare_toolkit: AShareToolkit):
        self.config = config
        self.ashare_toolkit = ashare_toolkit
        
        # 估值分析权重配置
        self.valuation_weights = config.get('valuation_weights', {
            'absolute_valuation': 0.30,     # 绝对估值水平
            'relative_valuation': 0.25,     # 相对估值比较
            'pr_model_analysis': 0.20,      # PR估值模型
            'market_signals': 0.15,         # 市场信号
            'ownership_analysis': 0.10      # 股东结构分析
        })
        
        # PR估值评级标准
        self.pr_thresholds = {
            'severely_undervalued': 0.5,    # 严重低估
            'undervalued': 0.8,             # 低估
            'fairly_valued': 1.2,           # 合理估值
            'overvalued': 1.5,              # 高估
            'severely_overvalued': float('inf')  # 严重高估
        }
        
        # 评级标准
        self.valuation_grades = {
            'A+': 90, 'A': 80, 'A-': 70,
            'B+': 60, 'B': 50, 'B-': 40,
            'C+': 30, 'C': 20, 'C-': 10,
            'D': 0
        }
    
    async def analyze_valuation(self, symbol: str, 
                              analysis_period_days: int = 252) -> ValuationAnalysisResult:
        """
        分析股票估值水平
        
        Args:
            symbol: 股票代码
            analysis_period_days: 分析期间天数，默认252个交易日(1年)
        
        Returns:
            ValuationAnalysisResult: 估值分析结果
        """
        logger.info(f"开始估值分析: {symbol}")
        
        try:
            # 1. 收集估值数据
            valuation_data = await self._collect_valuation_data(symbol, analysis_period_days)
            
            if not valuation_data:
                return ValuationAnalysisResult(
                    symbol=symbol,
                    status=AnalysisStatus.FAILED,
                    error_message="无法获取估值数据"
                )
            
            # 2. 计算估值指标
            metrics = await self._calculate_valuation_metrics(valuation_data)
            
            # 3. 执行5个分析模块
            analysis_results = {}
            
            # 模块1: 绝对估值分析
            analysis_results['absolute_valuation'] = await self._analyze_absolute_valuation(
                valuation_data, metrics
            )
            
            # 模块2: 相对估值分析
            analysis_results['relative_valuation'] = await self._analyze_relative_valuation(
                symbol, valuation_data, metrics
            )
            
            # 模块3: PR估值模型分析
            analysis_results['pr_model'] = await self._analyze_pr_model(
                valuation_data, metrics
            )
            
            # 模块4: 市场信号分析
            analysis_results['market_signals'] = await self._analyze_market_signals(
                symbol, valuation_data, metrics
            )
            
            # 模块5: 股东结构分析
            analysis_results['ownership_analysis'] = await self._analyze_ownership_structure(
                symbol, valuation_data, metrics
            )
            
            # 4. 综合评分
            overall_score, valuation_grade, timing = self._calculate_valuation_score(metrics)
            metrics.valuation_score = overall_score
            metrics.valuation_grade = valuation_grade
            metrics.investment_timing = timing
            
            # 5. 生成分析报告
            analysis_summary = self._generate_valuation_summary(symbol, metrics, analysis_results)
            market_signals = self._extract_market_signals(metrics, analysis_results)
            valuation_risks = self._identify_valuation_risks(metrics, analysis_results)
            
            return ValuationAnalysisResult(
                symbol=symbol,
                analysis_date=datetime.now(),
                status=AnalysisStatus.COMPLETED,
                valuation_metrics=metrics,
                market_signals=market_signals,
                analysis_summary=analysis_summary,
                valuation_risks=valuation_risks,
                data_sources=[
                    DataSource(
                        name="A股估值数据API",
                        endpoint="/financial/ratios",
                        version="v1.1.0"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"估值分析失败 {symbol}: {e}")
            return ValuationAnalysisResult(
                symbol=symbol,
                status=AnalysisStatus.FAILED,
                error_message=f"估值分析错误: {str(e)}"
            )
    
    async def _collect_valuation_data(self, symbol: str, period_days: int) -> Dict[str, Any]:
        """收集估值数据"""
        valuation_data = {}
        
        try:
            # 获取财务比率数据
            ratios_result = await self.ashare_toolkit.get_financial_ratios(symbol)
            if ratios_result.get('success'):
                valuation_data['financial_ratios'] = ratios_result.get('data', {})
            
            # 获取股票基础信息
            basic_info_result = await self.ashare_toolkit.get_stock_basic_info(symbol)
            if basic_info_result.get('success'):
                valuation_data['basic_info'] = basic_info_result.get('data', {})
            
            # 获取历史行情数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
            
            quotes_result = await self.ashare_toolkit.get_daily_quotes(
                symbol, start_date=start_date, end_date=end_date, limit=period_days
            )
            if quotes_result.get('success'):
                valuation_data['historical_quotes'] = quotes_result.get('data', [])
            
            # 获取财务摘要
            summary_result = await self.ashare_toolkit.get_financial_summary(symbol)
            if summary_result.get('success'):
                valuation_data['financial_summary'] = summary_result.get('data', {})
            
        except Exception as e:
            logger.error(f"收集估值数据失败: {e}")
        
        return valuation_data
    
    async def _calculate_valuation_metrics(self, valuation_data: Dict[str, Any]) -> ValuationMetrics:
        """计算估值指标"""
        metrics = ValuationMetrics()
        
        try:
            financial_ratios = valuation_data.get('financial_ratios', {})
            historical_quotes = valuation_data.get('historical_quotes', [])
            
            # 基础估值指标
            if financial_ratios:
                # 这里假设API返回的数据中包含这些比率，如果没有需要自己计算
                metrics.pe_ratio = financial_ratios.get('pe_ratio')
                metrics.pb_ratio = financial_ratios.get('pb_ratio') 
                metrics.ps_ratio = financial_ratios.get('ps_ratio')
                
                # 计算PR比率 (PR = PE/ROE)
                pe_ratio = financial_ratios.get('pe_ratio')
                roe = financial_ratios.get('roe')
                
                if pe_ratio is not None and roe is not None and roe > 0:
                    metrics.pr_ratio = pe_ratio / roe
                    metrics.pr_assessment = self._assess_pr_ratio(metrics.pr_ratio)
            
            # 从历史行情计算市场信号
            if historical_quotes and len(historical_quotes) >= 20:
                # 计算价格动量 (最近20天收益率)
                latest_price = historical_quotes[0].get('close')
                price_20_days_ago = historical_quotes[19].get('close') if len(historical_quotes) > 19 else None
                
                if latest_price and price_20_days_ago:
                    metrics.price_momentum = ((latest_price - price_20_days_ago) / price_20_days_ago) * 100
                
                # 计算波动率
                prices = [quote.get('close') for quote in historical_quotes[:30] if quote.get('close')]
                if len(prices) >= 10:
                    returns = [(prices[i] - prices[i+1]) / prices[i+1] for i in range(len(prices)-1)]
                    import statistics
                    volatility = statistics.stdev(returns) * 100 if len(returns) >= 2 else 0
                    
                    if volatility > 5:
                        metrics.volatility_level = 'high'
                    elif volatility > 2:
                        metrics.volatility_level = 'medium'
                    else:
                        metrics.volatility_level = 'low'
                
                # 分析交易量趋势
                volumes = [quote.get('volume') for quote in historical_quotes[:10] if quote.get('volume')]
                if len(volumes) >= 5:
                    recent_avg = sum(volumes[:5]) / 5
                    earlier_avg = sum(volumes[5:]) / len(volumes[5:]) if len(volumes) > 5 else recent_avg
                    
                    if recent_avg > earlier_avg * 1.2:
                        metrics.trading_volume_trend = 'increasing'
                    elif recent_avg < earlier_avg * 0.8:
                        metrics.trading_volume_trend = 'decreasing'
                    else:
                        metrics.trading_volume_trend = 'stable'
            
        except Exception as e:
            logger.error(f"计算估值指标错误: {e}")
        
        return metrics
    
    def _assess_pr_ratio(self, pr_ratio: float) -> str:
        """评估PR比率"""
        if pr_ratio <= self.pr_thresholds['severely_undervalued']:
            return 'severely_undervalued'
        elif pr_ratio <= self.pr_thresholds['undervalued']:
            return 'undervalued'
        elif pr_ratio <= self.pr_thresholds['fairly_valued']:
            return 'fairly_valued'
        elif pr_ratio <= self.pr_thresholds['overvalued']:
            return 'overvalued'
        else:
            return 'severely_overvalued'
    
    async def _analyze_absolute_valuation(self, valuation_data: Dict[str, Any], 
                                        metrics: ValuationMetrics) -> Dict[str, Any]:
        """分析绝对估值水平"""
        analysis = {
            'module_name': '绝对估值分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # PE比率评估
            if metrics.pe_ratio is not None:
                if 0 < metrics.pe_ratio <= 15:
                    analysis['score'] += 30
                    analysis['insights'].append(f"PE比率合理：{metrics.pe_ratio:.1f}")
                elif 15 < metrics.pe_ratio <= 25:
                    analysis['score'] += 25
                    analysis['insights'].append(f"PE比率适中：{metrics.pe_ratio:.1f}")
                elif 25 < metrics.pe_ratio <= 40:
                    analysis['score'] += 15
                    analysis['concerns'].append(f"PE比率偏高：{metrics.pe_ratio:.1f}")
                elif metrics.pe_ratio > 40:
                    analysis['concerns'].append(f"PE比率过高：{metrics.pe_ratio:.1f}")
                else:
                    analysis['concerns'].append(f"PE比率异常：{metrics.pe_ratio:.1f}")
            
            # PB比率评估
            if metrics.pb_ratio is not None:
                if 0 < metrics.pb_ratio <= 2:
                    analysis['score'] += 25
                    analysis['insights'].append(f"PB比率健康：{metrics.pb_ratio:.1f}")
                elif 2 < metrics.pb_ratio <= 3:
                    analysis['score'] += 20
                elif 3 < metrics.pb_ratio <= 5:
                    analysis['score'] += 10
                    analysis['concerns'].append(f"PB比率偏高：{metrics.pb_ratio:.1f}")
                else:
                    analysis['concerns'].append(f"PB比率过高：{metrics.pb_ratio:.1f}")
            
            # PS比率评估
            if metrics.ps_ratio is not None:
                if 0 < metrics.ps_ratio <= 3:
                    analysis['score'] += 25
                    analysis['insights'].append(f"PS比率合理：{metrics.ps_ratio:.1f}")
                elif 3 < metrics.ps_ratio <= 6:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"PS比率偏高：{metrics.ps_ratio:.1f}")
            
            # 确保最低分数
            if analysis['score'] < 20:
                analysis['score'] = 20
            
        except Exception as e:
            logger.error(f"绝对估值分析错误: {e}")
            analysis['concerns'].append("绝对估值分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_relative_valuation(self, symbol: str, valuation_data: Dict[str, Any], 
                                        metrics: ValuationMetrics) -> Dict[str, Any]:
        """分析相对估值"""
        analysis = {
            'module_name': '相对估值分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 由于缺乏行业数据，这里提供基础框架
            # 实际实现需要获取同行业公司的估值数据进行比较
            
            # 基于历史数据的相对估值分析
            historical_quotes = valuation_data.get('historical_quotes', [])
            
            if historical_quotes and len(historical_quotes) >= 60:
                # 计算当前价格相对于历史价格的位置
                current_price = historical_quotes[0].get('close')
                prices = [quote.get('close') for quote in historical_quotes if quote.get('close')]
                
                if current_price and len(prices) >= 60:
                    max_price = max(prices)
                    min_price = min(prices)
                    
                    price_percentile = (current_price - min_price) / (max_price - min_price) * 100
                    
                    if price_percentile <= 30:
                        analysis['score'] += 40
                        analysis['insights'].append(f"当前价格处于历史低位：{price_percentile:.1f}%分位")
                    elif price_percentile <= 50:
                        analysis['score'] += 30
                        analysis['insights'].append(f"当前价格处于历史中低位：{price_percentile:.1f}%分位")
                    elif price_percentile <= 70:
                        analysis['score'] += 20
                    else:
                        analysis['concerns'].append(f"当前价格处于历史高位：{price_percentile:.1f}%分位")
            
            # 默认给一些基础分数
            if analysis['score'] < 30:
                analysis['score'] = 30
                analysis['insights'].append("相对估值分析需要更多行业对比数据")
            
        except Exception as e:
            logger.error(f"相对估值分析错误: {e}")
            analysis['concerns'].append("相对估值分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_pr_model(self, valuation_data: Dict[str, Any], 
                              metrics: ValuationMetrics) -> Dict[str, Any]:
        """分析PR估值模型 (PR = PE/ROE)"""
        analysis = {
            'module_name': 'PR估值模型分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            if metrics.pr_ratio is not None and metrics.pr_assessment is not None:
                
                # 根据PR评估给分
                if metrics.pr_assessment == 'severely_undervalued':
                    analysis['score'] += 90
                    analysis['insights'].append(f"PR模型显示严重低估：PR={metrics.pr_ratio:.2f} (极佳买入机会)")
                elif metrics.pr_assessment == 'undervalued':
                    analysis['score'] += 80
                    analysis['insights'].append(f"PR模型显示低估：PR={metrics.pr_ratio:.2f} (良好买入机会)")
                elif metrics.pr_assessment == 'fairly_valued':
                    analysis['score'] += 60
                    analysis['insights'].append(f"PR模型显示合理估值：PR={metrics.pr_ratio:.2f} (持有观望)")
                elif metrics.pr_assessment == 'overvalued':
                    analysis['score'] += 30
                    analysis['concerns'].append(f"PR模型显示高估：PR={metrics.pr_ratio:.2f} (谨慎投资)")
                else:  # severely_overvalued
                    analysis['score'] += 10
                    analysis['concerns'].append(f"PR模型显示严重高估：PR={metrics.pr_ratio:.2f} (建议规避)")
                
                # 添加PR模型解释
                financial_ratios = valuation_data.get('financial_ratios', {})
                pe_ratio = financial_ratios.get('pe_ratio')
                roe = financial_ratios.get('roe')
                
                if pe_ratio is not None and roe is not None:
                    analysis['insights'].append(f"PR计算: PE({pe_ratio:.1f}) ÷ ROE({roe:.1f}%) = {metrics.pr_ratio:.2f}")
                    
                    # PR模型理论指导
                    if metrics.pr_ratio < 1:
                        analysis['insights'].append("理论上PE增长空间较大，估值修复可期")
                    elif metrics.pr_ratio > 1.5:
                        analysis['insights'].append("PE可能存在泡沫，需警惕估值回归风险")
            
            else:
                analysis['score'] = 30
                analysis['concerns'].append("缺乏PR模型计算所需的PE或ROE数据")
            
        except Exception as e:
            logger.error(f"PR模型分析错误: {e}")
            analysis['concerns'].append("PR模型分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_market_signals(self, symbol: str, valuation_data: Dict[str, Any], 
                                    metrics: ValuationMetrics) -> Dict[str, Any]:
        """分析市场信号"""
        analysis = {
            'module_name': '市场信号分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 价格动量分析
            if metrics.price_momentum is not None:
                if metrics.price_momentum > 10:
                    analysis['score'] += 25
                    analysis['insights'].append(f"价格动量强劲：近20日上涨{metrics.price_momentum:.1f}%")
                elif metrics.price_momentum > 0:
                    analysis['score'] += 20
                    analysis['insights'].append(f"价格动量正面：近20日上涨{metrics.price_momentum:.1f}%")
                elif metrics.price_momentum > -10:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"价格动量疲弱：近20日下跌{abs(metrics.price_momentum):.1f}%")
            
            # 交易量趋势分析
            if metrics.trading_volume_trend == 'increasing':
                analysis['score'] += 25
                analysis['insights'].append("交易量呈上升趋势，市场关注度提升")
            elif metrics.trading_volume_trend == 'stable':
                analysis['score'] += 20
                analysis['insights'].append("交易量保持稳定")
            elif metrics.trading_volume_trend == 'decreasing':
                analysis['concerns'].append("交易量呈下降趋势，市场关注度降低")
            
            # 波动率分析
            if metrics.volatility_level == 'low':
                analysis['score'] += 20
                analysis['insights'].append("股价波动率较低，风险相对可控")
            elif metrics.volatility_level == 'medium':
                analysis['score'] += 15
                analysis['insights'].append("股价波动率适中")
            elif metrics.volatility_level == 'high':
                analysis['concerns'].append("股价波动率较高，投资风险较大")
            
            # 确保最低分数
            if analysis['score'] < 20:
                analysis['score'] = 20
            
        except Exception as e:
            logger.error(f"市场信号分析错误: {e}")
            analysis['concerns'].append("市场信号分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_ownership_structure(self, symbol: str, valuation_data: Dict[str, Any], 
                                         metrics: ValuationMetrics) -> Dict[str, Any]:
        """分析股东结构"""
        analysis = {
            'module_name': '股东结构分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 由于API数据限制，这里提供基础框架
            # 实际实现需要获取股东持股数据
            
            basic_info = valuation_data.get('basic_info', {})
            
            # 股本结构分析
            total_shares = basic_info.get('total_shares')
            float_shares = basic_info.get('float_shares')
            
            if total_shares and float_shares:
                float_ratio = float_shares / total_shares * 100
                
                if float_ratio > 80:
                    analysis['score'] += 30
                    analysis['insights'].append(f"流通比例较高：{float_ratio:.1f}%，流动性较好")
                elif float_ratio > 50:
                    analysis['score'] += 25
                    analysis['insights'].append(f"流通比例适中：{float_ratio:.1f}%")
                else:
                    analysis['score'] += 15
                    analysis['concerns'].append(f"流通比例较低：{float_ratio:.1f}%，可能影响流动性")
            
            # 默认分数
            if analysis['score'] < 25:
                analysis['score'] = 25
                analysis['insights'].append("股东结构分析需要更多持股明细数据")
            
        except Exception as e:
            logger.error(f"股东结构分析错误: {e}")
            analysis['concerns'].append("股东结构分析过程中出现数据错误")
        
        return analysis
    
    def _calculate_valuation_score(self, metrics: ValuationMetrics) -> Tuple[float, str, str]:
        """计算估值综合评分"""
        try:
            score_components = []
            
            # PR模型评分 (20%)
            pr_score = 50  # 默认分数
            if metrics.pr_assessment is not None:
                pr_score_map = {
                    'severely_undervalued': 95,
                    'undervalued': 85,
                    'fairly_valued': 65,
                    'overvalued': 35,
                    'severely_overvalued': 15
                }
                pr_score = pr_score_map.get(metrics.pr_assessment, 50)
            
            score_components.append(pr_score * self.valuation_weights['pr_model_analysis'])
            
            # 绝对估值评分 (30%)
            absolute_score = 50
            if metrics.pe_ratio is not None:
                if 0 < metrics.pe_ratio <= 15:
                    absolute_score = 80
                elif 15 < metrics.pe_ratio <= 25:
                    absolute_score = 70
                elif 25 < metrics.pe_ratio <= 40:
                    absolute_score = 50
                else:
                    absolute_score = 30
            
            score_components.append(absolute_score * self.valuation_weights['absolute_valuation'])
            
            # 市场信号评分 (15%)
            signal_score = 50
            if metrics.price_momentum is not None:
                if metrics.price_momentum > 10:
                    signal_score = 80
                elif metrics.price_momentum > 0:
                    signal_score = 70
                elif metrics.price_momentum > -10:
                    signal_score = 50
                else:
                    signal_score = 30
            
            score_components.append(signal_score * self.valuation_weights['market_signals'])
            
            # 其他权重使用默认分数
            remaining_weights = (
                self.valuation_weights['relative_valuation'] +
                self.valuation_weights['ownership_analysis']
            )
            score_components.append(55 * remaining_weights)
            
            # 计算总分
            overall_score = sum(score_components)
            
            # 确定评级
            valuation_grade = 'D'
            for grade, threshold in self.valuation_grades.items():
                if overall_score >= threshold:
                    valuation_grade = grade
                    break
            
            # 投资时机建议
            investment_timing = 'hold'  # 默认持有
            if metrics.pr_assessment in ['severely_undervalued', 'undervalued']:
                investment_timing = 'buy'
            elif metrics.pr_assessment in ['overvalued', 'severely_overvalued']:
                investment_timing = 'sell'
            
            return round(overall_score, 2), valuation_grade, investment_timing
            
        except Exception as e:
            logger.error(f"计算估值评分错误: {e}")
            return 50.0, 'C', 'hold'
    
    def _generate_valuation_summary(self, symbol: str, metrics: ValuationMetrics, 
                                  analysis_results: Dict[str, Any]) -> str:
        """生成估值分析摘要"""
        try:
            summary_parts = [
                f"## {symbol} 估值分析报告",
                f"**估值评级:** {metrics.valuation_grade} ({metrics.valuation_score:.1f}/100)",
                f"**投资建议:** {metrics.investment_timing.upper()}",
                "",
                "### 核心估值指标",
            ]
            
            if metrics.pe_ratio is not None:
                summary_parts.append(f"- PE比率: {metrics.pe_ratio:.2f}")
            if metrics.pb_ratio is not None:
                summary_parts.append(f"- PB比率: {metrics.pb_ratio:.2f}")
            if metrics.pr_ratio is not None:
                summary_parts.append(f"- PR比率: {metrics.pr_ratio:.2f} ({metrics.pr_assessment})")
            if metrics.price_momentum is not None:
                summary_parts.append(f"- 价格动量: {metrics.price_momentum:.1f}%")
            
            summary_parts.append("")
            summary_parts.append("### 分析模块评分")
            
            for module_name, result in analysis_results.items():
                module_title = result.get('module_name', module_name)
                score = result.get('score', 0)
                summary_parts.append(f"- {module_title}: {score}/100")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成估值分析摘要错误: {e}")
            return f"{symbol} 估值分析报告生成失败"
    
    def _extract_market_signals(self, metrics: ValuationMetrics, 
                              analysis_results: Dict[str, Any]) -> List[MarketSignal]:
        """提取市场信号"""
        signals = []
        
        try:
            # PR模型信号
            if metrics.pr_assessment is not None:
                if metrics.pr_assessment in ['severely_undervalued', 'undervalued']:
                    signals.append(MarketSignal(
                        signal_type='PR估值信号',
                        signal_strength='strong',
                        description=f'PR模型显示{metrics.pr_assessment}，估值具有吸引力',
                        impact='positive'
                    ))
                elif metrics.pr_assessment in ['overvalued', 'severely_overvalued']:
                    signals.append(MarketSignal(
                        signal_type='PR估值信号',
                        signal_strength='strong',
                        description=f'PR模型显示{metrics.pr_assessment}，估值偏高需谨慎',
                        impact='negative'
                    ))
            
            # 价格动量信号
            if metrics.price_momentum is not None:
                if metrics.price_momentum > 10:
                    signals.append(MarketSignal(
                        signal_type='价格动量信号',
                        signal_strength='strong',
                        description=f'强劲的价格上涨动量{metrics.price_momentum:.1f}%',
                        impact='positive'
                    ))
                elif metrics.price_momentum < -10:
                    signals.append(MarketSignal(
                        signal_type='价格动量信号',
                        signal_strength='strong',
                        description=f'明显的价格下跌动量{metrics.price_momentum:.1f}%',
                        impact='negative'
                    ))
            
            # 交易量信号
            if metrics.trading_volume_trend == 'increasing':
                signals.append(MarketSignal(
                    signal_type='交易量信号',
                    signal_strength='moderate',
                    description='交易量呈上升趋势，市场关注度提升',
                    impact='positive'
                ))
            
        except Exception as e:
            logger.error(f"提取市场信号错误: {e}")
        
        return signals[:10]  # 限制最多10个信号
    
    def _identify_valuation_risks(self, metrics: ValuationMetrics, 
                                analysis_results: Dict[str, Any]) -> List[str]:
        """识别估值风险"""
        risks = []
        
        try:
            for result in analysis_results.values():
                risks.extend(result.get('concerns', []))
            
            # 添加基于指标的风险评估
            if metrics.pr_assessment in ['overvalued', 'severely_overvalued']:
                risks.append("PR模型显示估值偏高，存在估值回归风险")
            
            if metrics.volatility_level == 'high':
                risks.append("股价波动率较高，短期投资风险较大")
            
            if metrics.valuation_score and metrics.valuation_score < 40:
                risks.append("综合估值评分较低，投资时机可能不佳")
            
        except Exception as e:
            logger.error(f"识别估值风险错误: {e}")
        
        return risks[:8]  # 限制最多8个风险

# 工具函数
async def create_valuation_analysis_agent(config: Dict[str, Any], 
                                        ashare_toolkit: AShareToolkit) -> ValuationAnalysisAgent:
    """创建估值分析Agent实例"""
    return ValuationAnalysisAgent(config, ashare_toolkit)