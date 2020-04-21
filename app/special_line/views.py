import os, logging
from flask import render_template, session, redirect, url_for, current_app, request, abort, g, Response, flash
from flask_login import login_required, current_user
from datetime import date, datetime
from ..models import SpecialLine
from . import special_line
from .common import get_saps
from .. import db
from ..main.common import get_host


@special_line.route('/special_line', methods=['GET', 'POST'])
@login_required
def index():
    search_date = date.today()
    city = session.get('city')
    if not city:
        return redirect(url_for('main.city_list'))
    host_list = get_host(city)
    
    if request.method == 'POST':
        host_name = request.form.get('host_name')
        form_date = request.form.get('date')
        if form_date:
            search_date = datetime.strptime(form_date,'%Y-%m-%d').date()
    else:
        host_name = request.args.get('host_name')
        if not host_name:
            host_name = host_list[0]

    if host_name == 'all':
        special_line_data = SpecialLine.query.filter_by(date_time = search_date).all()
    else:
        special_line_data = SpecialLine.query.filter_by(host_name = host_name, date_time = search_date).all()

    special_line_data = [(index, item) for index, item in enumerate(special_line_data) ]
    return render_template('report/special_line.html', host_name=host_name, host_list = host_list, special_line_data = special_line_data ,action='special_line')

def save_special_line(city, host_name, config):
    '''专线统计入库'''

    today_data_count = SpecialLine.query.filter_by(host_name = host_name, date_time = date.today()).count()

    if today_data_count:
        logging.info('special_line host: {} today is saved'.format(host_name))
        return

    special_line_data = get_saps(config)
    if special_line_data:
        logging.info('host: {} {} begin save'.format(host_name, 'special_line_data'))

    today = date.today()
    for item in special_line_data:

        #存入数据库
        special_line = SpecialLine(
            city = city,
            host_name = host_name,
            ies_id = item[0],
            ies_describe = item[1],
            gi_name = item[2],
            gi_describe = item[3],
            sap_name = item[4],
            ip = item[5],
            mac = item[6],
            egress_id = item[7],
            rate = item[8],
            date_time = today
        )

        db.session.add(special_line)
    db.session.commit()
    db.session.close()
