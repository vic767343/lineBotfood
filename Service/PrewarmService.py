"""
預熱服務 - 提前初始化連接和載入模型以減少首次響應時間
"""
import logging
import threading
import time
import requests
from typing import Optional
import google.generativeai as genai
from config import get_config

logger = logging.getLogger(__name__)

class PrewarmService:
    def __init__(self):
        self.is_prewarmed = False
        self.gemini_client = None
        self.prewarmed_connections = []
        
    def prewarm_gemini_connection(self):
        """預熱 Gemini API 連接"""
        try:
            config = get_config()
            genai.configure(api_key=config['gemini']['apikey'])
            
            # 預建立連接
            model = genai.GenerativeModel(config['gemini']['model'])
            
            # 發送一個簡單的測試請求來建立連接
            test_response = model.generate_content("Hello", stream=False)
            
            self.gemini_client = model
            logger.info("Gemini API 連接預熱完成")
            return True
            
        except Exception as e:
            logger.warning(f"Gemini API 預熱失敗: {str(e)}")
            return False
    
    def prewarm_database_connections(self):
        """預熱資料庫連接"""
        try:
            from Service.ConnectionFactory import ConnectionPool
            
            # 確保連接池已初始化
            pool = ConnectionPool()
            
            # 測試連接
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            logger.info("資料庫連接預熱完成")
            return True
            
        except Exception as e:
            logger.warning(f"資料庫連接預熱失敗: {str(e)}")
            return False
    
    def prewarm_services(self):
        """預熱所有服務"""
        if self.is_prewarmed:
            return True
            
        logger.info("開始預熱服務...")
        start_time = time.time()
        
        # 並行預熱
        tasks = []
        
        # Gemini API 預熱
        gemini_thread = threading.Thread(target=self.prewarm_gemini_connection)
        gemini_thread.start()
        tasks.append(gemini_thread)
        
        # 資料庫預熱
        db_thread = threading.Thread(target=self.prewarm_database_connections)
        db_thread.start()
        tasks.append(db_thread)
        
        # 等待所有預熱完成
        for task in tasks:
            task.join(timeout=10)  # 10秒超時
        
        self.is_prewarmed = True
        end_time = time.time()
        
        logger.info(f"服務預熱完成，耗時: {end_time - start_time:.2f}秒")
        return True
    
    def get_prewarmed_gemini_client(self):
        """獲取預熱的 Gemini 客戶端"""
        if not self.is_prewarmed:
            self.prewarm_services()
        return self.gemini_client

# 全域預熱服務實例
prewarm_service = PrewarmService()

def initialize_prewarm():
    """應用程式啟動時調用的預熱初始化"""
    def async_prewarm():
        try:
            prewarm_service.prewarm_services()
        except Exception as e:
            logger.error(f"服務預熱異常: {str(e)}")
    
    # 在背景執行預熱
    prewarm_thread = threading.Thread(target=async_prewarm, daemon=True)
    prewarm_thread.start()
    
    logger.info("預熱服務已啟動")
