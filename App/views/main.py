from flask import Blueprint,render_template

main = Blueprint('main', __name__)


# 首页视图
@main.route('/')
@main.route('/index/')
def index():
    return render_template('main/index.html')
