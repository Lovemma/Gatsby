# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, redirect
from flask_login import login_required, login_user, logout_user

from app.forms import LoginForm
from app.models.user import validate_login

bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = ''

    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        is_validated, user = validate_login(name, password)
        if is_validated:
            login_user(user)
            return redirect('/')
        error = 'Validation failed. Please try again'
    return render_template('admin/login_user.html', request=request,
                           form=form, error=error)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
