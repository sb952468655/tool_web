import os, sys
from flask import render_template, session, redirect, url_for, current_app, request
import openpyxl
from openpyxl.styles import Alignment
import docx
from docx.shared import Pt
from docx.shared import RGBColor
import time
import datetime
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

    from .report import get_report_data, get_device_name, get_port_ggl

    with open(os.path.join('app', 'static', '1.log')) as f:
        config = f.read()

    report_data = get_report_data(config)
    ggl_port = []
    res = []


    ggl_data = get_port_ggl(config)

    i = 0
    for item in report_data:
        if item[-1] != 'MDX GIGE-T ' and item[-1] != 'MDI GIGE-T ':
            ggl_port.append(item[0])

            try:
                res.append(item + [ggl_data[i][0]] + [ggl_data[i][1]])
            except Exception:
                print('端口数和光功率数量不匹配')
            
            i += 1
        else:
            res.append(item + [''] + [''])


    session['report'] = res
    return render_template('report.html', report_data = res)


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
    session['xunjian'] = xunjian_res
    for item in xunjian_res:
        xunjian_text += '{}\n{}\n{}\n\n'.format(item[0], item[1], item[2])
    return render_template('xunjian.html', xunjian_res=xunjian_text)

@main.route('/auto_config')
def auto_config():
    '''脚本自动配置'''

    return render_template('auto_config.html')


@main.route('/generate_excel')
def generate_excel():
    '''生成表格'''

    excel = openpyxl.Workbook()
    sheet = excel.active
    sheet['A1'] = '设备名'
    sheet['B1'] = '设备IP'
    sheet['C1'] = 'port'
    sheet['D1'] = '端口带宽'
    sheet['E1'] = 'Admin State'
    sheet['F1'] = 'Link State'
    sheet['G1'] = 'Port State'
    sheet['H1'] = 'CfgMTU'
    sheet['I1'] = 'OperMTU'
    sheet['J1'] = 'LAG'
    sheet['K1'] = 'PortMode'
    sheet['L1'] = 'PortEncp'
    sheet['M1'] = 'PortType'
    sheet['N1'] = 'C/QS/S/XFP/MDIMDX'
    sheet['O1'] = '收光功率'
    sheet['P1'] = '发光功率'
    sheet['Q1'] = '收光门限'
    sheet['R1'] = '发光门限'
    sheet['S1'] = '是否存在异常'

    sheet.column_dimensions['A'].width = 40.0
    sheet.column_dimensions['N'].width = 20.0
    cur_row = 2
    for item in session.get('report'):
        sheet['A'+ str(cur_row)] = item[0]
        # sheet['B'+ str(cur_row)] = item[1]
        sheet['C'+ str(cur_row)] = item[1]
        if '10' in item[11]:
            sheet['D'+ str(cur_row)] = '10GE'
        else:
            sheet['D'+ str(cur_row)] = 'GE'
        sheet['E'+ str(cur_row)] = item[2]
        sheet['F'+ str(cur_row)] = item[3]
        sheet['G'+ str(cur_row)] = item[4]
        sheet['H'+ str(cur_row)] = item[5]
        sheet['I'+ str(cur_row)] = item[6]
        sheet['J'+ str(cur_row)] = item[7]
        sheet['K'+ str(cur_row)] = item[8]
        sheet['L'+ str(cur_row)] = item[9]
        sheet['M'+ str(cur_row)] = item[10]
        sheet['N'+ str(cur_row)] = item[11]
        sheet['O'+ str(cur_row)] = item[12]
        sheet['P'+ str(cur_row)] = item[13]
        # sheet['Q'+ str(cur_row)] = item[0]
        # sheet['R'+ str(cur_row)] = item[0]
        # sheet['S'+ str(cur_row)] = item[0]

        cur_row += 1
    
    excel.save(os.path.join('app','static', 'port.xlsx'))

    return redirect(url_for('static', filename='port.xlsx'))


@main.route('/xj_report')
def xj_report():
    '''生成巡检报告'''


    doc = docx.Document(os.path.join('app','static','xunjian.docx'))
    area =  '常州移动' 
    doc.add_paragraph(area + '巡检报告', style='report-head')
    doc.add_paragraph('上海贝尔7750设备巡检报告', style='report-head')
    doc.add_paragraph()
    doc.add_paragraph()
    today_obj = datetime.datetime.now()
    today = '%d年%d月%d日' % (today_obj.year, today_obj.month, today_obj.day)
    doc.add_paragraph(today, style='report-date')
    doc.add_page_break()
    doc.add_heading('巡检情况汇总', 4)
    
    for line in session.get('xunjian'):
        p_name = doc.add_paragraph(line[0], style='report-info')

        if line[1]:
            p_info = doc.add_paragraph(line[1], style='report-info')
        if line[2]:
            p_warn = doc.add_paragraph('注：' + line[2], style='report-normal')

        if not line[1] and not line[2]:
            print('not a line 1, 2')
        doc.add_paragraph()
        
        font = p_name.runs[0].font
        font.color.rgb = RGBColor(0, 0, 0)

        font = p_info.runs[0].font
        font.color.rgb = RGBColor(0, 0, 255)

        font = p_warn.runs[0].font
        font.color.rgb = RGBColor(255, 0, 255)


    doc.add_heading('总结', 4)
    doc.add_paragraph('1，为了保障%s移动城域网7750设备正常运行，请定期清理过滤网。' % '常州',
        style='report-normal')

    for item in session.get('xunjian'):
        if 'Temperature' in item:
            doc.add_paragraph('2，板卡温度高建议清洗防尘网。',
            style='report-normal')
        break
    
    report_name = '%s移动巡检报告-%s.docx' % ('常州', today)
    doc.save( os.path.join('app', 'static', report_name))

    return redirect(url_for('static', filename = report_name))