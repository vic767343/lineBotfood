# ==========================================================
# 食物資料服務
# 專門用於處理食物主檔和明細檔資料表的CRUD操作
# ==========================================================

import logging
import sys
import os
import datetime
import re
from typing import List, Dict, Any, Optional, Tuple

# 將專案根目錄加入到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入連接工廠
from Service.ConnectionFactory import ConnectionFactory
# 導入優化的錯誤處理器和性能監控
from Service.PerformanceAPI import PerformanceMonitor

# 設置日誌記錄
logger = logging.getLogger(__name__)

class FoodDataService:
    """
    食物資料服務類別
    負責處理食物主檔和明細檔資料表的CRUD操作
    """
    
    def __init__(self):
        """初始化食物資料服務"""
        logger.info("初始化食物資料服務")
        
        # 初始化錯誤處理器和性能監控
        self.performance_monitor = PerformanceMonitor()
        
        # 檢查食物主檔及明細檔資料表是否存在，如果不存在則建立
        self._ensure_food_master_details_table_exists()
    
    @property
    def performance_monitor(self):
        """性能監控的 getter"""
        if not hasattr(self, '_performance_monitor'):
            self._performance_monitor = PerformanceMonitor()
        return self._performance_monitor
    
    @performance_monitor.setter
    def performance_monitor(self, value):
        """性能監控的 setter"""
        self._performance_monitor = value
    
    def _extract_number_from_text(self, text: str) -> int:
        """
        從文本中提取數字
        
        Args:
            text (str): 包含數字的文本，例如 "100卡" 或 "150cal"
            
        Returns:
            int: 提取出的數字，如果無法提取則返回0
        """
        @self.error_handler.fast_error_handler(default_response=0)
        def extract_logic():
            # 移除所有非數字字符
            number_str = re.sub(r'[^0-9]', '', text)
            
            # 轉換為整數
            if number_str:
                return int(number_str)
            return 0
        
        return extract_logic()
            
    def _ensure_food_master_details_table_exists(self) -> None:
        """
        確保食物主檔和明細檔資料表存在，若不存在則建立
        """
        @self.performance_monitor.timing_decorator("確保資料表存在")
        @self.error_handler.fast_error_handler()
        def ensure_tables():
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 讀取主檔SQL檔案
                base_dir = os.path.dirname(os.path.dirname(__file__))
                master_sql_file_path = os.path.join(base_dir, 'dataBaseSQL', 'foodMaster.sql')
                
                # 檢查主檔SQL檔案是否存在
                if not os.path.exists(master_sql_file_path):
                    logger.warning(f"主檔SQL檔案不存在: {master_sql_file_path}")
                    
                    # 手動建立主檔資料表
                    master_check_query = """
                    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'foodMaster')
                    BEGIN
                        CREATE TABLE foodMaster (
                            id NVARCHAR(100) PRIMARY KEY, 
                            -- 使用LineWebHookRESTController中image存檔的名稱(不含附檔名)
                            createDate DATETIME DEFAULT GETDATE(), -- 資料建立日期時間
                            user_id NVARCHAR(100) -- 與user關聯的ID
                        )
                    END
                    """
                    
                    # 執行建立主檔資料表的查詢
                    master_result = ConnectionFactory.execute_query(connection, master_check_query)
                    
                    if master_result:
                        logger.info("已確認 foodMaster 資料表存在或已成功建立")
                    else:
                        raise Exception("建立 foodMaster 資料表失敗")
                else:
                    # 從主檔SQL檔案讀取內容並執行
                    # 使用新的 ConnectionFactory 方法
                    master_result = ConnectionFactory.execute_file_script(connection, master_sql_file_path)
                    if master_result:
                        logger.info("已從主檔SQL檔案成功建立 foodMaster 資料表")
                    else:
                        raise Exception("執行主檔SQL腳本失敗")
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return ensure_tables()
    
    def get_food_masters(self, page: int = 1, page_size: int = 10, user_id: str = '') -> Dict[str, Any]:
        """
        獲取食物主檔列表，支援分頁和搜尋
        
        Args:
            page (int): 頁碼，從1開始
            page_size (int): 每頁顯示的記錄數
            user_id (str): 用戶ID過濾條件，空字符串表示不過濾
            
        Returns:
            dict: 包含食物主檔列表和總記錄數的字典
        """
        @self.performance_monitor.timing_decorator("獲取食物主檔列表")
        @self.error_handler.fast_error_handler(default_response={
            'masters': [],
            'total': 0,
            'page': page,
            'page_size': page_size,
            'total_pages': 0
        })
        def get_masters_logic():
            # 輸入驗證
            validation_error = self.error_handler.validate_input_fast(
                {'page': page, 'page_size': page_size}, 
                ['page', 'page_size']
            )
            if validation_error:
                raise ValueError(validation_error)
            
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 計算分頁偏移量
                offset = (page - 1) * page_size
                
                # 準備查詢參數
                params = []
                
                # 準備查詢條件
                where_clause = ""
                if user_id:
                    where_clause = " WHERE user_id = ?"
                    params.append(user_id)
                
                # 查詢總記錄數
                count_query = f"SELECT COUNT(*) AS total FROM foodMaster{where_clause}"
                
                # 使用新的 get_query_count 方法執行計數查詢
                total_count = ConnectionFactory.get_query_count(connection, count_query, params if params else None)
                
                # 查詢當前頁的數據
                query = f"""
                    SELECT id, createDate, user_id
                    FROM foodMaster{where_clause}
                    ORDER BY createDate DESC
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                """
                
                # 添加分頁參數
                query_params = params.copy()
                query_params.append(offset)
                query_params.append(page_size)
                
                # 使用新的 execute_query_with_cursor 方法執行查詢
                rows = ConnectionFactory.execute_query_with_cursor(connection, query, query_params)
                
                # 提取結果
                masters = []
                if rows:
                    for row in rows:
                        masters.append({
                            'id': row[0],
                            'createDate': row[1].isoformat() if row[1] else None,
                            'user_id': row[2]
                        })
                
                # 計算總頁數
                total_pages = (total_count + page_size - 1) // page_size
                
                return {
                    'masters': masters,
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': total_pages
                }
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return get_masters_logic()
    
    def get_food_master_by_id(self, master_id: str) -> Dict[str, Any]:
        """
        根據ID獲取食物主檔詳情
        
        Args:
            master_id (str): 主檔ID
            
        Returns:
            dict: 主檔詳情字典，如果未找到則返回None
        """
        @self.performance_monitor.timing_decorator("獲取食物主檔詳情")
        @self.error_handler.fast_error_handler(default_response=None)
        def get_master_by_id_logic():
            # 輸入驗證
            validation_error = self.error_handler.validate_input_fast(
                {'master_id': master_id}, 
                ['master_id']
            )
            if validation_error:
                raise ValueError(validation_error)
            
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 準備查詢
                query = """
                    SELECT id, createDate, user_id
                    FROM foodMaster
                    WHERE id = ?
                """
                
                # 執行查詢
                cursor = connection.cursor()
                cursor.execute(query, (master_id,))
                
                # 提取結果
                row = cursor.fetchone()
                cursor.close()
                
                if row:
                    return {
                        'id': row[0],
                        'createDate': row[1].isoformat() if row[1] else None,
                        'user_id': row[2]
                    }
                else:
                    return None
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return get_master_by_id_logic()
    
    def add_food_master(self, master_id: str, user_id: str) -> bool:
        """
        新增食物主檔
        
        Args:
            master_id (str): 主檔ID
            user_id (str): 用戶ID
            
        Returns:
            bool: 新增成功返回True，失敗返回False
        """
        @self.performance_monitor.timing_decorator("新增食物主檔")
        @self.error_handler.fast_error_handler(default_response=False)
        def add_master_logic():
            # 輸入驗證
            validation_error = self.error_handler.validate_input_fast(
                {'master_id': master_id, 'user_id': user_id}, 
                ['master_id', 'user_id']
            )
            if validation_error:
                raise ValueError(validation_error)
            
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 準備插入查詢
                query = """
                    INSERT INTO foodMaster (id, user_id)
                    VALUES (?, ?)
                """
                
                # 執行查詢
                cursor = connection.cursor()
                cursor.execute(query, (master_id, user_id))
                connection.commit()
                cursor.close()
                
                return True
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return add_master_logic()
    
    def update_food_master(self, master_id: str, user_id: str) -> bool:
        """
        更新食物主檔
        
        Args:
            master_id (str): 主檔ID
            user_id (str): 用戶ID
            
        Returns:
            bool: 更新成功返回True，失敗返回False
        """
        @self.performance_monitor.timing_decorator("更新食物主檔")
        @self.error_handler.fast_error_handler(default_response=False)
        def update_master_logic():
            # 輸入驗證
            validation_error = self.error_handler.validate_input_fast(
                {'master_id': master_id, 'user_id': user_id}, 
                ['master_id', 'user_id']
            )
            if validation_error:
                raise ValueError(validation_error)
            
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 準備更新查詢
                query = """
                    UPDATE foodMaster
                    SET user_id = ?
                    WHERE id = ?
                """
                
                # 執行查詢
                cursor = connection.cursor()
                cursor.execute(query, (user_id, master_id))
                connection.commit()
                cursor.close()
                
                return True
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return update_master_logic()
    
    def delete_food_master(self, master_id: str) -> bool:
        """
        刪除食物主檔
        
        Args:
            master_id (str): 主檔ID
            
        Returns:
            bool: 刪除成功返回True，失敗返回False
        """
        @self.performance_monitor.timing_decorator("刪除食物主檔")
        @self.error_handler.fast_error_handler(default_response=False)
        def delete_master_logic():
            # 輸入驗證
            validation_error = self.error_handler.validate_input_fast(
                {'master_id': master_id}, 
                ['master_id']
            )
            if validation_error:
                raise ValueError(validation_error)
            
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 準備刪除查詢
                query = """
                    DELETE FROM foodMaster
                    WHERE id = ?
                """
                
                # 執行查詢
                cursor = connection.cursor()
                cursor.execute(query, (master_id,))
                connection.commit()
                cursor.close()
                
                return True
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return delete_master_logic()
    
    def get_food_details(
        self, 
        page: int = 1, 
        page_size: int = 10, 
        master_id: str = '', 
        intent: str = ''
    ) -> Dict[str, Any]:
        """
        獲取食物明細列表，支援分頁和搜尋
        
        Args:
            page (int): 頁碼，從1開始
            page_size (int): 每頁顯示的記錄數
            master_id (str): 主檔ID過濾條件，空字符串表示不過濾
            intent (str): 意圖過濾條件，空字符串表示不過濾
            
        Returns:
            dict: 包含食物明細列表和總記錄數的字典
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return None
        
        try:
            # 計算分頁偏移量
            offset = (page - 1) * page_size
            
            # 準備查詢參數
            params = []
            
            # 準備查詢條件
            where_clauses = []
            if master_id:
                where_clauses.append("master_id = ?")
                params.append(master_id)
            
            if intent:
                where_clauses.append("intent = ?")
                params.append(intent)
            
            where_clause = ""
            if where_clauses:
                where_clause = " WHERE " + " AND ".join(where_clauses)
            
            # 查詢總記錄數
            count_query = f"SELECT COUNT(*) AS total FROM foodDetails{where_clause}"
            
            # 執行計數查詢
            cursor = connection.cursor()
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
            
            # 查詢當前頁的數據
            query = f"""
                SELECT id, master_id, intent, desc_text, calories, total_calories, createDate
                FROM foodDetails{where_clause}
                ORDER BY createDate DESC
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            
            # 添加分頁參數
            params.append(offset)
            params.append(page_size)
            
            # 執行查詢
            cursor.execute(query, params)
            
            # 提取結果
            details = []
            for row in cursor.fetchall():
                details.append({
                    'id': row[0],
                    'master_id': row[1],
                    'intent': row[2],
                    'desc_text': row[3],
                    'calories': row[4],
                    'total_calories': row[5],
                    'createDate': row[6].isoformat() if row[6] else None
                })
            
            cursor.close()
            
            # 返回結果
            return {
                'data': details,
                'totalCount': total_count
            }
        
        except Exception as e:
            logger.error(f"獲取食物明細列表時發生錯誤: {str(e)}")
            return None
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def get_food_detail_by_id(self, detail_id: int) -> Dict[str, Any]:
        """
        根據ID獲取食物明細詳情
        
        Args:
            detail_id (int): 明細ID
            
        Returns:
            dict: 明細詳情字典，如果未找到則返回None
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return None
        
        try:
            # 準備查詢
            query = """
                SELECT id, master_id, intent, desc_text, calories, total_calories, createDate
                FROM foodDetails
                WHERE id = ?
            """
            
            # 執行查詢
            cursor = connection.cursor()
            cursor.execute(query, (detail_id,))
            
            # 提取結果
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'id': row[0],
                    'master_id': row[1],
                    'intent': row[2],
                    'desc_text': row[3],
                    'calories': row[4],
                    'total_calories': row[5],
                    'createDate': row[6].isoformat() if row[6] else None
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"獲取食物明細詳情時發生錯誤: {str(e)}")
            return None
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def get_food_details_by_master_id(self, master_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        根據主檔ID獲取食物明細列表，支援分頁
        
        Args:
            master_id (str): 主檔ID
            page (int): 頁碼，從1開始
            page_size (int): 每頁顯示的記錄數
            
        Returns:
            dict: 包含食物明細列表和總記錄數的字典
        """
        # 使用現有的方法，只是傳入master_id參數
        return self.get_food_details(page=page, page_size=page_size, master_id=master_id)
    
    def add_food_detail(self, master_id: str, intent: str, desc_text: str, calories: int, total_calories: int) -> int:
        """
        新增食物明細
        
        Args:
            master_id (str): 主檔ID
            intent (str): 意圖
            desc_text (str): 食物描述
            calories (int): 卡路里
            total_calories (int): 總卡路里
            
        Returns:
            int: 新增成功返回明細ID，失敗返回0
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return 0
        
        try:
            # 準備插入查詢
            query = """
                INSERT INTO foodDetails (master_id, intent, desc_text, calories, total_calories)
                VALUES (?, ?, ?, ?, ?);
                SELECT SCOPE_IDENTITY() AS new_id;
            """
            
            # 執行查詢
            cursor = connection.cursor()
            cursor.execute(query, (master_id, intent, desc_text, calories, total_calories))
            
            # 獲取新插入的ID
            new_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            
            return int(new_id)
        
        except Exception as e:
            logger.error(f"新增食物明細時發生錯誤: {str(e)}")
            return 0
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def update_food_detail(
        self, 
        detail_id: int, 
        intent: str, 
        desc_text: str, 
        calories: int, 
        total_calories: int
    ) -> bool:
        """
        更新食物明細
        
        Args:
            detail_id (int): 明細ID
            intent (str): 意圖
            desc_text (str): 食物描述
            calories (int): 卡路里
            total_calories (int): 總卡路里
            
        Returns:
            bool: 更新成功返回True，失敗返回False
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            # 準備更新查詢
            query = """
                UPDATE foodDetails
                SET intent = ?, desc_text = ?, calories = ?, total_calories = ?
                WHERE id = ?
            """
            
            # 執行查詢
            cursor = connection.cursor()
            cursor.execute(query, (intent, desc_text, calories, total_calories, detail_id))
            connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            logger.error(f"更新食物明細時發生錯誤: {str(e)}")
            return False
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def delete_food_detail(self, detail_id: int) -> bool:
        """
        刪除食物明細
        
        Args:
            detail_id (int): 明細ID
            
        Returns:
            bool: 刪除成功返回True，失敗返回False
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            # 準備刪除查詢
            query = """
                DELETE FROM foodDetails
                WHERE id = ?
            """
            
            # 執行查詢
            cursor = connection.cursor()
            cursor.execute(query, (detail_id,))
            connection.commit()
            cursor.close()
            
            return True
        
        except Exception as e:
            logger.error(f"刪除食物明細時發生錯誤: {str(e)}")
            return False
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
            
    def add_food_analysis(self, master_id: str, user_id: str, analysis_data: dict) -> bool:
        """
        新增食物分析資料
        
        Args:
            master_id (str): 主檔ID
            user_id (str): 用戶ID
            analysis_data (dict): 分析資料
            
        Returns:
            bool: 是否成功
        """
        if not master_id or not user_id:
            logger.error("新增食物分析失敗: 缺少主檔ID或用戶ID")
            return False
        
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            # 開始事務
            connection.autocommit = False
            
            # 1. 插入主檔資料
            master_insert_query = """
            INSERT INTO foodMaster (id, user_id)
            VALUES (?, ?)
            """
            
            master_result = ConnectionFactory.execute_query(connection, master_insert_query, [master_id, user_id])
            
            if not master_result:
                logger.error(f"插入食物主檔失敗, ID: {master_id}")
                connection.rollback()
                return False
                
            # 2. 解析分析數據並插入明細檔
            intent = analysis_data.get('intent', '未知')
            items_raw = analysis_data.get('item', [])
            
            # 確保 items 是列表格式，防止 'int' object is not iterable 錯誤
            if isinstance(items_raw, list):
                items = items_raw
            elif isinstance(items_raw, dict):
                items = [items_raw]  # 如果是單個字典，包裝為列表
            else:
                logger.warning(f"無效的 item 資料格式: {type(items_raw)}, 值: {items_raw}")
                logger.debug(f"完整的 analysis_data: {analysis_data}")
                items = []
            
            # 檢查是否有全域的本餐共攝取數值
            global_total_cal_text = analysis_data.get('本餐共攝取', '0卡')
            global_total_calories = self._extract_number_from_text(global_total_cal_text)
            
            # 處理特殊情況：如果items中最後一個item只包含"本餐共攝取"，則提取它並移除
            if items and len(items) > 0:
                last_item = items[-1]
                if len(last_item) == 1 and '本餐共攝取' in last_item:
                    global_total_cal_text = last_item.get('本餐共攝取', '0卡')
                    global_total_calories = self._extract_number_from_text(global_total_cal_text)
                    items = items[:-1]  # 移除最後一個只包含總攝取量的項目
                    logger.info(f"從items中提取到本餐共攝取: {global_total_cal_text}")
            
            # 檢查是否為無法辨識的圖片且沒有項目
            if intent == '無法辨識' and (not items or len(items) == 0):
                # 對於無法辨識的圖片，在 foodDetail 中新增一筆空記錄
                msg = f"處理無法辨識的圖片，將在 foodDetail 中新增空記錄，主檔ID: {master_id}"
                logger.info(msg)
                
                details_insert_query = """
                INSERT INTO foodDetails (master_id, intent, desc_text, calories, total_calories)
                VALUES (?, ?, ?, ?, ?)
                """
                
                details_result = ConnectionFactory.execute_query(
                    connection, 
                    details_insert_query, 
                    [master_id, intent, None, None, None]
                )
                
                if not details_result:
                    logger.error(f"插入無法辨識圖片的明細檔失敗, 主檔ID: {master_id}")
                    connection.rollback()
                    return False
            else:
                # 正常處理有項目的圖片
                for item in items:
                    # 跳過只包含"本餐共攝取"的項目
                    if len(item) == 1 and '本餐共攝取' in item:
                        continue
                        
                    # 從item中提取數據
                    desc_text = item.get('desc', '')
                    
                    # 如果沒有desc，跳過這個項目
                    if not desc_text:
                        continue
                    
                    # 提取卡路里數值（移除單位）
                    calories_text = item.get('cal', '0cal')
                    calories = self._extract_number_from_text(calories_text)
                    
                    # 提取總卡路里數值（移除單位）
                    # 優先使用item中本餐共攝取，如果沒有則使用全域的
                    item_total_cal_text = item.get('本餐共攝取', '')
                    if item_total_cal_text:
                        total_calories = self._extract_number_from_text(item_total_cal_text)
                    else:
                        total_calories = global_total_calories
                    
                    # 插入明細檔
                    details_insert_query = """
                    INSERT INTO foodDetails (master_id, intent, desc_text, calories, total_calories)
                    VALUES (?, ?, ?, ?, ?)
                    """
                    
                    details_result = ConnectionFactory.execute_query(
                        connection, 
                        details_insert_query, 
                        [master_id, intent, desc_text, calories, total_calories]
                    )
                    
                    if not details_result:
                        logger.error(f"插入食物明細檔失敗, 主檔ID: {master_id}")
                        connection.rollback()
                        return False
            
            # 提交事務
            connection.commit()
            logger.info(f"成功插入食物分析資料, 主檔ID: {master_id}")
            return True
            
        except Exception as e:
            # 發生錯誤時回滾事務
            connection.rollback()
            logger.error(f"新增食物分析時發生錯誤: {str(e)}")
            return False
        
        finally:
            # 恢復自動提交
            connection.autocommit = True
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def get_food_analysis_by_id(self, master_id: str) -> Optional[Dict[str, Any]]:
        """
        根據主檔ID查詢食物分析資料
        
        Args:
            master_id (str): 主檔ID
                
        Returns:
            dict or None: 食物分析資料字典或None(查詢失敗時)
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return None
        
        try:
            # 1. 查詢主檔資料
            master_query = """
            SELECT id, createDate, user_id 
            FROM foodMaster 
            WHERE id = ?
            """
            
            master_result = ConnectionFactory.execute_query(connection, master_query, [master_id])
            
            if not master_result or len(master_result) == 0:
                logger.warning(f"未找到食物主檔資料, ID: {master_id}")
                return None
                
            # 2. 查詢明細檔資料
            details_query = """
            SELECT id, intent, desc_text, calories, total_calories 
            FROM foodDetails 
            WHERE master_id = ?
            """
            
            details_result = ConnectionFactory.execute_query(connection, details_query, [master_id])
            
            # 3. 組合資料
            master_data = {
                'id': master_result[0][0],
                'createDate': master_result[0][1],
                'user_id': master_result[0][2]
            }
            
            details_data = []
            for row in details_result:
                # 處理可能為 None 的欄位
                intent = row[1] if row[1] is not None else '無法辨識'
                desc = row[2] if row[2] is not None else '未識別食物'
                calories = row[3] if row[3] is not None else 0
                total_calories = row[4] if row[4] is not None else 0
                
                details_data.append({
                    'id': row[0],
                    'intent': intent,
                    'desc': desc,
                    'cal': f"{calories}cal",
                    '本餐共攝取': f"{total_calories}卡"
                })
            
            # 4. 返回符合原始分析格式的資料
            analysis_data = {
                'master': master_data,
                'intent': details_data[0]['intent'] if details_data else '未知',
                'item': details_data
            }
            
            logger.info(f"成功查詢食物分析資料, ID: {master_id}")
            return analysis_data
            
        except Exception as e:
            logger.error(f"查詢食物分析資料時發生錯誤: {str(e)}")
            return None
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def get_food_analyses_by_user_id(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        根據用戶ID查詢食物分析資料列表
        
        Args:
            user_id (str): 用戶ID
            limit (int): 限制返回數量，默認10
            offset (int): 跳過前面的記錄數，默認0
                
        Returns:
            list: 食物分析資料字典列表
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return []
        
        try:
            # 1. 查詢該用戶的主檔資料
            master_query = """
            SELECT id, createDate, user_id 
            FROM foodMaster 
            WHERE user_id = ? 
            ORDER BY createDate DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            
            master_result = ConnectionFactory.execute_query(connection, master_query, [user_id, offset, limit])
            
            if not master_result or len(master_result) == 0:
                logger.warning(f"未找到用戶的食物分析資料, 用戶ID: {user_id}")
                return []
                
            # 2. 查詢各主檔對應的明細檔資料
            result_list = []
            
            for master_row in master_result:
                master_id = master_row[0]
                
                # 查詢明細檔
                details_query = """
                SELECT id, intent, desc_text, calories, total_calories 
                FROM foodDetails 
                WHERE master_id = ?
                """
                
                details_result = ConnectionFactory.execute_query(connection, details_query, [master_id])
                
                # 組合資料
                master_data = {
                    'id': master_row[0],
                    'createDate': master_row[1],
                    'user_id': master_row[2]
                }
                
                details_data = []
                for row in details_result:
                    # 處理可能為 None 的欄位
                    intent = row[1] if row[1] is not None else '無法辨識'
                    desc = row[2] if row[2] is not None else '未識別食物'
                    calories = row[3] if row[3] is not None else 0
                    total_calories = row[4] if row[4] is not None else 0
                    
                    details_data.append({
                        'id': row[0],
                        'intent': intent,
                        'desc': desc,
                        'cal': f"{calories}cal",
                        '本餐共攝取': f"{total_calories}卡"
                    })
                
                # 添加到結果列表
                result_list.append({
                    'master': master_data,
                    'intent': details_data[0]['intent'] if details_data else '未知',
                    'item': details_data
                })
            
            msg = f"成功查詢用戶食物分析資料, 用戶ID: {user_id}, 找到 {len(result_list)} 筆記錄"
            logger.info(msg)
            return result_list
            
        except Exception as e:
            logger.error(f"查詢用戶食物分析資料時發生錯誤: {str(e)}")
            return []
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def update_food_analysis(self, master_id: str, analysis_data: Dict[str, Any]) -> bool:
        """
        更新食物分析資料
        
        Args:
            master_id (str): 主檔ID
            analysis_data (dict): 分析結果數據
                
        Returns:
            bool: 更新成功返回True，失敗返回False
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            # 開始事務
            connection.autocommit = False
            
            # 1. 檢查主檔是否存在
            check_query = "SELECT COUNT(*) FROM foodMaster WHERE id = ?"
            check_result = ConnectionFactory.execute_query(connection, check_query, [master_id])
            
            if not check_result or check_result[0][0] == 0:
                logger.warning(f"未找到要更新的食物主檔, ID: {master_id}")
                return False
                
            # 2. 刪除現有的明細檔資料
            delete_query = "DELETE FROM foodDetails WHERE master_id = ?"
            delete_result = ConnectionFactory.execute_query(connection, delete_query, [master_id])
            
            if not delete_result:
                logger.error(f"刪除食物明細檔失敗, 主檔ID: {master_id}")
                connection.rollback()
                return False
                
            # 3. 插入新的明細檔資料
            intent = analysis_data.get('intent', '未知')
            items_raw = analysis_data.get('item', [])
            
            # 確保 items 是列表格式，防止 'int' object is not iterable 錯誤
            if isinstance(items_raw, list):
                items = items_raw
            elif isinstance(items_raw, dict):
                items = [items_raw]  # 如果是單個字典，包裝為列表
            else:
                logger.warning(f"無效的 item 資料格式: {type(items_raw)}, 值: {items_raw}")
                logger.debug(f"完整的 analysis_data: {analysis_data}")
                items = []
            
            # 檢查是否為無法辨識的圖片且沒有項目
            if intent == '無法辨識' and (not items or len(items) == 0):
                # 對於無法辨識的圖片，在 foodDetail 中新增一筆空記錄
                msg = f"處理無法辨識的圖片，將在 foodDetail 中新增空記錄，主檔ID: {master_id}"
                logger.info(msg)
                
                details_insert_query = """
                INSERT INTO foodDetails (master_id, intent, desc_text, calories, total_calories)
                VALUES (?, ?, ?, ?, ?)
                """
                
                details_result = ConnectionFactory.execute_query(
                    connection, 
                    details_insert_query, 
                    [master_id, intent, None, None, None]
                )
                
                if not details_result:
                    logger.error(f"插入無法辨識圖片的明細檔失敗, 主檔ID: {master_id}")
                    connection.rollback()
                    return False
            else:
                # 正常處理有項目的圖片
                for item in items:
                    # 從item中提取數據
                    desc_text = item.get('desc', '')
                    
                    # 提取卡路里數值（移除單位）
                    calories_text = item.get('cal', '0cal')
                    calories = self._extract_number_from_text(calories_text)
                    
                    # 提取總卡路里數值（移除單位）
                    total_cal_text = item.get('本餐共攝取', '0卡')
                    total_calories = self._extract_number_from_text(total_cal_text)
                    
                    # 插入明細檔
                    details_insert_query = """
                    INSERT INTO foodDetails (master_id, intent, desc_text, calories, total_calories)
                    VALUES (?, ?, ?, ?, ?)
                    """
                    
                    details_result = ConnectionFactory.execute_query(
                        connection, 
                        details_insert_query, 
                        [master_id, intent, desc_text, calories, total_calories]
                    )
                    
                    if not details_result:
                        logger.error(f"插入更新後的食物明細檔失敗, 主檔ID: {master_id}")
                        connection.rollback()
                        return False
            
            # 提交事務
            connection.commit()
            logger.info(f"成功更新食物分析資料, 主檔ID: {master_id}")
            return True
            
        except Exception as e:
            # 發生錯誤時回滾事務
            connection.rollback()
            logger.error(f"更新食物分析資料時發生錯誤: {str(e)}")
            return False
        
        finally:
            # 恢復自動提交
            connection.autocommit = True
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def delete_food_analysis(self, master_id: str) -> bool:
        """
        刪除食物分析資料
        
        Args:
            master_id (str): 主檔ID
                
        Returns:
            bool: 刪除成功返回True，失敗返回False
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            # 開始事務
            connection.autocommit = False
            
            # 1. 先刪除明細檔資料
            details_delete_query = "DELETE FROM foodDetails WHERE master_id = ?"
            details_result = ConnectionFactory.execute_query(connection, details_delete_query, [master_id])
            
            if not details_result:
                logger.error(f"刪除食物明細檔失敗, 主檔ID: {master_id}")
                connection.rollback()
                return False
                
            # 2. 再刪除主檔資料
            master_delete_query = "DELETE FROM foodMaster WHERE id = ?"
            master_result = ConnectionFactory.execute_query(connection, master_delete_query, [master_id])
            
            if not master_result:
                logger.error(f"刪除食物主檔失敗, ID: {master_id}")
                connection.rollback()
                return False
            
            # 提交事務
            connection.commit()
            logger.info(f"成功刪除食物分析資料, 主檔ID: {master_id}")
            return True
            
        except Exception as e:
            # 發生錯誤時回滾事務
            connection.rollback()
            logger.error(f"刪除食物分析資料時發生錯誤: {str(e)}")
            return False
        
        finally:
            # 恢復自動提交
            connection.autocommit = True
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def get_total_calories_by_date(self, user_id: str, date: Optional[datetime.date] = None) -> int:
        """
        獲取用戶在特定日期的總卡路里（從明細檔中獲取）
        
        Args:
            user_id (str): 用戶ID
            date (datetime.date, optional): 日期，默認為今天
                
        Returns:
            int: 總卡路里數量
        """
        if date is None:
            date = datetime.date.today()
        
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return 0
        
        try:
            # 查詢該日期最新的總卡路里數量
            query = """
            SELECT TOP 1 fd.total_calories
            FROM foodMaster fm
            JOIN foodDetails fd ON fm.id = fd.master_id
            WHERE fm.user_id = ? 
            AND CONVERT(date, fm.createDate) = ?
            ORDER BY fm.createDate DESC
            """
            
            result = ConnectionFactory.execute_query(connection, query, [user_id, date])
            
            if result and len(result) > 0 and result[0][0]:
                total_calories = result[0][0]
                msg = f"成功獲取用戶總卡路里, 用戶ID: {user_id}, 日期: {date}, 總卡路里: {total_calories}"
                logger.info(msg)
                return total_calories
            else:
                logger.warning(f"未找到用戶卡路里記錄, 用戶ID: {user_id}, 日期: {date}")
                return 0
        
        except Exception as e:
            logger.error(f"獲取用戶總卡路里時發生錯誤: {str(e)}")
            return 0
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def bulk_insert_food_analyses(self, analyses_data_list: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        批量插入食物分析資料
        
        Args:
            analyses_data_list (list): 包含主檔ID、用戶ID和分析資料的字典列表
                每個字典格式: {'master_id': '主檔ID', 'user_id': '用戶ID', 'analysis_data': {...}}
                
        Returns:
            tuple: (成功數量, 失敗數量)
        """
        success_count = 0
        fail_count = 0
        
        for data in analyses_data_list:
            master_id = data.get('master_id')
            user_id = data.get('user_id')
            analysis_data = data.get('analysis_data')
            
            # 驗證必填欄位
            if not master_id or not user_id or not analysis_data:
                logger.warning("跳過無效的食物分析資料: 缺少必要資訊")
                fail_count += 1
                continue
            
            # 新增單筆食物分析資料
            if self.add_food_analysis(master_id, user_id, analysis_data):
                success_count += 1
            else:
                fail_count += 1
        
        logger.info(f"批量插入食物分析資料完成: 成功 {success_count} 筆, 失敗 {fail_count} 筆")
        return (success_count, fail_count)
        
    # ===== 統計分析 =====
    
    #獲取食物主檔總數量
    def get_food_master_count(self) -> int:
        """
        獲取食物主檔總數量
        
        Returns:
            int: 食物主檔總數量
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return 0
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM foodMaster")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"獲取食物主檔總數量時發生錯誤: {str(e)}")
            return 0
        finally:
            ConnectionFactory.close_connection(connection)
    
    #獲取食物明細總數量
    def get_food_details_count(self) -> int:
        """
        獲取食物明細總數量
        
        Returns:
            int: 食物明細總數量
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return 0
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM foodDetails")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"獲取食物明細總數量時發生錯誤: {str(e)}")
            return 0
        finally:
            ConnectionFactory.close_connection(connection)
    
    # 獲取特定用戶的食物分析數量
    def get_user_food_count(self, user_id: str) -> int:
        """
        獲取特定用戶的食物分析數量
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            int: 該用戶的食物分析數量
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return 0
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM foodMaster 
                WHERE user_id = ?
            """, (user_id,))
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logger.error(f"獲取用戶食物分析數量時發生錯誤: {str(e)}")
            return 0
        finally:
            ConnectionFactory.close_connection(connection)
    
    def get_most_common_intents(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        獲取最常見的食物意圖
        
        Args:
            limit (int): 返回結果的數量限制
            
        Returns:
            list: (意圖, 數量) 的元組列表
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return []
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT intent, COUNT(*) as count 
                FROM foodDetails
                GROUP BY intent 
                ORDER BY count DESC, intent ASC 
                OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
            """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            return [(row.intent, row.count) for row in results]
        except Exception as e:
            logger.error(f"獲取最常見食物意圖時發生錯誤: {str(e)}")
            return []
        finally:
            ConnectionFactory.close_connection(connection)
    
    def batch_update_intent(self, original_intent: str, new_intent: str) -> Optional[int]:
        """
        批量修改食物明細的餐點類型
        
        Args:
            original_intent (str): 原始餐點類型
            new_intent (str): 新餐點類型
            
        Returns:
            Optional[int]: 成功修改的記錄數量，失敗時返回None
        """
        logger.info(f"開始批量修改餐點類型：從 '{original_intent}' 到 '{new_intent}'")
        
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return None
        
        try:
            cursor = connection.cursor()
            
            # 執行批量更新
            cursor.execute("""
                UPDATE foodDetails 
                SET intent = ?
                WHERE intent = ?
            """, (new_intent, original_intent))
            
            # 獲取影響的行數
            updated_count = cursor.rowcount
            
            # 提交事務
            connection.commit()
            cursor.close()
            
            logger.info(f"批量修改完成，共修改了 {updated_count} 筆記錄")
            return updated_count
            
        except Exception as e:
            logger.error(f"批量修改餐點類型時發生錯誤: {str(e)}")
            connection.rollback()
            return None
        finally:
            ConnectionFactory.close_connection(connection)

    def user_batch_update_intent(self, user_id, new_intent):
        """
        使用者層級批量修改食物明細的餐點類型
        
        Args:
            user_id (str): 使用者ID
            new_intent (str): 新的餐點類型
            
        Returns:
            int: 更新的記錄數，失敗返回None
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return None
        
        try:
            cursor = connection.cursor()
            
            # 批量更新該使用者的所有食物明細的餐點類型
            cursor.execute("""
                UPDATE foodDetails 
                SET intent = ?
                WHERE master_id IN (
                    SELECT id FROM foodMaster WHERE user_id = ?
                )
            """, (new_intent, user_id))
            
            # 獲取影響的行數
            updated_count = cursor.rowcount
            
            # 提交事務
            connection.commit()
            cursor.close()
            
            logger.info(f"使用者 {user_id} 批量修改完成，共修改了 {updated_count} 筆記錄")
            return updated_count
            
        except Exception as e:
            logger.error(f"使用者批量修改餐點類型時發生錯誤: {str(e)}")
            connection.rollback()
            return None
        finally:
            ConnectionFactory.close_connection(connection)
    
    def update_detail_intent(self, detail_id: int, new_intent: str) -> bool:
        """
        只修改食物明細的餐點類型
        
        Args:
            detail_id (int): 明細ID
            new_intent (str): 新的餐點類型
            
        Returns:
            bool: 修改成功返回True，失敗返回False
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            cursor = connection.cursor()
            
            # 只更新餐點類型
            cursor.execute("""
                UPDATE foodDetails 
                SET intent = ?
                WHERE id = ?
            """, (new_intent, detail_id))
            
            # 提交事務
            connection.commit()
            cursor.close()
            
            logger.info(f"明細ID {detail_id} 的餐點類型已修改為: {new_intent}")
            return True
            
        except Exception as e:
            logger.error(f"修改餐點類型時發生錯誤: {str(e)}")
            connection.rollback()
            return False
        finally:
            ConnectionFactory.close_connection(connection)

    def batch_update_user_intent(self, user_id: str, intent: str) -> bool:
        """
        批次更新指定用戶的所有食物明細的餐點類型
        
        Args:
            user_id (str): 用戶ID
            intent (str): 新的餐點類型
            
        Returns:
            bool: 更新成功返回True，失敗返回False
        """
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            cursor = connection.cursor()
            
            # 批次更新該用戶的所有明細的餐點類型
            cursor.execute("""
                UPDATE foodDetails 
                SET intent = ?
                WHERE master_id IN (
                    SELECT id FROM foodMaster WHERE user_id = ?
                )
            """, (intent, user_id))
            
            # 提交事務
            connection.commit()
            cursor.close()
            
            logger.info(f"用戶 {user_id} 的所有餐點類型已批次修改為: {intent}")
            return True
            
        except Exception as e:
            logger.error(f"批次修改用戶餐點類型時發生錯誤: {str(e)}")
            connection.rollback()
            return False
        finally:
            ConnectionFactory.close_connection(connection)

    def update_master_total_calories(self, master_id: str) -> bool:
        """
        更新指定主檔下所有明細的總卡路里
        
        Args:
            master_id (str): 主檔ID
            
        Returns:
            bool: 更新成功返回True，失敗返回False
        """
        # 建立資料庫連接
        connection = ConnectionFactory.create_connection()
        if not connection:
            logger.error("無法建立資料庫連接")
            return False
        
        try:
            # 先計算該主檔下所有明細的總卡路里
            calc_query = """
                SELECT SUM(ISNULL(calories, 0)) as total_calories
                FROM foodDetails
                WHERE master_id = ?
            """
            
            cursor = connection.cursor()
            cursor.execute(calc_query, (master_id,))
            result = cursor.fetchone()
            total_calories = result[0] if result and result[0] is not None else 0
            
            # 更新該主檔下所有明細的 total_calories 欄位
            update_query = """
                UPDATE foodDetails
                SET total_calories = ?
                WHERE master_id = ?
            """
            
            cursor.execute(update_query, (total_calories, master_id))
            connection.commit()
            cursor.close()
            
            logger.info(f"主檔 {master_id} 的總卡路里已更新為 {total_calories}")
            return True
        
        except Exception as e:
            logger.error(f"更新主檔 {master_id} 總卡路里時發生錯誤: {str(e)}")
            connection.rollback()
            return False
        
        finally:
            # 關閉資料庫連接
            ConnectionFactory.close_connection(connection)
    
    def get_past_7_days_food_records(self, user_id: str) -> List[Dict[str, Any]]:
        """
        獲取用戶過去7天的飲食記錄
        
        Args:
            user_id (str): 用戶ID
            
        Returns:
            List[Dict[str, Any]]: 過去7天的飲食記錄列表
        """
        @self.performance_monitor.timing_decorator("獲取過去7天飲食記錄")
        @self.error_handler.fast_error_handler(default_response=[])
        def get_past_7_days_logic():
            # 輸入驗證
            validation_error = self.error_handler.validate_input_fast(
                {'user_id': user_id}, 
                ['user_id']
            )
            if validation_error:
                raise ValueError(validation_error)
            
            # 建立資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法建立資料庫連接")
            
            try:
                # 計算7天前的日期
                seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
                
                # 查詢過去7天的飲食記錄
                query = """
                SELECT 
                    CONVERT(date, fm.createDate) as record_date,
                    fm.id as master_id,
                    fd.intent,
                    fd.desc_text,
                    fd.calories,
                    fd.total_calories,
                    fm.createDate
                FROM foodMaster fm
                LEFT JOIN foodDetails fd ON fm.id = fd.master_id
                WHERE fm.user_id = ? 
                AND CONVERT(date, fm.createDate) >= ?
                ORDER BY fm.createDate DESC, fd.id
                """
                
                result = ConnectionFactory.execute_query(connection, query, [user_id, seven_days_ago])
                
                if not result:
                    logger.info(f"用戶 {user_id} 過去7天沒有飲食記錄")
                    return []
                
                # 組織數據
                food_records = []
                current_date = None
                daily_record = None
                
                for row in result:
                    record_date = row[0]
                    master_id = row[1]
                    intent = row[2]
                    desc_text = row[3]
                    calories = row[4]
                    total_calories = row[5]
                    # row[6] is create_date - not currently used
                    
                    # 如果是新的日期，創建新的日記錄
                    if current_date != record_date:
                        if daily_record:
                            food_records.append(daily_record)
                        
                        current_date = record_date
                        daily_record = {
                            'date': record_date.isoformat() if record_date else None,
                            'total_calories': 0,
                            'foods': []
                        }
                    
                    # 添加食物記錄
                    if desc_text:
                        food_item = {
                            'intent': intent,
                            'description': desc_text,
                            'calories': calories
                        }
                        daily_record['foods'].append(food_item)
                    
                    # 更新當日總卡路里（取最新的total_calories）
                    if total_calories:
                        daily_record['total_calories'] = total_calories
                
                # 添加最後一天的記錄
                if daily_record:
                    food_records.append(daily_record)
                
                logger.info(f"成功獲取用戶 {user_id} 過去7天的飲食記錄，共 {len(food_records)} 天")
                return food_records
            
            finally:
                # 關閉資料庫連接
                ConnectionFactory.close_connection(connection)
        
        return get_past_7_days_logic()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        獲取服務性能統計資訊
        
        Returns:
            dict: 性能統計數據
        """
        stats = self.performance_monitor.get_performance_stats()
        return {
            'service_name': 'FoodDataService',
            'performance_stats': stats,
            'should_alert': self.performance_monitor.should_alert(),
            'error_handler_stats': {
                'error_count': self.error_handler.error_count,
                'last_error_time': self.error_handler.last_error_time
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        服務健康檢查
        
        Returns:
            dict: 健康檢查結果
        """
        @self.performance_monitor.timing_decorator("健康檢查")
        @self.error_handler.fast_error_handler(default_response={
            'status': 'unhealthy',
            'message': '健康檢查失敗',
            'timestamp': datetime.datetime.now().isoformat()
        })
        def health_check_logic():
            
            # 檢查資料庫連接
            connection = ConnectionFactory.create_connection()
            if not connection:
                raise Exception("無法連接到資料庫")
            
            try:
                # 簡單查詢測試
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                # 獲取性能統計
                perf_stats = self.get_performance_stats()
                
                return {
                    'status': 'healthy',
                    'message': 'FoodDataService 運行正常',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'performance': perf_stats
                }
            
            finally:
                ConnectionFactory.close_connection(connection)
        
        return health_check_logic()
