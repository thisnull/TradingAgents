"""
报告整合Agent
整合所有分析结果，使用金字塔原理生成最终投资分析报告
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from ..utils.analysis_states import (
    AnalysisResult,
    InvestmentRecommendation,
    AnalysisStatus,
    FinancialAnalysisResult,
    IndustryAnalysisResult,
    ValuationAnalysisResult,
    DataSource
)
from ..agents.financial_analysis_agent import FinancialMetrics
from ..agents.industry_analysis_agent import IndustryMetrics  
from ..agents.valuation_analysis_agent import ValuationMetrics, MarketSignal

logger = logging.getLogger(__name__)

@dataclass
class IntegratedMetrics:
    """整合分析指标"""
    # 综合评分
    financial_score: Optional[float] = None
    industry_score: Optional[float] = None
    valuation_score: Optional[float] = None
    overall_score: Optional[float] = None
    
    # 综合评级
    overall_grade: Optional[str] = None
    confidence_level: Optional[str] = None
    
    # 投资建议
    investment_action: Optional[str] = None  # buy/hold/sell
    position_size_suggestion: Optional[str] = None  # large/medium/small
    holding_period_suggestion: Optional[str] = None  # short/medium/long
    
    # 风险评估
    risk_level: Optional[str] = None  # low/medium/high
    risk_reward_ratio: Optional[float] = None

class ReportIntegrationAgent:
    """报告整合Agent - 整合所有分析生成最终投资报告"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # 整合权重配置
        self.integration_weights = config.get('integration_weights', {
            'financial_analysis': 0.40,    # 财务分析权重
            'industry_analysis': 0.30,     # 行业分析权重
            'valuation_analysis': 0.30     # 估值分析权重
        })
        
        # 评级标准
        self.overall_grades = {
            'A+': 90, 'A': 80, 'A-': 70,
            'B+': 60, 'B': 50, 'B-': 40,
            'C+': 30, 'C': 20, 'C-': 10,
            'D': 0
        }
        
        # 投资建议阈值
        self.investment_thresholds = {
            'strong_buy': 85,
            'buy': 70,
            'hold': 50,
            'sell': 30,
            'strong_sell': 0
        }
    
    async def integrate_analysis_results(self, 
                                       symbol: str,
                                       financial_result: FinancialAnalysisResult,
                                       industry_result: IndustryAnalysisResult,
                                       valuation_result: ValuationAnalysisResult) -> AnalysisResult:
        """
        整合所有分析结果生成最终报告
        
        Args:
            symbol: 股票代码
            financial_result: 财务分析结果
            industry_result: 行业分析结果  
            valuation_result: 估值分析结果
        
        Returns:
            AnalysisResult: 整合分析结果
        """
        logger.info(f"开始整合分析结果: {symbol}")
        
        try:
            # 1. 提取各模块评分
            integrated_metrics = self._extract_module_scores(
                financial_result, industry_result, valuation_result
            )
            
            # 2. 计算综合评分
            overall_score, overall_grade = self._calculate_overall_score(integrated_metrics)
            integrated_metrics.overall_score = overall_score
            integrated_metrics.overall_grade = overall_grade
            
            # 3. 生成投资建议
            investment_recommendation = self._generate_investment_recommendation(
                symbol, integrated_metrics, financial_result, industry_result, valuation_result
            )
            
            # 4. 使用金字塔原理生成报告
            final_report = self._generate_pyramid_report(
                symbol, integrated_metrics, financial_result, industry_result, valuation_result
            )
            
            # 5. 整合关键洞察
            key_insights = self._integrate_key_insights(
                financial_result, industry_result, valuation_result
            )
            
            # 6. 整合风险因素
            risk_factors = self._integrate_risk_factors(
                financial_result, industry_result, valuation_result
            )
            
            # 7. 整合数据源
            all_data_sources = self._integrate_data_sources(
                financial_result, industry_result, valuation_result
            )
            
            return AnalysisResult(
                symbol=symbol,
                analysis_date=datetime.now(),
                status=AnalysisStatus.COMPLETED,
                financial_analysis=financial_result,
                industry_analysis=industry_result,
                valuation_analysis=valuation_result,
                investment_recommendation=investment_recommendation,
                integrated_metrics=integrated_metrics,
                final_report=final_report,
                key_insights=key_insights,
                risk_factors=risk_factors,
                data_sources=all_data_sources
            )
            
        except Exception as e:
            logger.error(f"整合分析结果失败 {symbol}: {e}")
            return AnalysisResult(
                symbol=symbol,
                status=AnalysisStatus.FAILED,
                error_message=f"报告整合错误: {str(e)}"
            )
    
    def _extract_module_scores(self, 
                              financial_result: FinancialAnalysisResult,
                              industry_result: IndustryAnalysisResult,
                              valuation_result: ValuationAnalysisResult) -> IntegratedMetrics:
        """提取各模块评分"""
        metrics = IntegratedMetrics()
        
        try:
            # 财务分析评分
            if financial_result.status == AnalysisStatus.COMPLETED and financial_result.financial_metrics:
                metrics.financial_score = financial_result.financial_metrics.overall_score
            
            # 行业分析评分
            if industry_result.status == AnalysisStatus.COMPLETED and industry_result.industry_metrics:
                metrics.industry_score = industry_result.industry_metrics.competitive_advantage_score
            
            # 估值分析评分
            if valuation_result.status == AnalysisStatus.COMPLETED and valuation_result.valuation_metrics:
                metrics.valuation_score = valuation_result.valuation_metrics.valuation_score
            
        except Exception as e:
            logger.error(f"提取模块评分错误: {e}")
        
        return metrics
    
    def _calculate_overall_score(self, metrics: IntegratedMetrics) -> Tuple[float, str]:
        """计算综合评分"""
        try:
            score_components = []
            
            # 财务分析评分
            if metrics.financial_score is not None:
                score_components.append(
                    metrics.financial_score * self.integration_weights['financial_analysis']
                )
            else:
                score_components.append(50 * self.integration_weights['financial_analysis'])
            
            # 行业分析评分
            if metrics.industry_score is not None:
                score_components.append(
                    metrics.industry_score * self.integration_weights['industry_analysis']
                )
            else:
                score_components.append(50 * self.integration_weights['industry_analysis'])
            
            # 估值分析评分
            if metrics.valuation_score is not None:
                score_components.append(
                    metrics.valuation_score * self.integration_weights['valuation_analysis']
                )
            else:
                score_components.append(50 * self.integration_weights['valuation_analysis'])
            
            # 计算总分
            overall_score = sum(score_components)
            
            # 确定评级
            overall_grade = 'D'
            for grade, threshold in self.overall_grades.items():
                if overall_score >= threshold:
                    overall_grade = grade
                    break
            
            return round(overall_score, 2), overall_grade
            
        except Exception as e:
            logger.error(f"计算综合评分错误: {e}")
            return 50.0, 'C'
    
    def _generate_investment_recommendation(self, 
                                          symbol: str,
                                          metrics: IntegratedMetrics,
                                          financial_result: FinancialAnalysisResult,
                                          industry_result: IndustryAnalysisResult,
                                          valuation_result: ValuationAnalysisResult) -> InvestmentRecommendation:
        """生成投资建议"""
        try:
            # 基于综合评分确定投资行动
            if metrics.overall_score >= self.investment_thresholds['strong_buy']:
                investment_action = 'strong_buy'
                position_size = 'large'
                confidence = 'high'
            elif metrics.overall_score >= self.investment_thresholds['buy']:
                investment_action = 'buy'
                position_size = 'medium'
                confidence = 'medium'
            elif metrics.overall_score >= self.investment_thresholds['hold']:
                investment_action = 'hold'
                position_size = 'small'
                confidence = 'medium'
            elif metrics.overall_score >= self.investment_thresholds['sell']:
                investment_action = 'sell'
                position_size = 'small'
                confidence = 'medium'
            else:
                investment_action = 'strong_sell'
                position_size = 'small'
                confidence = 'high'
            
            # 基于估值分析调整建议
            if (valuation_result.status == AnalysisStatus.COMPLETED and 
                valuation_result.valuation_metrics and 
                valuation_result.valuation_metrics.investment_timing):
                
                valuation_timing = valuation_result.valuation_metrics.investment_timing
                if valuation_timing == 'buy' and investment_action in ['hold', 'sell']:
                    investment_action = 'buy'
                elif valuation_timing == 'sell' and investment_action in ['buy', 'strong_buy']:
                    investment_action = 'hold'
            
            # 确定持有期建议
            holding_period = 'medium'  # 默认中期
            if investment_action in ['strong_buy', 'buy']:
                holding_period = 'long'
            elif investment_action in ['sell', 'strong_sell']:
                holding_period = 'short'
            
            # 风险评估
            risk_level = self._assess_risk_level(financial_result, industry_result, valuation_result)
            
            # 目标价位估算
            target_price_range = self._estimate_target_price(
                symbol, financial_result, valuation_result
            )
            
            return InvestmentRecommendation(
                symbol=symbol,
                recommendation_date=datetime.now(),
                investment_action=investment_action,
                target_price_range=target_price_range,
                holding_period=holding_period,
                position_size_suggestion=position_size,
                confidence_level=confidence,
                risk_level=risk_level,
                key_reasons=[
                    f"综合评分: {metrics.overall_score:.1f}/100 ({metrics.overall_grade})",
                    f"财务质量: {metrics.financial_score:.1f}/100" if metrics.financial_score else "财务数据不足",
                    f"行业地位: {metrics.industry_score:.1f}/100" if metrics.industry_score else "行业数据不足", 
                    f"估值水平: {metrics.valuation_score:.1f}/100" if metrics.valuation_score else "估值数据不足"
                ]
            )
            
        except Exception as e:
            logger.error(f"生成投资建议错误: {e}")
            return InvestmentRecommendation(
                symbol=symbol,
                recommendation_date=datetime.now(),
                investment_action='hold',
                confidence_level='low',
                key_reasons=["分析过程中出现错误，建议谨慎投资"]
            )
    
    def _assess_risk_level(self, 
                          financial_result: FinancialAnalysisResult,
                          industry_result: IndustryAnalysisResult,
                          valuation_result: ValuationAnalysisResult) -> str:
        """评估风险水平"""
        try:
            risk_factors = 0
            
            # 财务风险评估
            if financial_result.financial_metrics:
                if (financial_result.financial_metrics.debt_ratio and 
                    financial_result.financial_metrics.debt_ratio > 70):
                    risk_factors += 1
                if (financial_result.financial_metrics.roe and 
                    financial_result.financial_metrics.roe < 5):
                    risk_factors += 1
                if (financial_result.financial_metrics.current_ratio and 
                    financial_result.financial_metrics.current_ratio < 1.0):
                    risk_factors += 1
            
            # 行业风险评估
            if industry_result.industry_metrics:
                if (industry_result.industry_metrics.competitive_advantage_score and
                    industry_result.industry_metrics.competitive_advantage_score < 40):
                    risk_factors += 1
            
            # 估值风险评估
            if valuation_result.valuation_metrics:
                if (valuation_result.valuation_metrics.pr_assessment in 
                    ['overvalued', 'severely_overvalued']):
                    risk_factors += 1
                if (valuation_result.valuation_metrics.volatility_level == 'high'):
                    risk_factors += 1
            
            # 根据风险因素数量确定风险等级
            if risk_factors >= 4:
                return 'high'
            elif risk_factors >= 2:
                return 'medium'
            else:
                return 'low'
            
        except Exception as e:
            logger.error(f"评估风险水平错误: {e}")
            return 'medium'
    
    def _estimate_target_price(self, symbol: str,
                             financial_result: FinancialAnalysisResult,
                             valuation_result: ValuationAnalysisResult) -> Optional[Tuple[float, float]]:
        """估算目标价位区间"""
        try:
            # 由于缺乏当前股价数据，这里返回None
            # 实际实现需要获取当前股价并基于估值模型计算目标价
            return None
            
        except Exception as e:
            logger.error(f"估算目标价位错误: {e}")
            return None
    
    def _generate_pyramid_report(self, 
                               symbol: str,
                               metrics: IntegratedMetrics,
                               financial_result: FinancialAnalysisResult,
                               industry_result: IndustryAnalysisResult,
                               valuation_result: ValuationAnalysisResult) -> str:
        """使用金字塔原理生成最终报告"""
        try:
            report_sections = []
            
            # === 第1层：核心结论 ===
            report_sections.append("# 投资分析报告")
            report_sections.append(f"## 股票代码：{symbol}")
            report_sections.append(f"## 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
            report_sections.append("")
            
            # 核心结论
            report_sections.append("## 📊 核心结论")
            report_sections.append(f"**综合评级：{metrics.overall_grade} ({metrics.overall_score:.1f}/100)**")
            
            # 投资建议
            action_display = {
                'strong_buy': '强烈买入 🟢',
                'buy': '买入 🟢', 
                'hold': '持有 🟡',
                'sell': '卖出 🔴',
                'strong_sell': '强烈卖出 🔴'
            }
            
            if hasattr(metrics, 'investment_action') and metrics.investment_action:
                action_text = action_display.get(metrics.investment_action, '持有')
                report_sections.append(f"**投资建议：{action_text}**")
            
            report_sections.append("")
            
            # === 第2层：关键支撑论据 ===
            report_sections.append("## 🎯 关键支撑论据")
            
            # 财务分析要点
            if financial_result.status == AnalysisStatus.COMPLETED:
                report_sections.append("### 💰 财务质量分析")
                if financial_result.financial_metrics:
                    fm = financial_result.financial_metrics
                    report_sections.append(f"- **财务评级**：{fm.quality_grade} ({fm.overall_score:.1f}/100)")
                    if fm.roe:
                        report_sections.append(f"- **ROE水平**：{fm.roe:.2f}%")
                    if fm.debt_ratio:
                        report_sections.append(f"- **负债率**：{fm.debt_ratio:.2f}%")
                    if fm.current_ratio:
                        report_sections.append(f"- **流动比率**：{fm.current_ratio:.2f}")
                
                # 财务亮点
                if financial_result.key_insights:
                    report_sections.append("- **财务亮点**：")
                    for insight in financial_result.key_insights[:3]:
                        report_sections.append(f"  - {insight}")
                report_sections.append("")
            
            # 行业地位分析要点
            if industry_result.status == AnalysisStatus.COMPLETED:
                report_sections.append("### 🏭 行业地位分析")
                if industry_result.industry_metrics:
                    im = industry_result.industry_metrics
                    report_sections.append(f"- **行业地位**：{im.industry_position_grade} ({im.competitive_advantage_score:.1f}/100)")
                    if im.company_vs_industry_roe:
                        direction = "超越" if im.company_vs_industry_roe > 0 else "低于"
                        report_sections.append(f"- **ROE相对表现**：{direction}行业平均{abs(im.company_vs_industry_roe):.1f}%")
                
                # 竞争优势
                if industry_result.competitive_advantages:
                    report_sections.append("- **竞争优势**：")
                    for advantage in industry_result.competitive_advantages[:3]:
                        report_sections.append(f"  - {advantage}")
                report_sections.append("")
            
            # 估值分析要点
            if valuation_result.status == AnalysisStatus.COMPLETED:
                report_sections.append("### 📈 估值水平分析")
                if valuation_result.valuation_metrics:
                    vm = valuation_result.valuation_metrics
                    report_sections.append(f"- **估值评级**：{vm.valuation_grade} ({vm.valuation_score:.1f}/100)")
                    if vm.pr_ratio and vm.pr_assessment:
                        assessment_map = {
                            'severely_undervalued': '严重低估',
                            'undervalued': '低估',
                            'fairly_valued': '合理估值',
                            'overvalued': '高估',
                            'severely_overvalued': '严重高估'
                        }
                        assessment_text = assessment_map.get(vm.pr_assessment, vm.pr_assessment)
                        report_sections.append(f"- **PR估值模型**：{vm.pr_ratio:.2f} ({assessment_text})")
                    if vm.pe_ratio:
                        report_sections.append(f"- **PE比率**：{vm.pe_ratio:.2f}")
                
                # 市场信号
                if valuation_result.market_signals:
                    report_sections.append("- **关键市场信号**：")
                    for signal in valuation_result.market_signals[:3]:
                        impact_emoji = "🟢" if signal.impact == 'positive' else "🔴" if signal.impact == 'negative' else "🟡"
                        report_sections.append(f"  - {impact_emoji} {signal.description}")
                report_sections.append("")
            
            # === 第3层：详细分析数据 ===
            report_sections.append("## 📋 详细分析数据")
            
            # 评分矩阵
            report_sections.append("### 评分矩阵")
            report_sections.append("| 分析维度 | 评分 | 权重 | 加权得分 |")
            report_sections.append("|---------|------|------|----------|")
            
            if metrics.financial_score:
                weighted_score = metrics.financial_score * self.integration_weights['financial_analysis']
                report_sections.append(f"| 财务分析 | {metrics.financial_score:.1f} | {self.integration_weights['financial_analysis']*100:.0f}% | {weighted_score:.1f} |")
            
            if metrics.industry_score:
                weighted_score = metrics.industry_score * self.integration_weights['industry_analysis']
                report_sections.append(f"| 行业分析 | {metrics.industry_score:.1f} | {self.integration_weights['industry_analysis']*100:.0f}% | {weighted_score:.1f} |")
            
            if metrics.valuation_score:
                weighted_score = metrics.valuation_score * self.integration_weights['valuation_analysis']
                report_sections.append(f"| 估值分析 | {metrics.valuation_score:.1f} | {self.integration_weights['valuation_analysis']*100:.0f}% | {weighted_score:.1f} |")
            
            report_sections.append(f"| **综合得分** | **{metrics.overall_score:.1f}** | **100%** | **{metrics.overall_score:.1f}** |")
            report_sections.append("")
            
            # 风险提示
            report_sections.append("## ⚠️ 风险提示")
            all_risks = []
            
            if financial_result.risk_factors:
                all_risks.extend(financial_result.risk_factors)
            if industry_result.industry_risks:
                all_risks.extend(industry_result.industry_risks)
            if valuation_result.valuation_risks:
                all_risks.extend(valuation_result.valuation_risks)
            
            if all_risks:
                for risk in all_risks[:5]:  # 最多5个风险
                    report_sections.append(f"- {risk}")
            else:
                report_sections.append("- 基于当前分析，未发现重大风险因素")
            
            report_sections.append("")
            
            # 数据来源说明
            report_sections.append("## 📝 数据来源说明")
            report_sections.append("本报告基于以下数据源进行分析：")
            report_sections.append("- A股财务数据API (财务报表、财务比率)")
            report_sections.append("- A股行情数据API (价格、交易量)")
            report_sections.append("- 股票基础信息API (公司基本面)")
            if valuation_result.valuation_metrics and hasattr(valuation_result.valuation_metrics, 'pr_ratio'):
                report_sections.append("- PR估值模型 (PE/ROE比率分析)")
            
            report_sections.append("")
            report_sections.append("---")
            report_sections.append("*本报告仅供参考，不构成投资建议。投资有风险，决策需谨慎。*")
            
            return "\n".join(report_sections)
            
        except Exception as e:
            logger.error(f"生成金字塔报告错误: {e}")
            return f"# {symbol} 投资分析报告\n\n报告生成失败，请检查数据完整性。"
    
    def _integrate_key_insights(self, 
                              financial_result: FinancialAnalysisResult,
                              industry_result: IndustryAnalysisResult,
                              valuation_result: ValuationAnalysisResult) -> List[str]:
        """整合关键洞察"""
        all_insights = []
        
        try:
            # 收集各模块的洞察
            if financial_result.key_insights:
                all_insights.extend([f"[财务] {insight}" for insight in financial_result.key_insights])
            
            if industry_result.competitive_advantages:
                all_insights.extend([f"[行业] {insight}" for insight in industry_result.competitive_advantages])
            
            if valuation_result.market_signals:
                signal_insights = [f"[估值] {signal.description}" for signal in valuation_result.market_signals if signal.impact == 'positive']
                all_insights.extend(signal_insights)
            
            # 去重并限制数量
            unique_insights = list(dict.fromkeys(all_insights))  # 保持顺序去重
            return unique_insights[:10]  # 最多10个洞察
            
        except Exception as e:
            logger.error(f"整合关键洞察错误: {e}")
            return ["分析过程中出现错误"]
    
    def _integrate_risk_factors(self, 
                              financial_result: FinancialAnalysisResult,
                              industry_result: IndustryAnalysisResult,
                              valuation_result: ValuationAnalysisResult) -> List[str]:
        """整合风险因素"""
        all_risks = []
        
        try:
            # 收集各模块的风险
            if financial_result.risk_factors:
                all_risks.extend([f"[财务风险] {risk}" for risk in financial_result.risk_factors])
            
            if industry_result.industry_risks:
                all_risks.extend([f"[行业风险] {risk}" for risk in industry_result.industry_risks])
            
            if valuation_result.valuation_risks:
                all_risks.extend([f"[估值风险] {risk}" for risk in valuation_result.valuation_risks])
            
            # 去重并限制数量
            unique_risks = list(dict.fromkeys(all_risks))
            return unique_risks[:10]  # 最多10个风险
            
        except Exception as e:
            logger.error(f"整合风险因素错误: {e}")
            return ["分析过程中出现错误"]
    
    def _integrate_data_sources(self, 
                              financial_result: FinancialAnalysisResult,
                              industry_result: IndustryAnalysisResult,
                              valuation_result: ValuationAnalysisResult) -> List[DataSource]:
        """整合数据源"""
        all_sources = []
        
        try:
            if financial_result.data_sources:
                all_sources.extend(financial_result.data_sources)
            
            if industry_result.data_sources:
                all_sources.extend(industry_result.data_sources)
            
            if valuation_result.data_sources:
                all_sources.extend(valuation_result.data_sources)
            
            # 去重（基于name和endpoint）
            unique_sources = []
            seen = set()
            for source in all_sources:
                key = (source.name, source.endpoint)
                if key not in seen:
                    unique_sources.append(source)
                    seen.add(key)
            
            return unique_sources
            
        except Exception as e:
            logger.error(f"整合数据源错误: {e}")
            return []

# 工具函数
async def create_report_integration_agent(config: Dict[str, Any]) -> ReportIntegrationAgent:
    """创建报告整合Agent实例"""
    return ReportIntegrationAgent(config)