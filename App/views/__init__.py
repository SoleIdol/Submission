from .main import main  # 导入main蓝本对象
from .user import user  # 导入user蓝本对象
from .owncenter import owncenter  # 导入个人中心的蓝本对象
from .expert import expert
from .expertcenter import expertcenter
from .admin import admin
from .admincenter import admincenter
from .common import common


# 循环迭代的蓝本配置
blueprint_config = [
    (main, ''),
    (user, ''),
    (owncenter, ''),
    (expert, ''),
    (expertcenter, ''),
    (admin, ''),
    (admincenter, ''),
    (common, '')
]


# 注册蓝本对象的函数
def register_blueprint(app):
    # 循环迭代注册蓝本
    for blueprint, perfix in blueprint_config:
        app.register_blueprint(blueprint, url_perfix=perfix)
