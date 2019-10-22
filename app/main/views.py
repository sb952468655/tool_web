import os, sys
from flask import render_template, session, redirect, url_for, current_app, request
from . import main
from ..check_pool import all_check
from ..inspection import mobile
sys.path.append('../')
# from . report import get_report_data
# from . import report
# from .forms import NameForm, UploadForm

@main.route('/')
def index():

    return redirect(url_for('main.report_port'))


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

    from .report import get_report_data, get_device_name

    with open(os.path.join('app', 'static', 'uploads', 'config.log')) as f:
        config = f.read()

    report_data = get_report_data(config)
    return render_template('report.html', report_data = report_data)


@main.route('/check_config')
def check_config():

    with open(os.path.join('app', 'static', 'uploads', 'config.log')) as f:
        config = f.read()

    check_res = all_check.all_check(config)
    return render_template('check.html', check_res=check_res)

@main.route('/xunjian')
def xunjian():
    '''巡检'''

    xunjian_res = mobile.xunjian()
    xunjian_text = ''
    for item in xunjian_res:
        xunjian_text += '{}\n{}\n{}\n\n'.format(item[0], item[1], item[2])
    return render_template('xunjian.html', xunjian_res=xunjian_text)
