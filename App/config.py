import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# 配置类基类
class Config():
    SECRET_KEY = 'SUI&bian^zi#fu%chuan'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不追踪数据
    BOOTSTRAP_SERVE_LOCAL = True   # 加载本地静态资源文件
    # 头像上传配置
    UPLOADED_PHOTOS_DEST = os.path.join(BASE_DIR, 'static/upload/icon')
    # 稿件上传配置
    UPLOADED_FILES_DEST = os.path.join(BASE_DIR, 'static/upload/files')
    MAX_CONTENT_LENGTH = 1024 * 1024 * 64


# 开发环境
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://idol:123456@123.56.82.187:3306/contribute_dev'
    DEBUG = True
    TESTING = False


# 测试环境
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://idol:123456@123.56.82.187:3306/contribute_test'
    DEBUG = False
    TESTING = True


# 生产环境
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://idol:123456@123.56.82.187:3306/contribute'
    DEBUG = False
    TESTING = False


# 配置类字典 简化
configDict = {
    'default': DevelopmentConfig,
    'dev': DevelopmentConfig,
    'Test': TestingConfig,
    'production': ProductionConfig
}
