# ==========================================================
# 資料庫配置檔案
# 專門用於存放資料庫連接配置，避免循環導入問題
# ==========================================================

import os

# SQL Server 資料庫連接配置
db_config = {
    'serverName': 'localhost',
    'databaseName': 'Food',
    'userName': 'sa',
    'password': os.getenv('PASSWORD'),  # Use environment variable
    'driver': 'ODBC Driver 18 for SQL Server'
}
