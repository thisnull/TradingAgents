"""
Gemini API诊断和监控工具

专门用于诊断和监控Gemini API的500错误问题，提供详细的错误分析和建议。
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass 
class APIErrorEvent:
    """API错误事件记录"""
    timestamp: datetime
    error_type: str
    error_message: str
    model_name: str
    request_size: int
    response_time: float
    retry_count: int
    is_resolved: bool
    resolution_time: Optional[float] = None


class GeminiDiagnostics:
    """Gemini API诊断器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化诊断器
        
        Args:
            max_history: 保持的历史错误记录数量
        """
        self.error_history = deque(maxlen=max_history)
        self.error_stats = defaultdict(int)
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_retry_attempts": 0,
            "average_response_time": 0.0,
            "last_reset": datetime.now()
        }
        
        # 500错误特征分析
        self.error_patterns = {
            "500_internal_error": {
                "keywords": ["500", "internal error", "internal server error"],
                "frequency": 0,
                "typical_causes": [
                    "服务器临时过载",
                    "模型推理超时", 
                    "请求过于复杂",
                    "API服务重启"
                ],
                "suggested_actions": [
                    "减少请求复杂度",
                    "使用指数退避重试",
                    "切换到更稳定的模型版本",
                    "分批处理大型请求"
                ]
            },
            "rate_limit": {
                "keywords": ["rate limit", "quota", "too many requests"],
                "frequency": 0,
                "typical_causes": [
                    "请求频率过高",
                    "超出配额限制"
                ],
                "suggested_actions": [
                    "增加请求间隔",
                    "检查API配额设置",
                    "实施请求队列管理"
                ]
            },
            "timeout": {
                "keywords": ["timeout", "timed out", "deadline exceeded"],
                "frequency": 0,
                "typical_causes": [
                    "网络延迟过高",
                    "请求处理时间过长"
                ],
                "suggested_actions": [
                    "增加超时时间",
                    "优化请求内容",
                    "检查网络连接"
                ]
            }
        }
    
    def record_error(self, error: Exception, model_name: str = "", 
                    request_size: int = 0, response_time: float = 0.0,
                    retry_count: int = 0) -> str:
        """
        记录API错误
        
        Args:
            error: 异常对象
            model_name: 模型名称
            request_size: 请求大小（字符数）
            response_time: 响应时间
            retry_count: 重试次数
            
        Returns:
            错误类型标识
        """
        error_msg = str(error).lower()
        error_type = self._classify_error(error_msg)
        
        # 记录错误事件
        event = APIErrorEvent(
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=str(error),
            model_name=model_name,
            request_size=request_size,
            response_time=response_time,
            retry_count=retry_count,
            is_resolved=False
        )
        
        self.error_history.append(event)
        self.error_stats[error_type] += 1
        self.performance_metrics["failed_requests"] += 1
        self.performance_metrics["total_retry_attempts"] += retry_count
        
        # 更新错误模式频率
        if error_type in self.error_patterns:
            self.error_patterns[error_type]["frequency"] += 1
        
        logger.warning(f"🚨 记录API错误: {error_type} - {str(error)}")
        return error_type
    
    def record_success(self, model_name: str = "", response_time: float = 0.0):
        """记录成功请求"""
        self.performance_metrics["successful_requests"] += 1
        self.performance_metrics["total_requests"] += 1
        
        # 更新平均响应时间
        total_successful = self.performance_metrics["successful_requests"] 
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total_successful - 1) + response_time) / total_successful
        )
    
    def _classify_error(self, error_msg: str) -> str:
        """分类错误类型"""
        for error_type, pattern in self.error_patterns.items():
            for keyword in pattern["keywords"]:
                if keyword in error_msg:
                    return error_type
        return "unknown_error"
    
    def analyze_recent_errors(self, hours: int = 24) -> Dict[str, Any]:
        """
        分析最近的错误模式
        
        Args:
            hours: 分析最近N小时的错误
            
        Returns:
            错误分析报告
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            event for event in self.error_history 
            if event.timestamp > cutoff_time
        ]
        
        if not recent_errors:
            return {
                "status": "healthy",
                "message": f"最近{hours}小时内无错误记录",
                "recommendations": ["系统运行正常，继续监控"]
            }
        
        # 错误统计
        error_counts = defaultdict(int)
        total_retries = 0
        
        for event in recent_errors:
            error_counts[event.error_type] += 1
            total_retries += event.retry_count
        
        # 找出最频繁的错误
        most_common_error = max(error_counts.items(), key=lambda x: x[1])
        
        analysis = {
            "analysis_period": f"{hours}小时",
            "total_errors": len(recent_errors),
            "error_breakdown": dict(error_counts),
            "most_common_error": {
                "type": most_common_error[0],
                "count": most_common_error[1],
                "percentage": (most_common_error[1] / len(recent_errors)) * 100
            },
            "total_retry_attempts": total_retries,
            "average_retries_per_error": total_retries / len(recent_errors),
            "recommendations": []
        }
        
        # 生成建议
        error_type = most_common_error[0]
        if error_type in self.error_patterns:
            pattern = self.error_patterns[error_type]
            analysis["likely_causes"] = pattern["typical_causes"]
            analysis["recommendations"] = pattern["suggested_actions"]
        
        # 严重程度评估
        error_rate = len(recent_errors) / hours
        if error_rate > 5:  # 每小时超过5个错误
            analysis["severity"] = "high"
            analysis["recommendations"].insert(0, "🚨 错误频率过高，建议立即检查系统配置")
        elif error_rate > 2:
            analysis["severity"] = "medium"
            analysis["recommendations"].insert(0, "⚠️ 错误频率偏高，建议优化请求策略")
        else:
            analysis["severity"] = "low"
        
        return analysis
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        total_requests = self.performance_metrics["total_requests"]
        if total_requests == 0:
            return {
                "status": "no_data",
                "message": "暂无请求数据",
                "success_rate": 0.0
            }
        
        success_rate = (self.performance_metrics["successful_requests"] / total_requests) * 100
        
        health_status = {
            "success_rate": success_rate,
            "total_requests": total_requests,
            "failed_requests": self.performance_metrics["failed_requests"],
            "average_response_time": self.performance_metrics["average_response_time"],
            "total_retries": self.performance_metrics["total_retry_attempts"],
            "monitoring_since": self.performance_metrics["last_reset"].isoformat()
        }
        
        # 健康等级评估
        if success_rate >= 95:
            health_status["status"] = "excellent"
            health_status["message"] = "系统运行状态优秀"
        elif success_rate >= 90:
            health_status["status"] = "good"
            health_status["message"] = "系统运行状态良好"
        elif success_rate >= 80:
            health_status["status"] = "warning"
            health_status["message"] = "系统运行状态需要关注"
        else:
            health_status["status"] = "critical"
            health_status["message"] = "系统运行状态严重异常"
        
        return health_status
    
    def generate_diagnostic_report(self) -> str:
        """生成诊断报告"""
        health = self.get_health_status()
        recent_analysis = self.analyze_recent_errors()
        
        report_lines = [
            "# Gemini API 诊断报告",
            f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 系统健康状态",
            f"- **状态等级**: {health.get('status', 'unknown')}",
            f"- **成功率**: {health.get('success_rate', 0):.2f}%",
            f"- **总请求数**: {health.get('total_requests', 0)}",
            f"- **失败请求数**: {health.get('failed_requests', 0)}",
            f"- **平均响应时间**: {health.get('average_response_time', 0):.2f}秒",
            f"- **总重试次数**: {health.get('total_retries', 0)}",
            "",
            "## 最近24小时错误分析"
        ]
        
        if recent_analysis.get("total_errors", 0) > 0:
            report_lines.extend([
                f"- **总错误数**: {recent_analysis['total_errors']}",
                f"- **最常见错误**: {recent_analysis['most_common_error']['type']} ({recent_analysis['most_common_error']['count']}次)",
                f"- **严重程度**: {recent_analysis.get('severity', 'unknown')}",
                "",
                "### 错误类型分布"
            ])
            
            for error_type, count in recent_analysis["error_breakdown"].items():
                report_lines.append(f"- {error_type}: {count}次")
            
            if "likely_causes" in recent_analysis:
                report_lines.extend([
                    "",
                    "### 可能原因",
                ])
                for cause in recent_analysis["likely_causes"]:
                    report_lines.append(f"- {cause}")
            
            if "recommendations" in recent_analysis:
                report_lines.extend([
                    "",
                    "### 改进建议"
                ])
                for rec in recent_analysis["recommendations"]:
                    report_lines.append(f"- {rec}")
        else:
            report_lines.append("- 最近24小时内无错误记录 ✅")
        
        # 历史趋势
        report_lines.extend([
            "",
            "## 错误类型历史统计"
        ])
        
        for error_type, count in sorted(self.error_stats.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"- {error_type}: {count}次")
        
        return "\n".join(report_lines)
    
    def reset_stats(self):
        """重置统计数据"""
        self.error_history.clear()
        self.error_stats.clear()
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_retry_attempts": 0,
            "average_response_time": 0.0,
            "last_reset": datetime.now()
        }
        
        for pattern in self.error_patterns.values():
            pattern["frequency"] = 0
        
        logger.info("📊 诊断统计数据已重置")


# 全局诊断实例
_global_diagnostics = None

def get_global_diagnostics() -> GeminiDiagnostics:
    """获取全局诊断实例"""
    global _global_diagnostics
    if _global_diagnostics is None:
        _global_diagnostics = GeminiDiagnostics()
    return _global_diagnostics


def save_diagnostic_report(output_path: str = "gemini_diagnostics_report.md") -> str:
    """
    保存诊断报告到文件
    
    Args:
        output_path: 输出文件路径
        
    Returns:
        保存的文件路径
    """
    diagnostics = get_global_diagnostics()
    report = diagnostics.generate_diagnostic_report()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"📋 诊断报告已保存到: {output_path}")
    return output_path