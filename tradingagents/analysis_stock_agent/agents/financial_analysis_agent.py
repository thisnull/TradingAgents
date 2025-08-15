"""
财务分析Agent
分析股票的核心财务指标，生成财务质量评估报告
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from ..tools.ashare_toolkit import AShareToolkit, AShareAPIError
from ..utils.analysis_states import (
    FinancialAnalysisResult, 
    AnalysisStatus,
    DataSource
)
from ..utils.data_validator import DataValidator, DataQualityChecker

logger = logging.getLogger(__name__)

@dataclass
class FinancialMetrics:
    """财务指标数据结构"""
    # 营收和利润指标
    revenue_growth_rate: Optional[float] = None
    profit_growth_rate: Optional[float] = None  
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    
    # ROE相关指标
    roe: Optional[float] = None
    roa: Optional[float] = None
    roe_stability: Optional[float] = None
    dupont_analysis: Optional[Dict[str, float]] = None
    
    # 资产负债指标
    debt_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    asset_turnover: Optional[float] = None
    
    # 现金流指标
    operating_cf_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None
    cf_to_revenue_ratio: Optional[float] = None
    
    # 股东回报指标
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    share_buyback_ratio: Optional[float] = None
    
    # 综合评分
    overall_score: Optional[float] = None
    quality_grade: Optional[str] = None

class FinancialAnalysisAgent:
    """财务分析Agent - 分析股票核心财务指标"""
    
    def __init__(self, config: Dict[str, Any], ashare_toolkit: AShareToolkit):
        self.config = config
        self.ashare_toolkit = ashare_toolkit
        
        # 评分权重配置
        self.scoring_weights = config.get('scoring_weights', {
            'profitability': 0.25,  # 盈利能力
            'efficiency': 0.20,     # 运营效率
            'solvency': 0.20,       # 偿债能力
            'cash_flow': 0.20,      # 现金流质量
            'shareholder_returns': 0.15  # 股东回报
        })
        
        # 评级标准
        self.grade_thresholds = {
            'A+': 90, 'A': 80, 'A-': 70,
            'B+': 60, 'B': 50, 'B-': 40,
            'C+': 30, 'C': 20, 'C-': 10,
            'D': 0
        }
    
    async def analyze_financial_performance(self, symbol: str, 
                                          analysis_period: int = 3) -> FinancialAnalysisResult:
        """
        分析股票财务表现
        
        Args:
            symbol: 股票代码
            analysis_period: 分析年限，默认3年
        
        Returns:
            FinancialAnalysisResult: 财务分析结果
        """
        logger.info(f"开始财务分析: {symbol}")
        
        try:
            # 1. 数据收集
            financial_data = await self._collect_financial_data(symbol, analysis_period)
            
            if not financial_data:
                return FinancialAnalysisResult(
                    symbol=symbol,
                    status=AnalysisStatus.FAILED,
                    error_message="无法获取财务数据"
                )
            
            # 2. 计算财务指标
            metrics = await self._calculate_financial_metrics(financial_data)
            
            # 3. 执行5个分析模块
            analysis_results = {}
            
            # 模块1: 营收和利润分析
            analysis_results['revenue_profit'] = await self._analyze_revenue_profit(financial_data, metrics)
            
            # 模块2: ROE分析
            analysis_results['roe_analysis'] = await self._analyze_roe(financial_data, metrics)
            
            # 模块3: 资产负债表分析
            analysis_results['balance_sheet'] = await self._analyze_balance_sheet(financial_data, metrics)
            
            # 模块4: 现金流分析
            analysis_results['cash_flow'] = await self._analyze_cash_flow(financial_data, metrics)
            
            # 模块5: 股东回报分析
            analysis_results['shareholder_returns'] = await self._analyze_shareholder_returns(financial_data, metrics)
            
            # 4. 综合评分
            overall_score, quality_grade = self._calculate_overall_score(metrics)
            metrics.overall_score = overall_score
            metrics.quality_grade = quality_grade
            
            # 5. 生成分析报告
            analysis_summary = self._generate_analysis_summary(symbol, metrics, analysis_results)
            key_insights = self._extract_key_insights(metrics, analysis_results)
            risk_factors = self._identify_risk_factors(metrics, analysis_results)
            
            return FinancialAnalysisResult(
                symbol=symbol,
                analysis_date=datetime.now(),
                status=AnalysisStatus.COMPLETED,
                financial_metrics=metrics,
                analysis_summary=analysis_summary,
                key_insights=key_insights,
                risk_factors=risk_factors,
                data_sources=[
                    DataSource(
                        name="A股财务数据API",
                        endpoint="/financial/reports",
                        version="v1.1.0"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"财务分析失败 {symbol}: {e}")
            return FinancialAnalysisResult(
                symbol=symbol,
                status=AnalysisStatus.FAILED,
                error_message=f"财务分析错误: {str(e)}"
            )
    
    async def _collect_financial_data(self, symbol: str, years: int) -> Dict[str, Any]:
        """收集财务数据"""
        try:
            # 获取最新财务报表
            reports_result = await self.ashare_toolkit.get_financial_reports(
                symbol=symbol,
                limit=years * 4  # 季报数据
            )
            
            # 获取财务比率
            ratios_result = await self.ashare_toolkit.get_financial_ratios(symbol)
            
            # 获取财务摘要
            summary_result = await self.ashare_toolkit.get_financial_summary(symbol, years)
            
            # 整合数据
            financial_data = {
                'reports': reports_result.get('data', []) if reports_result.get('success') else [],
                'ratios': ratios_result.get('data', {}) if ratios_result.get('success') else {},
                'summary': summary_result.get('data', {}) if summary_result.get('success') else {}
            }
            
            return financial_data
            
        except AShareAPIError as e:
            logger.error(f"获取财务数据失败: {e}")
            return {}
    
    async def _calculate_financial_metrics(self, financial_data: Dict[str, Any]) -> FinancialMetrics:
        """计算财务指标"""
        metrics = FinancialMetrics()
        
        reports = financial_data.get('reports', [])
        ratios = financial_data.get('ratios', {})
        
        if not reports:
            logger.warning("财务报表数据为空")
            return metrics
        
        try:
            # 计算营收和利润增长率
            if len(reports) >= 2:
                latest_revenue = reports[0].get('total_revenue', 0)
                prev_revenue = reports[1].get('total_revenue', 0)
                if prev_revenue > 0:
                    metrics.revenue_growth_rate = ((latest_revenue - prev_revenue) / prev_revenue) * 100
                
                latest_profit = reports[0].get('net_profit', 0)
                prev_profit = reports[1].get('net_profit', 0)
                if prev_profit > 0:
                    metrics.profit_growth_rate = ((latest_profit - prev_profit) / prev_profit) * 100
            
            # 从比率数据中提取指标
            if ratios:
                metrics.roe = ratios.get('roe')
                metrics.roa = ratios.get('roa')
                metrics.gross_margin = ratios.get('gross_profit_margin')
                metrics.net_margin = ratios.get('net_profit_margin')
                metrics.debt_ratio = ratios.get('debt_to_asset_ratio')
                metrics.current_ratio = ratios.get('current_ratio')
                metrics.quick_ratio = ratios.get('quick_ratio')
            
            # 计算ROE稳定性（过去几年ROE的标准差）
            if len(reports) >= 3:
                roe_values = []
                for report in reports[:4]:  # 最近4个季度
                    roe = report.get('roe')
                    if roe is not None:
                        roe_values.append(float(roe))
                
                if len(roe_values) >= 3:
                    import statistics
                    metrics.roe_stability = statistics.stdev(roe_values)
            
            # 计算现金流指标
            if reports:
                latest_report = reports[0]
                operating_cf = latest_report.get('operating_cash_flow', 0)
                total_revenue = latest_report.get('total_revenue', 0)
                
                if total_revenue > 0:
                    metrics.cf_to_revenue_ratio = (operating_cf / total_revenue) * 100
                
                # 自由现金流 = 经营现金流 - 资本支出
                capex = latest_report.get('capital_expenditure', 0)
                metrics.free_cash_flow = operating_cf - capex if capex else operating_cf
            
        except Exception as e:
            logger.error(f"计算财务指标时出错: {e}")
        
        return metrics
    
    async def _analyze_revenue_profit(self, financial_data: Dict[str, Any], 
                                    metrics: FinancialMetrics) -> Dict[str, Any]:
        """分析营收和利润"""
        analysis = {
            'module_name': '营收和利润分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 营收增长评估
            if metrics.revenue_growth_rate is not None:
                if metrics.revenue_growth_rate > 20:
                    analysis['score'] += 25
                    analysis['insights'].append(f"营收增长强劲：{metrics.revenue_growth_rate:.1f}%")
                elif metrics.revenue_growth_rate > 10:
                    analysis['score'] += 20
                    analysis['insights'].append(f"营收增长良好：{metrics.revenue_growth_rate:.1f}%")
                elif metrics.revenue_growth_rate > 0:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"营收下降：{metrics.revenue_growth_rate:.1f}%")
            
            # 利润增长评估
            if metrics.profit_growth_rate is not None:
                if metrics.profit_growth_rate > 20:
                    analysis['score'] += 25
                    analysis['insights'].append(f"利润增长优秀：{metrics.profit_growth_rate:.1f}%")
                elif metrics.profit_growth_rate > 10:
                    analysis['score'] += 20
                elif metrics.profit_growth_rate > 0:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"利润下降：{metrics.profit_growth_rate:.1f}%")
            
            # 毛利率评估
            if metrics.gross_margin is not None:
                if metrics.gross_margin > 40:
                    analysis['score'] += 25
                    analysis['insights'].append(f"毛利率优秀：{metrics.gross_margin:.1f}%")
                elif metrics.gross_margin > 20:
                    analysis['score'] += 20
                elif metrics.gross_margin > 10:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"毛利率偏低：{metrics.gross_margin:.1f}%")
            
            # 净利率评估
            if metrics.net_margin is not None:
                if metrics.net_margin > 20:
                    analysis['score'] += 25
                    analysis['insights'].append(f"净利率优秀：{metrics.net_margin:.1f}%")
                elif metrics.net_margin > 10:
                    analysis['score'] += 20
                elif metrics.net_margin > 5:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"净利率偏低：{metrics.net_margin:.1f}%")
            
        except Exception as e:
            logger.error(f"营收利润分析错误: {e}")
            analysis['concerns'].append("分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_roe(self, financial_data: Dict[str, Any], 
                         metrics: FinancialMetrics) -> Dict[str, Any]:
        """分析ROE指标"""
        analysis = {
            'module_name': 'ROE分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # ROE水平评估
            if metrics.roe is not None:
                if metrics.roe > 20:
                    analysis['score'] += 40
                    analysis['insights'].append(f"ROE优秀：{metrics.roe:.1f}%")
                elif metrics.roe > 15:
                    analysis['score'] += 30
                    analysis['insights'].append(f"ROE良好：{metrics.roe:.1f}%")
                elif metrics.roe > 10:
                    analysis['score'] += 20
                elif metrics.roe > 0:
                    analysis['score'] += 10
                else:
                    analysis['concerns'].append(f"ROE为负：{metrics.roe:.1f}%")
            
            # ROE稳定性评估
            if metrics.roe_stability is not None:
                if metrics.roe_stability < 3:
                    analysis['score'] += 30
                    analysis['insights'].append(f"ROE稳定性优秀：波动性{metrics.roe_stability:.1f}")
                elif metrics.roe_stability < 5:
                    analysis['score'] += 20
                elif metrics.roe_stability < 10:
                    analysis['score'] += 10
                else:
                    analysis['concerns'].append(f"ROE波动较大：{metrics.roe_stability:.1f}")
            
            # ROA对比分析
            if metrics.roa is not None and metrics.roe is not None:
                if metrics.roa > 10:
                    analysis['insights'].append(f"资产回报率优秀：{metrics.roa:.1f}%")
                elif metrics.roa > 5:
                    analysis['insights'].append(f"资产回报率良好：{metrics.roa:.1f}%")
                else:
                    analysis['concerns'].append(f"资产回报率偏低：{metrics.roa:.1f}%")
                
                # 杠杆分析
                if metrics.roe > metrics.roa * 1.5:
                    analysis['insights'].append("公司有效运用财务杠杆")
                elif metrics.roe < metrics.roa:
                    analysis['concerns'].append("财务杠杆可能存在负面影响")
            
        except Exception as e:
            logger.error(f"ROE分析错误: {e}")
            analysis['concerns'].append("ROE分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_balance_sheet(self, financial_data: Dict[str, Any], 
                                   metrics: FinancialMetrics) -> Dict[str, Any]:
        """分析资产负债表"""
        analysis = {
            'module_name': '资产负债表分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 负债率评估
            if metrics.debt_ratio is not None:
                if metrics.debt_ratio < 30:
                    analysis['score'] += 30
                    analysis['insights'].append(f"负债率健康：{metrics.debt_ratio:.1f}%")
                elif metrics.debt_ratio < 50:
                    analysis['score'] += 25
                elif metrics.debt_ratio < 70:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"负债率偏高：{metrics.debt_ratio:.1f}%")
            
            # 流动比率评估
            if metrics.current_ratio is not None:
                if metrics.current_ratio > 2.0:
                    analysis['score'] += 25
                    analysis['insights'].append(f"流动性充足：流动比率{metrics.current_ratio:.2f}")
                elif metrics.current_ratio > 1.5:
                    analysis['score'] += 20
                elif metrics.current_ratio > 1.0:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"流动性不足：流动比率{metrics.current_ratio:.2f}")
            
            # 速动比率评估
            if metrics.quick_ratio is not None:
                if metrics.quick_ratio > 1.0:
                    analysis['score'] += 25
                    analysis['insights'].append(f"速动比率良好：{metrics.quick_ratio:.2f}")
                elif metrics.quick_ratio > 0.8:
                    analysis['score'] += 20
                elif metrics.quick_ratio > 0.5:
                    analysis['score'] += 15
                else:
                    analysis['concerns'].append(f"速动比率偏低：{metrics.quick_ratio:.2f}")
            
        except Exception as e:
            logger.error(f"资产负债表分析错误: {e}")
            analysis['concerns'].append("资产负债表分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_cash_flow(self, financial_data: Dict[str, Any], 
                               metrics: FinancialMetrics) -> Dict[str, Any]:
        """分析现金流"""
        analysis = {
            'module_name': '现金流分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 现金流/营收比率评估
            if metrics.cf_to_revenue_ratio is not None:
                if metrics.cf_to_revenue_ratio > 15:
                    analysis['score'] += 40
                    analysis['insights'].append(f"现金流质量优秀：现金流/营收={metrics.cf_to_revenue_ratio:.1f}%")
                elif metrics.cf_to_revenue_ratio > 10:
                    analysis['score'] += 30
                elif metrics.cf_to_revenue_ratio > 5:
                    analysis['score'] += 20
                else:
                    analysis['concerns'].append(f"现金流质量偏低：现金流/营收={metrics.cf_to_revenue_ratio:.1f}%")
            
            # 自由现金流评估
            if metrics.free_cash_flow is not None:
                if metrics.free_cash_flow > 0:
                    analysis['score'] += 30
                    analysis['insights'].append(f"自由现金流为正：{metrics.free_cash_flow/10000:.2f}万元")
                else:
                    analysis['concerns'].append(f"自由现金流为负：{metrics.free_cash_flow/10000:.2f}万元")
            
        except Exception as e:
            logger.error(f"现金流分析错误: {e}")
            analysis['concerns'].append("现金流分析过程中出现数据错误")
        
        return analysis
    
    async def _analyze_shareholder_returns(self, financial_data: Dict[str, Any], 
                                         metrics: FinancialMetrics) -> Dict[str, Any]:
        """分析股东回报"""
        analysis = {
            'module_name': '股东回报分析',
            'score': 0,
            'insights': [],
            'concerns': []
        }
        
        try:
            # 这部分数据可能需要从其他API获取
            # 暂时给一个基础分数
            analysis['score'] = 50
            analysis['insights'].append("股东回报分析需要更多数据支持")
            
        except Exception as e:
            logger.error(f"股东回报分析错误: {e}")
            analysis['concerns'].append("股东回报分析过程中出现数据错误")
        
        return analysis
    
    def _calculate_overall_score(self, metrics: FinancialMetrics) -> Tuple[float, str]:
        """计算综合评分"""
        try:
            # 基于各个指标计算加权分数
            scores = []
            
            # 盈利能力分数 (25%)
            profitability_score = 0
            if metrics.roe is not None:
                if metrics.roe > 20:
                    profitability_score += 40
                elif metrics.roe > 15:
                    profitability_score += 30
                elif metrics.roe > 10:
                    profitability_score += 20
                elif metrics.roe > 0:
                    profitability_score += 10
            
            if metrics.net_margin is not None:
                if metrics.net_margin > 20:
                    profitability_score += 30
                elif metrics.net_margin > 10:
                    profitability_score += 20
                elif metrics.net_margin > 5:
                    profitability_score += 10
            
            scores.append(min(100, profitability_score) * self.scoring_weights['profitability'])
            
            # 偿债能力分数 (20%)
            solvency_score = 0
            if metrics.debt_ratio is not None:
                if metrics.debt_ratio < 30:
                    solvency_score += 40
                elif metrics.debt_ratio < 50:
                    solvency_score += 30
                elif metrics.debt_ratio < 70:
                    solvency_score += 20
            
            if metrics.current_ratio is not None:
                if metrics.current_ratio > 2.0:
                    solvency_score += 30
                elif metrics.current_ratio > 1.5:
                    solvency_score += 20
                elif metrics.current_ratio > 1.0:
                    solvency_score += 10
            
            scores.append(min(100, solvency_score) * self.scoring_weights['solvency'])
            
            # 增长能力分数 (20%)
            growth_score = 50  # 默认分数
            if metrics.revenue_growth_rate is not None:
                if metrics.revenue_growth_rate > 20:
                    growth_score = 90
                elif metrics.revenue_growth_rate > 10:
                    growth_score = 80
                elif metrics.revenue_growth_rate > 0:
                    growth_score = 70
                else:
                    growth_score = 30
            
            scores.append(growth_score * self.scoring_weights['efficiency'])
            
            # 现金流分数 (20%)
            cashflow_score = 50  # 默认分数
            if metrics.cf_to_revenue_ratio is not None:
                if metrics.cf_to_revenue_ratio > 15:
                    cashflow_score = 90
                elif metrics.cf_to_revenue_ratio > 10:
                    cashflow_score = 80
                elif metrics.cf_to_revenue_ratio > 5:
                    cashflow_score = 70
                else:
                    cashflow_score = 40
            
            scores.append(cashflow_score * self.scoring_weights['cash_flow'])
            
            # 股东回报分数 (15%)
            shareholder_score = 50  # 默认分数，待完善
            scores.append(shareholder_score * self.scoring_weights['shareholder_returns'])
            
            # 计算总分
            overall_score = sum(scores)
            
            # 确定评级
            quality_grade = 'D'
            for grade, threshold in self.grade_thresholds.items():
                if overall_score >= threshold:
                    quality_grade = grade
                    break
            
            return round(overall_score, 2), quality_grade
            
        except Exception as e:
            logger.error(f"计算综合评分错误: {e}")
            return 50.0, 'C'
    
    def _generate_analysis_summary(self, symbol: str, metrics: FinancialMetrics, 
                                 analysis_results: Dict[str, Any]) -> str:
        """生成分析摘要"""
        try:
            summary_parts = [
                f"## {symbol} 财务分析报告",
                f"**综合评级:** {metrics.quality_grade} ({metrics.overall_score:.1f}/100)",
                "",
                "### 核心财务指标",
            ]
            
            if metrics.roe is not None:
                summary_parts.append(f"- ROE: {metrics.roe:.2f}%")
            if metrics.net_margin is not None:
                summary_parts.append(f"- 净利率: {metrics.net_margin:.2f}%")
            if metrics.debt_ratio is not None:
                summary_parts.append(f"- 负债率: {metrics.debt_ratio:.2f}%")
            if metrics.current_ratio is not None:
                summary_parts.append(f"- 流动比率: {metrics.current_ratio:.2f}")
            
            summary_parts.append("")
            summary_parts.append("### 分析模块评分")
            
            for module_name, result in analysis_results.items():
                module_title = result.get('module_name', module_name)
                score = result.get('score', 0)
                summary_parts.append(f"- {module_title}: {score}/100")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"生成分析摘要错误: {e}")
            return f"{symbol} 财务分析报告生成失败"
    
    def _extract_key_insights(self, metrics: FinancialMetrics, 
                            analysis_results: Dict[str, Any]) -> List[str]:
        """提取关键洞察"""
        insights = []
        
        try:
            for result in analysis_results.values():
                insights.extend(result.get('insights', []))
            
            # 添加综合洞察
            if metrics.overall_score and metrics.overall_score > 80:
                insights.append("公司整体财务状况优秀，值得重点关注")
            elif metrics.overall_score and metrics.overall_score > 60:
                insights.append("公司财务状况良好，但有待进一步观察")
            
        except Exception as e:
            logger.error(f"提取关键洞察错误: {e}")
        
        return insights[:10]  # 限制最多10个洞察
    
    def _identify_risk_factors(self, metrics: FinancialMetrics, 
                             analysis_results: Dict[str, Any]) -> List[str]:
        """识别风险因素"""
        risks = []
        
        try:
            for result in analysis_results.values():
                risks.extend(result.get('concerns', []))
            
            # 添加综合风险评估
            if metrics.overall_score and metrics.overall_score < 40:
                risks.append("公司整体财务状况存在较大风险")
            
        except Exception as e:
            logger.error(f"识别风险因素错误: {e}")
        
        return risks[:10]  # 限制最多10个风险

# 工具函数
async def create_financial_analysis_agent(config: Dict[str, Any], 
                                        ashare_toolkit: AShareToolkit) -> FinancialAnalysisAgent:
    """创建财务分析Agent实例"""
    return FinancialAnalysisAgent(config, ashare_toolkit)