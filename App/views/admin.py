from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from App.models import User  # User 模型类

admin = Blueprint('admin', __name__)

"""
# 注册步骤
1. 创建模型类
2. 加载flask-migrate扩展库（迁移）
3. 在视图函数中导入模型类
4. 验证用户名是否存在
5. 获取模板前台传递过来的数据
6. 存储
7. 明文密码变成密文密码（加密存储）
8. 消息闪现（注册成功）
"""


# 在最开始没有管理员时，使用本方法创建一个至高无上的管理员
@admin.route('/root/', methods=['GET', 'POST'])
def root():
    # 创建管理员表单对象
    ad = User()
    if User.query.filter(User.username == 'root').first():
        # 管理员已经存在
        num = 1
    else:
        # 给一个最开始的管理员、权限全开
        ad.username = 'root'
        ad.password = '123456'
        ad.email = '1234567898@qq.com'
        ad.registerTime = datetime.now()
        ad.status = '管理员'
        ad.leaderId = 0
        ad.permissions = 31
        # flash('测试')
        if ad.save():
            # 注册成功
            num = 2
        else:
            # 注册失败
            num = 3
    return render_template('admin/root_register.html', num=num)


@admin.route('/register_ad/', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.status == '管理员':  # 当前用户是管理员，才会渲染下面的模板，否则渲染nocan.html
        # 创建管理员表单对象
        ad = User()
        if request.method == 'POST':
            if User.query.filter(User.username == request.form.get('adname')).first():
                flash('用户名已存在')
            if User.query.filter(User.email == request.form.get('email')).first():
                flash('邮箱已存在')
            if request.form.get('passwd') != request.form.get('repass'):
                flash('两次输入的密码不一样，请重新输入...')
            else:
                ad.username = request.form.get('adname')
                ad.password = request.form.get('passwd')
                ad.email = request.form.get('email')
                ad.registerTime = datetime.now()
                ad.status = '管理员'

                ad.leaderId = current_user.id
                num = 0  # 权限初始值
                if request.form.get('pe1'):
                    num += int(request.form.get('pe1'))
                if request.form.get('pe2'):
                    num += int(request.form.get('pe2'))
                if request.form.get('pe4'):
                    num += int(request.form.get('pe4'))
                if request.form.get('pe8'):
                    num += int(request.form.get('pe8'))
                ad.permissions = num
                if ad.save():
                    flash('注册成功...')
                else:
                    flash('注册失败...')
        if current_user.permissions & 8:
            # 可以创建超级管理员，可设置管理员拥有的权限
            return render_template('admin/register_ad1.html')
        elif current_user.permissions & 4:
            # 可以创建普通管理员，没有权限的管理员
            return render_template('admin/register_ad2.html')
        else:
            return render_template('common/noPermission.html')
    else:
        return render_template('common/nocan.html', u=current_user.username)


@admin.route('/login_ad/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ad = User.query.filter(User.username == request.form.get('adname')).first()
        if not ad:
            flash('请输入正确的用户名')
        elif not ad.check_password(request.form.get('passwd')):
            flash('密码有误，请输入正确的密码...')
        else:
            # 修改登录时间
            ad.lastLogin = datetime.now()
            ad.save()
            login_user(ad, remember=True)  # 使用第三方扩展库处理登录状态的维持
            return redirect(url_for('admin.main_page'))
    return render_template('admin/login_ad.html')


# 用户主页面
@admin.route('/main_page_ad/')
@login_required
def main_page():
    if current_user.status == '管理员':  # 当前用户是管理员，才会渲染下面的模板，否则渲染nocan.html
        return render_template('main/main_admin.html', user=current_user)
    else:
        return render_template('common/nocan.html', u=current_user.username)


# 退出登录
@admin.route('/logout_ad/')
def logout():
    logout_user()  # 清除当前用户所有数据
    return redirect(url_for('main.index'))
