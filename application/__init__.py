from flask import Flask
from pathlib import Path

# 將專案根目錄加入到系統路徑

# 創建 Flask 應用程式實例
app = Flask(__name__,
           static_folder=str(Path(__file__).parent.parent / 'static'),
           template_folder=str(Path(__file__).parent.parent / 'templates'))      # 設定 static 與 templates 資料夾路徑


# 設定根目錄路由重定向至API
# @app.route('/')
# def api_info():
#     return jsonify({
#         "status": "success",
#         "message": "請使用 /api/v1/ 端點訪問API服務"
#     })


