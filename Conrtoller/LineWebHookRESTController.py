from flask import Blueprint, request, jsonify
import logging
import requests
import json
import os
import time
import hashlib
from pathlib import Path
from Service.lineJoinService import LineJoinService
from Service.nlpService import NLPService
from Service.ImageProcessService import ImageProcessService
from Service.managerCalService import ManagerCalService
from Service.FoodDataService import FoodDataService
from Service.OptimizedErrorHandler import OptimizedErrorHandler
from Service.SimpleCache import app_cache, nlp_cache, image_cache, user_cache
from Service.AsyncProcessor import async_processor
from Service.UnifiedResponseService import unified_response_service
from config.line_config import lineToken, getContentURL, sendReplyMessageUrl

# 創建藍圖
line_webhook_bp = Blueprint('line_webhook', __name__, url_prefix='/api/v1')
# 初始化服務
line_join_service = LineJoinService()
# 設置日誌記錄
logger = logging.getLogger(__name__)

# 事件去重機制 - 用於追蹤已處理的事件
class EventDeduplicator:
    def __init__(self, max_size=1000, expire_time=300):  # 5分鐘過期
        self.processed_events = {}
        self.max_size = max_size
        self.expire_time = expire_time
    
    def _generate_event_key(self, event):
        """生成事件的唯一識別鍵"""
        # 使用關鍵字段生成事件標識
        key_parts = [
            event.get('type', ''),
            event.get('replyToken', ''),
            event.get('source', {}).get('userId', ''),
            event.get('message', {}).get('id', ''),
            event.get('timestamp', '')
        ]
        key_string = '|'.join(str(part) for part in key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def is_duplicate(self, event):
        """檢查事件是否已被處理過"""
        event_key = self._generate_event_key(event)
        current_time = time.time()
        
        # 清理過期的事件記錄
        self._cleanup_expired_events(current_time)
        
        # 檢查事件是否已處理
        if event_key in self.processed_events:
            logger.warning(f"檢測到重複事件: {event_key}")
            return True
        
        # 記錄新事件
        self.processed_events[event_key] = current_time
        return False
    
    def _cleanup_expired_events(self, current_time):
        """清理過期的事件記錄"""
        if len(self.processed_events) > self.max_size:
            # 如果超過最大大小，清理最舊的一半記錄
            sorted_events = sorted(self.processed_events.items(), key=lambda x: x[1])
            for key, _ in sorted_events[:self.max_size // 2]:
                del self.processed_events[key]
        
        # 清理過期事件
        expired_keys = [
            key for key, timestamp in self.processed_events.items()
            if current_time - timestamp > self.expire_time
        ]
        for key in expired_keys:
            del self.processed_events[key]

# 初始化事件去重器
event_deduplicator = EventDeduplicator()

# 全域服務實例 - 避免重複初始化
_nlp_service = None
_image_process_service = None
_manager_cal_service = None
_food_data_service = None

def get_nlp_service():
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPService()
    return _nlp_service

def get_image_process_service():
    global _image_process_service
    if _image_process_service is None:
        _image_process_service = ImageProcessService()
    return _image_process_service

def get_manager_cal_service():
    global _manager_cal_service
    if _manager_cal_service is None:
        _manager_cal_service = ManagerCalService()
    return _manager_cal_service

def get_food_data_service():
    global _food_data_service
    if _food_data_service is None:
        _food_data_service = FoodDataService()
    return _food_data_service

class LineMessageHandler:
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {lineToken}'
        }
        # 使用單例服務實例
        self.nlp_service = get_nlp_service()
        self.image_process_service = get_image_process_service()
        self.manager_cal_service = get_manager_cal_service()
        self.food_data_service = get_food_data_service()
        # 初始化優化的錯誤處理器
        self.error_handler = OptimizedErrorHandler(__name__)
        
    @OptimizedErrorHandler(logger_name=__name__).fast_error_handler("抱歉，處理您的訊息時發生錯誤")
    def handle_message_event(self, event):
        """處理 LINE Webhook 的 message 事件"""
        # 簡化驗證邏輯 - 快速失敗原則
        if not isinstance(event, dict) or event.get('type') != 'message':
            return None
        
        message = event.get('message', {})
        source = event.get('source', {})
        message_type = message.get('type')
        user_id = source.get('userId')
        reply_token = event.get('replyToken')
        
        # 確保必要的資訊存在
        if not reply_token:
            logger.warning(f"訊息事件缺少 replyToken，跳過處理: {event}")
            return None
            
        if not user_id:
            logger.warning(f"訊息事件缺少 userId，跳過處理: {event}")
            return None
        
        # 快速處理不同訊息類型
        if message_type == 'text':
            self._handle_text_message_fast(event, user_id, reply_token)
        elif message_type == 'image':
            self._handle_image_message(event, user_id, reply_token)
        elif message_type == 'audio':
            self._handle_audio_message(event, user_id, reply_token)
        else:
            # 快速回覆不支援的訊息類型
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': f'抱歉，目前不支援 {message_type} 類型的訊息'
                }])
        return None
    
    def _handle_text_message_fast(self, event, user_id, reply_token):
        """快速處理文字訊息 - 使用統一響應服務"""
        text = event.get('message', {}).get('text', '')
        if not text or not user_id:
            return
        
        # 使用統一響應服務處理
        response = unified_response_service.process_message(user_id, text)
        if response:
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': response['result']
                }])
            return
        
        # 3. 檢查快取
        cache_key = f"nlp_{user_id}_{text}"
        cached_response = nlp_cache.get(cache_key)
        if cached_response:
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': cached_response
                }])
            return
        
        # 4. 異步處理 NLP
        try:
            nlp_response = self.nlp_service.nlpProcess(user_id, text)
            
            if 'result' in nlp_response and reply_token:
                response_text = nlp_response['result']
                # 快取結果
                nlp_cache.set(cache_key, response_text)
                
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': response_text
                }])
        except Exception as e:
            logger.error(f"NLP處理錯誤: {str(e)}")
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': "抱歉，處理您的訊息時發生錯誤，請稍後再試。"
                }])
    
    # 註解掉的舊方法 - 已被 _handle_text_message_fast 取代
    # def _handle_text_message(self, event, reply_token):
    #     """處理文字訊息"""
    #     text = event.get('message', {}).get('text', '')
    #     user_id = event.get('source', {}).get('userId', '')
    #     
    #     try:
    #         # 將文字訊息直接送至 NLP 服務處理
    #         nlp_response = self.nlp_service.nlpProcess(user_id, text)
    #         
    #         # 處理 NLP 服務回應
    #         if 'result' in nlp_response:
    #             if reply_token:
    #                 self.send_reply(reply_token, [{
    #                     'type': 'text',
    #                     'text': nlp_response['result']
    #                 }])
    #         else:
    #             logger.warning(f"未知的 NLP 回應格式: {nlp_response}")
    #             if reply_token:
    #                 self.send_reply(reply_token, [{
    #                     'type': 'text',
    #                     'text': "很抱歉，無法處理您的請求。"
    #                 }])
    #                 
    #     except Exception as e:
    #         logger.error(f"文字訊息處理時發生錯誤: {str(e)}")
    #         error_message = f"處理文字訊息時發生錯誤: {str(e)}"
    #         
    #         # 將錯誤訊息傳送給 NLP 服務處理
         
                    
    # 送回覆訊息給使用者             
    def send_reply(self, reply_token, messages):
        """發送回覆訊息給使用者"""
        try:
            # 檢查 reply_token 是否有效
            if not reply_token:
                logger.warning("嘗試使用空的 reply_token 發送訊息")
                return False
                
            # 確保 messages 是列表
            if not isinstance(messages, list):
                messages = [messages]
                
            data = {
                'replyToken': reply_token,
                'messages': messages
            }
            
            logger.info(f"發送回覆訊息: 目標token={reply_token[:10]}..., 訊息數量={len(messages)}")
            
            response = requests.post(
                sendReplyMessageUrl,
                headers=self.headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                logger.info("回覆訊息發送成功")
                return True
            elif response.status_code == 400:
                # replyToken 已被使用或無效
                logger.warning(f"replyToken 無效或已使用: {response.status_code}, {response.text}")
                return False
            else:
                logger.error(f"發送回覆訊息失敗: {response.status_code}, {response.text}")
                return False
    
        except Exception as e:
            logger.error(f"發送回覆訊息時發生錯誤: {str(e)}")
            return False
        
    def _handle_image_message(self, event, user_id, reply_token):
        """處理圖片訊息"""
        message_id = event.get('message', {}).get('id')
        
        # 建立儲存圖片的目錄
        image_dir = Path('static/images')
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # 取得該使用者現有的圖片數量作為序號
        existing_files = list(image_dir.glob(f'{user_id}-*.jpg'))
        sequence_number = len(existing_files) + 1
        
        # 組合檔案路徑
        file_path = image_dir / f'{user_id}-{sequence_number}.jpg'
        
        # 從 LINE 平台下載圖片
        content_url = getContentURL.format(messageId=message_id)
        response = requests.get(content_url, headers=self.headers)
        
        if response.status_code == 200:
            # 儲存圖片
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # 使用 ImageProcessService 處理圖片
            image_analysis = self.image_process_service.imageParse(str(file_path))
            
            # 將圖片分析結果存入資料庫
            # 使用文件名稱(不含副檔名)作為 master_id
            master_id = file_path.stem
            
            # 檢查並處理不同的回應格式
            processed_analysis = None
            reply_text = None
            
            # 處理食物分析數據的輔助函數
            def process_food_analysis(data):
                """處理食物分析數據，統一格式處理邏輯"""
                # 安全地處理 item 數量統計
                items = data.get('item', [])
                if isinstance(items, list):
                    item_count = len(items)
                else:
                    item_count = 1 if items else 0
                    logger.warning(f"item 不是列表格式: {type(items)}, 值: {items}")
                
                reply_text = f"已分析您的{data.get('intent', '餐點')}照片，共識別出{item_count}項食物。"
                return reply_text
            
            if 'intent' in image_analysis and 'item' in image_analysis:
                # 直接是正確的食物分析格式
                processed_analysis = image_analysis
                reply_text = process_food_analysis(image_analysis)
                logger.info(f"收到正確格式的食物分析數據")
            elif 'result' in image_analysis:
                # 需要從 result 欄位解析
                result_text = image_analysis['result']
                reply_text = result_text
                
                # 嘗試從 result 中解析 JSON
                try:
                    import re
                    import json
                    
                    # 查找被 ```json 和 ``` 包圍的 JSON 內容
                    json_match = re.search(r'```json\s*\n(.*?)\n```', result_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                        parsed_data = json.loads(json_str)
                        if 'intent' in parsed_data and 'item' in parsed_data:
                            processed_analysis = parsed_data
                            reply_text = process_food_analysis(parsed_data)
                            logger.info(f"成功從 result 中解析出食物分析數據")
                
                except Exception as e:
                    logger.warning(f"無法從 result 解析 JSON: {str(e)}")
                    # 保持原始 reply_text
            else:
                # 未知格式
                reply_text = "圖片分析完成，但格式異常。"
                logger.warning(f"收到未知格式的圖片分析回應: {image_analysis}")
            
            # 如果成功解析出食物分析數據，存入資料庫
            if processed_analysis:
                try:
                    db_result = self.food_data_service.add_food_analysis(master_id, user_id, processed_analysis)
                    
                    if db_result:
                        logger.info(f"成功將食物分析數據寫入資料庫，主檔ID: {master_id}")
                        # 更新回覆訊息，包含卡路里資訊
                        total_cal = processed_analysis.get('本餐共攝取', '未知')
                        if total_cal != '未知':
                            reply_text += f"\n本餐共攝取：{total_cal}"
                        
                        # 將圖片分析結果傳遞給 nlpService 進行進一步處理
                        try:
                            logger.info(f"將圖片分析結果傳遞給 nlpService 進行進一步處理")
                            enhanced_analysis = self.nlp_service.process_image_analysis(user_id, processed_analysis)
                            
                            if enhanced_analysis and 'result' in enhanced_analysis:
                                # 使用增強後的回覆訊息
                                formatted_message = enhanced_analysis['result']
                                
                                # 如果回覆權杖有效，直接回覆用戶增強後的分析結果
                                if reply_token:
                                    self.send_reply(reply_token, [{
                                        'type': 'text',
                                        'text': formatted_message
                                    }])
                                return  # 結束處理，避免重複回覆
                            else:
                                logger.warning(f"nlpService 返回的結果無效或沒有 result 字段: {enhanced_analysis}")
                        except Exception as e:
                            logger.error(f"nlpService 處理時發生錯誤: {str(e)}")
                            # 出錯時繼續使用原始的回覆邏輯
                    
                except Exception as e:
                    logger.error(f"存入資料庫時發生錯誤: {master_id},{str(e)}")
                    reply_text += f"\n（資料庫錯誤：{str(e)}）"
            
            # 如果有回覆權杖，直接回覆用戶分析結果
            if reply_token and reply_text:
                # 獲取intent與items
                formatted_message = ""
                
                if processed_analysis:
                    intent_type = processed_analysis.get('intent', '餐點')
                    formatted_message = f"🍽️ 已分析您的【{intent_type}】照片\n\n"
                    
                    # 處理items列表
                    items = processed_analysis.get('item', [])
                    if isinstance(items, list) and items:
                        formatted_message += "🔍 識別出的食物：\n"
                        for idx, item in enumerate(items, 1):
                            desc = item.get('desc', '未知食物')
                            cal = item.get('cal', '未知卡路里')
                            formatted_message += f"{idx}. {desc} : {cal}\n"
                        
                        # 添加總卡路里信息
                        total_cal = processed_analysis.get('本餐共攝取', '未知')
                        if total_cal != '未知':
                            formatted_message += f"\n📊 本餐共攝取：{total_cal}"
                    else:
                        formatted_message += "無法識別食物內容"
                else:
                    formatted_message = reply_text
                
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': formatted_message
                }])
        else:
            #TODO 單向循環是否麻煩？
            # 下載圖片失敗，直接在控制器處理錯誤
            error_msg = f'圖片下載失敗，錯誤碼：{response.status_code}'
            logger.error(error_msg)
            
            # 直接處理錯誤訊息並回覆
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': f"很抱歉，處理您的圖片時發生錯誤: {error_msg}"
                }])
            
    def _handle_audio_message(self, event, user_id, reply_token):
        """處理音訊訊息"""
        message_id = event.get('message', {}).get('id')
        
        # 建立儲存音訊的目錄
        audio_dir = Path('static/audio')
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 取得該使用者現有的音訊數量作為序號
        existing_files = list(audio_dir.glob(f'{user_id}-*.mp3'))
        sequence_number = len(existing_files) + 1
        
        # 組合檔案路徑
        file_path = audio_dir / f'{user_id}-{sequence_number}.mp3'
        
        # 從 LINE 平台下載音訊
        content_url = getContentURL.format(messageId=message_id)
        response = requests.get(content_url, headers=self.headers)
        
        if response.status_code == 200:
            # 儲存音訊
            with open(file_path, 'wb') as f:
                f.write(response.content)
                
            # 如果有回覆權杖，直接回覆音訊已儲存的訊息
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': f'已收到您的音訊並儲存為：{file_path.name}'
                }])
        else:
            # 下載音訊失敗
            error_msg = f'音訊下載失敗，錯誤碼：{response.status_code}'
            logger.error(error_msg)
            
            # 如果有回覆權杖，直接回覆錯誤訊息
            if reply_token:
                self.send_reply(reply_token, [{
                    'type': 'text',
                    'text': error_msg
                }])

# 初始化訊息處理器
line_message_handler = LineMessageHandler()

@line_webhook_bp.route('/linehook', methods=['POST'])
def line_webhook_handler():
    """處理來自LINE平台的Webhook事件 - 包含去重機制的優化版本"""
    # 快速驗證
    if not request.is_json:
        return jsonify({"status": "error", "message": "請求必須是JSON格式"}), 400

    payload = request.get_json()
    
    # 簡化驗證
    events = payload.get('events', [])
    if not isinstance(events, list):
        return jsonify({"status": "error", "message": "events格式不正確"}), 400
        
    # 快速處理事件 - 加入去重檢查
    results = []
    for event in events:
        # 檢查是否為重複事件
        if event_deduplicator.is_duplicate(event):
            results.append({
                "status": "skipped", 
                "message": "重複事件已忽略",
                "event_type": event.get('type', 'unknown')
            })
            continue
            
        event_type = event.get('type')
        
        if event_type == 'follow':
            result = line_join_service.handle_follow_event(event)
            results.append({"event_type": "follow", "result": result})
        elif event_type == 'unfollow':
            result = line_join_service.handle_unfollow_event(event)
            results.append({"event_type": "unfollow", "result": result})
        elif event_type == 'join':
            result = line_join_service.handle_join_event(event)
            results.append({"event_type": "join", "result": result})
        elif event_type == 'message':
            # 確保 replyToken 存在且未被使用過
            reply_token = event.get('replyToken')
            if reply_token:
                # 非阻塞處理訊息
                line_message_handler.handle_message_event(event)
                results.append({"event_type": "message", "result": "處理中"})
            else:
                logger.warning(f"訊息事件缺少 replyToken: {event}")
                results.append({"event_type": "message", "result": "無效的 replyToken"})
        else:
            results.append({"status": "warning", "message": f"未知事件類型: {event_type}"})
    
    return jsonify({"status": "success", "results": results}), 200
