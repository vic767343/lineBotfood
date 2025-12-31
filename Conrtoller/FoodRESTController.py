from flask import Blueprint, request, jsonify
import logging
import os
import sys
import json
from typing import Dict, Any, List, Optional

# 將專案根目錄加入到系統路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 導入服務
from Service.FoodDataService import FoodDataService

# 創建藍圖
food_rest_bp = Blueprint('food_rest', __name__, url_prefix='/api/v1/food')

# 延遲初始化服務 - 避免重複初始化
_food_data_service = None

def get_food_data_service():
    global _food_data_service
    if _food_data_service is None:
        _food_data_service = FoodDataService()
    return _food_data_service

# 設置日誌記錄
logger = logging.getLogger(__name__)

@food_rest_bp.route('/master', methods=['GET'])
def get_food_masters():
    """獲取食物主檔列表，支援分頁和搜尋"""
    # 獲取分頁參數
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    # 獲取搜尋參數
    user_id = request.args.get('userId', '')
    
    # 獲取主檔列表
    result = get_food_data_service().get_food_masters(page, page_size, user_id)
    
    if result:
        return jsonify({
            "status": "success",
            "data": result.get('masters', []),
            "totalCount": result.get('total', 0),
            "page": page,
            "pageSize": page_size
        })
    else:
        return {"status": "error", "message": "獲取食物主檔列表失敗"}

@food_rest_bp.route('/master/<string:master_id>', methods=['GET'])
@error_handler.api_error_handler()
def get_food_master(master_id):
    """獲取指定的食物主檔詳情"""
    # 獲取主檔詳情
    master = get_food_data_service().get_food_master_by_id(master_id)
    
    if master:
        return jsonify({"status": "success", "data": master})
    else:
        return {"status": "error", "message": "找不到指定的食物主檔"}

@food_rest_bp.route('/master', methods=['POST'])
@error_handler.api_error_handler()
def add_food_master():
    """新增食物主檔"""
    # 獲取請求數據
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['user_id'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    # 新增主檔
    master_id = get_food_data_service().add_food_master(
        data.get('master_id', ''),
        data.get('user_id')
    )
    
    if master_id:
        return jsonify({
            "status": "success",
            "message": "食物主檔新增成功",
            "data": {"id": master_id, "user_id": data.get('user_id')}
        })
    else:
        return {"status": "error", "message": "食物主檔新增失敗"}

@food_rest_bp.route('/master/<string:master_id>', methods=['PUT'])
@error_handler.api_error_handler()
def update_food_master(master_id):
    """更新食物主檔"""
    # 獲取請求數據
    data = request.json
    
    # 更新主檔
    success = get_food_data_service().update_food_master(
        master_id,
        data.get('desc_text', ''),
        data.get('total_calories', 0)
    )
    
    if success:
        return jsonify({
            "status": "success",
            "message": "食物主檔更新成功",
            "data": {"id": master_id}
        })
    else:
        return {"status": "error", "message": "食物主檔更新失敗"}

@food_rest_bp.route('/master/<string:master_id>', methods=['DELETE'])
@error_handler.api_error_handler()
def delete_food_master(master_id):
    """刪除食物主檔"""
    # 刪除主檔
    success = get_food_data_service().delete_food_master(master_id)
    
    if success:
        return jsonify({"status": "success", "message": "食物主檔刪除成功"})
    else:
        return {"status": "error", "message": "食物主檔刪除失敗"}

@food_rest_bp.route('/details', methods=['GET'])
@error_handler.api_error_handler()
def get_food_details():
    """獲取食物明細列表，支援分頁和搜尋"""
    # 獲取分頁參數
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    # 獲取搜尋參數
    master_id = request.args.get('masterId', '')
    intent = request.args.get('intent', '')
    
    # 獲取明細列表
    result = get_food_data_service().get_food_details(page, page_size, master_id, intent)
    
    if result:
        return jsonify({
            "status": "success",
            "data": result.get('data', []),
            "totalCount": result.get('totalCount', 0),
            "page": page,
            "pageSize": page_size
        })
    else:
        return {"status": "error", "message": "獲取食物明細列表失敗"}

@food_rest_bp.route('/details/<int:detail_id>', methods=['GET'])
@error_handler.api_error_handler()
def get_food_detail(detail_id):
    """獲取指定的食物明細詳情"""
    # 獲取明細詳情
    detail = get_food_data_service().get_food_detail_by_id(detail_id)
    
    if detail:
        return jsonify({"status": "success", "data": detail})
    else:
        return {"status": "error", "message": "找不到指定的食物明細"}

@food_rest_bp.route('/details', methods=['POST'])
@error_handler.api_error_handler()
def add_food_detail():
    """新增食物明細"""
    # 獲取請求數據
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['master_id'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    # 新增明細
    detail_id = get_food_data_service().add_food_detail(
        data.get('master_id'),
        data.get('intent', ''),
        data.get('desc_text', ''),
        data.get('calories', 0),
        data.get('total_calories', 0)
    )
    
    if detail_id:
        return jsonify({
            "status": "success",
            "message": "食物明細新增成功",
            "data": {"id": detail_id, "master_id": data.get('master_id')}
        })
    else:
        return {"status": "error", "message": "食物明細新增失敗"}

@food_rest_bp.route('/details/<int:detail_id>', methods=['PUT'])
@error_handler.api_error_handler()
def update_food_detail(detail_id):
    """更新食物明細"""
    # 獲取請求數據
    data = request.json
    
    # 更新明細
    success = get_food_data_service().update_food_detail(
        detail_id,
        data.get('intent', ''),
        data.get('desc_text', ''),
        data.get('calories', 0),
        data.get('total_calories', 0)
    )
    
    if success:
        return jsonify({
            "status": "success",
            "message": "食物明細更新成功",
            "data": {"id": detail_id}
        })
    else:
        return {"status": "error", "message": "食物明細更新失敗"}

@food_rest_bp.route('/details/<int:detail_id>', methods=['DELETE'])
@error_handler.api_error_handler()
def delete_food_detail(detail_id):
    """刪除食物明細"""
    # 刪除明細
    success = get_food_data_service().delete_food_detail(detail_id)
    
    if success:
        return jsonify({"status": "success", "message": "食物明細刪除成功"})
    else:
        return {"status": "error", "message": "食物明細刪除失敗"}

@food_rest_bp.route('/master/<string:master_id>/details', methods=['GET'])
@error_handler.api_error_handler()
def get_food_details_by_master(master_id):
    """根據主檔ID獲取食物明細列表"""
    # 獲取分頁參數
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    
    # 獲取明細列表
    result = get_food_data_service().get_food_details_by_master_id(master_id, page, page_size)
    
    if result:
        return jsonify({
            "status": "success",
            "data": result.get('data', []),
            "totalCount": result.get('totalCount', 0),
            "page": page,
            "pageSize": page_size
        })
    else:
        return {"status": "error", "message": "獲取食物明細列表失敗"}

@food_rest_bp.route('/details/batch-update-intent', methods=['PUT'])
@error_handler.api_error_handler()
def batch_update_detail_intent():
    """批次更新食物明細的餐點類型"""
    # 獲取請求數據
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['details', 'intent'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    details = data.get('details', [])
    intent = data.get('intent')
    
    # 批次更新餐點類型
    success_count = 0
    total_count = len(details)
    
    for detail in details:
        detail_id = detail.get('id')
        if detail_id:
            success = get_food_data_service().update_detail_intent(detail_id, intent)
            if success:
                success_count += 1
    
    if success_count == total_count:
        return jsonify({
            "status": "success",
            "message": f"成功更新 {success_count} 筆餐點類型"
        })
    elif success_count > 0:
        return jsonify({
            "status": "partial_success",
            "message": f"部分成功: 更新了 {success_count}/{total_count} 筆餐點類型"
        })
    else:
        return {"status": "error", "message": "所有餐點類型更新失敗"}

@food_rest_bp.route('/details/batch-update-intent-by-type', methods=['PUT'])
@error_handler.api_error_handler()
def batch_update_intent_by_type():
    """根據原始餐點類型批次更新食物明細的餐點類型"""
    # 獲取請求數據
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['original_intent', 'new_intent'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    original_intent = data.get('original_intent')
    new_intent = data.get('new_intent')
    
    # 執行批次更新
    updated_count = get_food_data_service().batch_update_intent(original_intent, new_intent)
    
    if updated_count is not None:
        return jsonify({
            "status": "success",
            "message": f"成功批次更新 {updated_count} 筆記錄",
            "updated_count": updated_count
        })
    else:
        return {"status": "error", "message": "批次更新失敗"}

@food_rest_bp.route('/details/user-batch-update-intent', methods=['PUT'])
@error_handler.api_error_handler()
def user_batch_update_detail_intent():
    """使用者批次更新食物明細的餐點類型"""
    # 獲取請求數據
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['user_id', 'intent'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    user_id = data.get('user_id')
    intent = data.get('intent')
    
    # 批次更新餐點類型
    success = get_food_data_service().batch_update_user_intent(user_id, intent)
    
    if success:
        return jsonify({"status": "success", "message": "使用者餐點類型批次更新成功"})
    else:
        return {"status": "error", "message": "使用者餐點類型批次更新失敗"}

@food_rest_bp.route('/details/<int:detail_id>/intent', methods=['PUT'])
@error_handler.api_error_handler()
def update_detail_intent(detail_id):
    """修改指定明細的餐點類型"""
    # 獲取請求數據
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data, ['intent'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    # 執行修改餐點類型
    success = get_food_data_service().update_detail_intent(detail_id, data.get('intent'))
    
    if success:
        return jsonify({"status": "success", "message": "餐點類型修改成功"})
    else:
        return {"status": "error", "message": "餐點類型修改失敗"}

@food_rest_bp.route('/master/<string:master_id>/update-total-calories', methods=['PUT'])
@error_handler.api_error_handler()
def update_master_total_calories(master_id):
    """更新指定主檔下所有明細的總卡路里"""
    # 更新總卡路里
    success = get_food_data_service().update_master_total_calories(master_id)
    
    if success:
        return jsonify({"status": "success", "message": "總卡路里更新成功"})
    else:
        return {"status": "error", "message": "總卡路里更新失敗"}

# 食物分析相關端點

@food_rest_bp.route('/analysis', methods=['POST'])
@error_handler.api_error_handler()
def add_food_analysis():
    """新增食物分析"""
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['master_id', 'user_id', 'analysis_data'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    success = get_food_data_service().add_food_analysis(
        data.get('master_id'),
        data.get('user_id'),
        data.get('analysis_data')
    )
    
    if success:
        return jsonify({"status": "success", "message": "食物分析新增成功"})
    else:
        return {"status": "error", "message": "食物分析新增失敗"}

@food_rest_bp.route('/analysis/<string:master_id>', methods=['GET'])
@error_handler.api_error_handler()
def get_food_analysis(master_id):
    """獲取指定的食物分析"""
    analysis = get_food_data_service().get_food_analysis_by_id(master_id)
    
    if analysis:
        return jsonify({"status": "success", "data": analysis})
    else:
        return {"status": "error", "message": "找不到指定的食物分析"}

@food_rest_bp.route('/analysis/user/<string:user_id>', methods=['GET'])
@error_handler.api_error_handler()
def get_user_food_analyses(user_id):
    """獲取用戶的食物分析列表"""
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    analyses = get_food_data_service().get_food_analyses_by_user_id(user_id, limit, offset)
    
    return jsonify({
        "status": "success",
        "data": analyses,
        "count": len(analyses)
    })

@food_rest_bp.route('/analysis/<string:master_id>', methods=['PUT'])
@error_handler.api_error_handler()
def update_food_analysis(master_id):
    """更新食物分析"""
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['analysis_data'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    success = get_food_data_service().update_food_analysis(master_id, data.get('analysis_data'))
    
    if success:
        return jsonify({"status": "success", "message": "食物分析更新成功"})
    else:
        return {"status": "error", "message": "食物分析更新失敗"}

@food_rest_bp.route('/analysis/<string:master_id>', methods=['DELETE'])
@error_handler.api_error_handler()
def delete_food_analysis(master_id):
    """刪除食物分析"""
    success = get_food_data_service().delete_food_analysis(master_id)
    
    if success:
        return jsonify({"status": "success", "message": "食物分析刪除成功"})
    else:
        return {"status": "error", "message": "食物分析刪除失敗"}

@food_rest_bp.route('/analysis/bulk', methods=['POST'])
@error_handler.api_error_handler()
def bulk_insert_analyses():
    """批量插入食物分析"""
    data = request.json
    
    # 快速驗證
    validation_error = error_handler.validate_input_fast(data or {}, ['analyses_data'])
    if validation_error:
        return {"status": "error", "message": validation_error}
    
    success_count, total_count = get_food_data_service().bulk_insert_food_analyses(data.get('analyses_data'))
    
    return jsonify({
        "status": "success" if success_count == total_count else "partial_success",
        "message": f"成功插入 {success_count}/{total_count} 筆分析數據",
        "success_count": success_count,
        "total_count": total_count
    })

# 統計相關端點

@food_rest_bp.route('/stats/calories/user/<string:user_id>', methods=['GET'])
@error_handler.api_error_handler()
def get_user_daily_calories(user_id):
    """獲取用戶指定日期的總卡路里"""
    date_str = request.args.get('date')
    
    if date_str:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {"status": "error", "message": "日期格式錯誤，請使用 YYYY-MM-DD 格式"}
    else:
        date_obj = None
    
    total_calories = get_food_data_service().get_total_calories_by_date(user_id, date_obj)
    
    return jsonify({
        "status": "success",
        "data": {
            "user_id": user_id,
            "date": date_str if date_str else "today",
            "total_calories": total_calories
        }
    })

@food_rest_bp.route('/stats/counts', methods=['GET'])
@error_handler.api_error_handler()
def get_food_counts():
    """獲取食物數據統計"""
    master_count = get_food_data_service().get_food_master_count()
    details_count = get_food_data_service().get_food_details_count()
    
    return jsonify({
        "status": "success",
        "data": {
            "master_count": master_count,
            "details_count": details_count
        }
    })

@food_rest_bp.route('/stats/user/<string:user_id>/count', methods=['GET'])
@error_handler.api_error_handler()
def get_user_food_count(user_id):
    """獲取用戶的食物記錄數量"""
    count = get_food_data_service().get_user_food_count(user_id)
    
    return jsonify({
        "status": "success",
        "data": {
            "user_id": user_id,
            "food_count": count
        }
    })

@food_rest_bp.route('/stats/intents/common', methods=['GET'])
@error_handler.api_error_handler()
def get_common_intents():
    """獲取最常見的餐點類型"""
    limit = int(request.args.get('limit', 5))
    
    intents = get_food_data_service().get_most_common_intents(limit)
    
    return jsonify({
        "status": "success",
        "data": [{"intent": intent, "count": count} for intent, count in intents]
    })

@food_rest_bp.route('/records/user/<string:user_id>/past-7-days', methods=['GET'])
@error_handler.api_error_handler()
def get_user_past_7_days_records(user_id):
    """獲取用戶過去7天的食物記錄"""
    records = get_food_data_service().get_past_7_days_food_records(user_id)
    
    return jsonify({
        "status": "success",
        "data": records,
        "count": len(records)
    })

# 系統監控端點

@food_rest_bp.route('/system/performance', methods=['GET'])
@error_handler.api_error_handler()
def get_performance_stats():
    """獲取系統性能統計"""
    stats = get_food_data_service().get_performance_stats()
    
    return jsonify({
        "status": "success",
        "data": stats
    })

@food_rest_bp.route('/system/health', methods=['GET'])
@error_handler.api_error_handler()
def health_check():
    """系統健康檢查"""
    health_status = get_food_data_service().health_check()
    
    status_code = "success" if health_status.get('status') == 'healthy' else "error"
    
    return jsonify({
        "status": status_code,
        "data": health_status
    })