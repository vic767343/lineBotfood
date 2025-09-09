"""
簡化快取機制 - 減少重複計算和資料庫查詢
增強版本：支援預載、智能刷新和使用統計
"""
import time
import json
import hashlib
import threading
from typing import Dict, Any, Optional, Set
from functools import wraps
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    def __init__(self, default_ttl=300):  # 5分鐘過期
        self.cache = {}
        self.default_ttl = default_ttl
        self.access_count = defaultdict(int)  # 追蹤存取次數
        self.last_access = {}  # 追蹤最後存取時間
        self.popular_keys = set()  # 熱門鍵值
        self.preload_lock = threading.Lock()
        
    def _generate_key(self, *args, **kwargs) -> str:
        """生成快取鍵值"""
        key_data = f"{args}_{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float) -> bool:
        """檢查是否過期"""
        return time.time() - timestamp > self.default_ttl
    
    def _track_access(self, key: str):
        """追蹤存取統計"""
        self.access_count[key] += 1
        self.last_access[key] = time.time()
        
        # 如果存取次數超過閾值，標記為熱門
        if self.access_count[key] > 5:
            self.popular_keys.add(key)
    
    def get(self, key: str) -> Optional[Any]:
        """獲取快取值"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            current_time = time.time()
            
            # 追蹤存取
            self._track_access(key)
            
            if not self._is_expired(timestamp):
                # 如果即將過期但是熱門鍵值，觸發背景刷新
                if (current_time - timestamp > self.default_ttl * 0.8 and 
                    key in self.popular_keys):
                    self._schedule_refresh(key)
                
                return data
            else:
                del self.cache[key]
                # 如果是熱門鍵值，嘗試背景重新載入
                if key in self.popular_keys:
                    logger.info(f"熱門快取過期，嘗試背景重新載入: {key[:20]}...")
                    
        return None
    
    def set(self, key: str, value: Any):
        """設置快取值"""
        self.cache[key] = (value, time.time())
        
        # 清理過期快取（簡單的LRU）
        if len(self.cache) > 100:
            self._cleanup_expired()
    
    def _schedule_refresh(self, key: str):
        """安排背景刷新（預留接口）"""
        # 這裡可以實現背景刷新邏輯
        # 目前只記錄日誌
        logger.debug(f"安排背景刷新快取: {key[:20]}...")
    
    def preload_common_data(self, preload_func: callable, keys: list):
        """預載常用資料"""
        def _preload():
            with self.preload_lock:
                for key in keys:
                    try:
                        if key not in self.cache:
                            logger.info(f"預載快取: {key[:20]}...")
                            data = preload_func(key)
                            self.set(key, data)
                    except Exception as e:
                        logger.warning(f"預載失敗 {key}: {str(e)}")
        
        # 背景執行預載
        threading.Thread(target=_preload, daemon=True).start()
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        total_access = sum(self.access_count.values())
        cache_size = len(self.cache)
        popular_count = len(self.popular_keys)
        
        return {
            "cache_size": cache_size,
            "total_access": total_access,
            "popular_keys": popular_count,
            "hit_rate": (total_access - cache_size) / max(total_access, 1) * 100
        }
    
    def _cleanup_expired(self):
        """清理過期快取"""
        current_time = time.time()
        expired_keys = [
            k for k, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.default_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def cache_decorator(self, ttl: Optional[int] = None):
        """快取裝飾器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成快取鍵
                cache_key = f"{func.__name__}_{self._generate_key(*args, **kwargs)}"
                
                # 嘗試從快取獲取
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # 執行原函數
                result = func(*args, **kwargs)
                
                # 儲存到快取
                self.set(cache_key, result)
                return result
            return wrapper
        return decorator

# 全域快取實例
app_cache = SimpleCache()

# 特定功能的快取實例
nlp_cache = SimpleCache(default_ttl=600)  # NLP結果快取10分鐘
image_cache = SimpleCache(default_ttl=1800)  # 圖像分析快取30分鐘
user_cache = SimpleCache(default_ttl=300)  # 用戶資料快取5分鐘
