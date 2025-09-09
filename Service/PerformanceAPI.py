"""
性能監控 API - 提供系統性能指標和核心監控功能
"""
from flask import Blueprint, jsonify
from Service.ConnectionFactory import ConnectionFactory
from Service.SimpleCache import app_cache, nlp_cache, image_cache, user_cache
from Service.UnifiedResponseService import unified_response_service
import time
import logging
from typing import Dict, Any
from functools import wraps
from collections import deque

# PerformanceMonitor 類別定義
class PerformanceMonitor:
    def __init__(self):
        self.response_times = deque(maxlen=100)  # 保存最近100次的響應時間
        self.error_count = 0
        self.total_requests = 0
        self.logger = logging.getLogger(__name__)
        
    def timing_decorator(self, operation_name: str = "operation"):
        """
        用於測量方法執行時間的裝飾器
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                self.total_requests += 1
                
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    self.response_times.append(response_time)
                    
                    # 只在響應時間過長時記錄警告
                    if response_time > 3.0:  # 超過3秒
                        self.logger.warning(f"{operation_name} 響應時間過長: {response_time:.2f}秒")
                    
                    return result
                    
                except Exception as e:
                    self.error_count += 1
                    end_time = time.time()
                    response_time = end_time - start_time
                    self.response_times.append(response_time)
                    
                    self.logger.error(f"{operation_name} 發生錯誤 (耗時: {response_time:.2f}秒): {str(e)}")
                    raise
                    
            return wrapper
        return decorator
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        獲取性能統計資訊
        """
        if not self.response_times:
            return {
                "total_requests": self.total_requests,
                "error_count": self.error_count,
                "avg_response_time": 0,
                "max_response_time": 0,
                "min_response_time": 0
            }
        
        times = list(self.response_times)
        return {
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.total_requests) * 100 if self.total_requests > 0 else 0,
            "avg_response_time": sum(times) / len(times),
            "max_response_time": max(times),
            "min_response_time": min(times),
            "recent_requests": len(times)
        }
    
    def should_alert(self) -> bool:
        """
        判斷是否應該發出性能警報
        """
        if len(self.response_times) < 10:
            return False
            
        # 計算最近10次請求的平均響應時間
        recent_times = list(self.response_times)[-10:]
        avg_recent = sum(recent_times) / len(recent_times)
        
        # 如果平均響應時間超過2秒，發出警報
        return avg_recent > 2.0

# 創建全局性能監控實例
performance_monitor = PerformanceMonitor()

# 創建藍圖
performance_bp = Blueprint('performance', __name__, url_prefix='/api/v1/performance')

@performance_bp.route('/stats', methods=['GET'])
def get_performance_stats():
    """獲取性能統計"""
    try:
        # 應用程式性能統計
        app_stats = performance_monitor.get_performance_stats()
        
        # 資料庫性能統計
        db_stats = ConnectionFactory.get_performance_stats()
        
        # 快取統計（增強版）
        cache_stats = {
            "app_cache": app_cache.get_stats() if hasattr(app_cache, 'get_stats') else {"size": len(app_cache.cache)},
            "nlp_cache": nlp_cache.get_stats() if hasattr(nlp_cache, 'get_stats') else {"size": len(nlp_cache.cache)},
            "image_cache": image_cache.get_stats() if hasattr(image_cache, 'get_stats') else {"size": len(image_cache.cache)},
            "user_cache": user_cache.get_stats() if hasattr(user_cache, 'get_stats') else {"size": len(user_cache.cache)}
        }
        
        # 快速響應優化統計
        optimization_stats = unified_response_service.get_optimization_stats()
        
        return jsonify({
            "status": "success",
            "timestamp": time.time(),
            "performance": app_stats,
            "database": db_stats,
            "cache": cache_stats,
            "optimization": optimization_stats,
            "recommendations": _get_performance_recommendations(app_stats, db_stats, optimization_stats)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"獲取性能統計失敗: {str(e)}"
        }), 500

@performance_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    try:
        # 簡單的健康檢查
        db_connection = ConnectionFactory.create_connection()
        db_healthy = db_connection is not None
        if db_connection:
            ConnectionFactory.close_connection(db_connection)
        
        # 檢查性能警報
        performance_alert = performance_monitor.should_alert()
        
        health_status = "healthy" if db_healthy and not performance_alert else "warning"
        
        return jsonify({
            "status": health_status,
            "timestamp": time.time(),
            "database": "connected" if db_healthy else "disconnected",
            "performance": "normal" if not performance_alert else "slow"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"健康檢查失敗: {str(e)}"
        }), 500

def _get_performance_recommendations(app_stats, db_stats, optimization_stats):
    """生成性能建議"""
    recommendations = []
    
    # 檢查平均響應時間
    if app_stats.get("avg_response_time", 0) > 2.0:
        recommendations.append("平均響應時間過長，建議檢查 NLP 和圖像處理性能")
    
    # 檢查錯誤率
    if app_stats.get("error_rate", 0) > 5.0:
        recommendations.append("錯誤率過高，建議檢查錯誤日誌")
    
    # 檢查資料庫性能
    if db_stats.get("avg_query_time", 0) > 1.0:
        recommendations.append("資料庫查詢時間過長，建議優化查詢或加入索引")
    
    # 檢查連接池使用
    if db_stats.get("active_connections", 0) >= 5:
        recommendations.append("資料庫連接池接近滿載，考慮增加連接數")
    
    # 檢查快速響應效率
    quick_response_rate = optimization_stats.get("quick_response_rate", 0)
    if quick_response_rate < 20:
        recommendations.append("快速響應命中率較低，考慮擴展快速響應模式")
    elif quick_response_rate > 60:
        recommendations.append("快速響應效果良好！響應時間已大幅優化")
    
    # 檢查快取效果
    cache_hit_rate = optimization_stats.get("cache_hits", 0) / max(
        optimization_stats.get("cache_hits", 0) + optimization_stats.get("cache_misses", 0), 1
    ) * 100
    
    if cache_hit_rate < 50:
        recommendations.append("快取命中率較低，建議檢查快取策略")
    
    return recommendations
