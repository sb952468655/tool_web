import os, sys
from flask import render_template, session, redirect, url_for, current_app, request
from . import main
# from . report import get_report_data
# from . import report
# from .forms import NameForm, UploadForm

@main.route('/')
def index():

    return redirect(url_for('main.report_port'))

@main.route('/xunjian')
def xunjian():
    return render_template('index.html', title = '巡检')

@main.route('/report')
def report():
    items = [
        ['show port', '检查端口是否有down的', 'sdsdsdsd'],
        ['show port detail', '检查端口光功率', 'sdsdsdsd'],
        ['show lag', '检查lag信息', 'sdsdsdsd'],
        ['show lag detail', '检查lag信息', 'sdsdsdsd'],
        ['show lag des', '检查lag信息', 'sdsdsdsd'],
        ['show router interface', '计算固定地址使用情况', 'sdsdsdsd'],
        ['show router arp', '计算固定地址使用情况', 'sdsdsdsd'],
        ['show router dhcp servers', '计算dhcp地址、地址利用率', 'sdsdsdsd'],
        ['show router dhcp local-dhcp-server "dhcp-s1" summary', '计算dhcp地址、地址利用率', 'sdsdsdsd'],
        ['admin display-config', '计算每个端口的业务种类、数量', 'sdsdsdsd'],
        ['show service service-using ies', '计算每个端口的业务种类、数量', 'sdsdsdsd'],
        ['show service service-using vprn', '计算每个端口的业务种类、数量', 'sdsdsdsd'],
        ['show service sap-using', '计算每个端口的业务种类、数量', 'sdsdsdsd'],
        ['show lag description', '计算每个端口的业务种类、数量', 'sdsdsdsd']
    ]

    return render_template('index.html', items = items)

@main.route('/report_port')
def report_port():
    '''统计报表-端口明细'''

    sys.path.append('../')
    from .report import get_report_data, get_device_name

    with open(os.path.join('app', 'static', 'uploads', 'config.log')) as f:
        config = f.read()

    report_data = get_report_data(config)
    return render_template('report.html', report_data = report_data)


@main.route('/check_config')
def check_config():
    return render_template('index.html', title = '配置检查')