from flask import Blueprint, request, jsonify, render_template
import logging
import os
import sys

# 將專案根目錄加入到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Service.OptimizedErrorHandler import OptimizedErrorHandler

# 創建藍圖
food_bp = Blueprint('food', __name__, url_prefix='/food')

# 初始化錯誤處理器
error_handler = OptimizedErrorHandler(__name__)

# 設置日誌記錄
logger = logging.getLogger(__name__)

@food_bp.route('/', methods=['GET'])
@error_handler.fast_error_handler("無法訪問食物管理頁面")
def food_page():
    """返回食物管理頁面"""
    logger.info("訪問食物管理頁面")
    return render_template('food.html')
