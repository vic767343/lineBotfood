# Conrtoller/__init__.py

# 匯入藍圖
from Conrtoller.LineWebHookRESTController import line_webhook_bp
from Conrtoller.FoodController import food_bp
from Conrtoller.FoodRESTController import food_rest_bp
from Service.PerformanceAPI import performance_bp
from Conrtoller.HomeController import home_blueprint

# 註冊路由的函數
def register_routes(app):
    """註冊所有控制器的路由到Flask應用程式"""
    app.register_blueprint(home_blueprint)  # 註冊首頁控制器
    app.register_blueprint(line_webhook_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(food_rest_bp)
    app.register_blueprint(performance_bp)  # 新增性能監控API
