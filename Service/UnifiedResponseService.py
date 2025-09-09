"""
統一響應優化服務 - 整合快速響應和快取機制
整合了 FastResponseOptimizer 和 FastResponseHandler 的功能
"""
from typing import Dict, Any, Optional, List
from Service.SimpleCache import SimpleCache, nlp_cache
import re
import time
import logging
import threading

logger = logging.getLogger(__name__)

class UnifiedResponseService:
    def __init__(self):
        # 創建專用的響應快取
        self.response_cache = SimpleCache(default_ttl=600)  # 10分鐘過期
        
        # 預定義的完全匹配（從FastResponseHandler整合）
        self.exact_matches = {
            "你好": "您好！我是營養助手，可以幫您分析食物和管理卡路里。",
            "謝謝": "不客氣！有什麼需要幫助的嗎？", 
            "再見": "再見！祝您有美好的一天！",
            "hi": "Hello! I'm your nutrition assistant.",
            "hello": "Hello! How can I help you today?",
            "thank you": "You're welcome!",
            "thanks": "You're welcome!",
            "bye": "Goodbye! Have a great day!",
        }
        
        # 預定義的模式匹配（從FastResponseOptimizer整合）
        self.pattern_matches = {
            r'你好|哈囉|嗨|hi|hello': "您好！我是您的營養助手，有什麼可以幫助您的嗎？",
            r'謝謝|感謝|thank': "不客氣！很高興能幫助您 😊",
            r'再見|bye|掰掰': "再見！記得保持健康的飲食習慣哦 👋",
            r'幫助|help|怎麼用': "我可以幫您：\n📊 分析食物營養\n📈 追蹤卡路里\n📋 查詢飲食紀錄\n💪 計算BMI",
        }
        
        # FAQ回應（從FastResponseOptimizer整合）
        self.faq_responses = {
            "如何計算BMI": "BMI = 體重(kg) / 身高(m)²\n正常範圍：18.5-24.9\n請告訴我您的身高體重，我來幫您計算！",
            "怎麼記錄食物": "您可以:\n1️⃣ 拍照上傳食物圖片\n2️⃣ 直接輸入食物名稱\n3️⃣ 描述您吃了什麼\n我會自動分析營養成分！",
            "卡路里查詢": "請告訴我您想查詢的時間範圍:\n• 今天\n• 昨天\n• 這週\n• 本月\n或指定日期範圍",
        }
        
        # 關鍵詞快速識別（從FastResponseOptimizer整合）
        self.intent_keywords = {
            'greeting': ['你好', '哈囉', '嗨', 'hi', 'hello'],
            'thanks': ['謝謝', '感謝', 'thank'],
            'goodbye': ['再見', 'bye', '掰掰'],
            'help': ['幫助', 'help', '怎麼用'],
            'bmi': ['BMI', 'bmi', '身體質量', '體重指數'],
            'calories': ['卡路里', '熱量', 'cal', 'kcal'],
            'food_record': ['記錄', '紀錄', '輸入', '新增'],
            'search': ['查詢', '搜尋', '找', '看'],
        }
        
        # 編譯正則表達式以提高性能
        self.compiled_patterns = {
            re.compile(pattern, re.IGNORECASE): response 
            for pattern, response in self.pattern_matches.items()
        }
        
        # 統計
        self.total_requests = 0
        self.quick_response_count = 0
        self.stats = {
            "exact_match_hits": 0,
            "pattern_match_hits": 0,
            "faq_match_hits": 0,
            "cache_hits": 0,
        }
    
    def should_use_quick_response(self, message_text: str) -> bool:
        """判斷是否應該使用快速響應"""
        # 短訊息通常可以快速響應
        if len(message_text.strip()) <= 10:
            return True
        
        # 包含快速響應關鍵詞
        intent = self.quick_intent_classify(message_text)
        if intent in ['greeting', 'thanks', 'goodbye', 'help']:
            return True
        
        return False
    
    def quick_intent_classify(self, message_text: str) -> Optional[str]:
        """快速意圖分類"""
        normalized_text = message_text.lower()
        
        # 使用關鍵詞快速分類
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in normalized_text:
                    return intent
        
        return None
    
    def process_message(self, user_id: str, message_text: str) -> Optional[Dict[str, Any]]:
        """
        統一的訊息處理方法
        整合所有快速響應和快取檢查邏輯
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # 檢查是否可以快速響應
            if not self.should_use_quick_response(message_text):
                return None
            
            # 1. 檢查是否已有快取結果
            cache_key = f"response:{user_id}:{message_text}"
            cached_result = self.response_cache.get(cache_key)
            
            if cached_result:
                self.stats["cache_hits"] += 1
                self.quick_response_count += 1
                
                return {
                    "result": cached_result,
                    "intent": self.quick_intent_classify(message_text),
                    "processing_time": time.time() - start_time,
                    "source": "cache"
                }
            
            # 2. 檢查完全匹配
            normalized_text = message_text.lower().strip()
            for key, response in self.exact_matches.items():
                if normalized_text == key.lower() or normalized_text == key.lower() + "！" or normalized_text == key.lower() + "!":
                    self.stats["exact_match_hits"] += 1
                    self.quick_response_count += 1
                    
                    # 儲存到快取
                    self.response_cache.set(cache_key, response)
                    return {
                        "result": response,
                        "intent": self.quick_intent_classify(message_text),
                        "processing_time": time.time() - start_time,
                        "source": "exact_match"
                    }
            
            # 3. 檢查模式匹配
            for pattern, response in self.compiled_patterns.items():
                if pattern.search(normalized_text):
                    self.stats["pattern_match_hits"] += 1
                    self.quick_response_count += 1
                    
                    # 儲存到快取
                    self.response_cache.set(cache_key, response)
                    return {
                        "result": response,
                        "intent": self.quick_intent_classify(message_text),
                        "processing_time": time.time() - start_time,
                        "source": "pattern_match"
                    }
            
            # 4. 檢查FAQ匹配
            for question, answer in self.faq_responses.items():
                if self._similarity_check(normalized_text, question.lower()):
                    self.stats["faq_match_hits"] += 1
                    self.quick_response_count += 1
                    
                    # 儲存到快取
                    self.response_cache.set(cache_key, answer)
                    return {
                        "result": answer,
                        "intent": self.quick_intent_classify(message_text),
                        "processing_time": time.time() - start_time,
                        "source": "faq_match"
                    }
            
            # 沒有快速響應
            return None
            
        except Exception as e:
            logger.error(f"統一響應服務處理失敗: {str(e)}")
            return None
    
    def _similarity_check(self, text1: str, text2: str) -> bool:
        """簡單的相似度檢查"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return False
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) > 0.6
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """獲取優化統計"""
        quick_response_rate = (
            self.quick_response_count / max(self.total_requests, 1) * 100
        )
        
        cache_stats = self.response_cache.get_stats()
        
        return {
            "total_requests": self.total_requests,
            "quick_responses": self.quick_response_count,
            "quick_response_rate": quick_response_rate,
            "exact_match_hits": self.stats["exact_match_hits"],
            "pattern_match_hits": self.stats["pattern_match_hits"],
            "faq_match_hits": self.stats["faq_match_hits"],
            "cache_hits": self.stats["cache_hits"],
            "cache_stats": cache_stats
        }

# 全域統一響應服務實例
unified_response_service = UnifiedResponseService()
