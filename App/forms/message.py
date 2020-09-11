from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


# 评论回复表单
class Review(FlaskForm):
    name = StringField('评论用户', render_kw={'readonly': 'true'})  # 只读
    judge = BooleanField()  # 是否是当前用户
    content = TextAreaField('评论内容', validators=[DataRequired('评论必填')], render_kw={'placeholder': '评论不得超过不得超过80字'})
