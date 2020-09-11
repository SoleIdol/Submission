from flask import Blueprint, render_template, flash, request, current_app
from flask_uploads import DOCUMENTS
from flask_login import current_user, login_required
from App.forms import UserInfo, Upload, UploadFiles  # 导入个人信息显示模型类、头像类及文件上传表单类
from App.extensions import file, db, uploadFiles
import os
from PIL import Image
import time
from App.models import UserFiles, User, Message

owncenter = Blueprint('owncenter', __name__)


# 查看与修改个人信息
@owncenter.route('/user_info/', methods=['GET', 'POST'])
@login_required
def user_info():
    if current_user.status == '作者':  # 当前用户是作者，才会渲染下面的模板，否则渲染nocan.html
        form = UserInfo()
        if form.validate_on_submit():
            # 更改聊天记录中的信息
            for m in Message.query.filter(Message.uid == current_user.id, Message.expert == False):
                m.name = form.username.data

            # 更改稿件中的信息
            for f in UserFiles.query.filter(UserFiles.uid == current_user.id):
                f.username = form.username.data

            # 更改用户信息
            current_user.username = form.username.data
            current_user.age = form.age.data
            current_user.sex = form.sex.data
            if current_user.save():
                flash('修改成功')
            else:
                flash('修改失败')
        # 表单设置默认值
        form.username.data = current_user.username
        form.age.data = current_user.age
        form.sex.data = current_user.sex
        form.email.data = current_user.email
        form.lastLogin.data = current_user.lastLogin
        form.register.data = current_user.registerTime
        return render_template('owncenter/user_info.html', form=form)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 修改密码
@owncenter.route('/alterPasswd/', methods=['POST', 'GET'])
@login_required
def alterPasswd():
    if current_user.status == '作者':
        if request.method == 'POST':
            flag = True
            # 找到当前用户
            u = User.query.filter(User.username == current_user.username).first()

            oldpass = request.form.get('oldpass')
            newpass1 = request.form.get('newpass1')
            newpass2 = request.form.get('newpass2')

            if not u.check_password(oldpass):
                flag = False
                flash('您输入的原始密码不正确，请重新输入...')
            if newpass1 == newpass2:
                if len(newpass1) < 6 or len(newpass1) > 12:
                    flag = False
                    flash('密码长度在6~12之间...')
            else:
                flag = False
                flash('新密码两次输入的不一致,请重新输入...')
            if flag:
                print('输入合法')
                # 输入合法 密文存储
                u.password = newpass1
                print(u.save())
                if u.save():
                    flash('密码修改成功...')

        return render_template('owncenter/alterPasswd.html')
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 使用uuid扩展库生成唯一的名称
def random_filename(suffix):
    import uuid
    u = uuid.uuid4()
    return str(u) + '.' + suffix


# 图片缩放处理
def img_zoom(path, prefix='s_', width=100, height=100):
    # 打开文件
    img = Image.open(path)
    # 重新设计尺寸
    img.thumbnail((width, height))
    # 拆分传递进来的图片的路径 拆分进行前缀的拼接  /a/b.jpg  /a/s_b.jpg
    pathSplit = os.path.split(path)
    # 拼接好前缀 进行重新拼接成一个新的path
    path = os.path.join(pathSplit[0], prefix + pathSplit[1])
    # 保存缩放后的图片 保留原图片
    # 保存缩放
    img.save(path)


# 头像上传
@owncenter.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.status == '作者':
        form = Upload()
        if form.validate_on_submit():
            icon = request.files.get('icon')  # 获取上传对象
            suffix = icon.filename.split('.')[-1]  # 获取后缀
            newName = random_filename(suffix)  # 获取新的图片名称
            # 保存图片 以新名称
            file.save(icon, name=newName)
            delPath = current_app.config['UPLOADED_PHOTOS_DEST']
            # 删除之前上传过的图片
            if current_user.icon != 'default.jpg':  # 如果不等于 证明之前有上传过头像 否则就是没有上传过新头像
                os.remove(os.path.join(delPath, current_user.icon))
                os.remove(os.path.join(delPath, 'm_' + current_user.icon))
                os.remove(os.path.join(delPath, 's_' + current_user.icon))
            current_user.icon = newName  # 更改当前对象的图片名称
            db.session.add(current_user)  # 更新到数据库中
            db.session.commit()
            # 拼接图片路径
            path = os.path.join(delPath, newName)
            # 进行头像的多次缩放
            img_zoom(path)
            img_zoom(path, 'm_', 200, 200)
        return render_template('owncenter/upload.html', form=form)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 稿件上传
@owncenter.route('/uploadFiles/', methods=['GET', 'POST'])
@login_required
def upload_files():
    if current_user.status == '作者':
        form = UploadFiles()
        form.username = current_user.username
        user_file = UserFiles()
        if request.method == 'POST' and request.files.get('file') and form.validate_on_submit():
            file = request.files.get('file')  # 获取上传对象
            suffix = file.filename.split('.')[-1]  # 获取后缀
            if suffix not in DOCUMENTS:
                flash('文件格式不准许')
            else:
                user_file.fileOldName = file.filename  # 原文件名
                # 判断新文件名是否唯一
                while True:
                    user_file.fileNewName = random_filename(suffix)  # 获取新文件名
                    file_url = os.path.join(current_app.config['UPLOADED_FILES_DEST'], user_file.fileNewName)
                    if not os.path.exists(file_url):
                        break

                # 保存稿件 以新名称
                uploadFiles.save(file, name=user_file.fileNewName)

                user_file.fileTitle = form.fileTitle.data  # 稿件标题
                user_file.keywords = form.keywords.data  # 稿件关键字
                user_file.digest = form.digest.data  # 稿件摘要
                user_file.fileSize = round(os.path.getsize(file_url) / 1024 / 1024, 2)  # 文件大小 单位：M
                user_file.username = current_user.username  # 稿件所属用户的名字
                user_file.uid = current_user.id  # 稿件所属用户的id
                user_file.uploadTime = time.strftime("%Y-%m-%d %H:%M:%S")  # 上传时间
                user_file.save()  # 保存数据库
                flash('文件上传成功')
        return render_template('owncenter/uploadFile.html', form=form)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 已投稿件的查询
@owncenter.route('/showFiles/', methods=['GET', 'POST'])
@login_required
def showFiles():
    if current_user.status == '作者':
        page = int(request.args.get('page', 1))  # 当前页数，request.args.get()方法获取页面的参数，如果没有获取到页码就默认为1
        per_page = 10  # 每页数量
        paginate = UserFiles.query.filter(UserFiles.username == current_user.username).paginate(page, per_page,
                                                                                                error_out=False)  # 创建分页器对象
        return render_template('owncenter/showFiles.html', paginate=paginate, pages=paginate.pages + 1)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 已审稿件的查询
@owncenter.route('/showPass/', methods=['GET', 'POST'])
@login_required
def showPass():
    if current_user.status == '作者':
        page = int(request.args.get('page', 1))  # 当前页数，request.args.get()方法获取页面的参数，如果没有获取到页码就默认为1
        per_page = 10  # 每页数量
        paginate = UserFiles.query.filter(
            UserFiles.username == current_user.username, UserFiles.state == '已审阅').paginate(page, per_page,
                                                                                            error_out=False)  # 创建分页器对象
        return render_template('owncenter/showPass.html', paginate=paginate, pages=paginate.pages + 1)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 稿件删除
@owncenter.route('/delFile/', methods=['GET', 'POST'])
@login_required
def delFile():
    if current_user.status == '作者':
        f = UserFiles.query.filter(UserFiles.id == request.form.get('id')).first()
        for ms in Message.query.filter(Message.fid == request.form.get('id')):
            ms.my_del()
        if f.my_del():
            delFilePath = current_app.config['UPLOADED_FILES_DEST']
            os.remove(os.path.join(delFilePath, request.form.get('newname')))
            return '删除成功'
        else:
            return '删除失败'
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 审阅反馈
@owncenter.route('/message/<uid>_<fid>_<eid>', methods=['GET', 'POST'])
@login_required
def message(uid, fid, eid):
    if current_user.id == int(uid):
        # 判断对方是否存在
        if not User.query.filter(User.id == int(eid)).first():
            return render_template('common/nonentity.html')
        else:
            m = Message()
            ums = Message.query.filter(
                Message.uid == int(uid), Message.fid == int(fid), Message.eid == int(eid)).order_by(
                Message.timestamp)

            # 页面最多显示信息条数
            num = 30
            # off 偏移量 跳过这么多数据再去查询
            off = len(ums.all()) - num
            if off > 0:
                showums = ums.offset(off)
            else:
                showums = ums.offset(0)

            content = request.form.get('text')
            eicon = User.query.filter(User.id == int(eid)).first().icon
            uicon = User.query.filter(User.id == int(uid)).first().icon

            if request.method == 'POST' and content:
                m.fid = int(fid)
                m.uid = int(uid)
                m.eid = int(eid)
                m.name = current_user.username  # 发消息的人
                m.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # 发送时间
                f = UserFiles.query.filter(UserFiles.id == int(fid)).first()
                m.title = f.fileTitle
                m.content = content  # 消息内容
                m.expert = False  # 不是专家发言
                m.save()
            return render_template('owncenter/message.html', ums=showums, eicon=eicon, uicon=uicon)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 消息记录
@owncenter.route('/message_old/<uid>_<fid>_<eid>', methods=['GET', 'POST'])
@login_required
def message_old(uid, fid, eid):
    if current_user.id == int(uid):
        m = Message()
        ums = Message.query.filter(Message.uid == uid, Message.fid == fid, Message.eid == eid).order_by(
            Message.timestamp)
        content = request.form.get('text')
        eicon = User.query.filter(User.id == int(eid)).first().icon
        uicon = User.query.filter(User.id == int(uid)).first().icon
        if request.method == 'POST' and content:
            m.fid = int(fid)
            m.uid = int(uid)
            m.eid = int(eid)
            m.name = current_user.username  # 发消息的人
            m.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # 发送时间
            f = UserFiles.query.filter(UserFiles.id == int(fid)).first()
            m.title = f.fileTitle
            m.content = content  # 消息内容
            m.expert = False  # 不是专家发言
            m.save()
            print('用户消息是否发送、保存成功:', m.save())
        return render_template('owncenter/message_old.html', ums=ums, eicon=eicon, uicon=uicon)
    else:
        return render_template('common/nocan.html', u=current_user.username)
