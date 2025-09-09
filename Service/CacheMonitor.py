# ==========================================================
# 快取監控工具
# 用於監控和管理應用程式的快取狀態
# ==========================================================

import json
import logging
from typing import Dict, Any
from Service.SimpleCache import user_cache, app_cache, nlp_cache, image_cache
from Service.PhysInfoDataService import PhysInfoDataService

logger = logging.getLogger(__name__)

class CacheMonitor:
    """快取監控類別"""
    
    def __init__(self):
        self.phys_service = PhysInfoDataService()
    
    def get_all_cache_stats(self) -> Dict[str, Any]:
        """
        獲取所有快取的統計資訊
        
        Returns:
            Dict: 所有快取的統計資訊
        """
        stats = {
            "user_cache": self._get_cache_stats(user_cache, "用戶資料快取"),
            "app_cache": self._get_cache_stats(app_cache, "應用程式快取"),
            "nlp_cache": self._get_cache_stats(nlp_cache, "NLP快取"),
            "image_cache": self._get_cache_stats(image_cache, "圖像快取"),
            "phys_info_specific": self._get_phys_info_cache_stats()
        }
        return stats
    
    def _get_cache_stats(self, cache_instance, cache_name: str) -> Dict[str, Any]:
        """
        獲取特定快取實例的統計資訊
        
        Args:
            cache_instance: 快取實例
            cache_name: 快取名稱
            
        Returns:
            Dict: 快取統計資訊
        """
        try:
            if hasattr(cache_instance, 'get_stats'):
                stats = cache_instance.get_stats()
                stats['name'] = cache_name
                return stats
            else:
                return {
                    "name": cache_name,
                    "cache_size": len(cache_instance.cache) if hasattr(cache_instance, 'cache') else 0,
                    "status": "basic_cache"
                }
        except Exception as e:
            logger.error(f"獲取快取 {cache_name} 統計時發生錯誤: {str(e)}")
            return {
                "name": cache_name,
                "error": str(e),
                "status": "error"
            }
    
    def _get_phys_info_cache_stats(self) -> Dict[str, Any]:
        """
        獲取身體資訊快取的詳細統計
        
        Returns:
            Dict: 身體資訊快取統計
        """
        try:
            phys_cache_keys = [k for k in user_cache.cache.keys() if k.startswith('phys_info')]
            return {
                "total_phys_cache_items": len(phys_cache_keys),
                "cache_keys": phys_cache_keys[:10],  # 只顯示前10個
                "cache_key_patterns": {
                    "phys_info_master": len([k for k in phys_cache_keys if k.startswith('phys_info_') and not k.startswith('phys_info_user_')]),
                    "phys_info_user": len([k for k in phys_cache_keys if k.startswith('phys_info_user_')])
                }
            }
        except Exception as e:
            logger.error(f"獲取身體資訊快取統計時發生錯誤: {str(e)}")
            return {"error": str(e)}
    
    def refresh_user_cache(self, user_id: str) -> Dict[str, Any]:
        """
        刷新特定用戶的快取
        
        Args:
            user_id: 用戶ID
            
        Returns:
            Dict: 操作結果
        """
        try:
            success = self.phys_service.refresh_user_cache(user_id)
            return {
                "status": "success" if success else "failed",
                "user_id": user_id,
                "message": "快取刷新成功" if success else "快取刷新失敗"
            }
        except Exception as e:
            logger.error(f"刷新用戶 {user_id} 快取時發生錯誤: {str(e)}")
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e)
            }
    
    def clear_expired_cache(self) -> Dict[str, Any]:
        """
        清除過期的快取項目
        
        Returns:
            Dict: 清除結果
        """
        try:
            initial_sizes = {}
            final_sizes = {}
            
            # 清除各個快取的過期項目
            for cache_name, cache_instance in [
                ("user_cache", user_cache),
                ("app_cache", app_cache),
                ("nlp_cache", nlp_cache),
                ("image_cache", image_cache)
            ]:
                if hasattr(cache_instance, '_cleanup_expired'):
                    initial_sizes[cache_name] = len(cache_instance.cache)
                    cache_instance._cleanup_expired()
                    final_sizes[cache_name] = len(cache_instance.cache)
            
            return {
                "status": "success",
                "initial_sizes": initial_sizes,
                "final_sizes": final_sizes,
                "items_removed": {k: initial_sizes[k] - final_sizes[k] for k in initial_sizes}
            }
        except Exception as e:
            logger.error(f"清除過期快取時發生錯誤: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def generate_cache_report(self) -> str:
        """
        生成快取報告
        
        Returns:
            str: 快取報告文字
        """
        try:
            stats = self.get_all_cache_stats()
            
            report = []
            report.append("=== 快取狀態報告 ===\n")
            
            for cache_name, cache_stats in stats.items():
                if cache_name == "phys_info_specific":
                    report.append(f"📊 身體資訊快取詳細統計:")
                    report.append(f"   - 總計快取項目: {cache_stats.get('total_phys_cache_items', 0)}")
                    report.append(f"   - Master ID 快取: {cache_stats.get('cache_key_patterns', {}).get('phys_info_master', 0)}")
                    report.append(f"   - User ID 快取: {cache_stats.get('cache_key_patterns', {}).get('phys_info_user', 0)}")
                else:
                    if "error" in cache_stats:
                        report.append(f"❌ {cache_stats.get('name', cache_name)}: 錯誤 - {cache_stats['error']}")
                    else:
                        hit_rate = cache_stats.get('hit_rate', 0)
                        cache_size = cache_stats.get('cache_size', 0)
                        total_access = cache_stats.get('total_access', 0)
                        
                        report.append(f"✅ {cache_stats.get('name', cache_name)}:")
                        report.append(f"   - 快取大小: {cache_size}")
                        report.append(f"   - 總存取次數: {total_access}")
                        report.append(f"   - 命中率: {hit_rate:.1f}%")
                
                report.append("")
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"生成快取報告時發生錯誤: {str(e)}")
            return f"生成快取報告時發生錯誤: {str(e)}"

# 創建全域監控實例
cache_monitor = CacheMonitor()
