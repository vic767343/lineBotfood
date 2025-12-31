# ==========================================================
# 資料庫連接工廠
# 專門用於建立和管理資料庫連接，集中所有資料庫訪問端點
# ==========================================================

import pyodbc
import sys
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from queue import Queue, Empty
from threading import Lock
import time

# 將專案根目錄加入到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入資料庫配置
from config.dataBase import db_config

# 設置日誌記錄
logger = logging.getLogger(__name__)

class ConnectionPool:
    """
    連接池管理器 - 優化資料庫連接性能
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.max_connections = 5
        self.min_connections = 2
        self.connection_pool = Queue(maxsize=self.max_connections)
        self.active_connections = 0
        self.pool_lock = Lock()
        self.connection_timeout = 30
        
        # 性能統計
        self.total_queries = 0
        self.total_time = 0
        
        # 初始化連接池
        self._initialize_pool()
        self._initialized = True
    
    def _create_connection_string(self):
        """創建連接字串"""
        if db_config['driver'] == 'ODBC Driver 17 for SQL Server':
            driver_path = '/opt/homebrew/lib/libmsodbcsql.17.dylib'
        elif db_config['driver'] == 'ODBC Driver 18 for SQL Server':
            driver_path = '/opt/homebrew/lib/libmsodbcsql.18.dylib'
        else:
            driver_path = None
            
        if driver_path:
            return (
                f"DRIVER={driver_path};"
                f"SERVER={db_config['serverName']};"
                f"DATABASE={db_config['databaseName']};"
                f"UID={db_config['userName']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
                f"Encrypt=yes;"
                f"Connection Timeout={self.connection_timeout};"
                f"Charset=UTF-8;"
            )
        else:
            return (
                f"DRIVER={{{db_config['driver']}}};"
                f"SERVER={db_config['serverName']};"
                f"DATABASE={db_config['databaseName']};"
                f"UID={db_config['userName']};"
                f"PWD={db_config['password']};"
                f"TrustServerCertificate=yes;"
                f"Encrypt=yes;"
                f"Connection Timeout={self.connection_timeout};"
                f"Charset=UTF-8;"
            )
    
    def _create_new_connection(self):
        """創建新的資料庫連接"""
        try:
            conn_str = self._create_connection_string()
            connection = pyodbc.connect(conn_str)
            connection.autocommit = True
            
            # 設置連接編碼為 UTF-8，確保中文字符的正確處理
            connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
            connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
            connection.setencoding(encoding='utf-8')
            
            return connection
        except pyodbc.Error as e:
            logger.error(f"創建資料庫連接失敗: {e}")
            return None
    
    def _initialize_pool(self):
        """初始化連接池"""
        for _ in range(self.min_connections):
            conn = self._create_new_connection()
            if conn:
                self.connection_pool.put(conn)
                self.active_connections += 1
    
    def get_connection(self, timeout=5):
        """從連接池獲取連接"""
        try:
            connection = self.connection_pool.get(timeout=timeout)
            if self._is_connection_valid(connection):
                return connection
            else:
                with self.pool_lock:
                    self.active_connections -= 1
                return self._create_new_connection()
                
        except Empty:
            if self.active_connections < self.max_connections:
                with self.pool_lock:
                    if self.active_connections < self.max_connections:
                        conn = self._create_new_connection()
                        if conn:
                            self.active_connections += 1
                        return conn
            
            logger.warning("無法從連接池獲取連接")
            return None
    
    def return_connection(self, connection):
        """將連接歸還給連接池"""
        if connection and self._is_connection_valid(connection):
            try:
                self.connection_pool.put_nowait(connection)
            except:
                self._close_connection(connection)
                with self.pool_lock:
                    self.active_connections -= 1
        else:
            self._close_connection(connection)
            with self.pool_lock:
                self.active_connections -= 1
    
    def _is_connection_valid(self, connection):
        """檢查連接是否有效"""
        if not connection:
            return False
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            return False
    
    def _close_connection(self, connection):
        """關閉單個連接"""
        if connection:
            try:
                connection.close()
            except:
                pass
    
    def get_performance_stats(self):
        """獲取性能統計"""
        if self.total_queries == 0:
            return {
                "total_queries": 0,
                "avg_query_time": 0,
                "active_connections": self.active_connections
            }
        
        return {
            "total_queries": self.total_queries,
            "avg_query_time": self.total_time / self.total_queries,
            "active_connections": self.active_connections,
            "pool_size": self.connection_pool.qsize()
        }

# 全域連接池實例
_connection_pool = ConnectionPool()

class ConnectionFactory:
    """
    優化的資料庫連接工廠類別
    包含連接池、性能監控和向後兼容性
    """
    
    @staticmethod
    def create_connection():
        """
        建立資料庫連接 - 優化版本使用連接池
        
        Returns:
            connection: 資料庫連接物件
        """
        return _connection_pool.get_connection()
    
    @staticmethod
    def close_connection(connection):
        """
        關閉資料庫連接 - 優化版本歸還到連接池
        
        Args:
            connection: 要關閉的資料庫連接物件
        """
        _connection_pool.return_connection(connection)
    
    @staticmethod
    def execute_query_fast(query, params=None, fetch_one=False):
        """
        快速執行查詢 - 使用連接池的新方法
        
        Args:
            query: SQL查詢語句
            params: 查詢參數 (可選)
            fetch_one: 是否只獲取一條記錄
            
        Returns:
            result: 查詢結果
        """
        start_time = time.time()
        connection = _connection_pool.get_connection()
        
        if not connection:
            logger.error("無法獲取資料庫連接")
            return None
        
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT") or "OUTPUT" in query.strip().upper():
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
                cursor.close()
                return result
            else:
                cursor.close()
                return True
                
        except pyodbc.Error as e:
            logger.error(f"執行查詢時發生錯誤: {e}")
            return None
        finally:
            # 記錄性能統計
            _connection_pool.total_queries += 1
            _connection_pool.total_time += time.time() - start_time
            
            # 歸還連接
            _connection_pool.return_connection(connection)
    
    @staticmethod
    def get_performance_stats():
        """獲取性能統計"""
        return _connection_pool.get_performance_stats()
    
    @staticmethod
    def execute_query(connection, query, params=None):
        """
        執行SQL查詢
        
        Args:
            connection: 資料庫連接物件
            query: SQL查詢語句
            params: 查詢參數 (可選)
            
        Returns:
            result: 查詢結果
        """
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # 檢查是否為SELECT查詢或含有OUTPUT子句的INSERT查詢
            if query.strip().upper().startswith("SELECT") or "OUTPUT" in query.strip().upper():
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                connection.commit()
                cursor.close()
                return True
                
        except pyodbc.Error as e:
            print(f"執行查詢時發生錯誤: {e}")
            return None
            
    @staticmethod
    def execute_query_with_cursor(connection, query, params=None, fetch_all=True):
        """
        執行SQL查詢並返回結果，不需要在外部管理游標
        
        Args:
            connection: 資料庫連接物件
            query: SQL查詢語句
            params: 查詢參數 (可選)
            fetch_all: 是否獲取所有結果，False則只獲取第一條記錄
            
        Returns:
            result: 查詢結果
        """
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # 檢查是否為SELECT查詢或含有OUTPUT子句的INSERT查詢
            if query.strip().upper().startswith("SELECT") or "OUTPUT" in query.strip().upper():
                if fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
                cursor.close()
                return result
            else:
                connection.commit()
                cursor.close()
                return True
                
        except pyodbc.Error as e:
            logger.error(f"執行查詢時發生錯誤: {e}")
            return None
            
    @staticmethod
    def execute_file_script(connection, file_path):
        """
        執行SQL檔案中的腳本
        
        Args:
            connection: 資料庫連接物件
            file_path: SQL檔案路徑
            
        Returns:
            bool: 是否成功執行
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"SQL檔案不存在: {file_path}")
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                
            cursor = connection.cursor()
            cursor.execute(sql_content)
            cursor.close()
            connection.commit()
            
            logger.info(f"已成功執行SQL檔案: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"執行SQL檔案時發生錯誤: {e}")
            return False
            
    @staticmethod
    def get_query_count(connection, query, params=None):
        """
        執行查詢並返回計數結果
        
        Args:
            connection: 資料庫連接物件
            query: SQL查詢語句，應該是一個COUNT查詢
            params: 查詢參數 (可選)
            
        Returns:
            int: 計數結果
        """
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            result = cursor.fetchone()[0]
            cursor.close()
            return result
            
        except pyodbc.Error as e:
            logger.error(f"執行計數查詢時發生錯誤: {e}")
            return 0
            
    @staticmethod
    def execute_batch_insert(connection, table_name, columns, values_list):
        """
        執行批量插入
        
        Args:
            connection: 資料庫連接物件
            table_name: 資料表名稱
            columns: 欄位名稱列表
            values_list: 值列表的列表
            
        Returns:
            bool: 是否成功執行
        """
        try:
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            
            query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            cursor = connection.cursor()
            for values in values_list:
                cursor.execute(query, values)
            
            connection.commit()
            cursor.close()
            return True
            
        except pyodbc.Error as e:
            logger.error(f"執行批量插入時發生錯誤: {e}")
            return False
