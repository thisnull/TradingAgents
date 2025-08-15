"""
数据缓存模块
提供数据缓存功能以提高性能和减少API调用
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps
import pickle
import logging

logger = logging.getLogger(__name__)

class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: str = "./cache", default_ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认缓存时间（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
    
    def _get_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将函数名和参数组合生成唯一键
        key_str = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def get(self, cache_key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存数据，如果不存在或过期则返回None
        """
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # 检查是否过期
            if time.time() - cache_data['timestamp'] > cache_data['ttl']:
                logger.debug(f"Cache expired for key: {cache_key}")
                cache_path.unlink()  # 删除过期缓存
                return None
            
            logger.debug(f"Cache hit for key: {cache_key}")
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None
    
    def set(self, cache_key: str, data: Any, ttl: Optional[int] = None):
        """
        设置缓存数据
        
        Args:
            cache_key: 缓存键
            data: 要缓存的数据
            ttl: 缓存时间（秒），None则使用默认值
        """
        cache_path = self._get_cache_path(cache_key)
        cache_data = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.debug(f"Cache set for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
    
    def delete(self, cache_key: str):
        """删除缓存"""
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Cache deleted for key: {cache_key}")
    
    def clear_all(self):
        """清空所有缓存"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        logger.info("All cache cleared")
    
    def cache_decorator(self, ttl: Optional[int] = None):
        """
        缓存装饰器
        
        Args:
            ttl: 缓存时间（秒）
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._get_cache_key(func.__name__, *args, **kwargs)
                
                # 尝试从缓存获取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 保存到缓存
                self.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_count": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir),
        }


class MemoryCache:
    """内存缓存（用于短期高频访问数据）"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认缓存时间（秒）
        """
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_count = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() - entry['timestamp'] > entry['ttl']:
            del self.cache[key]
            return None
        
        # 更新访问计数
        self.access_count[key] = self.access_count.get(key, 0) + 1
        return entry['data']
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None):
        """设置缓存数据"""
        # 如果缓存已满，删除最少访问的条目
        if len(self.cache) >= self.max_size and key not in self.cache:
            # 找出访问次数最少的键
            min_key = min(self.access_count.keys(), 
                         key=lambda k: self.access_count[k])
            del self.cache[min_key]
            del self.access_count[min_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl
        }
        self.access_count[key] = 0
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_count.clear()
