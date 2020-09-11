from App.extensions import db


# 自定义提交回滚类
class DB_base():
    # 添加一条数据
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            # print(e)  # 显示错误信息
            return False

    # 添加多条数据
    @staticmethod
    def save_all(*args):
        try:
            db.session.add_all(args)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False

    # 删除
    def my_del(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False
