from flask import Blueprint, render_template

home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/')
def home():
    """
    首頁路由處理函數
    
    Returns:
        render_template: 渲染首頁模板
    """
    return render_template('home.html')
