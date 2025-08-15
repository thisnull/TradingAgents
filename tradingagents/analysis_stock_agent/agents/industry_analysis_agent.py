"""
行业分析Agent
分析股票在行业中的地位和竞争优势
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from ..tools.ashare_toolkit import AShareToolkit, AShareAPIError
from ..utils.analysis_states import (
    IndustryAnalysisResult,
    AnalysisStatus,
    DataSource
)
from ..utils.data_validator import DataValidator, DataQualityChecker

logger = logging.getLogger(__name__)

@dataclass
class IndustryMetrics:
    """行业分析指标数据结构"""
    # 行业地位指标
    industry_rank: Optional[int] = None
    market_share: Optional[float] = None
    revenue_rank: Optional[int] = None
    profit_rank: Optional[int] = None
    
    # 竞争比较指标
    industry_avg_roe: Optional[float] = None
    company_vs_industry_roe: Optional[float] = None
    industry_avg_profit_margin: Optional[float] = None
    company_vs_industry_margin: Optional[float] = None
    
    # 增长比较指标
    industry_avg_growth: Optional[float] = None
    company_vs_industry_growth: Optional[float] = None
    
    # 估值比较指标
    industry_avg_pe: Optional[float] = None
    company_vs_industry_pe: Optional[float] = None
    
    # 竞争优势评分
    competitive_advantage_score: Optional[float] = None
    industry_position_grade: Optional[str] = None

@dataclass
class CompetitorInfo:
    """竞争对手信息"""
    symbol: str
    name: str
    market_cap: Optional[float] = None
    revenue: Optional[float] = None
    profit: Optional[float] = None
    roe: Optional[float] = None
    profit_margin: Optional[float] = None

class IndustryAnalysisAgent:
    """行业分析Agent - 分析股票行业地位和竞争优势"""
    
    def __init__(self, config: Dict[str, Any], ashare_toolkit: AShareToolkit):
        self.config = config
        self.ashare_toolkit = ashare_toolkit
        
        # 分析权重配置
        self.analysis_weights = config.get('industry_analysis_weights', {
            'market_position': 0.30,      # 市场地位
            'profitability_comparison': 0.25,  # 盈利能力比较
            'growth_comparison': 0.20,    # 增长能力比较
            'operational_efficiency': 0.15,   # 运营效率
            'financial_health': 0.10     # 财务健康度
        })
        
        # 竞争地位评级标准
        self.position_grades = {
            'A+': 90, 'A': 80, 'A-': 70,
            'B+': 60, 'B': 50, 'B-': 40,
            'C+': 30, 'C': 20, 'C-': 10,
            'D': 0
        }
    
    async def analyze_industry_position(self, symbol: str, 
                                      max_competitors: int = 10) -> IndustryAnalysisResult:
        """
        分析股票行业地位
        
        Args:
            symbol: 股票代码
            max_competitors: 最大竞争对手数量
        
        Returns:
            IndustryAnalysisResult: 行业分析结果
        """
        logger.info(f"开始行业分析: {symbol}")
        
        try:
            # 1. 获取目标公司基础信息
            company_info = await self._get_company_info(symbol)
            
            if not company_info:
                return IndustryAnalysisResult(
                    symbol=symbol,
                    status=AnalysisStatus.FAILED,
                    error_message="无法获取公司基础信息"
                )
            
            # 2. 获取同行业竞争对手
            competitors = await self._get_industry_competitors(
                company_info.get('industry', ''), 
                symbol, 
                max_competitors
            )
            
            # 3. 收集行业数据
            industry_data = await self._collect_industry_data(symbol, competitors)
            
            # 4. 计算行业指标
            metrics = await self._calculate_industry_metrics(symbol, industry_data)
            
            # 5. 执行4个分析模块
            analysis_results = {}
            
            # 模块1: 行业地位分析
            analysis_results['market_position'] = await self._analyze_market_position(
                symbol, industry_data, metrics
            )
            
            # 模块2: 竞争对手比较
            analysis_results['competitor_comparison'] = await self._analyze_competitor_comparison(
                symbol, industry_data, metrics
            )
            
            # 模块3: 竞争优势识别
            analysis_results['competitive_advantages'] = await self._analyze_competitive_advantages(
                symbol, industry_data, metrics
            )
            
            # 模块4: 行业趋势评估
            analysis_results['industry_trends'] = await self._analyze_industry_trends(
                symbol, industry_data, metrics
            )
            
            # 6. 综合评分
            overall_score, position_grade = self._calculate_industry_score(metrics)
            metrics.competitive_advantage_score = overall_score
            metrics.industry_position_grade = position_grade
            
            # 7. 生成分析报告
            analysis_summary = self._generate_industry_summary(symbol, metrics, analysis_results)
            competitive_advantages = self._extract_competitive_advantages(metrics, analysis_results)
            industry_risks = self._identify_industry_risks(metrics, analysis_results)
            
            return IndustryAnalysisResult(
                symbol=symbol,
                analysis_date=datetime.now(),
                status=AnalysisStatus.COMPLETED,
                industry_metrics=metrics,
                competitors_data=competitors,
                analysis_summary=analysis_summary,
                competitive_advantages=competitive_advantages,
                industry_risks=industry_risks,
                data_sources=[
                    DataSource(
                        name="A股行业数据API",
                        endpoint="/market/basic",
                        version="v1.1.0"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"行业分析失败 {symbol}: {e}")
            return IndustryAnalysisResult(
                symbol=symbol,
                status=AnalysisStatus.FAILED,
                error_message=f"行业分析错误: {str(e)}"
            )
    
    async def _get_company_info(self, symbol: str) -> Dict[str, Any]:
        """获取公司基础信息"""
        try:
            result = await self.ashare_toolkit.get_stock_basic_info(symbol)
            
            if result.get('success'):
                return result.get('data', {})
            else:
                logger.warning(f"获取公司信息失败: {symbol}")
                return {}
                
        except AShareAPIError as e:
            logger.error(f"获取公司基础信息失败: {e}")
            return {}
    
    async def _get_industry_competitors(self, industry: str, exclude_symbol: str, 
                                     max_count: int) -> List[CompetitorInfo]:
        """获取同行业竞争对手"""
        competitors = []
        
        try:
            # 获取同行业股票列表
            result = await self.ashare_toolkit.get_industry_stocks(industry, limit=max_count + 5)
            
            if result.get('success'):
                stocks = result.get('data', [])
                
                for stock in stocks:
                    if stock.get('symbol') != exclude_symbol and len(competitors) < max_count:
                        competitor = CompetitorInfo(
                            symbol=stock.get('symbol', ''),
                            name=stock.get('name', ''),
                            market_cap=stock.get('total_shares')  # 简化处理
                        )
                        competitors.append(competitor)
            
        except Exception as e:
            logger.error(f"获取竞争对手失败: {e}")
        
        return competitors
    
    async def _collect_industry_data(self, symbol: str, 
                                   competitors: List[CompetitorInfo]) -> Dict[str, Any]:
        """收集行业数据"""
        industry_data = {
            'target_company': {},
            'competitors': {},
            'industry_summary': {}
        }
        
        try:
            # 获取目标公司财务数据
            target_ratios = await self.ashare_toolkit.get_financial_ratios(symbol)
            if target_ratios.get('success'):
                industry_data['target_company'] = target_ratios.get('data', {})
            
            # 批量获取竞争对手财务数据
            competitor_symbols = [comp.symbol for comp in competitors]
            if competitor_symbols:
                competitors_ratios = await self.ashare_toolkit.batch_get_financial_ratios(
                    competitor_symbols
                )
                industry_data['competitors'] = competitors_ratios
            
        except Exception as e:
            logger.error(f"收集行业数据失败: {e}")
        
        return industry_data
    
    async def _calculate_industry_metrics(self, symbol: str, 
                                        industry_data: Dict[str, Any]) -> IndustryMetrics:
        """计算行业指标"""
        metrics = IndustryMetrics()
        
        try:
            target_data = industry_data.get('target_company', {})
            competitors_data = industry_data.get('competitors', {})
            
            if not target_data or not competitors_data:
                logger.warning("行业数据不足，无法进行完整比较")
                return metrics
            
            # 收集所有公司的财务指标
            all_companies_data = [target_data]
            valid_competitors = []
            
            for symbol_comp, comp_data in competitors_data.items():
                if comp_data:  # 确保数据非空
                    all_companies_data.append(comp_data)
                    valid_competitors.append(symbol_comp)
            
            if len(all_companies_data) < 2:
                logger.warning("有效竞争对手数据不足")
                return metrics
            
            # 计算行业平均值
            def safe_avg(values):
                valid_values = [v for v in values if v is not None]
                return sum(valid_values) / len(valid_values) if valid_values else None
            
            # ROE比较
            roe_values = [data.get('roe') for data in all_companies_data]
            metrics.industry_avg_roe = safe_avg(roe_values[1:])  # 排除目标公司
            
            target_roe = target_data.get('roe')
            if target_roe is not None and metrics.industry_avg_roe is not None:
                metrics.company_vs_industry_roe = target_roe - metrics.industry_avg_roe
            
            # 净利率比较
            margin_values = [data.get('net_profit_margin') for data in all_companies_data]
            metrics.industry_avg_profit_margin = safe_avg(margin_values[1:])
            
            target_margin = target_data.get('net_profit_margin')
            if target_margin is not None and metrics.industry_avg_profit_margin is not None:
                metrics.company_vs_industry_margin = target_margin - metrics.industry_avg_profit_margin
            
            # 计算排名
            if target_roe is not None:
                roe_ranking = sorted([v for v in roe_values if v is not None], reverse=True)
                if target_roe in roe_ranking:
                    metrics.revenue_rank = roe_ranking.index(target_roe) + 1
            
        except Exception as e:
            logger.error(f"计算行业指标错误: {e}")
        
        return metrics
    
    async def _analyze_market_position(self, symbol: str, industry_data: Dict[str, Any], 
                                     metrics: IndustryMetrics) -> Dict[str, Any]:
        """分析市场地位"""
        analysis = {
            'module_name': '市场地位分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # ROE排名评估
            if metrics.revenue_rank is not None:
                if metrics.revenue_rank <= 3:
                    analysis['score'] += 40
                    analysis['insights'].append(f"ROE行业排名优秀：第{metrics.revenue_rank}名")
                elif metrics.revenue_rank <= 5:
                    analysis['score'] += 30
                    analysis['insights'].append(f"ROE行业排名良好：第{metrics.revenue_rank}名")
                elif metrics.revenue_rank <= 10:
                    analysis['score'] += 20
                else:
                    analysis['concerns'].append(f"ROE行业排名偏后：第{metrics.revenue_rank}名")
            
            # ROE相对表现
            if metrics.company_vs_industry_roe is not None:
                if metrics.company_vs_industry_roe > 5:
                    analysis['score'] += 30
                    analysis['insights'].append(f"ROE显著超越行业平均：+{metrics.company_vs_industry_roe:.1f}%")
                elif metrics.company_vs_industry_roe > 0:
                    analysis['score'] += 20
                    analysis['insights'].append(f"ROE超越行业平均：+{metrics.company_vs_industry_roe:.1f}%")
                else:
                    analysis['concerns'].append(f"ROE低于行业平均：{metrics.company_vs_industry_roe:.1f}%")
            
            # 净利率相对表现
            if metrics.company_vs_industry_margin is not None:
                if metrics.company_vs_industry_margin > 3:
                    analysis['score'] += 30
                    analysis['insights'].append(f"净利率显著超越行业：+{metrics.company_vs_industry_margin:.1f}%")
                elif metrics.company_vs_industry_margin > 0:
                    analysis['score'] += 20
                    analysis['insights'].append(f"净利率超越行业：+{metrics.company_vs_industry_margin:.1f}%")
                else:
                    analysis['concerns'].append(f"净利率低于行业：{metrics.company_vs_industry_margin:.1f}%")
            
        except Exception as e:
            logger.error(f"市场地位分析错误: {e}")
            analysis['concerns'].append("市场地位分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_competitor_comparison(self, symbol: str, industry_data: Dict[str, Any], 
                                           metrics: IndustryMetrics) -> Dict[str, Any]:
        """分析竞争对手比较"""
        analysis = {
            'module_name': '竞争对手比较',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            target_data = industry_data.get('target_company', {})
            competitors_data = industry_data.get('competitors', {})
            
            if not target_data or not competitors_data:
                analysis['concerns'].append("缺乏足够的竞争对手数据进行比较")
                return analysis
            
            # 统计超越竞争对手的指标数量
            outperform_count = 0
            total_comparisons = 0
            
            target_roe = target_data.get('roe')
            target_margin = target_data.get('net_profit_margin')
            target_current_ratio = target_data.get('current_ratio')
            
            for comp_symbol, comp_data in competitors_data.items():
                if not comp_data:
                    continue
                
                total_comparisons += 1
                
                # ROE比较
                comp_roe = comp_data.get('roe')
                if target_roe is not None and comp_roe is not None and target_roe > comp_roe:
                    outperform_count += 1
                
                # 净利率比较
                comp_margin = comp_data.get('net_profit_margin')
                if target_margin is not None and comp_margin is not None and target_margin > comp_margin:
                    outperform_count += 1
                
                # 流动比率比较
                comp_current = comp_data.get('current_ratio')
                if target_current_ratio is not None and comp_current is not None and target_current_ratio > comp_current:
                    outperform_count += 1
            
            # 根据超越比例评分
            if total_comparisons > 0:
                outperform_ratio = outperform_count / (total_comparisons * 3)  # 3个指标
                
                if outperform_ratio > 0.7:
                    analysis['score'] += 80
                    analysis['insights'].append(f"在多数关键指标上超越竞争对手：{outperform_ratio*100:.1f}%")
                elif outperform_ratio > 0.5:
                    analysis['score'] += 60
                    analysis['insights'].append(f"在半数以上指标超越竞争对手：{outperform_ratio*100:.1f}%")
                elif outperform_ratio > 0.3:
                    analysis['score'] += 40
                else:
                    analysis['concerns'].append(f"仅在少数指标超越竞争对手：{outperform_ratio*100:.1f}%")
            
        except Exception as e:
            logger.error(f"竞争对手比较分析错误: {e}")
            analysis['concerns'].append("竞争对手比较分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_competitive_advantages(self, symbol: str, industry_data: Dict[str, Any], 
                                            metrics: IndustryMetrics) -> Dict[str, Any]:
        """分析竞争优势"""
        analysis = {
            'module_name': '竞争优势识别',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            target_data = industry_data.get('target_company', {})
            
            # 识别潜在竞争优势
            advantages = []
            
            # 盈利能力优势
            if metrics.company_vs_industry_roe is not None and metrics.company_vs_industry_roe > 5:
                advantages.append("显著的ROE优势")
                analysis['score'] += 25
            
            if metrics.company_vs_industry_margin is not None and metrics.company_vs_industry_margin > 3:
                advantages.append("优秀的成本控制能力")
                analysis['score'] += 25
            
            # 财务健康度优势
            current_ratio = target_data.get('current_ratio')
            if current_ratio is not None and current_ratio > 2.0:
                advantages.append("强劲的流动性管理")
                analysis['score'] += 20
            
            debt_ratio = target_data.get('debt_to_asset_ratio')
            if debt_ratio is not None and debt_ratio < 30:
                advantages.append("稳健的资本结构")
                analysis['score'] += 20
            
            # 运营效率优势
            if len(advantages) >= 3:
                advantages.append("多维度竞争优势")
                analysis['score'] += 10
            
            if advantages:
                analysis['insights'].extend(advantages)
            else:
                analysis['concerns'].append("未发现明显的竞争优势")
            
        except Exception as e:
            logger.error(f"竞争优势分析错误: {e}")
            analysis['concerns'].append("竞争优势分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_industry_trends(self, symbol: str, industry_data: Dict[str, Any], 
                                     metrics: IndustryMetrics) -> Dict[str, Any]:
        """分析行业趋势"""
        analysis = {
            'module_name': '行业趋势评估',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 由于数据限制，这里提供基础的趋势分析框架
            target_data = industry_data.get('target_company', {})
            
            # 基于现有指标推断趋势
            if metrics.industry_avg_roe is not None:
                if metrics.industry_avg_roe > 15:
                    analysis['score'] += 30
                    analysis['insights'].append(f"所处行业整体盈利能力良好：平均ROE {metrics.industry_avg_roe:.1f}%")
                elif metrics.industry_avg_roe > 10:
                    analysis['score'] += 20
                else:
                    analysis['concerns'].append(f"所处行业整体盈利能力一般：平均ROE {metrics.industry_avg_roe:.1f}%")
            
            if metrics.industry_avg_profit_margin is not None:
                if metrics.industry_avg_profit_margin > 10:
                    analysis['score'] += 30
                    analysis['insights'].append(f"行业利润率水平健康：平均净利率 {metrics.industry_avg_profit_margin:.1f}%")
                elif metrics.industry_avg_profit_margin > 5:
                    analysis['score'] += 20
                else:
                    analysis['concerns'].append(f"行业利润率偏低：平均净利率 {metrics.industry_avg_profit_margin:.1f}%")
            
            # 默认给一些基础分数
            analysis['score'] = max(analysis['score'], 40)
            if not analysis['insights']:
                analysis['insights'].append("行业趋势分析需要更多历史数据支持")
            
        except Exception as e:
            logger.error(f"行业趋势分析错误: {e}")
            analysis['concerns'].append("行业趋势分析过程中出现数据错误")
        
        return analysis
    
    def _calculate_industry_score(self, metrics: IndustryMetrics) -> Tuple[float, str]:
        """计算行业地位综合评分"""
        try:
            score_components = []
            
            # 相对ROE表现评分 (30%)
            roe_score = 50  # 默认分数
            if metrics.company_vs_industry_roe is not None:
                if metrics.company_vs_industry_roe > 10:
                    roe_score = 95
                elif metrics.company_vs_industry_roe > 5:
                    roe_score = 85
                elif metrics.company_vs_industry_roe > 0:
                    roe_score = 70
                elif metrics.company_vs_industry_roe > -5:
                    roe_score = 50
                else:
                    roe_score = 30
            
            score_components.append(roe_score * self.analysis_weights['profitability_comparison'])
            
            # 相对利润率表现评分 (25%)
            margin_score = 50
            if metrics.company_vs_industry_margin is not None:
                if metrics.company_vs_industry_margin > 5:
                    margin_score = 90
                elif metrics.company_vs_industry_margin > 2:
                    margin_score = 80
                elif metrics.company_vs_industry_margin > 0:
                    margin_score = 70
                elif metrics.company_vs_industry_margin > -2:
                    margin_score = 50
                else:
                    margin_score = 30
            
            score_components.append(margin_score * self.analysis_weights['market_position'])
            
            # 其他权重使用默认分数
            remaining_weights = (
                self.analysis_weights['growth_comparison'] +
                self.analysis_weights['operational_efficiency'] +
                self.analysis_weights['financial_health']
            )
            score_components.append(60 * remaining_weights)
            
            # 计算总分
            overall_score = sum(score_components)
            
            # 确定评级
            position_grade = 'D'
            for grade, threshold in self.position_grades.items():
                if overall_score >= threshold:
                    position_grade = grade
                    break
            
            return round(overall_score, 2), position_grade
            
        except Exception as e:
            logger.error(f"计算行业评分错误: {e}")
            return 50.0, 'C'
    
    def _generate_industry_summary(self, symbol: str, metrics: IndustryMetrics, 
                                 analysis_results: Dict[str, Any]) -> str:
        """生成行业分析摘要"""
        try:
            summary_parts = [
                f"## {symbol} 行业地位分析报告",
                f"**行业地位评级:** {metrics.industry_position_grade} ({metrics.competitive_advantage_score:.1f}/100)",
                "",
                "### 关键行业指标",
            ]
            
            if metrics.industry_avg_roe is not None:
                summary_parts.append(f"- 行业平均ROE: {metrics.industry_avg_roe:.2f}%")
            
            if metrics.company_vs_industry_roe is not None:
                direction = "超越" if metrics.company_vs_industry_roe > 0 else "低于"
                summary_parts.append(f"- ROE相对表现: {direction}行业平均{abs(metrics.company_vs_industry_roe):.2f}%")
            
            if metrics.company_vs_industry_margin is not None:
                direction = "超越" if metrics.company_vs_industry_margin > 0 else "低于"
                summary_parts.append(f"- 净利率相对表现: {direction}行业平均{abs(metrics.company_vs_industry_margin):.2f}%")
            
            summary_parts.append("")
            summary_parts.append("### 分析模块评分")
            
            for module_name, result in analysis_results.items():
                module_title = result.get('module_name', module_name)
                score = result.get('score', 0)
                summary_parts.append(f"- {module_title}: {score}/100")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成行业分析摘要错误: {e}")
            return f"{symbol} 行业分析报告生成失败"
    
    def _extract_competitive_advantages(self, metrics: IndustryMetrics, 
                                      analysis_results: Dict[str, Any]) -> List[str]:
        """提取竞争优势"""
        advantages = []
        
        try:
            for result in analysis_results.values():
                insights = result.get('insights', [])
                # 筛选包含"优势"、"超越"、"优秀"等关键词的洞察
                for insight in insights:
                    if any(keyword in insight for keyword in ['优势', '超越', '优秀', '显著', '强劲']):
                        advantages.append(insight)
            
            # 去重并限制数量
            advantages = list(set(advantages))[:8]
            
        except Exception as e:
            logger.error(f"提取竞争优势错误: {e}")
        
        return advantages
    
    def _identify_industry_risks(self, metrics: IndustryMetrics, 
                               analysis_results: Dict[str, Any]) -> List[str]:
        """识别行业风险"""
        risks = []
        
        try:
            for result in analysis_results.values():
                risks.extend(result.get('concerns', []))
            
            # 添加基于指标的风险评估
            if metrics.company_vs_industry_roe is not None and metrics.company_vs_industry_roe < -5:
                risks.append("ROE显著低于行业平均水平，竞争地位堪忧")
            
            if metrics.competitive_advantage_score and metrics.competitive_advantage_score < 40:
                risks.append("行业竞争地位较弱，面临较大竞争压力")
            
        except Exception as e:
            logger.error(f"识别行业风险错误: {e}")
        
        return risks[:8]  # 限制最多8个风险

# 工具函数
async def create_industry_analysis_agent(config: Dict[str, Any], 
                                       ashare_toolkit: AShareToolkit) -> IndustryAnalysisAgent:
    """创建行业分析Agent实例"""
    return IndustryAnalysisAgent(config, ashare_toolkit)