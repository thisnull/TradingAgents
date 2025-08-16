"""
LLM管理器模块

负责管理和创建不同类型的语言模型实例，支持OpenAI、Anthropic等多种提供商。
"""

import logging
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
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
            # OpenAI模型
            "gpt-4o": {
                "provider": "openai",
                "model_name": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 4096
            },
            "gpt-4o-mini": {
                "provider": "openai", 
                "model_name": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 4096
            },
            "o4-mini": {
                "provider": "openai",
                "model_name": "o1-mini",
                "temperature": 1.0,  # o1模型不支持temperature调节
                "max_tokens": 4096
            },
            "o1": {
                "provider": "openai",
                "model_name": "o1-preview",
                "temperature": 1.0,
                "max_tokens": 4096
            },
            
            # Anthropic模型
            "claude-3-opus": {
                "provider": "anthropic",
                "model_name": "claude-3-opus-20240229",
                "temperature": 0.1,
                "max_tokens": 4096
            },
            "claude-3-sonnet": {
                "provider": "anthropic",
                "model_name": "claude-3-sonnet-20240229", 
                "temperature": 0.1,
                "max_tokens": 4096
            },
            "claude-3-haiku": {
                "provider": "anthropic",
                "model_name": "claude-3-haiku-20240307",
                "temperature": 0.1,
                "max_tokens": 4096
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
                logger.warning(f"Model {model_name} not in supported models, using default gpt-4o-mini")
                model_name = "gpt-4o-mini"
            
            model_config = self.supported_models[model_name].copy()
            model_config.update(kwargs)  # 用传入的参数覆盖默认配置
            
            provider = model_config["provider"]
            
            # 创建LLM实例
            if provider == "openai":
                llm = self._create_openai_llm(model_config)
            elif provider == "anthropic":
                llm = self._create_anthropic_llm(model_config)
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
    
    def _create_openai_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
        """创建OpenAI LLM实例"""
        openai_config = {
            "model": config["model_name"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }
        
        # 添加API密钥和基础URL
        api_key = self.config.get("openai_api_key") or self.config.get("OPENAI_API_KEY")
        if api_key:
            openai_config["api_key"] = api_key
        
        base_url = self.config.get("openai_base_url") or self.config.get("OPENAI_BASE_URL")
        if base_url:
            openai_config["base_url"] = base_url
        
        # 处理o1模型的特殊情况
        if config["model_name"].startswith("o1"):
            # o1模型不支持temperature参数
            openai_config.pop("temperature", None)
            # o1模型使用max_completion_tokens而不是max_tokens
            openai_config["max_completion_tokens"] = openai_config.pop("max_tokens", 4096)
        
        return ChatOpenAI(**openai_config)
    
    def _create_anthropic_llm(self, config: Dict[str, Any]) -> ChatAnthropic:
        """创建Anthropic LLM实例"""
        anthropic_config = {
            "model": config["model_name"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }
        
        # 添加API密钥
        api_key = self.config.get("anthropic_api_key") or self.config.get("ANTHROPIC_API_KEY")
        if api_key:
            anthropic_config["api_key"] = api_key
        
        return ChatAnthropic(**anthropic_config)
    
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
            "openai_configured": bool(
                self.config.get("openai_api_key") or 
                self.config.get("OPENAI_API_KEY")
            ),
            "anthropic_configured": bool(
                self.config.get("anthropic_api_key") or 
                self.config.get("ANTHROPIC_API_KEY")
            ),
            "ollama_configured": True  # Ollama通常不需要密钥
        }
        
        return validation_results