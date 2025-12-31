import logging
import json
import traceback
from typing import Dict, Any, Optional
from Service.PhysInfoDataService import PhysInfoDataService
from Service.ConnectionFactory import ConnectionFactory

# 設置日誌記錄
logger = logging.getLogger(__name__)

class ManagerCalService:
    def __init__(self):
        """
        初始化卡路里管理服務
        """
        logger.info("初始化卡路里管理服務")
        self.phys_info_service = PhysInfoDataService()
        
    def calculate_cal_function_definition(self) -> Dict[str, Any]:
        """
        返回計算卡路里相關的 function 定義，用於 function calling
        
        Returns:
            dict: function calling 的定義
        """
        return {
            "name": "calculate_calories",
            "description": "計算用戶的 BMI、基礎代謝率(BMR)和每日建議卡路里攝取量",
            "parameters": {
                "type": "object",
                "properties": {
                    "sex": {
                        "type": "string", 
                        "description": "用戶的性別，如'男'或'女'"
                    },
                    "age": {
                        "type": "integer", 
                        "description": "用戶的年齡"
                    },
                    "height": {
                        "type": "number", 
                        "description": "用戶的身高(cm)"
                    },
                    "weight": {
                        "type": "number", 
                        "description": "用戶的體重(kg)"
                    }
                },
                "required": ["sex", "age", "height", "weight"]
            }
        }
    
    def process_cal_data(self, cal_data):
        """
        處理卡路里相關的JSON數據
        
        Args:
            cal_data (dict): 從NLP服務生成的卡路里相關JSON數據，
                             例如: {'height': 身高, 'weight': 體重, 'age': 年齡}
            
        Returns:
            dict: 處理後的結果，包含BMR(基礎代謝率)和每日建議卡路里攝取量
        """
        try:
            logger.info(f"開始處理卡路里數據: {cal_data}")
            
            # 檢查數據格式是否正確
            if '內容錯誤' in cal_data:
                logger.warning("輸入數據格式不正確")
                return {"result": "無法處理您的請求，請提供正確的身高、體重和年齡信息。"}
            
            # 確保必要的字段存在
            required_fields = ['height', 'weight', 'age']
            for field in required_fields:
                if field not in cal_data:
                    logger.warning(f"缺少必要字段: {field}")
                    return {"result": f"無法處理您的請求，缺少{field}信息。"}
            
            # 提取數據
            try:
                height = float(cal_data['height'])  # 身高(cm)
                weight = float(cal_data['weight'])  # 體重(kg)
                age = int(cal_data['age'])          # 年齡
                gender = cal_data.get('sex', cal_data.get('gender', '男'))  # 性別，默認為'男'
            except (ValueError, TypeError) as e:
                logger.error(f"數據轉換錯誤: {str(e)}")
                return {"result": "數據格式錯誤，請確保身高、體重和年齡為數字。"}
            
            # 計算BMI
            bmi = weight / ((height/100) ** 2)
            
            # 計算基礎代謝率(BMR)
            # 使用Mifflin-St Jeor公式
            if gender.lower() in ['男', 'male', 'm']:
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            # 計算每日建議卡路里攝取量(假設中等活動量，BMR * 1.55)
            daily_calories = bmr * 1.55
            
            # 計算減重時的建議卡路里攝取量(每日減少500大卡)
            weight_loss_calories = daily_calories - 500
            
            # 準備結果
            result = {
                "bmi": round(bmi, 2),
                "bmr": round(bmr),
                "daily_calories": round(daily_calories),
                "weight_loss_calories": round(weight_loss_calories),
                "result": f"您的BMI指數為{round(bmi, 2)}，基礎代謝率(BMR)為{round(bmr)}大卡。"
                         f"維持體重的每日建議攝取量為{round(daily_calories)}大卡，"
                         f"減重時的建議攝取量為{round(weight_loss_calories)}大卡。"
            }
            
            logger.info(f"卡路里數據處理完成: {result}")
            return result
            
        except Exception as e:
            error_msg = f"處理卡路里數據時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {"result": f"處理您的卡路里數據時發生錯誤: {str(e)}"}

    def execute_cal_function(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行卡路里計算函數，用於 function calling
        
        Args:
            function_args (dict): 從 LLM 獲取的函數參數
            
        Returns:
            dict: 包含計算結果的JSON物件
        """
        # 將 function_args 轉換為 process_cal_data 需要的格式
        cal_data = {
            'sex': function_args.get('sex', '男'),
            'gender': function_args.get('sex', '男'),  # 為了兼容
            'age': function_args.get('age'),
            'height': function_args.get('height'),
            'weight': function_args.get('weight')
        }
        
        # 調用現有的 process_cal_data 函數處理數據
        return self.process_cal_data(cal_data)
        
    def process_user_id(self, user_id: str) -> Dict[str, Any]:
        """
        根據用戶ID從資料庫獲取身體資訊並計算卡路里相關數據
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            dict: 處理後的結果，包含BMR(基礎代謝率)和每日建議卡路里攝取量
        """
        try:
            logger.info(f"根據用戶ID處理卡路里計算: {user_id}")
            
            # 使用新的方法直接通過user_id獲取身體資訊
            phys_info_response = self.phys_info_service.get_phys_info_by_user_id(user_id)
            
            # 檢查回應狀態
            if phys_info_response["status"] != "success":
                logger.warning(f"找不到用戶 {user_id} 的身體資訊: {phys_info_response['result']}")
                return {"result": "無法找到您的身體資訊，請先提供性別、年齡、身高和體重。"}
            
            # 從回應中獲取實際的身體資訊
            phys_info = phys_info_response["result"]
                
            # 將資料庫數據轉換為卡路里計算所需格式
            cal_data = {
                'gender': phys_info['gender'],
                'sex': phys_info['gender'],  # 為了兼容
                'age': phys_info['age'],
                'height': phys_info['height'],
                'weight': phys_info['weight']
            }
            
            # 調用現有的 process_cal_data 函數處理數據
            return self.process_cal_data(cal_data)
            
        except Exception as e:
            error_msg = f"處理用戶ID的卡路里數據時發生錯誤: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return {"result": f"處理您的卡路里數據時發生錯誤: {str(e)}"}
