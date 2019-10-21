import os
from flask import render_template, session, redirect, url_for, current_app, request
from . import main
# from .forms import NameForm, UploadForm

@main.route('/')
def index():
    return render_template('index.html', title = '巡检')

@main.route('/xunjian')
def xunjian():
    return render_template('index.html', title = '巡检')

@main.route('/report')
def report():
    return render_template('index.html', title = '报表')

@main.route('/check_config')
def check_config():
    return render_template('index.html', title = '配置检查')