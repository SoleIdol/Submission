from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class UploadFiles(FlaskForm):
    username = StringField('用户名', render_kw={'readonly': 'true'})  # 只读
    fileTitle = TextAreaField('标题', validators=[DataRequired('标题必填')], render_kw={'placeholder': '标题不得超过30字'})
    keywords = TextAreaField('关键字', validators=[DataRequired('关键字必填')], render_kw={'placeholder': '关键字不得超过30字'})
    digest = TextAreaField('稿件摘要', validators=[DataRequired('摘要必填')], render_kw={'placeholder': '摘要不得超过80字'})
