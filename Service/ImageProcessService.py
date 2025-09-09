import logging
import json
import google.generativeai as genai
import traceback
from pathlib import Path
from config import get_config
from config.Prompt import imagePrompt
import base64
from Service.OptimizedErrorHandler import OptimizedErrorHandler
from Service.SimpleCache import image_cache
from Service.AsyncProcessor import async_processor
import hashlib

# 設置日誌記錄
logger = logging.getLogger(__name__)

class ImageProcessService:
    def __init__(self):
        # 從配置檔讀取API金鑰、模型名稱和圖片處理的提示
        config = get_config()
        self.api_key = config['gemini']['apikey']
        self.model_name = config['gemini']['model']
        self.image_prompt = imagePrompt
        
        # 初始化錯誤處理器
        self.error_handler = OptimizedErrorHandler(__name__)
        
        # 初始化 Gemini
        genai.configure(api_key=self.api_key)
    
    @OptimizedErrorHandler(logger_name=__name__).fast_error_handler("處理圖片時發生錯誤")
    def imageParse(self, image_path):
        """
        處理圖片，進行圖像分析並回傳處理結果
        加入快取機制提升性能
        
        Args:
            image_path (str): 圖片的完整路徑
            
        Returns:
            dict: 包含處理結果的JSON物件
        """
        logger.info(f"開始處理圖片: {image_path}")
        
        # 確認圖片存在
        image_file = Path(image_path)
        if not image_file.exists():
            error_msg = f"圖片不存在: {image_path}"
            logger.error(error_msg)
            return {"result": error_msg}
        
        # 生成圖片快取鍵 (基於文件大小和修改時間)
        file_stat = image_file.stat()
        cache_key = hashlib.md5(f"{image_path}_{file_stat.st_size}_{file_stat.st_mtime}".encode()).hexdigest()
        
        # 檢查快取
        cached_result = image_cache.get(cache_key)
        if cached_result:
            logger.info(f"從快取獲取圖片分析結果: {image_path}")
            return cached_result
        
        # 讀取圖片
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # 使用 Gemini 模型處理圖片
        model = genai.GenerativeModel(self.model_name)
        
        # 創建帶有系統提示的請求
        image_parts = [
            {"text": self.image_prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_data).decode('utf-8')}}
        ]
        
        # 發送請求到 Gemini
        response = model.generate_content(image_parts)
        response_text = response.text
        
        # 檢查回應是否為 JSON 格式或包含 JSON 的文字
        try:
            # 首先嘗試直接解析整個回應為 JSON
            json_response = json.loads(response_text)
            logger.info(f"圖片處理完成，直接解析 JSON 成功")
        except json.JSONDecodeError:
            # 若都無法解析，則封裝為 result 格式
            logger.warning("無法解析 JSON，回傳原始文字")
            json_response = {"result": response_text}
        
        # 將結果存入快取
        image_cache.set(cache_key, json_response)
        
        logger.info(f"圖片處理完成")
        return json_response
