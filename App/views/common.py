from flask import Blueprint, request, current_app, render_template
from flask_login import login_required, current_user
import os
from App.models import UserFiles, User, Message

common = Blueprint('common', __name__)


# 注销用户
@common.route('/deluser/', methods=['GET', 'POST'])
@login_required
def deluser():
    if current_user.status == '管理员':
        if not current_user.permissions & 1:
            return '你没有注销其他用户权限'
    u = User.query.filter(User.id == request.form.get('id')).first()
    files = UserFiles.query.filter(UserFiles.uid == u.id)
    for f in files:
        # 删除用户文件的聊天记录
        for ms in Message.query.filter(Message.fid == f.id):
            ms.my_del()
        # 删除用户稿件
        if f.my_del():
            delFilePath = current_app.config['UPLOADED_FILES_DEST']
            os.remove(os.path.join(delFilePath, f.fileNewName))
    deliconPath = current_app.config['UPLOADED_PHOTOS_DEST']
    # 删除之前上传过的图片
    if u.icon != 'default.jpg':  # 如果不等于 证明之前有上传过头像 否则就是没有上传过新头像
        os.remove(os.path.join(deliconPath, u.icon))
        os.remove(os.path.join(deliconPath, 'm_' + u.icon))
        os.remove(os.path.join(deliconPath, 's_' + u.icon))
    if u.my_del():
        return '注销成功'
    else:
        return '注销失败'


# 合作伙伴
@common.route('/a-hzhb/', methods=['GET', 'POST'])
@login_required
def hzhb():
    return render_template('common/a-hzhb.html')


# 常见问题
@common.route('/a-cjwt/', methods=['GET', 'POST'])
@login_required
def cjwt():
    return render_template('common/a-cjwt.html')


# 使用教程-用户
@common.route('/a-syjc1/', methods=['GET', 'POST'])
@login_required
def syjc1():
    return render_template('common/a-syjc1.html')


# 使用教程-专家
@common.route('/a-syjc2/', methods=['GET', 'POST'])
@login_required
def syjc2():
    return render_template('common/a-syjc2.html')
