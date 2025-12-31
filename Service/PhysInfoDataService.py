# ==========================================================
# 使用者身體資訊資料服務
# 專門用於管理使用者身體資訊的 CRUD 操作
# ==========================================================

import sys
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple

# 將專案根目錄加入到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入資料庫連接工廠和優化錯誤處理器
from Service.ConnectionFactory import ConnectionFactory

# 設置日誌記錄
logger = logging.getLogger(__name__)

class PhysInfoDataService:
    """
    使用者身體資訊資料服務類別
    負責管理使用者身體資訊的 CRUD 操作
    """
    
    def __init__(self):
        # 預載常用用戶資料到快取
        self.preload_cache()
    
    def preload_cache(self):
        """
        預載最近活躍用戶的身體資訊到快取
        """
        try:
            connection = ConnectionFactory.create_connection()
            if not connection:
                return
                
            # 查詢最近更新的前20名用戶資料
            query = """
            SELECT TOP 20 master_id 
            FROM physInfo 
            ORDER BY updateDate DESC
            """
            
            cursor = connection.cursor()
            cursor.execute(query)
            recent_users = cursor.fetchall()
            cursor.close()
            ConnectionFactory.close_connection(connection)
            
            if recent_users:
                user_ids = [user[0] for user in recent_users]
                logger.info(f"找到 {len(user_ids)} 個近期活躍用戶")
                
        except Exception as e:
            logger.warning(f"獲取近期活躍用戶時發生錯誤: {str(e)}")
    
    
    def refresh_user_cache(self, user_id: str) -> bool:
        """
        獲取特定用戶的最新資料
        
        Args:
            user_id: 用戶ID
            
        Returns:
            bool: 是否成功獲取資料
        """
        try:
            # 直接查詢資料庫獲取最新資料
            result = self.get_phys_info(user_id)
            if result["status"] == "success":
                logger.info(f"成功獲取用戶 {user_id} 的最新資料")
                return True
            else:
                logger.warning(f"無法獲取用戶 {user_id} 的資料: {result['result']}")
                return False
                
        except Exception as e:
            logger.error(f"獲取用戶 {user_id} 資料時發生錯誤: {str(e)}")
            return False
    
    
    def create_phys_info(self, master_id: str, gender: str, age: int, height: float, weight: float, allergic_foods: List[str] = None) -> Dict[str, Any]:
        """
        建立使用者身體資訊
        
        Args:
            master_id: 關聯到foodMaster的ID
            gender: 性別
            age: 年齡
            height: 身高(cm)
            weight: 體重(kg)
            allergic_foods: 過敏食物清單 (可選)
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": bool/message}
        """
        # 快速驗證必要欄位
        validation_error = self.error_handler.validate_input_fast(
            {
                'master_id': master_id,
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight
            },
            ['master_id', 'gender', 'age', 'height', 'weight']
        )
        if validation_error:
            return {"status": "error", "result": validation_error}
        
        connection = ConnectionFactory.create_connection()
        if not connection:
            return {"status": "error", "result": "無法建立資料庫連接"}
            
        # 檢查master_id是否存在於foodMaster表中
        check_master_query = "SELECT COUNT(*) FROM foodMaster WHERE id = ?"
        master_exists = ConnectionFactory.get_query_count(connection, check_master_query, (master_id,))
        
        if master_exists == 0:
            # 如果主檔不存在，則自動創建
            try:
                logger.info(f"主檔ID {master_id} 不存在，將自動創建")
                
                # 插入主檔記錄
                insert_master_query = """
                INSERT INTO foodMaster (id, user_id)
                VALUES (?, ?)
                """
                
                # 這裡我們假設 master_id 和 user_id 是相同的，因為這是創建新記錄
                ConnectionFactory.execute_query(connection, insert_master_query, (master_id, master_id))
                logger.info(f"已創建主檔ID {master_id}")
            except Exception as e:
                logger.error(f"創建主檔記錄時發生錯誤: {str(e)}")
                ConnectionFactory.close_connection(connection)
                return {"status": "error", "result": f"創建主檔記錄時發生錯誤: {str(e)}"}
            
        # 檢查使用者是否已有身體資訊
        check_query = "SELECT COUNT(*) FROM physInfo WHERE master_id = ?"
        exists = ConnectionFactory.get_query_count(connection, check_query, (master_id,))
        
        # 處理過敏食物列表，轉換為JSON字符串，確保使用 utf-8 編碼
        allergic_foods_json = json.dumps(allergic_foods, ensure_ascii=False) if allergic_foods else '[]'
        
        if exists > 0:
            # 更新現有記錄，包含過敏食物欄位
            update_query = """
            UPDATE physInfo
            SET gender = ?, age = ?, height = ?, weight = ?, allergic_foods = ?
            WHERE master_id = ?
            """
            params = (gender, age, height, weight, allergic_foods_json, master_id)
            result = ConnectionFactory.execute_query(connection, update_query, params)
        else:
            # 建立新記錄，包含過敏食物欄位
            insert_query = """
            INSERT INTO physInfo (master_id, gender, age, height, weight, allergic_foods)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (master_id, gender, age, height, weight, allergic_foods_json)
            result = ConnectionFactory.execute_query(connection, insert_query, params)
            
        ConnectionFactory.close_connection(connection)
        
        return {
            "status": "success" if result else "error",
            "result": result if result else "操作失敗"
        }
    
    def get_phys_info(self, master_id: str) -> Dict[str, Any]:
        """
        獲取使用者身體資訊
        
        Args:
            master_id: 關聯到foodMaster的ID
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": dict/message}
        """
        # 快速驗證
        if not master_id:
            return {"status": "error", "result": "主檔ID不能為空"}
        
        connection = ConnectionFactory.create_connection()
        if not connection:
            return {"status": "error", "result": "無法建立資料庫連接"}
            
        try:
            cursor = connection.cursor()
            
            query = """
            SELECT id, master_id, gender, age, height, weight, allergic_foods, 
                   createDate, updateDate
            FROM physInfo
            WHERE master_id = ?
            """
            
            cursor.execute(query, (master_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return {"status": "error", "result": "找不到使用者資訊"}
                
            # 將查詢結果轉換為字典，包含過敏食物欄位
            phys_info = {
                'id': result[0],
                'master_id': result[1],
                'gender': result[2],
                'age': result[3],
                'height': result[4],
                'weight': result[5],
                'allergic_foods': json.loads(result[6]) if result[6] else [],
                'createDate': result[7],
                'updateDate': result[8]
            }
            
            return {"status": "success", "result": phys_info}
            
        except Exception as e:
            logger.error(f"獲取使用者身體資訊時發生錯誤: {str(e)}")
            return {"status": "error", "result": f"獲取身體資訊時發生錯誤: {str(e)}"}
            
        finally:
            ConnectionFactory.close_connection(connection)
    
    def update_phys_info(self, master_id: str, **kwargs) -> Dict[str, Any]:
        """
        更新使用者身體資訊
        
        Args:
            master_id: 關聯到foodMaster的ID
            **kwargs: 要更新的欄位及其值，可包含 gender, age, height, weight, allergic_foods
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": bool/message}
        """
        # 快速驗證
        if not master_id:
            return {"status": "error", "result": "主檔ID不能為空"}
        if not kwargs:
            return {"status": "error", "result": "沒有提供要更新的欄位"}
            
        connection = ConnectionFactory.create_connection()
        if not connection:
            return {"status": "error", "result": "無法建立資料庫連接"}
            
        # 檢查使用者是否存在
        check_query = "SELECT COUNT(*) FROM physInfo WHERE master_id = ?"
        exists = ConnectionFactory.get_query_count(connection, check_query, (master_id,))
        
        if exists == 0:
            ConnectionFactory.close_connection(connection)
            return {"status": "error", "result": f"主檔ID {master_id} 不存在"}
            
        # 準備更新語句
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if key == 'allergic_foods' and isinstance(value, list):
                set_clauses.append(f"{key} = ?")
                params.append(json.dumps(value, ensure_ascii=False))
            elif key in ['gender', 'age', 'height', 'weight']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            ConnectionFactory.close_connection(connection)
            return {"status": "error", "result": "沒有提供有效的更新欄位"}
            
        # 建立更新查詢
        update_query = f"""
        UPDATE physInfo
        SET {', '.join(set_clauses)}
        WHERE master_id = ?
        """
        
        params.append(master_id)
        result = ConnectionFactory.execute_query(connection, update_query, tuple(params))
        ConnectionFactory.close_connection(connection)
        
        return {
            "status": "success" if result else "error",
            "result": result if result else "更新失敗"
        }
    
    def delete_phys_info(self, master_id: str) -> Dict[str, Any]:
        """
        刪除使用者身體資訊
        
        Args:
            master_id: 關聯到foodMaster的ID
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": bool/message}
        """
        # 快速驗證
        if not master_id:
            return {"status": "error", "result": "主檔ID不能為空"}
        
        connection = ConnectionFactory.create_connection()
        if not connection:
            return {"status": "error", "result": "無法建立資料庫連接"}
            
        # 刪除查詢
        delete_query = "DELETE FROM physInfo WHERE master_id = ?"
        result = ConnectionFactory.execute_query(connection, delete_query, (master_id,))
        ConnectionFactory.close_connection(connection)
        
        return {
            "status": "success" if result else "error",
            "result": result if result else "刪除失敗"
        }
    
    def get_all_phys_info(self) -> Dict[str, Any]:
        """
        獲取所有使用者身體資訊
        
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": list/message}
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            return {"status": "error", "result": "無法建立資料庫連接"}
            
        query = """
        SELECT id, master_id, gender, age, height, weight, allergic_foods, 
               createDate, updateDate
        FROM physInfo
        ORDER BY updateDate DESC
        """
        
        results = ConnectionFactory.execute_query(connection, query)
        ConnectionFactory.close_connection(connection)
        
        if not results:
            return {"status": "success", "result": []}
            
        # 將查詢結果轉換為字典列表，包含過敏食物欄位
        phys_info_list = []
        for row in results:
            phys_info = {
                'id': row[0],
                'master_id': row[1],
                'gender': row[2],
                'age': row[3],
                'height': row[4],
                'weight': row[5],
                'allergic_foods': json.loads(row[6]) if row[6] else [],
                'createDate': row[7],
                'updateDate': row[8]
            }
            phys_info_list.append(phys_info)
            
        return {"status": "success", "result": phys_info_list}
            
    def calculate_bmi(self, master_id: str) -> Dict[str, Any]:
        """
        計算使用者的BMI值
        
        Args:
            master_id: 關聯到foodMaster的ID
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": float/message}
        """
        # 快速驗證
        if not master_id:
            return {"status": "error", "result": "主檔ID不能為空"}
            
        phys_info_result = self.get_phys_info(master_id)
        
        if phys_info_result["status"] != "success":
            return {"status": "error", "result": "找不到使用者身體資訊"}
            
        phys_info = phys_info_result["result"]
        height_m = phys_info['height'] / 100  # 轉換為公尺
        weight_kg = phys_info['weight']
        
        if height_m <= 0:
            return {"status": "error", "result": "身高必須大於0"}
            
        bmi = weight_kg / (height_m * height_m)
        return {"status": "success", "result": round(bmi, 2)}
            
    def calculate_bmr(self, master_id: str) -> Dict[str, Any]:
        """
        計算使用者的基礎代謝率(BMR)
        使用Mifflin-St Jeor方程式
        
        Args:
            master_id: 關聯到foodMaster的ID
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": float/message}
        """
        # 快速驗證
        if not master_id:
            return {"status": "error", "result": "主檔ID不能為空"}
            
        phys_info_result = self.get_phys_info(master_id)
        
        if phys_info_result["status"] != "success":
            return {"status": "error", "result": "找不到使用者身體資訊"}
            
        phys_info = phys_info_result["result"]
        gender = phys_info['gender']
        age = phys_info['age']
        height_cm = phys_info['height']
        weight_kg = phys_info['weight']
        
        # Mifflin-St Jeor方程式
        if gender.lower() in ['男', 'male', 'm']:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
            
        return {"status": "success", "result": round(bmr, 2)}
        
    def get_phys_info_by_user_id(self, user_id: str) -> Dict[str, Any]:
        """
        根據用戶ID獲取使用者身體資訊
        
        Args:
            user_id: 用戶ID
            
        Returns:
            Dict: 操作結果 {"status": "success/error", "result": dict/message}
        """
        # 快速驗證
        if not user_id:
            return {"status": "error", "result": "用戶ID不能為空"}
        
        connection = ConnectionFactory.create_connection()
        if not connection:
            return {"status": "error", "result": "無法建立資料庫連接"}
            
        try:
            # 首先嘗試精確匹配 user_id
            master_query = "SELECT id FROM foodMaster WHERE user_id = ?"
            master_result = ConnectionFactory.execute_query_with_cursor(connection, master_query, (user_id,), fetch_all=False)
            
            # 如果精確匹配失敗，再嘗試 id 匹配
            if not master_result:
                master_query = "SELECT id FROM foodMaster WHERE id = ?"
                master_result = ConnectionFactory.execute_query_with_cursor(connection, master_query, (user_id,), fetch_all=False)
            
            if not master_result:
                # 如果找不到master_id，嘗試直接查詢physInfo表
                logger.info(f"找不到用戶 {user_id} 的主檔，嘗試直接查詢身體資訊")
                
                cursor = connection.cursor()
                
                direct_query = """
                SELECT id, master_id, gender, age, height, weight, allergic_foods, 
                       createDate, updateDate
                FROM physInfo
                WHERE master_id = ?
                """
                
                cursor.execute(direct_query, (user_id,))
                result = cursor.fetchone()
                cursor.close()
                
                if not result:
                    return {"status": "error", "result": f"找不到用戶 {user_id} 的身體資訊"}
                    
                # 將查詢結果轉換為字典，包含過敏食物欄位
                phys_info = {
                    'id': result[0],
                    'master_id': result[1],
                    'gender': result[2],
                    'age': result[3],
                    'height': result[4],
                    'weight': result[5],
                    'allergic_foods': json.loads(result[6]) if result[6] else [],
                    'createDate': result[7],
                    'updateDate': result[8]
                }
                
                return {"status": "success", "result": phys_info}
            
            master_id = master_result[0]
            logger.info(f"找到用戶 {user_id} 對應的 master_id: {master_id}")
            
            # 然後查詢該master_id的身體資訊
            cursor = connection.cursor()
            
            phys_query = """
            SELECT id, master_id, gender, age, height, weight, allergic_foods, 
                   createDate, updateDate
            FROM physInfo
            WHERE master_id = ?
            """
            
            cursor.execute(phys_query, (master_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return {"status": "error", "result": f"找不到 master_id {master_id} 的身體資訊"}
                
            # 將查詢結果轉換為字典，包含過敏食物欄位
            phys_info = {
                'id': result[0],
                'master_id': result[1],
                'gender': result[2],
                'age': result[3],
                'height': result[4],
                'weight': result[5],
                'allergic_foods': json.loads(result[6]) if result[6] else [],
                'createDate': result[7],
                'updateDate': result[8]
            }
            
            return {"status": "success", "result": phys_info}
            
        except Exception as e:
            logger.error(f"根據用戶ID獲取使用者身體資訊時發生錯誤: {str(e)}")
            return {"status": "error", "result": f"獲取身體資訊時發生錯誤: {str(e)}"}
            
        finally:
            ConnectionFactory.close_connection(connection)
