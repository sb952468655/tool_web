from flask import render_template, session, redirect, url_for, current_app, request, abort, g, Response, flash
from flask_login import login_required, current_user
from . import special_line


@special_line.route('/special_line', methods=['GET', 'POST'])
@login_required
def index():
    return 'special_line'