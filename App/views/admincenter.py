from flask import Blueprint, render_template, flash, request, current_app
from App.forms import UserInfo  # 导入个人信息显示模型类
from flask_login import current_user, login_required
from App.forms import Upload  # 导入头像及文件上传表单类
from App.extensions import file, db
import os
from PIL import Image
from App.models import UserFiles, User, Message

admincenter = Blueprint('admincenter', __name__)


# 查看与修改个人信息
@admincenter.route('/admin_info/', methods=['GET', 'POST'])
@login_required
def admin_info():
    if current_user.status == '管理员':  # 当前用户是管理员，才会渲染下面的模板，否则渲染nocan.html
        form = UserInfo()
        if form.validate_on_submit():
            if current_user.username != 'root':
                current_user.username = form.username.data
            current_user.age = form.age.data
            current_user.sex = form.sex.data
            if current_user.save():
                flash('root用户名不会修改，其他信息修改成功')
            else:
                flash('修改失败')
        # 表单设置默认值
        form.username.data = current_user.username
        form.age.data = current_user.age
        form.sex.data = current_user.sex
        form.email.data = current_user.email
        form.lastLogin.data = current_user.lastLogin
        form.register.data = current_user.registerTime
        return render_template('admincenter/admin_info.html', form=form)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 我的权限
@admincenter.route('/admin_per/', methods=['GET', 'POST'])
@login_required
def admin_per():
    if current_user.status == '管理员':
        pe1 = current_user.permissions & 1
        pe2 = current_user.permissions & 2
        pe4 = current_user.permissions & 4
        pe8 = current_user.permissions & 8
        pers = [pe1, pe2, pe4, pe8]  # 权限
        return render_template('admincenter/pershow.html', pers=pers)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 修改密码
@admincenter.route('/alterPasswd_ad/', methods=['POST', 'GET'])
@login_required
def alterPasswd():
    if current_user.status == '管理员':  # 当前用户是管理员，才会渲染下面的模板，否则渲染nocan.html
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
                # 输入合法 密文存储
                u.password = newpass1
                if u.save():
                    flash('密码修改成功...')
        return render_template('admincenter/alterPasswd.html')
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
    # 拆分传递进来的图片的路径 拆分进行前缀的拼接
    pathSplit = os.path.split(path)
    # 拼接好前缀 进行重新拼接成一个新的path
    path = os.path.join(pathSplit[0], prefix + pathSplit[1])
    # 保存缩放后的图片 保留原图片
    # 保存缩放
    img.save(path)


# 头像上传
@admincenter.route('/upload_ad/', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.status == '管理员':
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
        return render_template('admincenter/upload.html', form=form)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 未审稿件的查询
@admincenter.route('/showFiles_ad/', methods=['GET', 'POST'])
@login_required
def showFiles():
    if current_user.status == '管理员':

        page = int(request.args.get('page', 1))  # 当前页数，request.args.get()方法获取页面的参数，如果没有获取到页码就默认为1
        per_page = 10  # 每页数量
        paginate = UserFiles.query.filter(UserFiles.state != '已审阅').paginate(page, per_page, error_out=False)  # 创建分页器对象
        return render_template('admincenter/showFiles.html', paginate=paginate, pages=paginate.pages + 1)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 所有稿件的查询
@admincenter.route('/allFiles_ad/', methods=['GET', 'POST'])
@login_required
def allFiles():
    if current_user.status == '管理员':
        page = int(request.args.get('page', 1))  # 当前页数，request.args.get()方法获取页面的参数，如果没有获取到页码就默认为1
        per_page = 10  # 每页数量
        paginate = UserFiles.query.filter().order_by(-UserFiles.referTime).paginate(page,
                                                                                                            per_page,
                                                                                                            error_out=False)  # 创建分页器对象
        return render_template('admincenter/allFiles.html', paginate=paginate, pages=paginate.pages + 1)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 稿件删除
@admincenter.route('/delFile_ad/', methods=['GET', 'POST'])
@login_required
def delFile():
    if current_user.status == '管理员':
        # 查看删除稿件权限
        yn = current_user.permissions & 2
        # print('权限yn:', yn, type(yn))
        if not current_user.permissions & 2:
            return '你没有权限删除文件'
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


# 用户列表查询
@admincenter.route('/userlist/', methods=['GET', 'POST'])
@login_required
def userlist():
    if current_user.status == '管理员':
        page = int(request.args.get('page', 1))  # 当前页数，request.args.get()方法获取页面的参数，如果没有获取到页码就默认为1
        per_page = 10  # 每页数量
        paginate = User.query.filter(User.status == '作者').paginate(page, per_page, error_out=False)  # 创建分页器对象
        return render_template('admincenter/userlist.html', paginate=paginate, pages=paginate.pages + 1)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 专家列表查询
@admincenter.route('/expertlist/', methods=['GET', 'POST'])
@login_required
def expertlist():
    if current_user.status == '管理员':
        page = int(request.args.get('page', 1))  # 当前页数，request.args.get()方法获取页面的参数，如果没有获取到页码就默认为1
        per_page = 10  # 每页数量
        paginate = User.query.filter(User.status == '专家').paginate(page, per_page, error_out=False)  # 创建分页器对象
        return render_template('admincenter/expertlist.html', paginate=paginate, pages=paginate.pages + 1)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 作者信息弹框
@admincenter.route('/email_ad/', methods=['GET', 'POST'])
@login_required
def email_ad():
    if current_user.status == '管理员':
        u = User.query.filter(User.id == request.form.get('uid')).first()
        return u.email
    else:
        return render_template('common/nocan.html', u=current_user.username)
