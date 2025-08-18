"""
LLM管理器模块

负责管理和创建不同类型的语言模型实例，主要支持Google Gemini和Ollama本地模型。
"""

import logging
import os
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama

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
            # Google Gemini 2.5系列模型
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
                "max_tokens": 8192
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
        # 基础配置
        gemini_config = {
            "model": config["model_name"],
            "temperature": config["temperature"],
            "max_output_tokens": config["max_tokens"]  # 使用 max_output_tokens 而不是 max_tokens
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