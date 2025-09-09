"""
優化的錯誤處理器，用於提高響應速度和統一錯誤處理流程
"""
import logging
from typing import Dict, Any, Optional, Union
from functools import wraps
import time

class OptimizedErrorHandler:
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self.error_count = 0
        self.last_error_time = None
        
    def fast_error_handler(self, default_response: str = "系統暫時無法處理您的請求，請稍後再試"):
        """
        快速錯誤處理裝飾器 - 減少錯誤處理時間
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    return self._handle_error(e, func.__name__, default_response)
            return wrapper
        return decorator
    
    def api_error_handler(self, success_status: int = 200):
        """
        API專用錯誤處理裝飾器 - 返回Flask jsonify格式
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    if isinstance(result, dict) and result.get('status') == 'error':
                        return result, 500
                    return result, success_status
                except Exception as e:
                    error_response = self._handle_error(e, func.__name__, "API請求處理失敗")
                    return error_response, 500
            return wrapper
        return decorator
    
    def _handle_error(self, exception: Exception, func_name: str, default_message: str) -> Dict[str, Any]:
        """
        統一錯誤處理邏輯
        """
        self.error_count += 1
        self.last_error_time = time.time()
        
        # 根據日誌級別決定記錄詳細程度
        if self.should_skip_detailed_logging():
            # 高頻錯誤時只記錄簡單訊息
            self.logger.warning(f"頻繁錯誤: {func_name}")
        elif self.logger.isEnabledFor(logging.DEBUG):
            # 開發模式記錄詳細錯誤
            self.logger.error(f"Error in {func_name}: {str(exception)}", exc_info=True)
        else:
            # 生產模式記錄基本錯誤
            self.logger.error(f"Error in {func_name}: {type(exception).__name__}")
        
        return {
            "result": default_message,
            "status": "error",
            "timestamp": time.time()
        }
    
    def validate_input_fast(self, data: Dict[str, Any], required_fields: list) -> Optional[str]:
        """
        快速輸入驗證 - 減少驗證時間
        """
        for field in required_fields:
            if field not in data or not data[field]:
                return f"缺少必要欄位: {field}"
        return None
    
    def should_skip_detailed_logging(self) -> bool:
        """
        判斷是否應該跳過詳細日誌記錄（基於錯誤頻率）
        """
        if self.error_count > 10 and self.last_error_time:
            # 如果錯誤頻繁，減少日誌記錄
            return time.time() - self.last_error_time < 60  # 1分鐘內
        return False
