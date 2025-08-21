"""
LLM管理器模块

负责管理和创建不同类型的语言模型实例，主要支持Google Gemini和Ollama本地模型。
集成了Gemini API诊断和监控功能。
"""

import logging
import os
import time
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from .gemini_diagnostics import get_global_diagnostics

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM管理器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LLM管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.llm_cache = {}  # LLM实例缓存
        
        # 支持的模型配置
        self.supported_models = {
            # Google Gemini 1.5系列模型（更稳定）
            "gemini-1.5-pro": {
                "provider": "gemini",
                "model_name": "gemini-1.5-pro",
                "temperature": 0.1,
                "max_tokens": 8192
            },
            "gemini-1.5-flash": {
                "provider": "gemini",
                "model_name": "gemini-1.5-flash",
                "temperature": 0.1,
                "max_tokens": 8192  # 1.5 Flash稳定版本，适中的token限制
            },
            
            # Google Gemini 2.5系列模型（可能不稳定）
            "gemini-2.5-pro": {
                "provider": "gemini",
                "model_name": "gemini-2.5-pro",
                "temperature": 0.1,
                "max_tokens": 8192
            },
            "gemini-2.5-flash": {
                "provider": "gemini",
                "model_name": "gemini-2.5-flash",
                "temperature": 0.1,
                "max_tokens": 32768  # 再次增加：从16384增加到32768支持完整趋势分析报告
            },
            
            # Ollama本地模型
            "llama3": {
                "provider": "ollama",
                "model_name": "llama3",
                "temperature": 0.1,
                "max_tokens": 4096
            },
            "qwen": {
                "provider": "ollama",
                "model_name": "qwen",
                "temperature": 0.1,
                "max_tokens": 4096
            }
        }
    
    def get_llm(self, model_name: str, **kwargs) -> Any:
        """
        获取LLM实例
        
        Args:
            model_name: 模型名称
            **kwargs: 额外的模型参数
            
        Returns:
            LLM实例
        """
        try:
            # 检查缓存
            cache_key = f"{model_name}_{hash(str(sorted(kwargs.items())))}"
            if cache_key in self.llm_cache:
                return self.llm_cache[cache_key]
            
            # 检查模型是否支持
            if model_name not in self.supported_models:
                logger.warning(f"Model {model_name} not in supported models, using default gemini-2.5-flash")
                model_name = "gemini-2.5-flash"
            
            model_config = self.supported_models[model_name].copy()
            model_config.update(kwargs)  # 用传入的参数覆盖默认配置
            
            provider = model_config["provider"]
            
            # 创建LLM实例
            if provider == "gemini":
                llm = self._create_gemini_llm(model_config)
            elif provider == "ollama":
                llm = self._create_ollama_llm(model_config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # 缓存实例
            self.llm_cache[cache_key] = llm
            
            logger.info(f"Created LLM instance: {model_name}")
            return llm
            
        except Exception as e:
            logger.error(f"Error creating LLM {model_name}: {str(e)}")
            raise
    
    def _create_gemini_llm(self, config: Dict[str, Any]) -> ChatGoogleGenerativeAI:
        """创建Google Gemini LLM实例"""
        # 基础配置 - 简化但有效的优化
        gemini_config = {
            "model": config["model_name"],
            "temperature": config["temperature"],
            "max_output_tokens": config["max_tokens"],
            "timeout": 300,  # 5分钟超时，应对复杂请求
            "max_retries": 5,  # 增加重试次数应对500错误
        }
        
        # 按优先级获取API密钥
        api_key = (
            os.getenv("GOOGLE_API_KEY") or 
            os.getenv("GEMINI_API_KEY") or
            self.config.get("google_api_key") or 
            self.config.get("gemini_api_key")
        )
        
        if not api_key:
            logger.error("Google API key not found in environment variables or config")
            logger.error("Please set one of: GOOGLE_API_KEY, GEMINI_API_KEY")
            raise ValueError("Missing Google API key. Please set GOOGLE_API_KEY environment variable.")
        
        # 显式设置API密钥
        gemini_config["google_api_key"] = api_key
        
        # 记录模型配置信息
        logger.info(f"Creating Gemini LLM with model: {config['model_name']}")
        
        try:
            return ChatGoogleGenerativeAI(**gemini_config)
        except Exception as e:
            logger.error(f"Failed to create Gemini LLM: {str(e)}")
            logger.error("Please verify your GOOGLE_API_KEY is valid and has access to Gemini models")
            raise
    
    def _wrap_gemini_with_error_handling(self, llm_instance):
        """为Gemini LLM添加特殊的错误处理包装，集成诊断系统"""
        from functools import wraps
        
        original_invoke = llm_instance.invoke
        diagnostics = get_global_diagnostics()
        
        @wraps(original_invoke)
        def enhanced_invoke(*args, **kwargs):
            max_attempts = 3
            base_delay = 5  # 基础延迟5秒
            start_time = time.time()
            
            # 计算请求大小
            request_size = 0
            if args:
                request_size = len(str(args[0])) if args[0] else 0
            
            for attempt in range(max_attempts):
                try:
                    result = original_invoke(*args, **kwargs)
                    
                    # 记录成功请求
                    response_time = time.time() - start_time
                    diagnostics.record_success(
                        model_name=getattr(llm_instance, 'model_name', 'gemini'),
                        response_time=response_time
                    )
                    
                    logger.info(f"✅ Gemini API调用成功 (响应时间: {response_time:.2f}s)")
                    return result
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    response_time = time.time() - start_time
                    
                    # 记录错误到诊断系统
                    error_type = diagnostics.record_error(
                        error=e,
                        model_name=getattr(llm_instance, 'model_name', 'gemini'),
                        request_size=request_size,
                        response_time=response_time,
                        retry_count=attempt + 1
                    )
                    
                    # 专门处理500错误
                    if "500" in error_msg or "internal error" in error_msg:
                        if attempt < max_attempts - 1:
                            delay = base_delay * (2 ** attempt)  # 指数退避
                            logger.warning(f"🔄 Gemini 500错误，{delay}秒后重试 (尝试 {attempt + 1}/{max_attempts})")
                            logger.warning(f"错误详情: {str(e)}")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error("❌ Gemini 500错误重试次数已用尽")
                            # 生成诊断建议
                            health = diagnostics.get_health_status()
                            recent_analysis = diagnostics.analyze_recent_errors(hours=1)
                            
                            logger.error(f"系统健康状态: {health.get('status', 'unknown')} (成功率: {health.get('success_rate', 0):.1f}%)")
                            
                            if recent_analysis.get('recommendations'):
                                logger.error("建议措施:")
                                for rec in recent_analysis['recommendations'][:3]:
                                    logger.error(f"  - {rec}")
                            
                            raise Exception(f"Gemini API持续500错误，已重试{max_attempts}次。错误类型: {error_type}。建议: 稍后重试或检查API配额。原始错误: {str(e)}")
                    
                    # 其他类型错误的特殊处理
                    elif "rate limit" in error_msg or "quota" in error_msg:
                        logger.error(f"🚫 API配额或速率限制错误: {str(e)}")
                        raise Exception(f"API配额不足或请求过于频繁: {str(e)}")
                    
                    elif "timeout" in error_msg or "deadline" in error_msg:
                        logger.error(f"⏰ API超时错误: {str(e)}")
                        if attempt < max_attempts - 1:
                            delay = base_delay * (attempt + 1)  # 线性增加延迟
                            logger.warning(f"网络超时，{delay}秒后重试")
                            time.sleep(delay)
                            continue
                    
                    # 其他错误直接抛出
                    raise
            
        llm_instance.invoke = enhanced_invoke
        return llm_instance
    
    def _create_ollama_llm(self, config: Dict[str, Any]) -> ChatOllama:
        """创建Ollama LLM实例"""
        ollama_config = {
            "model": config["model_name"],
            "temperature": config["temperature"]
        }
        
        # 添加Ollama服务器URL
        base_url = self.config.get("ollama_base_url", "http://localhost:11434")
        ollama_config["base_url"] = base_url
        
        return ChatOllama(**ollama_config)
    
    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表
        
        Returns:
            模型名称列表
        """
        return list(self.supported_models.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型配置信息
        """
        return self.supported_models.get(model_name)
    
    def add_custom_model(self, model_name: str, config: Dict[str, Any]):
        """
        添加自定义模型
        
        Args:
            model_name: 模型名称
            config: 模型配置
        """
        required_fields = ["provider", "model_name", "temperature", "max_tokens"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        self.supported_models[model_name] = config
        logger.info(f"Added custom model: {model_name}")
    
    def clear_cache(self):
        """清空LLM缓存"""
        self.llm_cache.clear()
        logger.info("LLM cache cleared")
    
    def validate_config(self) -> Dict[str, bool]:
        """
        验证配置
        
        Returns:
            验证结果字典
        """
        validation_results = {
            "gemini_configured": bool(
                os.getenv("GOOGLE_API_KEY") or 
                os.getenv("GEMINI_API_KEY") or
                self.config.get("google_api_key") or 
                self.config.get("gemini_api_key")
            ),
            "ollama_configured": True  # Ollama通常不需要密钥
        }
        
        return validation_results
    
    def get_diagnostics_report(self) -> str:
        """获取诊断报告"""
        diagnostics = get_global_diagnostics()
        return diagnostics.generate_diagnostic_report()
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状态"""
        diagnostics = get_global_diagnostics()
        return diagnostics.get_health_status()
    
    def save_diagnostics_report(self, output_path: str = "gemini_diagnostics_report.md") -> str:
        """
        保存诊断报告到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            保存的文件路径
        """
        from .gemini_diagnostics import save_diagnostic_report
        return save_diagnostic_report(output_path)
    
    def reset_diagnostics(self):
        """重置诊断数据"""
        diagnostics = get_global_diagnostics()
        diagnostics.reset_stats()
        logger.info("🔄 LLM诊断数据已重置")