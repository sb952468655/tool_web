from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_required, login_user, logout_user, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, ChangePasswordForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # next = request.args.get('next')
            # if next is None or not next.startswith('/'):
            #     next = url_for('main.index')
            return redirect(url_for('main.index'))
        flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('city')
    if session.get('city_name'):
        session.pop('city_name')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            flash('密码错误')
    return render_template("auth/change_password.html", form=form)