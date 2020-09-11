from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from App.models import User  # 导入User模型类


# 注册表单类
class Register(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('用户名不能为空'), Length(
        min=3, max=12, message='用户名在3~12位之间')], render_kw={'placeholder': '请输入用户名'})
    userpass = PasswordField('密码', validators=[DataRequired('密码不能为空'), Length(
        min=6, max=12, message='密码在6~12位之间')], render_kw={'placeholder': '请输入密码'})
    confirm = PasswordField('确认密码', validators=[DataRequired('确认密码不能为空'), EqualTo(
        'userpass', message='两次输入的密码不一致')], render_kw={'placeholder': '请再次输入密码'})
    email = StringField('邮箱', validators=[DataRequired('邮箱不能为空'), Email(
        message='请输入有效的邮箱地址')], render_kw={'placeholder': '请输入绑定用户的邮箱'})
    submit = SubmitField('注册')

    # 验证用户名是否存在
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已存在,请重新输入...')

    # 验证邮箱是否存在
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已存在,请重新输入...')


# 登录表单类
class Login(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('用户名不能为空'), Length(min=3, max=12, message='用户名在3~12位之间')],
                           render_kw={'placeholder': '请输入用户名...'})
    userpass = PasswordField('密码', validators=[DataRequired('密码不能为空...'), Length(min=6, max=12, message='密码在6~12位之间')],
                             render_kw={'placeholder': '请输入密码...'})
    remember = BooleanField('记住我', default='checked')
    submit = SubmitField('登录')

    # 验证用户名是否存在
    def validate_username(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError('请输入正确的用户名或密码')
