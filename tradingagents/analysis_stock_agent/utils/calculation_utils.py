"""
财务计算工具模块

提供各种财务指标计算、估值模型、技术分析等计算功能。
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


class FinancialCalculator:
    """财务指标计算器"""
    
    @staticmethod
    def calculate_profitability_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算盈利能力指标
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            盈利能力指标字典
        """
        ratios = {}
        
        try:
            # 基础数据
            revenue = float(financial_data.get('total_revenue', 0))
            operating_revenue = float(financial_data.get('operating_revenue', 0))
            gross_profit = float(financial_data.get('gross_profit', 0))
            operating_profit = float(financial_data.get('operating_profit', 0))
            net_profit = float(financial_data.get('net_profit', 0))
            total_assets = float(financial_data.get('total_assets', 0))
            total_equity = float(financial_data.get('total_equity', 0))
            
            # 毛利率
            if revenue > 0:
                ratios['gross_profit_margin'] = (gross_profit / revenue) * 100
                ratios['net_profit_margin'] = (net_profit / revenue) * 100
                
            if operating_revenue > 0:
                ratios['operating_profit_margin'] = (operating_profit / operating_revenue) * 100
            
            # ROA (资产回报率)
            if total_assets > 0:
                ratios['roa'] = (net_profit / total_assets) * 100
            
            # ROE (净资产收益率)
            if total_equity > 0:
                ratios['roe'] = (net_profit / total_equity) * 100
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating profitability ratios: {str(e)}")
        
        return ratios
    
    @staticmethod
    def calculate_liquidity_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算流动性指标
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            流动性指标字典
        """
        ratios = {}
        
        try:
            current_assets = float(financial_data.get('total_current_assets', 0))
            current_liabilities = float(financial_data.get('total_current_liabilities', 0))
            
            # 流动比率
            if current_liabilities > 0:
                ratios['current_ratio'] = current_assets / current_liabilities
                
            # 速动比率 (假设速动资产 = 流动资产 - 存货)
            inventory = float(financial_data.get('inventory', 0))
            quick_assets = current_assets - inventory
            if current_liabilities > 0:
                ratios['quick_ratio'] = quick_assets / current_liabilities
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating liquidity ratios: {str(e)}")
        
        return ratios
    
    @staticmethod
    def calculate_leverage_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算杠杆指标
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            杠杆指标字典
        """
        ratios = {}
        
        try:
            total_assets = float(financial_data.get('total_assets', 0))
            total_liabilities = float(financial_data.get('total_liabilities', 0))
            total_equity = float(financial_data.get('total_equity', 0))
            
            # 资产负债率
            if total_assets > 0:
                ratios['debt_to_asset_ratio'] = (total_liabilities / total_assets) * 100
            
            # 权益乘数
            if total_equity > 0:
                ratios['equity_multiplier'] = total_assets / total_equity
            
            # 债务权益比
            if total_equity > 0:
                ratios['debt_to_equity_ratio'] = total_liabilities / total_equity
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating leverage ratios: {str(e)}")
        
        return ratios
    
    @staticmethod
    def calculate_efficiency_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算运营效率指标
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            运营效率指标字典
        """
        ratios = {}
        
        try:
            revenue = float(financial_data.get('total_revenue', 0))
            total_assets = float(financial_data.get('total_assets', 0))
            
            # 总资产周转率
            if total_assets > 0:
                ratios['total_asset_turnover'] = revenue / total_assets
                
            # 这里可以添加更多效率指标，如存货周转率、应收账款周转率等
            # 需要更详细的财务数据
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating efficiency ratios: {str(e)}")
        
        return ratios
    
    @staticmethod
    def calculate_growth_rates(financial_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        计算成长性指标
        
        Args:
            financial_history: 历史财务数据列表
            
        Returns:
            成长性指标字典
        """
        growth_rates = {}
        
        if len(financial_history) < 2:
            return growth_rates
        
        try:
            # 按报告日期排序
            sorted_data = sorted(financial_history, 
                               key=lambda x: x.get('report_date', ''), 
                               reverse=True)
            
            # 计算各项增长率
            metrics = ['total_revenue', 'net_profit', 'total_assets', 'total_equity']
            
            for metric in metrics:
                values = []
                for data in sorted_data:
                    value = data.get(metric)
                    if value is not None:
                        values.append(float(value))
                
                if len(values) >= 2:
                    # 年化增长率
                    latest = values[0]
                    earliest = values[-1]
                    years = len(values) - 1
                    
                    if earliest > 0:
                        cagr = ((latest / earliest) ** (1/years) - 1) * 100
                        growth_rates[f'{metric}_cagr'] = cagr
                    
                    # 最近一年增长率
                    if len(values) >= 2:
                        yoy_growth = ((values[0] / values[1]) - 1) * 100 if values[1] > 0 else 0
                        growth_rates[f'{metric}_yoy'] = yoy_growth
                        
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating growth rates: {str(e)}")
        
        return growth_rates
    
    @staticmethod
    def calculate_cashflow_ratios(financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算现金流指标
        
        Args:
            financial_data: 财务数据字典
            
        Returns:
            现金流指标字典
        """
        ratios = {}
        
        try:
            net_profit = float(financial_data.get('net_profit', 0))
            operating_cashflow = float(financial_data.get('net_cash_flow_from_operating', 0))
            investing_cashflow = float(financial_data.get('net_cash_flow_from_investing', 0))
            financing_cashflow = float(financial_data.get('net_cash_flow_from_financing', 0))
            
            # 经营现金流与净利润比
            if net_profit > 0:
                ratios['ocf_to_net_income'] = operating_cashflow / net_profit
            
            # 自由现金流
            free_cashflow = operating_cashflow + investing_cashflow
            ratios['free_cashflow'] = free_cashflow
            
            # 现金流覆盖率
            if financing_cashflow < 0:  # 有债务偿还或股利支付
                ratios['cashflow_coverage'] = operating_cashflow / abs(financing_cashflow)
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating cashflow ratios: {str(e)}")
        
        return ratios


class ValuationCalculator:
    """估值计算器"""
    
    @staticmethod
    def calculate_relative_valuation(market_data: Dict[str, Any], 
                                   financial_data: Dict[str, Any]) -> Dict[str, float]:
        """
        计算相对估值指标
        
        Args:
            market_data: 市场数据
            financial_data: 财务数据
            
        Returns:
            相对估值指标字典
        """
        valuations = {}
        
        try:
            # 市场数据
            market_cap = float(market_data.get('market_cap', 0))
            price = float(market_data.get('current_price', 0))
            shares_outstanding = float(market_data.get('shares_outstanding', 0))
            
            # 财务数据
            net_profit = float(financial_data.get('net_profit', 0))
            total_equity = float(financial_data.get('total_equity', 0))
            revenue = float(financial_data.get('total_revenue', 0))
            book_value = total_equity
            
            # PE比率
            if shares_outstanding > 0 and net_profit > 0:
                eps = net_profit / shares_outstanding
                if eps > 0:
                    valuations['pe_ratio'] = price / eps
            
            # PB比率
            if shares_outstanding > 0 and book_value > 0:
                book_value_per_share = book_value / shares_outstanding
                if book_value_per_share > 0:
                    valuations['pb_ratio'] = price / book_value_per_share
            
            # PS比率
            if market_cap > 0 and revenue > 0:
                valuations['ps_ratio'] = market_cap / revenue
            
            # PEG比率 (需要增长率数据)
            # 这里简化处理，实际需要历史数据计算增长率
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating relative valuation: {str(e)}")
        
        return valuations
    
    @staticmethod
    def calculate_dcf_valuation(financial_history: List[Dict[str, Any]],
                              assumptions: Dict[str, float]) -> Dict[str, float]:
        """
        计算DCF估值
        
        Args:
            financial_history: 历史财务数据
            assumptions: 估值假设 (增长率、折现率等)
            
        Returns:
            DCF估值结果
        """
        dcf_result = {}
        
        try:
            # 获取假设参数
            growth_rate = assumptions.get('growth_rate', 0.05)  # 5%
            terminal_growth = assumptions.get('terminal_growth', 0.03)  # 3%
            discount_rate = assumptions.get('discount_rate', 0.10)  # 10%
            forecast_years = assumptions.get('forecast_years', 5)
            
            # 获取最新自由现金流
            if not financial_history:
                return dcf_result
                
            latest_data = financial_history[0]
            operating_cf = float(latest_data.get('net_cash_flow_from_operating', 0))
            investing_cf = float(latest_data.get('net_cash_flow_from_investing', 0))
            
            base_fcf = operating_cf + investing_cf  # 简化的自由现金流
            
            if base_fcf <= 0:
                return dcf_result
            
            # 预测未来现金流
            forecast_fcf = []
            for year in range(1, forecast_years + 1):
                fcf = base_fcf * ((1 + growth_rate) ** year)
                forecast_fcf.append(fcf)
            
            # 计算终值
            terminal_fcf = forecast_fcf[-1] * (1 + terminal_growth)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth)
            
            # 折现到现值
            pv_fcf = sum([fcf / ((1 + discount_rate) ** (i + 1)) 
                         for i, fcf in enumerate(forecast_fcf)])
            pv_terminal = terminal_value / ((1 + discount_rate) ** forecast_years)
            
            enterprise_value = pv_fcf + pv_terminal
            
            dcf_result['enterprise_value'] = enterprise_value
            dcf_result['pv_forecast_fcf'] = pv_fcf
            dcf_result['pv_terminal_value'] = pv_terminal
            dcf_result['terminal_value'] = terminal_value
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating DCF valuation: {str(e)}")
        
        return dcf_result
    
    @staticmethod
    def calculate_dividend_discount_model(dividend_history: List[float],
                                        assumptions: Dict[str, float]) -> Dict[str, float]:
        """
        计算股利贴现模型估值
        
        Args:
            dividend_history: 历史股利数据
            assumptions: 估值假设
            
        Returns:
            DDM估值结果
        """
        ddm_result = {}
        
        try:
            if not dividend_history or len(dividend_history) < 2:
                return ddm_result
            
            # 计算股利增长率
            growth_rates = []
            for i in range(1, len(dividend_history)):
                if dividend_history[i-1] > 0:
                    growth = (dividend_history[i] / dividend_history[i-1]) - 1
                    growth_rates.append(growth)
            
            if not growth_rates:
                return ddm_result
            
            avg_growth = sum(growth_rates) / len(growth_rates)
            
            # 获取假设参数
            required_return = assumptions.get('required_return', 0.10)
            growth_rate = assumptions.get('dividend_growth', avg_growth)
            
            # Gordon增长模型
            if required_return > growth_rate:
                last_dividend = dividend_history[-1]
                next_dividend = last_dividend * (1 + growth_rate)
                fair_value = next_dividend / (required_return - growth_rate)
                
                ddm_result['fair_value'] = fair_value
                ddm_result['next_dividend'] = next_dividend
                ddm_result['growth_rate'] = growth_rate
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating DDM: {str(e)}")
        
        return ddm_result


class TechnicalCalculator:
    """技术分析计算器"""
    
    @staticmethod
    def calculate_moving_averages(prices: List[float], periods: List[int]) -> Dict[str, List[float]]:
        """
        计算移动平均线
        
        Args:
            prices: 价格列表
            periods: 周期列表
            
        Returns:
            移动平均线字典
        """
        mas = {}
        
        if len(prices) < max(periods):
            return mas
        
        prices_series = pd.Series(prices)
        
        for period in periods:
            ma = prices_series.rolling(window=period).mean().tolist()
            mas[f'ma_{period}'] = ma
        
        return mas
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """
        计算RSI指标
        
        Args:
            prices: 价格列表
            period: 计算周期
            
        Returns:
            RSI值列表
        """
        if len(prices) < period + 1:
            return []
        
        prices_series = pd.Series(prices)
        delta = prices_series.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.tolist()
    
    @staticmethod
    def calculate_macd(prices: List[float], 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> Dict[str, List[float]]:
        """
        计算MACD指标
        
        Args:
            prices: 价格列表
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            MACD指标字典
        """
        if len(prices) < slow_period:
            return {}
        
        prices_series = pd.Series(prices)
        
        # 计算EMA
        ema_fast = prices_series.ewm(span=fast_period).mean()
        ema_slow = prices_series.ewm(span=slow_period).mean()
        
        # MACD线
        macd_line = ema_fast - ema_slow
        
        # 信号线
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # 柱状图
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line.tolist(),
            'signal_line': signal_line.tolist(),
            'histogram': histogram.tolist()
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], 
                                period: int = 20, 
                                std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        计算布林带
        
        Args:
            prices: 价格列表
            period: 计算周期
            std_dev: 标准差倍数
            
        Returns:
            布林带字典
        """
        if len(prices) < period:
            return {}
        
        prices_series = pd.Series(prices)
        
        # 中轨（移动平均线）
        middle_band = prices_series.rolling(window=period).mean()
        
        # 标准差
        std = prices_series.rolling(window=period).std()
        
        # 上轨和下轨
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return {
            'upper_band': upper_band.tolist(),
            'middle_band': middle_band.tolist(),
            'lower_band': lower_band.tolist()
        }


class RiskCalculator:
    """风险计算器"""
    
    @staticmethod
    def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
        """
        计算波动率
        
        Args:
            returns: 收益率列表
            annualize: 是否年化
            
        Returns:
            波动率
        """
        if len(returns) < 2:
            return 0.0
        
        returns_series = pd.Series(returns)
        volatility = returns_series.std()
        
        if annualize:
            volatility *= math.sqrt(252)  # 假设一年252个交易日
        
        return volatility
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], 
                             risk_free_rate: float = 0.03) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率列表
            risk_free_rate: 无风险利率
            
        Returns:
            夏普比率
        """
        if len(returns) < 2:
            return 0.0
        
        returns_series = pd.Series(returns)
        excess_returns = returns_series - (risk_free_rate / 252)  # 日无风险利率
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std() * math.sqrt(252)
        return sharpe
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> Dict[str, float]:
        """
        计算最大回撤
        
        Args:
            prices: 价格列表
            
        Returns:
            最大回撤信息
        """
        if len(prices) < 2:
            return {}
        
        prices_series = pd.Series(prices)
        cumulative_returns = (prices_series / prices_series.iloc[0])
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        
        max_drawdown = drawdown.min()
        max_drawdown_idx = drawdown.idxmin()
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_date_idx': max_drawdown_idx,
            'current_drawdown': drawdown.iloc[-1]
        }