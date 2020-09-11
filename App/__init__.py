from flask import Flask
from App.views import register_blueprint  # 导入views注册蓝本对象的方法
from .config import configDict  # 导入配置类字典
from .extensions import init_app


# 加载整个App项目 并返回App对象
def create_app(configName='production'):
    app = Flask(__name__)
    # 加载配置类
    app.config.from_object(configDict[configName])
    # 注册蓝本
    register_blueprint(app)
    # 初始化扩展库
    init_app(app)
    return app
