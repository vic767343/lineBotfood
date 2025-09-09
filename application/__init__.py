from flask import Flask, jsonify
from pathlib import Path
import logging
import sys
import os

# 將專案根目錄加入到系統路徑

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 創建 Flask 應用程式實例
app = Flask(__name__,
           static_folder=str(Path(__file__).parent.parent / 'static'),
           template_folder=str(Path(__file__).parent.parent / 'templates'))      # 設定 static 與 templates 資料夾路徑

# 初始化預熱服務
try:
    from Service.PrewarmService import initialize_prewarm
    initialize_prewarm()
    logging.info("預熱服務已啟動")
except Exception as e:
    logging.warning(f"預熱服務啟動失敗: {str(e)}")

# 設定根目錄路由重定向至API
# @app.route('/')
# def api_info():
#     return jsonify({
#         "status": "success",
#         "message": "請使用 /api/v1/ 端點訪問API服務"
#     })

# 初始化路由設定
from Conrtoller import register_routes
register_routes(app)


