import logging
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import json
import google.generativeai as genai
from config import get_config
from config.Prompt import chatPrompt, chatSearchPrompt, imageProcessReplyprompt
import traceback
import re
import datetime
from typing import Dict, Any, Optional, List
from Service.managerCalService import ManagerCalService
from Service.FoodDataService import FoodDataService
from Service.PhysInfoDataService import PhysInfoDataService
from Service.ConnectionFactory import ConnectionFactory


# 設置日誌記錄
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        # 從配置檔讀取API金鑰和模型名稱
        config = get_config()
        self.api_key = config['gemini']['apikey']
        self.model_name = config['gemini']['model']
        self.chat_prompt = chatPrompt
        self.chat_search_prompt = chatSearchPrompt
        self.image_process_reply_prompt = imageProcessReplyprompt
        
        # 混合檢測架構配置
        self.enable_unified_detection = True  # 是否啟用統一檢測
        self.fallback_to_individual = True    # 是否允許回退到獨立檢測
        self.unified_confidence_threshold = 0.7  # 統一檢測的信心度閾值
        self.phys_info_function = {
            "name": "extract_physical_info",
            "description": "從用戶訊息中提取身體資訊",
            "parameters": {
                "type": "object",
                "properties": {
                    "gender": {
                        "type": "string",
                        "description": "用戶的性別(男/女)"
                    },
                    "age": {
                        "type": "integer",
                        "description": "用戶的年齡(歲)"
                    },
                    "height": {
                        "type": "number",
                        "description": "用戶的身高(cm)"
                    },
                    "weight": {
                        "type": "number",
                        "description": "用戶的體重(kg)"
                    },
                    "allergic_foods": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "用戶過敏的食物清單"
                    }
                },
                "required": ["gender", "age", "height", "weight"]
            }
        }
        
        # 初始化搜索意圖的 function 定義
        self.search_intent_function = {
            "name": "extract_search_intent",
            "description": "從用戶訊息中提取搜索意圖和時間範圍",
            "parameters": {
                "type": "object",
                "properties": {
                    "has_search_intent": {
                        "type": "boolean",
                        "description": "用戶是否有搜索意圖"
                    },
                    "time_period": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "搜索起始日期 (YYYY-MM-DD格式)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "搜索結束日期 (YYYY-MM-DD格式)"
                            },
                            "period_type": {
                                "type": "string",
                                "enum": ["today", "yesterday", "this_week", "last_week", "this_month", "last_month", "specific_date", "date_range"],
                                "description": "時間段類型"
                            }
                        },
                        "required": ["period_type"]
                    }
                },
                "required": ["has_search_intent"]
            }
        }
        
        # 延遲初始化相關服務 - 避免重複創建
        self._manager_cal_service = None
        self._food_data_service = None
        self._phys_info_service = None
        
        # 儲存每個用戶的對話歷史
        self.conversation_history = {}
        
        # 初始化卡路里管理意圖檢測的 function 定義
        self.calorie_intent_function = {
            "name": "detect_calorie_management_intent",
            "description": "檢測用戶訊息是否包含卡路里管理或減重計劃的意圖",
            "parameters": {
                "type": "object",
                "properties": {
                    "has_calorie_intent": {
                        "type": "boolean",
                        "description": "用戶是否有卡路里管理、減重計劃或健康飲食控制的意圖"
                    },
                    "intent_type": {
                        "type": "string",
                        "enum": ["weight_loss", "calorie_planning", "diet_control", "health_management", "none"],
                        "description": "卡路里管理意圖的具體類型"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "檢測結果的信心度 (0.0 到 1.0 之間)"
                    },
                    "reason": {
                        "type": "string",
                        "description": "判斷的依據或原因"
                    }
                },
                "required": ["has_calorie_intent", "intent_type", "confidence"]
            }
        }
        
        # 統一意圖檢測的 function 定義
        self.unified_intent_function = {
            "name": "detect_all_intents",
            "description": "統一檢測用戶訊息中所有可能的意圖類型",
            "parameters": {
                "type": "object",
                "properties": {
                    "primary_intent": {
                        "type": "string",
                        "enum": ["calorie_management", "search_history", "physical_info", "general_chat", "image_query"],
                        "description": "主要意圖類型"
                    },
                    "calorie_intent": {
                        "type": "object",
                        "properties": {
                            "has_intent": {"type": "boolean"},
                            "intent_type": {
                                "type": "string", 
                                "enum": ["weight_loss", "calorie_planning", "diet_control", "health_management", "none"]
                            },
                            "confidence": {"type": "number"}
                        },
                        "required": ["has_intent", "confidence"]
                    },
                    "search_intent": {
                        "type": "object",
                        "properties": {
                            "has_intent": {"type": "boolean"},
                            "time_period": {
                                "type": "object",
                                "properties": {
                                    "period_type": {
                                        "type": "string",
                                        "enum": ["today", "yesterday", "this_week", "last_week", "this_month", "last_month", "specific_date", "date_range"]
                                    }
                                }
                            }
                        },
                        "required": ["has_intent"]
                    },
                    "physical_info": {
                        "type": "object",
                        "properties": {
                            "has_intent": {"type": "boolean"},
                            "extracted_info": {
                                "type": "object",
                                "properties": {
                                    "gender": {"type": "string"},
                                    "age": {"type": "integer"},
                                    "height": {"type": "number"},
                                    "weight": {"type": "number"},
                                    "allergic_foods": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["has_intent"]
                    },
                    "confidence": {
                        "type": "number",
                        "description": "整體檢測的信心度"
                    }
                },
                "required": ["primary_intent", "confidence"]
            }
        }
        
        # 初始化 Gemini
        genai.configure(api_key=self.api_key)
        
    @property
    def manager_cal_service(self):
        if self._manager_cal_service is None:
            self._manager_cal_service = ManagerCalService()
        return self._manager_cal_service
    
    @property 
    def food_data_service(self):
        if self._food_data_service is None:
            self._food_data_service = FoodDataService()
        return self._food_data_service
    
    @property
    def phys_info_service(self):
        if self._phys_info_service is None:
            # 引入並初始化 PhysInfoDataService
            from Service.PhysInfoDataService import PhysInfoDataService
            self._phys_info_service = PhysInfoDataService()
        return self._phys_info_service
    
    def unified_intent_detection(self, message_text: str) -> Dict[str, Any]:
        """
        統一的意圖檢測，一次 API 調用識別所有可能的意圖
        包含快取機制以提高響應速度
        """
        
        # 使用 Gemini 進行統一意圖解析
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": 0.2}
        )
        
        # 設置 function calling
        tools = [{"function_declarations": [self.unified_intent_function]}]
        
        prompt = f"""
        分析以下用戶訊息，識別其中包含的所有意圖類型：
        
        1. 卡路里管理意圖：減重、瘦身、卡路里控制、飲食規劃等
        2. 搜索意圖：查詢歷史食物記錄、卡路里統計等
        3. 生理資訊：提供身高、體重、年齡、性別等個人資料
        4. 一般對話：日常聊天、詢問等
        5. 圖片查詢：關於食物圖片的詢問
        
        用戶訊息：{message_text}
        """
        
        response = model.generate_content(prompt, tools=tools)
        
        # 提取 function calling 結果
        function_response = None
        for part in response.parts:
            if hasattr(part, 'function_call'):
                function_response = part.function_call
                break
        
        if function_response and function_response.name == "detect_all_intents":
            result = dict(function_response.args)
            result['success'] = True
            result['method'] = 'unified'
            
            logger.info(f"統一意圖檢測成功: {result.get('primary_intent')}")
            return result
        
        logger.warning("統一意圖檢測未能獲取有效結果")
        return {
            'success': False,
            'error': 'No valid function response',
            'method': 'unified'
        }

    def quick_intent_screening(self, message_text: str) -> List[str]:
        """
        快速意圖預篩選，使用關鍵詞進行初步判斷
        
        Args:
            message_text (str): 用戶訊息文字
            
        Returns:
            list: 可能的意圖類型列表
        """
        possible_intents = []
        
        # 卡路里管理關鍵詞
        calorie_keywords = ["減重", "減肥", "瘦身", "卡路里", "熱量", "飲食計劃", "控制", "管理", "健康", "體重"]
        calorie_context_keywords = ["規劃", "計劃", "建議", "想要", "需要", "幫我", "想", "要"]
        
        has_calorie = any(keyword in message_text for keyword in calorie_keywords)
        has_calorie_context = any(keyword in message_text for keyword in calorie_context_keywords)
        
        # 只有當有卡路里關鍵詞且有相關上下文時，才判定為卡路里管理意圖
        if has_calorie and has_calorie_context:
            possible_intents.append("calorie_management")
        
        # 搜索關鍵詞
        search_keywords = ["查詢", "搜尋", "歷史", "記錄", "統計"]
        search_time_keywords = ["昨天", "前天", "上週", "上個月", "本週", "本月"]
        general_chat_negative = ["天氣", "心情", "你好", "謝謝", "再見", "如何", "什麼", "為什麼"]
        
        has_search = any(keyword in message_text for keyword in search_keywords)
        has_time = any(keyword in message_text for keyword in search_time_keywords)
        has_general = any(keyword in message_text for keyword in general_chat_negative)
        
        # 明確的搜索意圖：有搜索詞或時間詞，且不是一般對話
        if (has_search or has_time) and not has_general:
            possible_intents.append("search_history")
        
        # 生理資訊關鍵詞 - 保持與 _detect_physical_info_by_keywords 一致
        physical_keywords = ["男", "女", "歲", "身高", "體重", "公分", "公斤", "cm", "kg", "CM", "KG", "過敏"]
        number_pattern = r'\d+'
        
        has_physical = any(keyword in message_text for keyword in physical_keywords)
        has_numbers = bool(re.search(number_pattern, message_text))
        physical_count = sum(1 for keyword in physical_keywords if keyword in message_text)
        
        # 需要至少3個生理關鍵詞和數字才判定為生理資訊
        if has_physical and has_numbers and physical_count >= 3:
            possible_intents.append("physical_info")
        
        # 圖片相關關鍵詞
        image_keywords = ["照片", "圖片", "拍攝", "識別", "分析", "圖像"]
        if any(keyword in message_text for keyword in image_keywords):
            possible_intents.append("image_query")
        
        # 如果沒有匹配任何關鍵詞，視為一般對話
        if not possible_intents:
            possible_intents.append("general_chat")
        
        logger.info(f"快速篩選結果: {possible_intents}")
        return possible_intents

    def smart_intent_detection(self, message_text: str) -> Dict[str, Any]:
        """
        智能意圖檢測：結合快速篩選和精確檢測
        """
        logger.info(f"開始智能意圖檢測: {message_text}")
        
        # 第一層：快速關鍵詞預篩選
        possible_intents = self.quick_intent_screening(message_text)
        
        # 第二層：根據篩選結果選擇檢測策略
        if len(possible_intents) == 1 and possible_intents[0] == "general_chat":
            # 純一般對話，跳過複雜檢測
            return {
                'primary_intent': 'general_chat',
                'method': 'keyword_screening',
                'success': True,
                'possible_intents': possible_intents
            }
        
        elif len(possible_intents) == 1:
            # 只有一個明確意圖，使用專門的檢測函數
            intent_type = possible_intents[0]
            if intent_type == "calorie_management":
                result = self.check_calorie_management_intent(message_text)
                return {
                    'primary_intent': 'calorie_management',
                    'calorie_intent': result,
                    'method': 'individual',
                    'success': True
                }
            elif intent_type == "search_history":
                result = self.check_search_intent(message_text)
                return {
                    'primary_intent': 'search_history',
                    'search_intent': result,
                    'method': 'individual',
                    'success': True
                }
            else:
                # 對於其他單一意圖，也使用統一檢測
                if self.enable_unified_detection:
                    return self.unified_intent_detection(message_text)
                else:
                    return self._fallback_to_individual_detection(message_text)
        
        else:
            # 多個可能意圖或複雜情況，使用統一檢測
            if self.enable_unified_detection:
                unified_result = self.unified_intent_detection(message_text)
                if unified_result.get('success', False):
                    return unified_result
            
            # 統一檢測失敗，回退到獨立檢測
            if self.fallback_to_individual:
                return self._fallback_to_individual_detection(message_text)
            else:
                return {
                    'primary_intent': 'general_chat',
                    'method': 'fallback',
                    'success': False,
                    'error': 'All detection methods failed'
                }

    def _fallback_to_individual_detection(self, message_text: str) -> Dict[str, Any]:
        """
        回退到獨立檢測方法
        
        Args:
            message_text (str): 用戶訊息文字
            
        Returns:
            dict: 檢測結果
        """
        try:
            logger.info("使用獨立檢測方法作為回退")
            
            # 依序檢測各種意圖
            # 1. 檢測卡路里管理意圖
            calorie_result = self.check_calorie_management_intent(message_text)
            if calorie_result.get("has_calorie_intent", False):
                return {
                    'primary_intent': 'calorie_management',
                    'calorie_intent': calorie_result,
                    'method': 'individual_fallback',
                    'success': True
                }
            
            # 2. 檢測搜索意圖
            search_result = self.check_search_intent(message_text)
            if search_result.get("has_search_intent", False):
                return {
                    'primary_intent': 'search_history',
                    'search_intent': search_result,
                    'method': 'individual_fallback',
                    'success': True
                }
            
            # 3. 檢測生理資訊
            # 使用關鍵詞檢測方法
            if self._detect_physical_info_by_keywords(message_text):
                return {
                    'primary_intent': 'physical_info',
                    'physical_info': {'has_info': True, 'confidence': 0.8},
                    'method': 'individual_fallback',
                    'success': True
                }
            
            # 4. 默認為一般對話
            return {
                'primary_intent': 'general_chat',
                'method': 'individual_fallback',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"獨立檢測回退也失敗: {str(e)}")
            return {
                'primary_intent': 'general_chat',
                'method': 'final_fallback',
                'success': False,
                'error': str(e)
            }
    
    def generate_diet_planning_for_new_user(self, user_id: str) -> Dict[str, Any]:
        """
        為新用戶生成卡路里計算結果和未來三天飲食規劃
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            dict: 包含卡路里計算結果和未來三天飲食規劃的字典
        """
        try:
            logger.info(f"開始為新用戶 {user_id} 生成飲食規劃")
            
            # 1. 獲取卡路里計算結果
            cal_result = self.manager_cal_service.process_user_id(user_id)
            
            # 2. 獲取用戶的過敏食物資訊
            # 使用新的方法直接通過user_id獲取身體資訊
            phys_info_response = self.phys_info_service.get_phys_info_by_user_id(user_id)
            allergic_foods = []
            if phys_info_response["status"] == "success":
                allergic_foods = phys_info_response["result"].get('allergic_foods', [])
            
            # 3. 對於新用戶，沒有過去的飲食記錄，使用空列表
            past_records = []
            
            # 4. 使用Gemini生成未來三天飲食規劃
            planning_result = self._generate_diet_plan_with_gemini(
                cal_result, past_records, allergic_foods, user_id
            )
            
            # 5. 合併結果
            final_result = f"{cal_result.get('result', '')}\n\n{planning_result}"
            
            return {
                "result": final_result,
                "status": "success",
                "calorie_info": cal_result,
                "diet_planning": planning_result
            }
            
        except Exception as e:
            error_msg = f"生成新用戶飲食規劃時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "result": error_msg,
                "status": "error"
            }
    
    def _generate_diet_plan_with_gemini(self, cal_result: Dict[str, Any], past_records: List[Dict[str, Any]], 
                                      allergic_foods: List[str], user_id: str) -> str:
        """
        使用Gemini LLM生成未來三天的飲食規劃
        包含快取機制以提高響應速度
        """
        try:
            
            # 準備提示詞
            prompt = f"""
            基於以下用戶資訊，請為用戶規劃未來三天的健康飲食計劃，總文長400字：

            ## 用戶基本資訊
            - 用戶ID: {user_id}
            - BMI: {cal_result.get('bmi', '未知')}
            - 基礎代謝率(BMR): {cal_result.get('bmr', '未知')} 大卡
            - 維持體重每日建議攝取量: {cal_result.get('daily_calories', '未知')} 大卡
            - 減重時建議攝取量: {cal_result.get('weight_loss_calories', '未知')} 大卡
            - 過敏食物: {', '.join(allergic_foods) if allergic_foods else '無'}

            ## 過去7天飲食記錄
            """
            
            if past_records:
                for record in past_records:
                    prompt += f"\n日期: {record.get('date', '未知')}, 總卡路里: {record.get('total_calories', 0)} 大卡\n"
                    foods = record.get('foods', [])
                    if foods:
                        for food in foods:
                            prompt += f"  - {food.get('name', '未知食物')}: {food.get('calories', '未知')} 大卡\n"
                    else:
                        prompt += "  - 無具體食物記錄\n"
            else:
                prompt += "\n暫無過去飲食記錄（新用戶）\n"
            
            prompt += f"""
            
            ## 請提供以下內容：
            1. **未來三天飲食規劃**：
               - 每天的早餐、午餐、晚餐建議(50字)
               - 每餐的大概卡路里分配(50字)
               - 考慮用戶的卡路里需求和過敏食物(50字)
               - 如果有過去飲食記錄，請分析飲食習慣並給出改善建議(50字)
            
            2. **營養建議**：
               - 基於BMI和目標，提供具體的營養建議(100字以內)
               - 如果用戶需要減重，請提供相應的飲食策略(100字以內)
               
            請以友善、實用的語氣回覆，讓用戶容易理解和執行。
            """
            
            # 配置並調用 Gemini
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.7}
            )
            
            # 生成回應
            response = model.generate_content(prompt)
            result = response.text
            
            logger.info(f"已生成飲食規劃結果: {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"生成飲食規劃失敗: {str(e)}")
            return f"抱歉，生成飲食規劃時發生錯誤: {str(e)}"
    @performance_monitor.timing_decorator("nlpProcess")
    def nlpProcess(self, user_id, message_text):
        """
        處理聊天訊息字串，進行語義分析並回傳處理結果
        使用混合檢測架構，結合統一檢測和獨立檢測的優勢
        """
        logger.info(f"開始處理用戶 {user_id} 的訊息: {message_text}")
        
        # 使用智能意圖檢測
        intent_result = self.smart_intent_detection(message_text)
        
        if not intent_result.get('success', False):
            logger.warning(f"意圖檢測失敗，使用一般對話處理")
            return self._process_general_chat(user_id, message_text)
        
        primary_intent = intent_result.get('primary_intent')
        
        # 根據主要意圖進行相應處理
        if primary_intent == 'calorie_management':
            return self._process_calorie_intent(user_id, message_text, intent_result)
        elif primary_intent == 'search_history':
            return self._process_search_intent(user_id, message_text, intent_result)
        elif primary_intent == 'physical_info':
            return self._process_physical_info_intent(user_id, message_text, intent_result)
        elif primary_intent == 'image_query':
            return {"result": "請上傳您要分析的食物照片，我將為您提供詳細的營養分析。"}
        else:  # general_chat
            return self._process_general_chat(user_id, message_text)

    def _process_calorie_intent(self, user_id: str, message_text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理卡路里管理意圖
        """
        # 從統一檢測結果或獨立檢測結果中提取信心度
        calorie_data = intent_result.get('calorie_intent', {})
        confidence = calorie_data.get('confidence', 0.0)
        intent_type = calorie_data.get('intent_type', 'general')
        
        # 如果信心度太低，視為無意圖
        if confidence < 0.6:
            return self._process_general_chat(user_id, message_text)
        
        # 檢查用戶是否已有生理資料
        # 使用新的方法直接通過user_id獲取身體資訊
        phys_info_response = self.phys_info_service.get_phys_info_by_user_id(user_id)
        
        if phys_info_response["status"] == "success":
            phys_info = phys_info_response["result"]
            # 獲取卡路里計算結果
            cal_result = self.manager_cal_service.process_user_id(user_id)
            # 使用過敏食物資訊
            allergic_foods = phys_info.get('allergic_foods', [])
            past_records = []
            
            # 生成飲食規劃
            planning_result = self._generate_diet_plan_with_gemini(
                cal_result, past_records, allergic_foods, user_id
            )
            
            final_result = f"{cal_result.get('result', '')}\n\n{planning_result}"
            
            return {
                "result": final_result,
                "status": "success",
                "calorie_info": cal_result,
                "diet_planning": planning_result
            }
        else:
            return {"result": "請提供你的性別,年齡(歲),身高(cm),體重(kg)一定要有單位,以及對什麼食物過敏"}

    def _process_search_intent(self, user_id: str, message_text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理搜索意圖
        """
        search_data = intent_result.get('search_intent', {})
        time_period = search_data.get('time_period', {})
        return self.searchProcess(user_id, message_text, time_period)

    def _process_physical_info_intent(self, user_id: str, message_text: str, intent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理生理資訊意圖
        """
        return self.process_physical_info(user_id, message_text)

    def _process_general_chat(self, user_id: str, message_text: str) -> Dict[str, Any]:
        """
        處理一般對話
        """
        # 檢查是否已有此用戶的對話歷史，若無則初始化
        if user_id not in self.conversation_history:
            # 初始化對話歷史時加入系統提示
            model = genai.GenerativeModel(self.model_name)
            chat = model.start_chat(history=[])
            
            # 將系統提示作為第一條消息添加到對話中
            if self.chat_prompt:
                chat.send_message(self.chat_prompt)
            
            self.conversation_history[user_id] = chat
        
        # 取得用戶的對話歷史
        chat = self.conversation_history[user_id]
        
        # 發送訊息到 Gemini 並取得回應
        response = chat.send_message(message_text)
        response_text = response.text
        
        # 檢查回應是否為 JSON 格式
        try:
            # 嘗試解析回應為 JSON
            json_response = json.loads(response_text)
            # 如果不含 result 欄位，則加上 result 欄位
            if "result" not in json_response:
                json_response = {"result": response_text}
        except json.JSONDecodeError:
            # 若回應不是 JSON 格式，則封裝為 JSON
            json_response = {"result": response_text}
        
        logger.info(f"一般對話處理完成")
        return json_response
    

    def process_physical_info(self, user_id: str, message_text: str) -> Dict[str, Any]:
        """
        處理用戶輸入的生理資訊，將其存儲到資料庫並進行卡路里計算
        
        Args:
            user_id (str): 用戶ID
            message_text (str): 用戶傳入的訊息文字
            
        Returns:
            dict: 包含處理結果的JSON物件
        """
        try:
            logger.info(f"開始處理用戶 {user_id} 的生理資訊: {message_text}")
            
            # 使用 Gemini 進行訊息解析，利用 function calling
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.2}
            )
            
            # 設置 function calling
            tools = [
                {
                    "function_declarations": [self.phys_info_function],
                }
            ]
            
            response = model.generate_content(
                f"從以下用戶訊息中提取身體資訊（性別、年齡、身高、體重、過敏食物）：\n\n{message_text}",
                tools=tools
            )
            
            # 提取 function calling 結果
            function_response = None
            for part in response.parts:
                if hasattr(part, 'function_call'):
                    function_response = part.function_call
                    break
            
            if function_response and function_response.name == "extract_physical_info":
                # 使用 function_response.args 直接作為結果，轉換為普通字典
                result = dict(function_response.args)

                # 確保過敏食物是列表，並轉成普通 list
                allergic_foods = result.get("allergic_foods", [])
                if hasattr(allergic_foods, '__iter__') and not isinstance(allergic_foods, str):
                    allergic_foods = list(allergic_foods)
                else:
                    allergic_foods = []
                
                # 記錄過敏食物信息
                logger.info(f"用戶 {user_id} 報告的過敏食物: {allergic_foods}")

                # 使用 PhysInfoDataService 存儲資訊，包含過敏食物
                create_result = self.phys_info_service.create_phys_info(
                    master_id=user_id,
                    gender=result["gender"],
                    age=result["age"],
                    height=float(result["height"]),
                    weight=float(result["weight"]),
                    allergic_foods=allergic_foods
                )
                
                if create_result.get("status") == "success":
                    # 成功儲存後，調用 ManagerCalService 進行計算，並生成未來三天飲食規劃
                    logger.info(f"用戶 {user_id} 生理資訊儲存成功，開始生成飲食規劃")
                    return self.generate_diet_planning_for_new_user(user_id)
                else:
                    return {
                        "result": "資料儲存失敗，請稍後再試",
                        "status": "error"
                    }
            else:
                # 如果沒有成功提取資訊
                return {
                    "result": "無法從您的訊息中提取完整的生理資訊，請確保提供性別、年齡、身高和體重",
                    "status": "incomplete"
                }
                
        except Exception as e:
            error_msg = f"處理生理資訊時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "result": error_msg,
                "status": "error"
            }
            
    
    def parse_physical_info(self, message_text: str) -> Dict[str, Any]:
        """
        從文本中解析出身體資訊
        
        Args:
            message_text (str): 包含身體資訊的文本，如 "男性,28歲,170公分,75kg,糙米飯過敏"
            
        Returns:
            Dict: 解析後的身體資訊，包含 gender, age, height, weight, allergic_foods
        """
        try:
            logger.info(f"開始解析身體資訊: {message_text}")
            
            # 使用 Gemini 進行訊息解析，利用 function calling
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.2}
            )
            
            # 設置 function calling
            tools = [
                {
                    "function_declarations": [self.phys_info_function],
                }
            ]
            
            response = model.generate_content(
                f"從以下用戶訊息中提取身體資訊（性別、年齡、身高、體重、過敏食物）：\n\n{message_text}",
                tools=tools
            )
            
            # 提取 function calling 結果
            function_response = None
            for part in response.parts:
                if hasattr(part, 'function_call'):
                    function_response = part.function_call
                    break
            
            if function_response and function_response.name == "extract_physical_info":
                # 使用 function_response.args 直接作為結果，轉換為普通字典
                result = dict(function_response.args)

                # 確保過敏食物是列表，並轉成普通 list
                allergic_foods = result.get("allergic_foods", [])
                if hasattr(allergic_foods, '__iter__') and not isinstance(allergic_foods, str):
                    allergic_foods = list(allergic_foods)
                else:
                    allergic_foods = []
                
                # 更新結果字典
                result["allergic_foods"] = allergic_foods
                
                return result
            else:
                # 如果 Gemini 無法解析，則嘗試使用正則表達式
                result = {}
                
                # 匹配性別
                gender_match = re.search(r'(男|女)(?:性)?', message_text)
                if gender_match:
                    gender = gender_match.group(1)
                    result["gender"] = "男性" if gender == "男" else "女性"
                
                # 匹配年齡
                age_match = re.search(r'(\d+)(?:歲|岁)', message_text)
                if age_match:
                    result["age"] = int(age_match.group(1))
                
                # 匹配身高
                height_match = re.search(r'(\d+(?:\.\d+)?)(?:公分|cm|CM)', message_text)
                if height_match:
                    result["height"] = float(height_match.group(1))
                
                # 匹配體重
                weight_match = re.search(r'(\d+(?:\.\d+)?)(?:kg|KG|公斤)', message_text)
                if weight_match:
                    result["weight"] = float(weight_match.group(1))
                
                # 匹配過敏食物
                allergic_match = re.search(r'(.+)(?:過敏|过敏)', message_text)
                if allergic_match:
                    allergic_foods = allergic_match.group(1).strip()
                    result["allergic_foods"] = [allergic_foods]
                else:
                    result["allergic_foods"] = []
                
                # 檢查是否有所需的所有資訊
                if all(key in result for key in ["gender", "age", "height", "weight"]):
                    return result
                else:
                    return None
                
        except Exception as e:
            error_msg = f"解析身體資訊時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return None

    def searchProcess(self, user_id: str, message_text: str, time_period: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        處理搜索食物歷史記錄的請求，使用 chatSearchPrompt 系統提示進行語意解析，
        從資料庫獲取相關數據，並使用 FoodDataService 的 get_total_calories_by_date 方法進行處理
        
        Args:
            user_id (str): 用戶ID
            message_text (str): 用戶傳入的訊息文字
            time_period (dict): 時間範圍參數，由 check_search_intent 方法提供
            
        Returns:
            dict: 包含處理結果的JSON物件，格式為 {"result": 處理結果訊息}
        """
        try:
            logger.info(f"開始處理用戶 {user_id} 的搜索請求: {message_text}")
            
            # 從 time_period 中提取日期信息
            date_info = None
            if time_period:
                period_type = time_period.get("period_type")
                today = datetime.date.today()
                
                if period_type == "today":
                    date_info = today
                elif period_type == "yesterday":
                    date_info = today - datetime.timedelta(days=1)
                elif period_type == "this_week":
                    # 計算本週的起始日期（週一）
                    start_of_week = today - datetime.timedelta(days=today.weekday())
                    date_info = start_of_week  # 或者可以返回一個日期範圍
                elif period_type == "last_week":
                    # 計算上週的起始日期
                    start_of_last_week = today - datetime.timedelta(days=today.weekday() + 7)
                    date_info = start_of_last_week  # 或者可以返回一個日期範圍
                elif period_type == "specific_date":
                    # 使用指定的日期
                    start_date = time_period.get("start_date")
                    if start_date:
                        try:
                            date_info = datetime.date.fromisoformat(start_date)
                        except ValueError:
                            logger.warning(f"無效的日期格式: {start_date}")
            
            # 如果沒有從 function calling 獲取到日期，嘗試從消息中提取
            if not date_info:
                date_info = self._extract_date_from_message(message_text)
            
            # 如果還是沒有日期信息，默認為今天
            if not date_info:
                date_info = datetime.date.today()
                logger.info(f"未找到明確的日期信息，使用今天的日期: {date_info}")
            
            # 查詢該日期的總卡路里
            total_calories = self.food_data_service.get_total_calories_by_date(user_id, date_info)
            
            # 判斷用戶是否有飲食記錄，如果沒有，直接生成飲食規劃
            if not total_calories:
                logger.info(f"用戶 {user_id} 在 {date_info} 沒有飲食記錄，直接生成飲食規劃")
                planning_result = self.generate_diet_planning_for_new_user(user_id)
                planning_result["result"] = f"您在 {date_info.isoformat() if isinstance(date_info, datetime.date) else date_info} 沒有飲食記錄。\n\n為您生成的飲食規劃：\n{planning_result.get('result', '')}"
                return planning_result
            
            # 組織查詢數據，用於 LLM 分析
            search_data = {
                "user_id": user_id,
                "date": date_info.isoformat() if isinstance(date_info, datetime.date) else date_info,
                "total_calories": total_calories,
                "query": message_text
            }
            
            # 使用 chatSearchPrompt 進行數據分析和建議生成
            search_prompt = f"{self.chat_search_prompt}\n\n用戶ID: {user_id}\n日期: {search_data['date']}\n總卡路里: {total_calories}\n用戶訊息: {message_text}"
            
            # 使用新的 model 實例來生成搜索結果
            model = genai.GenerativeModel(self.model_name)
            search_response = model.generate_content(search_prompt)
            search_result = search_response.text.strip()
            
            logger.info(f"搜索分析結果: {search_result}")
            
            # 如果用戶有對話歷史，將搜索結果添加到對話歷史中
            if user_id in self.conversation_history:
                chat = self.conversation_history[user_id]
                chat.send_message(f"用戶搜索請求: {message_text}")
                chat.send_message(f"系統搜索結果: {search_result}")
            
            # 返回結果
            return {"result": search_result}
            
        except Exception as e:
            error_msg = f"搜索處理過程中發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {"result": f"處理您的搜索請求時發生錯誤: {str(e)}"}

    def process_image_analysis(self, user_id: str, image_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理圖片分析結果，使用 imageProcessReplyprompt 系統提示，
        提供關於食物分析的進一步建議和評論
        
        Args:
            user_id (str): 用戶ID
            image_analysis (dict): 圖片分析結果，包含 intent 和 item 等信息
            
        Returns:
            dict: 包含處理結果的JSON物件，包括原始分析和進一步建議
        """
        try:
            logger.info(f"開始處理用戶 {user_id} 的圖片分析結果: {image_analysis}")
            
            # 檢查輸入的有效性
            if not isinstance(image_analysis, dict):
                return {
                    "result": "無效的圖片分析格式",
                    "status": "error"
                }
            
            # 初始化一個新的對話，使用圖片處理回覆系統提示
            model = genai.GenerativeModel(self.model_name)
            chat = model.start_chat(history=[])
            
            # 加入系統提示
            if self.image_process_reply_prompt:
                chat.send_message(self.image_process_reply_prompt)
            
            # 準備提供給LLM的食物分析摘要
            intent = image_analysis.get('intent', '未知餐點')
            items = image_analysis.get('item', [])
            total_cal = image_analysis.get('本餐共攝取', '未知')
            
            # 生成食物項目摘要
            food_items_summary = ""
            if isinstance(items, list) and items:
                for idx, item in enumerate(items, 1):
                    desc = item.get('desc', '未知食物')
                    cal = item.get('cal', '未知卡路里')
                    food_items_summary += f"{idx}. {desc} : {cal}\n"
            else:
                food_items_summary = "無法識別食物內容"
            
            # 構建提示給LLM
            user_prompt = f"""
            用戶拍攝了一張【{intent}】的照片，分析結果如下：
            
            識別出的食物：
            {food_items_summary}
            
            本餐共攝取：{total_cal}
            
            請根據上述食物分析，提供簡短的餐點評價和營養建議。如果這是一個正餐(早餐、午餐或晚餐)，
            請指出最多兩項缺少營養素或食物種類，並給予鼓勵。總文長300字。
            """
            
            # 獲取 LLM 回應
            response = chat.send_message(user_prompt)
            response_text = response.text
            
            # 合併原始分析結果和進一步建議
            enhanced_analysis = image_analysis.copy()  # 複製原始分析
            enhanced_analysis['nlp_suggestion'] = response_text  # 添加NLP建議
            
            # 為了向後兼容，也添加 result 字段
            result_message = f"🍽️ 已分析您的【{intent}】照片\n\n"
            
            if isinstance(items, list) and items:
                result_message += "🔍 識別出的食物：\n"
                for idx, item in enumerate(items, 1):
                    desc = item.get('desc', '未知食物')
                    cal = item.get('cal', '未知卡路里')
                    result_message += f"{idx}. {desc} : {cal}\n"
                
                if total_cal != '未知':
                    result_message += f"\n📊 本餐共攝取：{total_cal}\n"
            else:
                result_message += "無法識別食物內容\n"
            
            # 添加NLP建議
            result_message += f"\n💡 營養建議：\n{response_text}"
            
            enhanced_analysis['result'] = result_message
            
            logger.info(f"圖片分析結果處理完成: {enhanced_analysis}")
            return enhanced_analysis
            
        except Exception as e:
            error_msg = f"處理圖片分析結果時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "result": f"處理您的圖片分析結果時發生錯誤: {str(e)}",
                "status": "error"
            }
    
    def check_calorie_management_intent(self, message_text: str) -> Dict[str, Any]:
        """
        使用 function calling 檢查用戶訊息是否有卡路里管理意圖
        包含快取機制以提高響應速度
        
        Args:
            message_text (str): 用戶傳入的訊息文字
            
        Returns:
            dict: 包含卡路里管理意圖檢測結果的字典
        """
        try:
            logger.info(f"開始檢查訊息是否有卡路里管理意圖: {message_text}")
            
            
            # 使用 Gemini 進行意圖解析
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.2}
            )
            
            # 設置 function calling
            tools = [
                {
                    "function_declarations": [self.calorie_intent_function],
                }
            ]
            
            prompt = f"""
            分析以下用戶訊息，判斷是否包含卡路里管理、減重計劃、飲食控制或健康管理的意圖。
            
            考慮以下情境：
            - 想要減重、瘦身、減肥
            - 計劃或控制卡路里攝取
            - 設定飲食目標
            - 健康管理相關需求
            - 體重管理計劃
            
            用戶訊息：{message_text}
            """
            
            response = model.generate_content(prompt, tools=tools)
            
            # 提取 function calling 結果
            function_response = None
            for part in response.parts:
                if hasattr(part, 'function_call'):
                    function_response = part.function_call
                    break
            
            if function_response and function_response.name == "detect_calorie_management_intent":
                # 使用 function_response.args 直接作為結果
                result = dict(function_response.args)  # 轉換為普通字典
                
                logger.info(f"檢測到卡路里管理意圖: {result}")
                return result
            
            # 未檢測到意圖的結果
            no_intent_result = {
                "has_calorie_intent": False,
                "intent_type": "none",
                "confidence": 0.0
            }
            logger.info("未檢測到卡路里管理意圖")
            return no_intent_result
                
        except Exception as e:
            error_msg = f"檢查卡路里管理意圖時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {
                "has_calorie_intent": False,
                "intent_type": "none", 
                "confidence": 0.0,
                "error": str(e)
            }
#TODO 意圖重複？？_process_search_intent
    def check_search_intent(self, message_text: str) -> Dict[str, Any]:
        """
        使用 function calling 檢查用戶訊息是否有搜索意圖
        
        Args:
            message_text (str): 用戶傳入的訊息文字
            
        Returns:
            dict: 包含搜索意圖和時間範圍的字典
        """
        try:
            logger.info(f"開始檢查訊息是否有搜索意圖: {message_text}")
            
            # 使用 Gemini 進行意圖解析
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": 0.2}
            )
            
            # 設置 function calling
            tools = [
                {
                    "function_declarations": [self.search_intent_function],
                }
            ]
            
            response = model.generate_content(
                f"從以下用戶訊息中判斷是否包含搜索食物歷史或查詢卡路里攝取量的意圖，並提取相關時間範圍：\n\n{message_text}",
                tools=tools
            )
            
            # 提取 function calling 結果
            function_response = None
            for part in response.parts:
                if hasattr(part, 'function_call'):
                    function_response = part.function_call
                    break
            
            if function_response and function_response.name == "extract_search_intent":
                # 使用 function_response.args 直接作為結果
                result = dict(function_response.args)  # 轉換為普通字典
                logger.info(f"檢測到搜索意圖: {result}")
                return result
            
            logger.info("未檢測到搜索意圖")
            return {"has_search_intent": False}
                
        except Exception as e:
            error_msg = f"檢查搜索意圖時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {"has_search_intent": False}
    
    def _extract_date_from_message(self, message_text: str) -> Optional[datetime.date]:
        """
        從用戶訊息中提取日期信息
        
        Args:
            message_text (str): 用戶訊息文字
            
        Returns:
            datetime.date or None: 提取到的日期，如果無法提取則返回 None
        """
        today = datetime.date.today()
        
        # 匹配完整日期格式，如 "2023-01-01", "2023/01/01", "2023.01.01"
        date_pattern = r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})'
        full_date_match = re.search(date_pattern, message_text)
        if full_date_match:
            try:
                year = int(full_date_match.group(1))
                month = int(full_date_match.group(2))
                day = int(full_date_match.group(3))
                return datetime.date(year, month, day)
            except ValueError:
                logger.warning("日期格式無效")
        
        # 匹配部分日期，如 "3月1日", "3-1", "3/1"
        partial_date_pattern = r'(\d{1,2})[-/月](\d{1,2})[日號]?'
        partial_date_match = re.search(partial_date_pattern, message_text)
        if partial_date_match:
            try:
                month = int(partial_date_match.group(1))
                day = int(partial_date_match.group(2))
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return datetime.date(today.year, month, day)
            except ValueError:
                logger.warning("部分日期格式無效")
        
        # 匹配相對日期，如 "昨天", "今天", "前天"
        if "今天" in message_text or "今日" in message_text:
            return today
        elif "昨天" in message_text or "昨日" in message_text:
            return today - datetime.timedelta(days=1)
        elif "前天" in message_text:
            return today - datetime.timedelta(days=2)
        elif "上週" in message_text or "上星期" in message_text:
            return today - datetime.timedelta(days=7)
        elif "上個月" in message_text:
            # 簡單處理，減去30天
            return today - datetime.timedelta(days=30)
        
        # 匹配數字+天前，如 "3天前"
        days_ago_pattern = r'(\d+)天前'
        days_ago_match = re.search(days_ago_pattern, message_text)
        if days_ago_match:
            try:
                days = int(days_ago_match.group(1))
                return today - datetime.timedelta(days=days)
            except ValueError:
                logger.warning("天數格式無效")
        
        # 如果都無法匹配，返回 None
        return None
    
    def _detect_physical_info_by_keywords(self, message_text: str) -> bool:
        """
        使用關鍵詞檢測方法判斷訊息是否包含生理資訊
        
        Args:
            message_text (str): 用戶訊息文字
            
        Returns:
            bool: 是否包含完整的生理資訊
        """
        gender_keywords = ["男", "女", "性別"]
        age_keywords = ["歲", "岁", "年齡", "年紀"]
        height_keywords = ["身高", "公分", "cm", "CM"]
        weight_keywords = ["體重", "公斤", "kg", "KG"]
        
        has_gender = any(keyword in message_text for keyword in gender_keywords)
        has_age = any(keyword in message_text for keyword in age_keywords)
        has_height = any(keyword in message_text for keyword in height_keywords)
        has_weight = any(keyword in message_text for keyword in weight_keywords)
        
        # 簡單地檢查是否同時包含這四類關鍵詞，以及是否包含數字
        contains_numbers = bool(re.search(r'\d+', message_text))
        return has_gender and has_age and has_height and has_weight and contains_numbers

    def get_detection_stats(self) -> Dict[str, Any]:
        """
        獲取檢測方法使用統計
        
        Returns:
            dict: 統計資訊
        """
        # 這裡可以添加統計邏輯，追蹤不同檢測方法的使用情況
        return {
            "unified_detection_enabled": self.enable_unified_detection,
            "fallback_enabled": self.fallback_to_individual,
            "confidence_threshold": self.unified_confidence_threshold,
            "last_detection_method": getattr(self, '_last_detection_method', 'unknown')
        }

    def configure_detection_method(self, 
                                 enable_unified: bool = None,
                                 enable_fallback: bool = None,
                                 confidence_threshold: float = None) -> Dict[str, Any]:
        """
        動態配置檢測方法
        
        Args:
            enable_unified (bool): 是否啟用統一檢測
            enable_fallback (bool): 是否啟用回退機制
            confidence_threshold (float): 統一檢測的信心度閾值
            
        Returns:
            dict: 配置結果
        """
        old_config = {
            "enable_unified_detection": self.enable_unified_detection,
            "fallback_to_individual": self.fallback_to_individual,
            "unified_confidence_threshold": self.unified_confidence_threshold
        }
        
        if enable_unified is not None:
            self.enable_unified_detection = enable_unified
            
        if enable_fallback is not None:
            self.fallback_to_individual = enable_fallback
            
        if confidence_threshold is not None:
            if 0.0 <= confidence_threshold <= 1.0:
                self.unified_confidence_threshold = confidence_threshold
            else:
                logger.warning(f"無效的信心度閾值: {confidence_threshold}, 應在 0.0-1.0 之間")
        
        new_config = {
            "enable_unified_detection": self.enable_unified_detection,
            "fallback_to_individual": self.fallback_to_individual,
            "unified_confidence_threshold": self.unified_confidence_threshold
        }
        
        logger.info(f"檢測方法配置已更新: {old_config} -> {new_config}")
        return {
            "success": True,
            "old_config": old_config,
            "new_config": new_config
        }