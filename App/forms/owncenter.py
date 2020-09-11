from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from flask_wtf.file import FileAllowed, FileRequired, FileField
from App.extensions import file  # 导入文件上传配置对象


# 修改与查看个人信息的表单类
from App.models import User


class UserInfo(FlaskForm):
    username = StringField('用户名')
    sex = RadioField(label='性别', choices=[('男', '男'), ('女', '女'),('保密','保密')], validators=[DataRequired('性别必选')])
    age = IntegerField('年龄', validators=[DataRequired('年龄不能为空'), NumberRange(min=1, max=99, message='年龄在1~99之间')])
    email = StringField('邮箱', render_kw={'readonly': 'true'})
    lastLogin = StringField('上次登录时间', render_kw={'disabled': 'true'})
    register = StringField('注册时间', render_kw={'disabled': 'true'})
    submit = SubmitField('修改')

    # 验证用户名是否存在
    def validate_username(self, field):
        if current_user.username != field.data:  # if 登录时的用户名不等于输入的用户名
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('修改的用户名已存在，请重新输入，已为你切换为原始用户名...')


# 文件上传类
class Upload(FlaskForm):
    icon = FileField('头像上传', validators=[FileRequired('您还没有选择上传的头像'), FileAllowed(file, message='该文件类型不允许上传')])
    submit = SubmitField('上传')

