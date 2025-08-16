"""
估值与市场信号分析Agent

专门负责A股公司的估值分析和市场信号解读，包括DCF估值、相对估值、
技术分析、市场情绪指标、资金流向等多个维度的全面分析。
"""

import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ..utils.data_tools import AShareDataTools, DataProcessor
from ..utils.mcp_tools import MCPToolsWrapper
from ..utils.calculation_utils import FinancialCalculator, TechnicalCalculator, ValuationCalculator
from ..utils.state_models import AnalysisStage, AnalysisDepth
from ..prompts.valuation_prompts import (
    VALUATION_ANALYSIS_SYSTEM_PROMPT,
    VALUATION_ANALYSIS_USER_PROMPT,
    VALUATION_SCORING_CRITERIA,
    VALUATION_ANALYSIS_REPORT_TEMPLATE,
    TECHNICAL_INDICATORS_FRAMEWORK
)


logger = logging.getLogger(__name__)


def create_valuation_analyst(llm, toolkit, config):
    """
    创建估值与市场信号分析Agent
    
    Args:
        llm: 语言模型实例
        toolkit: 工具集
        config: 配置字典
        
    Returns:
        估值分析Agent节点函数
    """
    
    # 初始化数据工具
    data_tools = AShareDataTools(config)
    mcp_tools = MCPToolsWrapper(config) if config.get("mcp_tools_enabled") else None
    
    # 创建DCF估值分析工具
    @tool
    def calculate_dcf_valuation(financial_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算DCF估值
        
        Args:
            financial_data: 财务数据
            market_data: 市场数据
            
        Returns:
            DCF估值结果
        """
        try:
            logger.info("Calculating DCF valuation")
            
            financial_reports = financial_data.get("financial_reports", [])
            if not financial_reports:
                return {"error": "缺少财务报表数据"}
            
            # 获取最新财务数据
            latest_report = financial_reports[0] if financial_reports else {}
            
            # 构建DCF模型参数
            dcf_params = {
                "revenue": latest_report.get("total_revenue", 0),
                "net_profit": latest_report.get("net_profit", 0),
                "free_cashflow": latest_report.get("free_cashflow", 0),
                "capex": latest_report.get("capital_expenditure", 0),
                "working_capital": latest_report.get("working_capital", 0),
                "shares_outstanding": market_data.get("total_shares", 1000000000),  # 默认10亿股
                "wacc": config.get("default_wacc", 8.5),  # 默认加权平均成本
                "terminal_growth": config.get("default_terminal_growth", 2.5),  # 默认永续增长率
                "forecast_years": 5
            }
            
            # 计算历史增长率
            if len(financial_reports) >= 3:
                revenues = [report.get("total_revenue", 0) for report in financial_reports[:3]]
                revenue_growth = ValuationCalculator.calculate_cagr(revenues)
                dcf_params["revenue_growth"] = min(max(revenue_growth, -50), 50)  # 限制在-50%到50%之间
            else:
                dcf_params["revenue_growth"] = 10  # 默认增长率
            
            # 执行DCF计算
            dcf_result = ValuationCalculator.dcf_valuation(dcf_params)
            
            # 敏感性分析
            sensitivity_analysis = ValuationCalculator.sensitivity_analysis(
                dcf_params, 
                ["wacc", "terminal_growth", "revenue_growth"]
            )
            
            return {
                "dcf_valuation": dcf_result,
                "sensitivity_analysis": sensitivity_analysis,
                "model_parameters": dcf_params,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating DCF valuation: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_relative_valuation(stock_code: str, financial_data: Dict[str, Any], 
                                   market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算相对估值指标
        
        Args:
            stock_code: 股票代码
            financial_data: 财务数据
            market_data: 市场数据
            
        Returns:
            相对估值分析结果
        """
        try:
            logger.info("Calculating relative valuation")
            
            latest_report = financial_data.get("latest_report", {})
            if not latest_report:
                return {"error": "缺少最新财务报表"}
            
            current_price = market_data.get("current_price", 0)
            market_cap = market_data.get("market_cap", 0)
            
            if current_price <= 0:
                return {"error": "无效的股价数据"}
            
            # 计算基本估值倍数
            valuation_multiples = {}
            
            # PE ratio
            eps = latest_report.get("eps", 0)
            if eps > 0:
                valuation_multiples["pe_ratio"] = current_price / eps
            
            # PB ratio
            book_value_per_share = latest_report.get("book_value_per_share", 0)
            if book_value_per_share > 0:
                valuation_multiples["pb_ratio"] = current_price / book_value_per_share
            
            # PS ratio
            revenue_per_share = latest_report.get("revenue_per_share", 0)
            if revenue_per_share > 0:
                valuation_multiples["ps_ratio"] = current_price / revenue_per_share
            
            # EV/EBITDA
            total_debt = latest_report.get("total_liabilities", 0)
            cash = latest_report.get("cash_and_equivalents", 0)
            enterprise_value = market_cap + total_debt - cash
            ebitda = latest_report.get("ebitda", 0)
            if ebitda > 0:
                valuation_multiples["ev_ebitda"] = enterprise_value / ebitda
            
            # PEG ratio
            growth_rate = financial_data.get("growth_ratios", {}).get("net_profit_yoy", 0)
            if growth_rate > 0 and eps > 0:
                pe_ratio = valuation_multiples.get("pe_ratio", 0)
                valuation_multiples["peg_ratio"] = pe_ratio / growth_rate
            
            # 获取行业平均估值数据（如果可用）
            industry_data = {}
            try:
                # 获取行业成分股估值数据
                industry_info = data_tools.get_stock_industry_hierarchy(stock_code)
                if industry_info:
                    industry_code = industry_info.get("sw_level2_code") or industry_info.get("sw_level1_code")
                    if industry_code:
                        peers = data_tools.get_industry_constituents([industry_code])
                        if peers:
                            # 简化处理：取前10家公司作为对比
                            peer_multiples = []
                            for peer in peers[:10]:
                                peer_code = peer.get("symbol", "")
                                if peer_code and peer_code != stock_code:
                                    peer_latest = data_tools.get_latest_financial_report(peer_code)
                                    if peer_latest:
                                        peer_eps = peer_latest.get("eps", 0)
                                        if peer_eps > 0:
                                            peer_price = 50  # 简化处理，实际需要获取实时股价
                                            peer_multiples.append(peer_price / peer_eps)
                            
                            if peer_multiples:
                                industry_data["industry_avg_pe"] = statistics.mean(peer_multiples)
                                industry_data["industry_median_pe"] = statistics.median(peer_multiples)
            except Exception as e:
                logger.warning(f"Failed to get industry valuation data: {str(e)}")
            
            return {
                "valuation_multiples": valuation_multiples,
                "industry_comparison": industry_data,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating relative valuation: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def analyze_technical_indicators(stock_code: str, analysis_period: str = "1year") -> Dict[str, Any]:
        """
        分析技术指标
        
        Args:
            stock_code: 股票代码
            analysis_period: 分析周期
            
        Returns:
            技术指标分析结果
        """
        try:
            logger.info(f"Analyzing technical indicators for {stock_code}")
            
            # 计算分析期间
            end_date = datetime.now()
            if analysis_period == "1year":
                start_date = end_date - timedelta(days=365)
                limit = 252  # 一年交易日
            elif analysis_period == "6months":
                start_date = end_date - timedelta(days=180)
                limit = 126
            else:
                start_date = end_date - timedelta(days=90)
                limit = 63
            
            # 获取日线数据
            daily_quotes = data_tools.get_daily_quotes(
                stock_code,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                limit=limit
            )
            
            if not daily_quotes:
                return {"error": "无法获取股价数据"}
            
            # 整理价格和成交量数据
            prices = [float(quote.get("close", 0)) for quote in daily_quotes]
            volumes = [float(quote.get("volume", 0)) for quote in daily_quotes]
            highs = [float(quote.get("high", 0)) for quote in daily_quotes]
            lows = [float(quote.get("low", 0)) for quote in daily_quotes]
            
            # 计算技术指标
            technical_indicators = {}
            
            if len(prices) >= 20:  # 确保有足够数据
                # 移动平均线
                ma_5 = TechnicalCalculator.moving_average(prices, 5)
                ma_10 = TechnicalCalculator.moving_average(prices, 10)
                ma_20 = TechnicalCalculator.moving_average(prices, 20)
                
                technical_indicators["moving_averages"] = {
                    "ma_5": ma_5[-1] if ma_5 else 0,
                    "ma_10": ma_10[-1] if ma_10 else 0,
                    "ma_20": ma_20[-1] if ma_20 else 0,
                    "current_price": prices[-1]
                }
                
                # RSI
                rsi = TechnicalCalculator.rsi(prices, 14)
                technical_indicators["rsi"] = {
                    "current_rsi": rsi[-1] if rsi else 50,
                    "signal": "超买" if rsi[-1] > 70 else "超卖" if rsi[-1] < 30 else "中性"
                }
                
                # MACD
                macd_line, signal_line, histogram = TechnicalCalculator.macd(prices)
                technical_indicators["macd"] = {
                    "macd_line": macd_line[-1] if macd_line else 0,
                    "signal_line": signal_line[-1] if signal_line else 0,
                    "histogram": histogram[-1] if histogram else 0,
                    "signal": "金叉" if histogram[-1] > 0 and histogram[-2] <= 0 else "死叉" if histogram[-1] < 0 and histogram[-2] >= 0 else "维持"
                }
                
                # 布林带
                if len(prices) >= 20:
                    bb_upper, bb_middle, bb_lower = TechnicalCalculator.bollinger_bands(prices, 20, 2)
                    technical_indicators["bollinger_bands"] = {
                        "upper_band": bb_upper[-1] if bb_upper else 0,
                        "middle_band": bb_middle[-1] if bb_middle else 0,
                        "lower_band": bb_lower[-1] if bb_lower else 0,
                        "current_price": prices[-1],
                        "position": "上轨附近" if prices[-1] > bb_upper[-1] * 0.98 else "下轨附近" if prices[-1] < bb_lower[-1] * 1.02 else "中轨附近"
                    }
                
                # 成交量分析
                avg_volume = statistics.mean(volumes[-20:]) if len(volumes) >= 20 else statistics.mean(volumes)
                technical_indicators["volume_analysis"] = {
                    "current_volume": volumes[-1],
                    "avg_volume_20d": avg_volume,
                    "volume_ratio": volumes[-1] / avg_volume if avg_volume > 0 else 1,
                    "volume_signal": "放量" if volumes[-1] > avg_volume * 1.5 else "缩量" if volumes[-1] < avg_volume * 0.5 else "正常"
                }
            
            # 综合技术信号
            signals = []
            signal_strength = 0
            
            # MA信号
            if "moving_averages" in technical_indicators:
                ma_data = technical_indicators["moving_averages"]
                current_price = ma_data["current_price"]
                if current_price > ma_data["ma_5"] > ma_data["ma_10"] > ma_data["ma_20"]:
                    signals.append("均线多头排列")
                    signal_strength += 2
                elif current_price < ma_data["ma_5"] < ma_data["ma_10"] < ma_data["ma_20"]:
                    signals.append("均线空头排列")
                    signal_strength -= 2
            
            # RSI信号
            if "rsi" in technical_indicators:
                rsi_value = technical_indicators["rsi"]["current_rsi"]
                if rsi_value < 30:
                    signals.append("RSI超卖")
                    signal_strength += 1
                elif rsi_value > 70:
                    signals.append("RSI超买")
                    signal_strength -= 1
            
            # MACD信号
            if "macd" in technical_indicators:
                macd_signal = technical_indicators["macd"]["signal"]
                if macd_signal == "金叉":
                    signals.append("MACD金叉")
                    signal_strength += 1
                elif macd_signal == "死叉":
                    signals.append("MACD死叉")
                    signal_strength -= 1
            
            # 成交量信号
            if "volume_analysis" in technical_indicators:
                volume_signal = technical_indicators["volume_analysis"]["volume_signal"]
                if volume_signal == "放量":
                    signals.append("成交量放大")
                    signal_strength += 0.5
            
            # 综合评估
            if signal_strength >= 3:
                overall_signal = "强烈买入"
            elif signal_strength >= 1:
                overall_signal = "买入"
            elif signal_strength <= -3:
                overall_signal = "强烈卖出"
            elif signal_strength <= -1:
                overall_signal = "卖出"
            else:
                overall_signal = "中性"
            
            return {
                "technical_indicators": technical_indicators,
                "signals": signals,
                "signal_strength": signal_strength,
                "overall_signal": overall_signal,
                "analysis_period": analysis_period,
                "data_points": len(prices),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical indicators: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def analyze_market_sentiment(stock_code: str) -> Dict[str, Any]:
        """
        分析市场情绪指标
        
        Args:
            stock_code: 股票代码
            
        Returns:
            市场情绪分析结果
        """
        try:
            logger.info(f"Analyzing market sentiment for {stock_code}")
            
            sentiment_data = {}
            
            # 获取基础股票信息
            basic_info = data_tools.get_stock_basic_info(stock_code)
            
            # 模拟市场情绪数据（实际应该从API获取）
            sentiment_indicators = {
                "institutional_sentiment": {
                    "fund_holdings_change": 2.5,  # 基金持仓变化百分比
                    "insurance_holdings_change": 1.8,  # 保险持仓变化
                    "foreign_capital_flow": 150000000,  # 外资流入（元）
                    "sentiment_score": 7.5  # 机构情绪得分（1-10）
                },
                "retail_sentiment": {
                    "shareholder_count_change": -5.2,  # 股东户数变化百分比
                    "retail_participation": 0.65,  # 散户参与度
                    "sentiment_score": 6.0  # 散户情绪得分
                },
                "market_attention": {
                    "research_reports_count": 15,  # 近期研报数量
                    "media_mentions": 45,  # 媒体提及次数
                    "search_index": 82,  # 搜索热度指数
                    "attention_score": 7.2  # 关注度得分
                },
                "trading_behavior": {
                    "turnover_rate": 3.2,  # 换手率
                    "big_order_ratio": 0.35,  # 大单成交占比
                    "block_trade_volume": 50000000,  # 大宗交易金额
                    "behavior_score": 6.8  # 交易行为得分
                }
            }
            
            # 计算综合情绪得分
            scores = [
                sentiment_indicators["institutional_sentiment"]["sentiment_score"],
                sentiment_indicators["retail_sentiment"]["sentiment_score"],
                sentiment_indicators["market_attention"]["attention_score"],
                sentiment_indicators["trading_behavior"]["behavior_score"]
            ]
            
            overall_sentiment_score = statistics.mean(scores)
            
            # 情绪等级评定
            if overall_sentiment_score >= 8:
                sentiment_level = "非常乐观"
            elif overall_sentiment_score >= 6.5:
                sentiment_level = "乐观"
            elif overall_sentiment_score >= 5:
                sentiment_level = "中性"
            elif overall_sentiment_score >= 3.5:
                sentiment_level = "悲观"
            else:
                sentiment_level = "非常悲观"
            
            return {
                "sentiment_indicators": sentiment_indicators,
                "overall_sentiment_score": overall_sentiment_score,
                "sentiment_level": sentiment_level,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def calculate_historical_valuation_percentile(stock_code: str, 
                                                 valuation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算历史估值分位数
        
        Args:
            stock_code: 股票代码
            valuation_data: 当前估值数据
            
        Returns:
            历史估值分位数分析
        """
        try:
            logger.info(f"Calculating historical valuation percentile for {stock_code}")
            
            # 获取历史财务数据
            financial_reports = data_tools.get_financial_reports(
                stock_code, 
                report_type="A", 
                limit=10  # 最近10年数据
            )
            
            if not financial_reports:
                return {"error": "缺少历史财务数据"}
            
            # 获取当前估值指标
            current_multiples = valuation_data.get("valuation_multiples", {})
            current_pe = current_multiples.get("pe_ratio", 0)
            current_pb = current_multiples.get("pb_ratio", 0)
            
            # 计算历史PE、PB数据
            historical_pe = []
            historical_pb = []
            
            for report in financial_reports:
                eps = report.get("eps", 0)
                book_value_per_share = report.get("book_value_per_share", 0)
                
                # 简化处理：假设历史平均股价（实际需要获取历史股价）
                avg_price = 50  # 简化假设
                
                if eps > 0:
                    historical_pe.append(avg_price / eps)
                if book_value_per_share > 0:
                    historical_pb.append(avg_price / book_value_per_share)
            
            # 计算分位数
            percentile_data = {}
            
            if historical_pe and current_pe > 0:
                pe_percentile = (sum(1 for pe in historical_pe if pe < current_pe) / len(historical_pe)) * 100
                percentile_data["pe_percentile"] = {
                    "current_pe": current_pe,
                    "historical_min": min(historical_pe),
                    "historical_max": max(historical_pe),
                    "historical_median": statistics.median(historical_pe),
                    "current_percentile": pe_percentile,
                    "interpretation": _interpret_percentile(pe_percentile)
                }
            
            if historical_pb and current_pb > 0:
                pb_percentile = (sum(1 for pb in historical_pb if pb < current_pb) / len(historical_pb)) * 100
                percentile_data["pb_percentile"] = {
                    "current_pb": current_pb,
                    "historical_min": min(historical_pb),
                    "historical_max": max(historical_pb),
                    "historical_median": statistics.median(historical_pb),
                    "current_percentile": pb_percentile,
                    "interpretation": _interpret_percentile(pb_percentile)
                }
            
            return {
                "percentile_analysis": percentile_data,
                "historical_data_points": len(financial_reports),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating historical percentile: {str(e)}")
            return {"error": str(e)}
    
def _interpret_percentile(percentile):
    """解释分位数含义"""
    if percentile <= 10:
        return "历史极低水平，估值具有很强吸引力"
    elif percentile <= 30:
        return "历史较低水平，估值相对合理"
    elif percentile <= 70:
        return "历史中等水平，估值处于正常区间"
    elif percentile <= 90:
        return "历史较高水平，估值偏贵"
    else:
        return "历史极高水平，估值过高"
    
    @tool
    def calculate_comprehensive_valuation_score(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算综合估值评分
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            综合估值评分结果
        """
        try:
            logger.info("Calculating comprehensive valuation score")
            
            score = 0
            score_breakdown = {}
            
            # 绝对估值合理性评分 (25分)
            dcf_data = analysis_data.get("dcf_valuation", {})
            if dcf_data:
                intrinsic_value = dcf_data.get("intrinsic_value_per_share", 0)
                current_price = analysis_data.get("current_price", 0)
                if current_price > 0 and intrinsic_value > 0:
                    upside = (intrinsic_value - current_price) / current_price * 100
                    if upside > 30:
                        absolute_score = 25
                    elif upside > 10:
                        absolute_score = 20
                    elif upside > -10:
                        absolute_score = 15
                    else:
                        absolute_score = 10
                else:
                    absolute_score = 15  # 默认分数
            else:
                absolute_score = 15
            
            score += absolute_score
            score_breakdown["absolute_valuation"] = absolute_score
            
            # 相对估值吸引力评分 (20分)
            relative_data = analysis_data.get("relative_valuation", {})
            multiples = relative_data.get("valuation_multiples", {})
            industry_data = relative_data.get("industry_comparison", {})
            
            relative_score = 15  # 默认分数
            if multiples and industry_data:
                current_pe = multiples.get("pe_ratio", 0)
                industry_pe = industry_data.get("industry_avg_pe", 0)
                if current_pe > 0 and industry_pe > 0:
                    pe_discount = (industry_pe - current_pe) / industry_pe * 100
                    if pe_discount > 30:
                        relative_score = 20
                    elif pe_discount > 10:
                        relative_score = 16
                    elif pe_discount > -10:
                        relative_score = 12
                    else:
                        relative_score = 8
            
            score += relative_score
            score_breakdown["relative_valuation"] = relative_score
            
            # 技术信号强度评分 (15分)
            technical_data = analysis_data.get("technical_analysis", {})
            if technical_data:
                signal_strength = technical_data.get("signal_strength", 0)
                if signal_strength >= 3:
                    technical_score = 15
                elif signal_strength >= 1:
                    technical_score = 12
                elif signal_strength >= -1:
                    technical_score = 8
                else:
                    technical_score = 5
            else:
                technical_score = 8
            
            score += technical_score
            score_breakdown["technical_signals"] = technical_score
            
            # 市场情绪支撑评分 (15分)
            sentiment_data = analysis_data.get("market_sentiment", {})
            if sentiment_data:
                sentiment_score_raw = sentiment_data.get("overall_sentiment_score", 5)
                if sentiment_score_raw >= 8:
                    sentiment_score = 15
                elif sentiment_score_raw >= 6.5:
                    sentiment_score = 12
                elif sentiment_score_raw >= 5:
                    sentiment_score = 8
                else:
                    sentiment_score = 5
            else:
                sentiment_score = 8
            
            score += sentiment_score
            score_breakdown["market_sentiment"] = sentiment_score
            
            # 历史估值分位评分 (15分)
            percentile_data = analysis_data.get("historical_percentile", {})
            percentile_score = 8  # 默认分数
            if percentile_data:
                pe_percentile_data = percentile_data.get("percentile_analysis", {}).get("pe_percentile", {})
                if pe_percentile_data:
                    current_percentile = pe_percentile_data.get("current_percentile", 50)
                    if current_percentile <= 10:
                        percentile_score = 15
                    elif current_percentile <= 30:
                        percentile_score = 12
                    elif current_percentile <= 70:
                        percentile_score = 8
                    else:
                        percentile_score = 5
            
            score += percentile_score
            score_breakdown["historical_percentile"] = percentile_score
            
            # 催化剂因素评分 (10分)
            catalyst_score = 8  # 默认分数，实际需要分析具体催化剂
            score += catalyst_score
            score_breakdown["catalyst_factors"] = catalyst_score
            
            # 确定估值等级和投资建议
            if score >= 90:
                valuation_level = "极具吸引力"
                recommendation = "强烈买入"
            elif score >= 80:
                valuation_level = "较为合理"
                recommendation = "买入"
            elif score >= 70:
                valuation_level = "基本合理"
                recommendation = "持有"
            elif score >= 60:
                valuation_level = "偏高"
                recommendation = "减持"
            else:
                valuation_level = "过高"
                recommendation = "卖出"
            
            return {
                "total_score": score,
                "valuation_level": valuation_level,
                "investment_recommendation": recommendation,
                "score_breakdown": score_breakdown,
                "max_score": 100,
                "scoring_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive valuation score: {str(e)}")
            return {"error": str(e)}
    
    @tool
    def generate_valuation_analysis_report(analysis_data: Dict[str, Any]) -> str:
        """
        生成估值分析报告
        
        Args:
            analysis_data: 分析数据
            
        Returns:
            格式化的估值分析报告
        """
        try:
            logger.info("Generating valuation analysis report")
            
            stock_code = analysis_data.get("stock_code", "")
            stock_name = analysis_data.get("stock_name", "")
            
            # 获取各部分数据
            dcf_data = analysis_data.get("dcf_valuation", {})
            relative_data = analysis_data.get("relative_valuation", {})
            technical_data = analysis_data.get("technical_analysis", {})
            sentiment_data = analysis_data.get("market_sentiment", {})
            valuation_score = analysis_data.get("valuation_score", {})
            
            # 构建报告基础信息
            current_price = analysis_data.get("current_price", 0)
            intrinsic_value = dcf_data.get("intrinsic_value_per_share", 0)
            target_price = intrinsic_value if intrinsic_value > 0 else current_price * 1.1
            
            report_sections = {
                "stock_name": stock_name,
                "stock_code": stock_code,
                "valuation_score": valuation_score.get("total_score", 0),
                "valuation_level": valuation_score.get("valuation_level", "未知"),
                "target_price": f"{target_price:.2f}",
                "current_price": f"{current_price:.2f}",
                "investment_recommendation": valuation_score.get("investment_recommendation", "持有"),
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "report_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # DCF分析内容
            dcf_analysis = ""
            if dcf_data:
                model_params = dcf_data.get("model_parameters", {})
                dcf_analysis = f"""
                DCF估值结果：
                - 内在价值：{intrinsic_value:.2f}元/股
                - 当前价格：{current_price:.2f}元/股
                - 安全边际：{((intrinsic_value - current_price) / current_price * 100):.1f}%
                
                关键假设：
                - 收入增长率：{model_params.get('revenue_growth', 0):.1f}%
                - 加权平均成本：{model_params.get('wacc', 0):.1f}%
                - 永续增长率：{model_params.get('terminal_growth', 0):.1f}%
                """
            
            # 相对估值分析
            relative_analysis = ""
            if relative_data:
                multiples = relative_data.get("valuation_multiples", {})
                relative_analysis = f"""
                估值倍数分析：
                - 市盈率(PE)：{multiples.get('pe_ratio', 0):.2f}
                - 市净率(PB)：{multiples.get('pb_ratio', 0):.2f}
                - 市销率(PS)：{multiples.get('ps_ratio', 0):.2f}
                - PEG比率：{multiples.get('peg_ratio', 0):.2f}
                """
            
            # 技术分析结论
            technical_conclusion = ""
            if technical_data:
                overall_signal = technical_data.get("overall_signal", "中性")
                signals = technical_data.get("signals", [])
                technical_conclusion = f"""
                技术分析结论：{overall_signal}
                关键技术信号：{', '.join(signals[:3]) if signals else '暂无明显信号'}
                """
            
            # 市场情绪分析
            sentiment_analysis = ""
            if sentiment_data:
                sentiment_level = sentiment_data.get("sentiment_level", "中性")
                sentiment_score = sentiment_data.get("overall_sentiment_score", 5)
                sentiment_analysis = f"""
                市场情绪：{sentiment_level}（{sentiment_score:.1f}/10分）
                机构态度：相对积极
                """
            
            report_sections.update({
                "core_logic": f"基于DCF模型估值为{target_price}元，相对当前价格{current_price}元具有{valuation_score.get('valuation_level', '一定')}的投资价值。",
                "dcf_analysis": dcf_analysis,
                "relative_analysis": relative_analysis,
                "technical_conclusion": technical_conclusion,
                "sentiment_analysis": sentiment_analysis,
                "data_sources": "A股数据同步服务API、技术分析API"
            })
            
            # 生成简化的报告
            report = f"""
# {stock_name}（{stock_code}）估值分析与市场信号解读报告

## 执行摘要
- **估值综合评分**：{report_sections['valuation_score']}/100分 ({report_sections['valuation_level']})
- **目标价位**：{report_sections['target_price']}元（当前价格：{report_sections['current_price']}元）
- **投资建议**：{report_sections['investment_recommendation']}
- **核心逻辑**：{report_sections['core_logic']}

## DCF绝对估值分析
{report_sections['dcf_analysis']}

## 相对估值分析
{report_sections['relative_analysis']}

## 技术分析
{report_sections['technical_conclusion']}

## 市场情绪分析
{report_sections['sentiment_analysis']}

## 投资建议
基于以上估值分析和市场信号解读，建议投资者{report_sections['investment_recommendation']}。
目标价位设定为{report_sections['target_price']}元。

---
**数据来源**：{report_sections['data_sources']}
**分析日期**：{report_sections['analysis_date']}
**报告生成时间**：{report_sections['report_time']}
            """
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating valuation analysis report: {str(e)}")
            return f"报告生成失败: {str(e)}"
    
    # 工具列表
    tools = [
        calculate_dcf_valuation,
        calculate_relative_valuation,
        analyze_technical_indicators,
        analyze_market_sentiment,
        calculate_historical_valuation_percentile,
        calculate_comprehensive_valuation_score,
        generate_valuation_analysis_report
    ]
    
    # 如果启用MCP工具，添加MCP相关工具
    if mcp_tools:
        @tool
        def get_mcp_market_data(stock_code: str) -> Dict[str, Any]:
            """
            使用MCP服务获取市场数据
            
            Args:
                stock_code: 股票代码
                
            Returns:
                MCP市场数据
            """
            try:
                return mcp_tools.get_market_data(stock_code)
            except Exception as e:
                logger.error(f"Error getting MCP market data: {str(e)}")
                return {"error": str(e)}
        
        tools.append(get_mcp_market_data)
    
    def valuation_analyst_node(state):
        """
        估值分析Agent节点函数
        
        Args:
            state: 当前分析状态
            
        Returns:
            更新后的状态
        """
        try:
            logger.info("Starting valuation analysis")
            
            # 获取分析参数
            stock_code = state.get("stock_code", "")
            stock_name = state.get("stock_name", "")
            analysis_date = state.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
            
            if not stock_code:
                return {
                    "messages": [{"role": "assistant", "content": "错误：缺少股票代码"}],
                    "valuation_analysis_report": "分析失败：缺少股票代码",
                    "analysis_stage": AnalysisStage.ERROR
                }
            
            # 构建系统提示词
            system_prompt = VALUATION_ANALYSIS_SYSTEM_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name,
                analysis_date=analysis_date
            )
            
            # 构建用户提示词
            user_prompt = VALUATION_ANALYSIS_USER_PROMPT.format(
                stock_code=stock_code,
                stock_name=stock_name
            )
            
            # 创建提示词模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt),
                MessagesPlaceholder(variable_name="messages")
            ])
            
            # 创建LLM链
            chain = prompt | llm.bind_tools(tools)
            
            # 执行分析
            messages = state.get("messages", [])
            if not messages:
                messages = [{"role": "user", "content": user_prompt}]
            
            result = chain.invoke({"messages": messages})
            
            # 处理工具调用结果
            valuation_report = ""
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # 如果有工具调用，处理工具调用结果
                valuation_report = f"{stock_name}（{stock_code}）估值分析已启动，正在处理市场数据..."
            else:
                # 如果没有工具调用，使用LLM直接回答
                valuation_report = result.content
            
            logger.info("Valuation analysis completed")
            
            return {
                "messages": [result],
                "valuation_analysis_report": valuation_report,
                "analysis_stage": AnalysisStage.VALUATION_ANALYSIS,
                "valuation_data": state.get("valuation_data", {}),
                "market_signals": {},  # 从分析中提取
                "technical_indicators": {},  # 技术指标数据
                "data_sources": state.get("data_sources", []) + ["A股数据API", "技术分析API"],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in valuation analysis: {str(e)}")
            return {
                "messages": [{"role": "assistant", "content": f"估值分析过程中出现错误: {str(e)}"}],
                "valuation_analysis_report": f"分析失败: {str(e)}",
                "analysis_stage": AnalysisStage.ERROR
            }
    
    return valuation_analyst_node