"""
数据验证和处理工具
确保输入数据的有效性和处理数据的一致性
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器"""
    
    # A股股票代码模式
    ASHARE_SYMBOL_PATTERN = r'^[0-9]{6}$'
    
    # 日期格式模式
    DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> bool:
        """验证A股股票代码格式"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # 检查6位数字格式
        if not re.match(DataValidator.ASHARE_SYMBOL_PATTERN, symbol):
            return False
        
        # 检查股票代码范围
        symbol_int = int(symbol)
        
        # A股代码范围验证
        valid_ranges = [
            (1, 999999),       # 所有6位数字
            # 可以根据需要添加更具体的范围限制
        ]
        
        return any(start <= symbol_int <= end for start, end in valid_ranges)
    
    @staticmethod
    def validate_date_string(date_str: str) -> bool:
        """验证日期字符串格式"""
        if not date_str or not isinstance(date_str, str):
            return False
        
        if not re.match(DataValidator.DATE_PATTERN, date_str):
            return False
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """验证日期范围的合理性"""
        if not DataValidator.validate_date_string(start_date):
            return False
        if not DataValidator.validate_date_string(end_date):
            return False
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 开始日期不能晚于结束日期
            if start > end:
                return False
            
            # 结束日期不能超过当前时间
            if end > datetime.now():
                return False
            
            # 日期范围不能超过10年
            if (end - start).days > 3650:
                return False
            
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """清理输入文本，移除潜在的危险字符"""
        if not text or not isinstance(text, str):
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除潜在的脚本注入字符
        dangerous_chars = ['<', '>', '"', "'", ';', '&']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def validate_numeric_value(value: Any, min_val: float = None, max_val: float = None) -> bool:
        """验证数值的有效性"""
        try:
            if value is None:
                return True  # None值被认为是有效的
            
            # 尝试转换为float
            if isinstance(value, str):
                if value.strip() == '':
                    return True
                float_val = float(value)
            elif isinstance(value, (int, float, Decimal)):
                float_val = float(value)
            else:
                return False
            
            # 检查是否为有效数字
            if not (-float('inf') < float_val < float('inf')):
                return False
            
            # 检查范围
            if min_val is not None and float_val < min_val:
                return False
            if max_val is not None and float_val > max_val:
                return False
            
            return True
        except (ValueError, TypeError, InvalidOperation):
            return False

class DataQualityChecker:
    """数据质量检查器"""
    
    @staticmethod
    def check_financial_data_completeness(data: Dict[str, Any]) -> float:
        """检查财务数据的完整性"""
        required_fields = [
            'total_revenue', 'net_profit', 'total_assets', 
            'total_liabilities', 'roe', 'gross_margin', 'net_margin',
            'operating_cash_flow', 'debt_ratio', 'current_ratio'
        ]
        
        if not data:
            return 0.0
        
        available_count = 0
        for field in required_fields:
            value = data.get(field)
            if value is not None and DataValidator.validate_numeric_value(value):
                available_count += 1
        
        completeness = available_count / len(required_fields)
        return round(completeness, 3)
    
    @staticmethod
    def detect_financial_anomalies(data: Dict[str, Any]) -> List[str]:
        """检测财务数据异常"""
        anomalies = []
        
        if not data:
            return anomalies
        
        # ROE异常检查
        roe = data.get('roe')
        if roe is not None:
            try:
                roe_val = float(roe)
                if roe_val > 100:
                    anomalies.append(f"ROE异常高: {roe_val}% (>100%)")
                elif roe_val < -50:
                    anomalies.append(f"ROE异常低: {roe_val}% (<-50%)")
            except (ValueError, TypeError):
                anomalies.append("ROE数据格式无效")
        
        # 负债率异常检查
        debt_ratio = data.get('debt_ratio')
        if debt_ratio is not None:
            try:
                debt_val = float(debt_ratio)
                if debt_val > 200:
                    anomalies.append(f"负债率异常高: {debt_val}% (>200%)")
                elif debt_val < 0:
                    anomalies.append(f"负债率为负: {debt_val}%")
            except (ValueError, TypeError):
                anomalies.append("负债率数据格式无效")
        
        # 毛利率异常检查
        gross_margin = data.get('gross_margin')
        if gross_margin is not None:
            try:
                margin_val = float(gross_margin)
                if margin_val < 0:
                    anomalies.append(f"毛利率为负: {margin_val}%")
                elif margin_val > 100:
                    anomalies.append(f"毛利率异常高: {margin_val}% (>100%)")
            except (ValueError, TypeError):
                anomalies.append("毛利率数据格式无效")
        
        # 流动比率异常检查
        current_ratio = data.get('current_ratio')
        if current_ratio is not None:
            try:
                ratio_val = float(current_ratio)
                if ratio_val < 0.1:
                    anomalies.append(f"流动比率异常低: {ratio_val} (<0.1)")
                elif ratio_val > 20:
                    anomalies.append(f"流动比率异常高: {ratio_val} (>20)")
            except (ValueError, TypeError):
                anomalies.append("流动比率数据格式无效")
        
        # 营收和净利润一致性检查
        revenue = data.get('total_revenue')
        net_profit = data.get('net_profit')
        if revenue is not None and net_profit is not None:
            try:
                revenue_val = float(revenue)
                profit_val = float(net_profit)
                if revenue_val != 0:
                    profit_margin = profit_val / revenue_val
                    if profit_margin > 1:
                        anomalies.append(f"净利润超过营收: 净利率{profit_margin*100:.1f}%")
                    elif profit_margin < -2:
                        anomalies.append(f"亏损严重: 净利率{profit_margin*100:.1f}%")
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        
        return anomalies
    
    @staticmethod
    def calculate_data_quality_score(data: Dict[str, Any]) -> float:
        """计算数据质量综合评分(0-10分)"""
        if not data:
            return 0.0
        
        # 完整性评分 (40%)
        completeness = DataQualityChecker.check_financial_data_completeness(data)
        completeness_score = completeness * 4
        
        # 异常检测评分 (30%)
        anomalies = DataQualityChecker.detect_financial_anomalies(data)
        anomaly_penalty = min(len(anomalies) * 0.5, 3.0)  # 每个异常扣0.5分，最多扣3分
        anomaly_score = max(0, 3.0 - anomaly_penalty)
        
        # 数据新鲜度评分 (20%)
        freshness_score = 2.0  # 默认给2分，实际可以根据数据时间戳计算
        
        # 数据格式规范性评分 (10%)
        format_score = 1.0  # 默认给1分，通过前面的验证说明格式基本正确
        
        total_score = completeness_score + anomaly_score + freshness_score + format_score
        return round(min(10.0, total_score), 2)

class DataFormatter:
    """数据格式化工具"""
    
    @staticmethod
    def format_currency(value: Any, unit: str = "万元") -> str:
        """格式化货币数值"""
        try:
            if value is None:
                return "暂无数据"
            
            num_val = float(value)
            if abs(num_val) >= 10000:
                return f"{num_val/10000:.2f}万{unit}"
            else:
                return f"{num_val:.2f}{unit}"
        except (ValueError, TypeError):
            return "数据格式错误"
    
    @staticmethod
    def format_percentage(value: Any, decimal_places: int = 2) -> str:
        """格式化百分比数值"""
        try:
            if value is None:
                return "暂无数据"
            
            num_val = float(value)
            return f"{num_val:.{decimal_places}f}%"
        except (ValueError, TypeError):
            return "数据格式错误"
    
    @staticmethod
    def format_ratio(value: Any, decimal_places: int = 2) -> str:
        """格式化比率数值"""
        try:
            if value is None:
                return "暂无数据"
            
            num_val = float(value)
            return f"{num_val:.{decimal_places}f}"
        except (ValueError, TypeError):
            return "数据格式错误"
    
    @staticmethod
    def clean_financial_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """清理和标准化财务数据"""
        cleaned_data = {}
        
        # 数值字段清理
        numeric_fields = [
            'total_revenue', 'operating_revenue', 'net_profit', 'gross_profit',
            'total_assets', 'total_liabilities', 'total_equity',
            'operating_cash_flow', 'roe', 'roa', 'gross_margin', 'net_margin',
            'debt_ratio', 'current_ratio', 'quick_ratio'
        ]
        
        for field in numeric_fields:
            value = raw_data.get(field)
            if value is not None:
                try:
                    # 尝试转换为float
                    if isinstance(value, str):
                        # 移除可能的千分位分隔符
                        value = value.replace(',', '').replace('，', '')
                        # 移除可能的单位符号
                        value = re.sub(r'[^\d\.\-\+]', '', value)
                    
                    cleaned_value = float(value)
                    cleaned_data[field] = cleaned_value
                except (ValueError, TypeError):
                    logger.warning(f"无法转换字段 {field} 的值: {value}")
                    cleaned_data[field] = None
            else:
                cleaned_data[field] = None
        
        # 字符串字段清理
        string_fields = ['symbol', 'company_name', 'industry', 'report_type']
        for field in string_fields:
            value = raw_data.get(field)
            if value is not None:
                cleaned_data[field] = DataValidator.sanitize_input(str(value))
            else:
                cleaned_data[field] = None
        
        # 日期字段清理
        date_fields = ['report_date', 'announce_date']
        for field in date_fields:
            value = raw_data.get(field)
            if value is not None:
                try:
                    if isinstance(value, str):
                        # 尝试解析日期
                        parsed_date = datetime.strptime(value[:10], '%Y-%m-%d')
                        cleaned_data[field] = parsed_date.strftime('%Y-%m-%d')
                    else:
                        cleaned_data[field] = str(value)
                except ValueError:
                    logger.warning(f"无法解析日期字段 {field} 的值: {value}")
                    cleaned_data[field] = None
            else:
                cleaned_data[field] = None
        
        return cleaned_data

# 验证函数
def validate_analysis_input(symbol: str, start_date: str = None, end_date: str = None) -> Tuple[bool, List[str]]:
    """验证分析输入参数"""
    errors = []
    
    # 验证股票代码
    if not DataValidator.validate_stock_symbol(symbol):
        errors.append(f"无效的股票代码: {symbol} (必须是6位数字)")
    
    # 验证日期范围
    if start_date and end_date:
        if not DataValidator.validate_date_range(start_date, end_date):
            errors.append(f"无效的日期范围: {start_date} 到 {end_date}")
    elif start_date and not DataValidator.validate_date_string(start_date):
        errors.append(f"无效的开始日期: {start_date}")
    elif end_date and not DataValidator.validate_date_string(end_date):
        errors.append(f"无效的结束日期: {end_date}")
    
    return len(errors) == 0, errors