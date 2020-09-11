from App.extensions import db, login_manger  # 导入模型对象
from .db_base import DB_base
from datetime import datetime
# 导入生成与验证密码的方法
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  # 包含登陆者信息


# User 模型类
class User(UserMixin, db.Model, DB_base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 自增id
    username = db.Column(db.String(12), index=True, unique=True)  # 用户名
    password_hash = db.Column(db.String(128))  # 密码 密文
    sex = db.Column(db.Enum('男', '女', '保密'), default='男')  # 性别
    status = db.Column(db.Enum('作者', '专家', '管理员'), default='作者')  # 身份
    age = db.Column(db.Integer, default=18)  # 年龄  默认18
    email = db.Column(db.String(50), unique=True)  # 邮箱
    icon = db.Column(db.String(70), default='default.jpg')  # 头像  默认为default.jpg
    lastLogin = db.Column(db.DateTime)  # 上次登录时间
    registerTime = db.Column(db.DateTime)  # 注册时间
    confirm = db.Column(db.Boolean, default=False)  # 激活状态  默认未激活 (需要发送邮箱进行激活)
    leaderId = db.Column(db.Integer, default=0)  # 幕后老大-->通过哪个id注册的管理员
    permissions = db.Column(db.Integer, default=0)  # 管理员权限

    # 权限级别:
    # 1:是否可以删除用户
    # 2:是否可以删除稿件
    # 4:是否可以注册普通用户(无权限的用户)
    # 8:是否可以注册超级用户(可以设置权限)
    # 16:暂定


    # 密码加密处理装饰器
    @property
    def password(self):
        raise ArithmeticError

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 检验密码正确性的方法
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 这是一个回调方法  实时获取当前表中用户数据的对象
@login_manger.user_loader
def user_loader(userid):
    return User.query.get(int(userid))


# 上传文件的 模型类
class UserFiles(db.Model, DB_base):
    __tablename__ = 'user_files'
    id = db.Column(db.Integer, primary_key=True)  # 自增id
    username = db.Column(db.String(12), index=True)  # 作者用户名
    ename = db.Column(db.String(12), index=True)  # 专家用户名
    uid = db.Column(db.Integer)  # 作者id
    eid = db.Column(db.Integer)  # 审稿者id
    fileOldName = db.Column(db.String(128))  # 上传的旧文件名
    fileNewName = db.Column(db.String(128))  # 上传的新文件名
    fileTitle = db.Column(db.String(128))  # 上传稿件标题
    keywords = db.Column(db.String(128))  # 上传稿件关键字
    digest = db.Column(db.String(256))  # 上传稿件摘要
    fileSize = db.Column(db.Float)  # 上传文件大小
    state = db.Column(db.Enum('未审阅', '审阅中', '已审阅'), default='未审阅')  # 稿件审阅状态
    uploadTime = db.Column(db.DateTime, default=None)  # 稿件上传时间
    referTime = db.Column(db.DateTime, default=None)  # 稿件审阅时间
    count = db.Column(db.Integer,default=0)  # 下载次数


# 审阅反馈的模型类
class Message(DB_base, db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.Integer)  # 文件id
    uid = db.Column(db.Integer)  # 作者id
    eid = db.Column(db.Integer)  # 审稿者id
    name = db.Column(db.String(12), index=True)  # 评论者用户名
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # 发送消息的时间
    state = db.Column(db.Enum('未回复', '已回复', '收到'), default='未回复')  # 消息回复状态
    title = db.Column(db.String(20), index=True)  # 稿件标题
    content = db.Column(db.String(256))  # 回复的内容
    expert = db.Column(db.Boolean, default=False)  # 是否为专家发言
