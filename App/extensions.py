from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy  # ORM模型扩展库
from flask_migrate import Migrate
from flask_login import LoginManager  # 处理用户登录的第三方扩展库
from flask_moment import Moment  # 格式化时间显示的扩展库
# 导入文件上传扩展库
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class, DOCUMENTS, ARCHIVES

# 实例化
bootstrap = Bootstrap()  # bootstrap扩展库
db = SQLAlchemy()  # ORM模型扩展库
migrate = Migrate()  # 模型迁移
login_manger = LoginManager()  # 处理登陆的第三方扩展库
moment = Moment()  # 实例化格式化时间显示的扩展库
file = UploadSet('photos', IMAGES)  # 头像文件限制
uploadFiles = UploadSet('files', DOCUMENTS)  # 上传稿件类型限制


# 加载app
def init_app(app):
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app=app, db=db)

    login_manger.init_app(app)
    login_manger.login_view = 'main.index'  # 当你没有登录访问了需要登录的路由的时候 进行登录的端点
    login_manger.login_message = '您还没有登录 请登陆后在访问'  # 提示信息
    login_manger.session_protection = 'strong'  # 设置session的保护级别 强

    # 配置文件上传
    configure_uploads(app, file)
    configure_uploads(app, uploadFiles)
    patch_request_class(app, size=None)
