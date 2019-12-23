import os, sys, zipfile, time, datetime, logging, re
from flask import render_template, session, redirect, url_for, current_app, request, abort, g, Response
import openpyxl
from openpyxl.styles import Alignment, PatternFill
import docx
from docx.shared import Pt
from docx.shared import RGBColor
from . import main
from ..check_pool import all_check
from ..inspection import mobile
from ..models import AddressCollect, LoadStatistic
from .config import g_city_to_name, g_log_path, g_backup_path
from .address import get_address_data
from .statistic import get_statistic_data, get_statistic_host_data
from urllib.request import quote, unquote
from .. import db
from ..models import CardPort1
from .report import get_host_list, get_card_detail, get_card_statistic, get_mda_detail, get_mda_statistic, get_port_statistic
from .common import get_log, get_host, get_today_log_name, get_city_list, get_host_logs
sys.path.append('../')

@main.route('/')
def index():
    session['action'] = 'report_port'
    return redirect(url_for('main.city_list'))


@main.route('/report_port/<host_name>')
def report_port(host_name):
    '''统计报表-端口明细'''

    card_data = []
    city = session.get('city')

    from .report import get_report_data, get_device_name, get_port_ggl, get_ip

    page = request.args.get('page', 1, type=int)
    count = CardPort1.query.filter_by(host_name = host_name, date_time = datetime.date.today()).count()
    if count == 0:
        
        config = get_log(city, host_name)
        if not config:
            abort(404)

        ip = get_ip(config)
        report_data = get_report_data(config)
        ggl_port = []
        res = []


        ggl_data = get_port_ggl(config)

        i = 0
        for item in report_data:
            if item[-1] != 'MDX GIGE-T ' and item[-1] != 'MDI GIGE-T ':
                ggl_port.append(item[0])
                port_is_ok = '否'
                #判断端口是否有异常
                if item[2] == 'Up' and item[3] == 'No' and item[4] != 'Up':
                    port_is_ok = '是'

                #判断端口ge或者10ge
                dk = ''
                if item[-1].startswith('10'):
                    dk = '10GE'
                elif item[-1].startswith('GIGE'):
                    dk = 'GE'
                try:
                    if item[2] == 'Up' and item[3] == 'Yes' and item[4] == 'Up':
                        if ggl_data[i][7] and (float(ggl_data[i][5]) < float(ggl_data[i][8]) or float(ggl_data[i][5]) > float(ggl_data[i][7])):
                            port_is_ok = '是'
                        if ggl_data[i][3] and (float(ggl_data[i][0]) < float(ggl_data[i][3]) or float(ggl_data[i][0]) > float(ggl_data[i][2])):
                            port_is_ok = '是'

                    res.append(item + [ggl_data[i][0], ggl_data[i][5], ggl_data[i][2]+'|'+ ggl_data[i][3], ggl_data[i][7]+'|'+ ggl_data[i][8], ip, port_is_ok, dk])

                except Exception:
                    # print('端口数和光功率数量不匹配')
                    continue
                
                i += 1
            else:
                res.append(item + ['','','','', ip, '', ''])

        for item in res:

            #存入数据库
            card_port = CardPort1(
                host_name = host_name,
                host_ip = item[16],
                port = item[1],
                port_dk = item[18],
                admin_state = item[2],
                link_state = item[3],
                port_state = item[4],
                cfg_mtu = item[5],
                oper_mtu = item[6],
                lag = item[7],
                port_mode = item[8],
                port_encp = item[9],
                port_type = item[10],
                c_qs_s_xfp_mdimdx = item[11],
                optical_power = item[12],
                output_power = item[13],
                optical_warn = item[14],
                output_warn = item[15],
                is_abnormal = item[17]
            )

            db.session.add(card_port)

        db.session.commit()
        session['report'] = res

        
    pageination = CardPort1.query.filter_by(host_name = host_name, date_time = datetime.date.today()).order_by(CardPort1.date_time.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False
    )
    card_data = pageination.items

    return render_template('report.html', 
        card_data = card_data, 
        action = 'report_port', 
        host_name=host_name,
        pageination = pageination)

@main.route('/host_list_data/<host_name>')
def host_list_data(host_name):
    '''设备清单统计'''
    city = session.get('city')
    host_list_data = get_host_list(city)

    return render_template('host_list_data.html', host_name=host_name, host_list_data = host_list_data ,action='host_list_data')

@main.route('/card_detail/<host_name>')
def card_detail(host_name):
    '''card明细'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)
    card_detail_data = get_card_detail(config)

    return render_template('card_detail.html', host_name=host_name, card_detail_data = card_detail_data ,action='card_detail')

@main.route('/card_statistic/<host_name>')
def card_statistic(host_name):
    '''card统计'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)

    card_statistic_data = get_card_statistic(config)

    return render_template('card_statistic.html', host_name=host_name, card_statistic_data = card_statistic_data ,action='card_statistic')

@main.route('/mda_detail/<host_name>')
def mda_detail(host_name):
    '''mda明细'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)
    mda_detail_data = get_mda_detail(config)

    return render_template('mda_detail.html', host_name=host_name,  mda_detail_data = mda_detail_data ,action='mda_detail')

@main.route('/mda_statistic/<host_name>')
def mda_statistic(host_name):
    '''mda统计'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)
    mda_statistic_data = get_mda_statistic(config)

    return render_template('mda_statistic.html', host_name=host_name,  mda_statistic_data = mda_statistic_data ,action='mda_statistic')

@main.route('/port_statistic/<host_name>')
def port_statistic(host_name):
    '''port统计'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)
    port_statistic_data = get_port_statistic(config)

    return render_template('port_statistic.html', host_name=host_name,  port_statistic_data = port_statistic_data ,action='port_statistic')


@main.route('/check_config/<host_name>')
def check_config(host_name):
    '''配置检查'''

    city = session.get('city')
    if not city:
        return redirect(url_for('main.city_list'))

    config = get_log(city, host_name)
    if not config:
        abort(404)
    check_res = all_check.all_check(config)

    session['host_name'] = host_name
    return render_template('check.html', check_data=check_res, host_name=host_name)

@main.route('/check_excel/<host_name>')
def check_excel(host_name):
    '''配置检查生成表格'''

    #先获取检查结果
    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)
    check_res = all_check.all_check(config)

    excel = openpyxl.Workbook()
    sheet = excel.active
    sheet['A1'] = '设备名'
    sheet['B1'] = '错误信息'
    sheet['C1'] = '检查项'

    sheet.column_dimensions['A'].width = 40.0
    sheet.column_dimensions['B'].width = 110.0
    sheet.column_dimensions['C'].width = 70.0
    cur_row = 2
    for item in check_res:
        for item2 in item[1]:
            sheet['A'+ str(cur_row)] = host_name.split('.')[0]
            sheet['B'+ str(cur_row)] = item2
            sheet['C'+ str(cur_row)] = item[0]

            cur_row += 1
    
    file_name = '{}_配置检查.xlsx'.format(host_name.split('.')[0])
    excel.save(os.path.join('app','static', file_name))

    return redirect(url_for('static', filename=file_name))


@main.route('/xunjian/<host_name>')
def xunjian(host_name):
    '''巡检'''
    city = session.get('city')
    if not city:
        return redirect(url_for('main.city_list'))

    config = get_log(city, host_name)
    if not config:
        abort(404)

    yesday_log = get_log(city, host_name, 1)
    if not yesday_log:
        yesday_log = config

    xunjian_data = mobile.xunjian(config, yesday_log)
    warn_data = [item for item in xunjian_data if item[0]]
    
    return render_template('xunjian/xunjian.html', xunjian_data=warn_data, host_name = host_name, city = city)

@main.route('/xunjian_output_all/<host_name>')
def xunjian_output_all(host_name):
    '''设备巡检-全量输出'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)

    xunjian_data = mobile.xunjian(config, config)
    warn_data = [item for item in xunjian_data if item[0]]
    
    return render_template('xunjian/xunjian_output_all.html', xunjian_data=warn_data, host_name = host_name, city = city)

@main.route('/xunjian_all_host')
def xunjian_all_host():
    '''所有设备巡检'''

    warn_data = []
    city = session.get('city')
    
    host_list = get_host(city)
    for i in host_list:
        log = get_log(city, i)
        yesday_log = get_log(city, i, 1)
        if log and yesday_log:
            xunjian_data = mobile.xunjian(log, yesday_log)
            warn_data.append((i, [item for item in xunjian_data if item[0]]))

    return render_template('xunjian/xunjian_all_host.html', xunjian_data=warn_data)

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
    sheet.column_dimensions['B'].width = 20.0
    sheet.column_dimensions['N'].width = 20.0
    sheet.column_dimensions['Q'].width = 15.0
    sheet.column_dimensions['R'].width = 15.0
    cur_row = 2
    for item in session.get('report'):
        sheet['A'+ str(cur_row)] = item[0]
        sheet['B'+ str(cur_row)] = item[16]
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
        sheet['O'+ str(cur_row)] = item[13]

        if item[2] == 'Up' and item[3] == 'Yes' and item[4] == 'Up' and item[13] and (float(item[13]) < float(item[15].split('|')[1]) or float(item[13]) > float(item[15].split('|')[0])):
            fill = PatternFill("solid", fgColor="FF0000")
            sheet['O'+ str(cur_row)].fill = fill


        sheet['P'+ str(cur_row)] = item[12]

        if item[2] == 'Up' and item[3] == 'Yes' and item[4] == 'Up' and item[12] and (float(item[12]) < float(item[14].split('|')[1]) or float(item[12]) > float(item[14].split('|')[0])):
            fill = PatternFill("solid", fgColor="FF0000")
            sheet['P'+ str(cur_row)].fill = fill

        sheet['Q'+ str(cur_row)] = item[15]
        sheet['R'+ str(cur_row)] = item[14]
        if item[2] == 'Up' and item[3] == 'No' and item[4] != 'Up':
            sheet['S'+ str(cur_row)] = '是'
            fill = PatternFill("solid", fgColor="FF0000")
            sheet['S'+ str(cur_row)].fill = fill
        else:
            sheet['S'+ str(cur_row)] = '否'

        cur_row += 1
    
    excel.save(os.path.join('app','static', 'port.xlsx'))

    return redirect(url_for('static', filename='port.xlsx'))

@main.route('/xj_log_export/<host_name>')
def xj_log_export(host_name):
    '''巡检日志导出'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)

    log_config_str = config[config.index('# Finished'):]
    with open(os.path.join(g_backup_path, host_name + '.log'), 'w') as f:
        f.write(log_config_str)

    return redirect(url_for('static', filename = 'backup/{}.log'.format(host_name)))

@main.route('/xj_log/<host_name>')
def xj_log(host_name):
    '''巡检log全量输出'''

    city = session.get('city')
    config = get_log(city, host_name)
    if not config:
        abort(404)

    log_str = config[config.index('# Finished'):]

    return render_template('xunjian/xunjian_log.html', log_str = log_str, host_name = host_name)

@main.route('/xj_report/<city>/<host_name>/<type>')
def xj_report(city, host_name, type):
    '''生成巡检报告'''

    config = get_log(city, host_name)
    if not config:
        abort(404)

    xunjian_data = mobile.xunjian(config, config)

    doc = docx.Document(os.path.join('app','static','xunjian.docx'))
    area = g_city_to_name.get(city) + '移动'
    doc.add_paragraph(area + '巡检报告', style='report-head')
    if type == '1':
        doc.add_paragraph('上海贝尔7750单设备巡检报告', style='report-head')
    else:
        doc.add_paragraph('上海贝尔7750单设备巡检输出', style='report-head')
    doc.add_paragraph()
    doc.add_paragraph()
    today_obj = datetime.datetime.now()
    today = '%d年%d月%d日' % (today_obj.year, today_obj.month, today_obj.day)
    doc.add_paragraph(today, style='report-date')
    doc.add_page_break()
    doc.add_heading('巡检情况汇总', 4)
    
    if type == '1':
        warn_data = [item for item in xunjian_data if item[0] and '正常' not in item[1]]
    else:
        warn_data = [item for item in xunjian_data if item[0]]
    
    p_name = doc.add_paragraph(host_name.split('.')[0], style='report-info')
    font = p_name.runs[0].font
    font.color.rgb = RGBColor(0, 0, 0)
    for line in warn_data:
        p_info = doc.add_paragraph(line[2], style='report-info')
        p_warn = doc.add_paragraph('注：' + line[1], style='report-normal')

        doc.add_paragraph()
        
        font = p_info.runs[0].font
        font.color.rgb = RGBColor(0, 0, 255)

        # font = p_warn.runs[0].font
        # font.color.rgb = RGBColor(255, 0, 255)


    doc.add_heading('总结', 4)

    doc.add_paragraph('1，为了保障%s移动城域网7750设备正常运行，请定期清理过滤网。' % '常州',
        style='report-normal')

    for item in warn_data:
        if 'Temperature' in item[1]:
            doc.add_paragraph('2，板卡温度高建议清洗防尘网。',
            style='report-normal')
        break

    if type == '1':
        report_name = '%s移动%s单设备巡检报告-%s.docx' % (g_city_to_name.get(city), host_name, today)
    else:
        report_name = '%s移动%s单设备巡检输出-%s.docx' % (g_city_to_name.get(city), host_name, today)

    doc.save( os.path.join('app', 'static', report_name))
    return redirect(url_for('static', filename = report_name))

@main.route('/xj_report_all_host')
def xj_report_all_host():
    '''所有设备巡检，生成巡检报告'''

    warn_data = []
    city = session.get('city')
    
    host_list = get_host(city)
    for i in host_list:
        log = get_log(city, i)
        yesday_log = get_log(city, i, 1)
        if log and yesday_log:
            xunjian_data = mobile.xunjian(log, yesday_log)
            warn_data.append((i, [item for item in xunjian_data if item[0]]))


    #生成报告
    doc = docx.Document(os.path.join('app','static','xunjian.docx'))

    area = g_city_to_name.get(city) + '移动'
    doc.add_paragraph(area + '巡检报告', style='report-head')
    doc.add_paragraph('上海贝尔7750设备巡检报告', style='report-head')
    doc.add_paragraph()
    doc.add_paragraph()
    today_obj = datetime.datetime.now()
    today = '%d年%d月%d日' % (today_obj.year, today_obj.month, today_obj.day)
    doc.add_paragraph(today, style='report-date')
    doc.add_page_break()
    doc.add_heading('巡检情况汇总', 4)
    
    p_num = 1
    for line in warn_data:
        p_name = doc.add_paragraph(str(p_num) + '. ' + line[0] + '\n', style='report-info')
        p_num += 1
        font = p_name.runs[0].font
        font.color.rgb = RGBColor(0, 0, 0)

        for j in line[1]:
            
            p_info = doc.add_paragraph(j[2], style='report-info')
            p_warn = doc.add_paragraph('注：' + j[1], style='report-normal')

            doc.add_paragraph()
            
            font = p_info.runs[0].font
            font.color.rgb = RGBColor(0, 0, 255)

            font = p_warn.runs[0].font
            if 'port状态巡检' == j[2]:
                font.size = Pt(9)
            else:
                font.size = Pt(12)
            # font.color.rgb = RGBColor(255, 0, 255)


    doc.add_heading('总结', 4)

    doc.add_paragraph('1，为了保障%s移动城域网7750设备正常运行，请定期清理过滤网。' % g_city_to_name.get(city),
        style='report-normal')

    for item in warn_data:
        for j in item[1]:
            if 'Temperature' in j[1]:
                doc.add_paragraph('2，板卡温度高建议清洗防尘网。',
                style='report-normal')
            break
    
    report_name = '%s移动巡检报告-%s.docx' % (g_city_to_name.get(city), today)
    doc.save( os.path.join('app', 'static', report_name))

    return redirect(url_for('static', filename = report_name))



@main.route('/city_list')
def city_list():
    '''地市列表'''

    city_data = []
    citys = get_city_list()
    for i in citys:
        city_data.append((i, g_city_to_name.get(i)))
    return render_template('city_list.html', city_data = city_data)


@main.route('/host_list/<action>')
def host_list(action):
    session['action'] = action
    if not session.get('city'):
        session['city'] = request.args.get('city')
        session['city_name'] = session.get('city')

    city = session.get('city')
    if not city:
        return redirect(url_for('main.city_list'))

    session['city_name'] = g_city_to_name.get(city)
    
    
    host_data = get_host(city)

    if action == 'config_backup':
        return redirect(url_for('main.config_backup'))

    return render_template('host_list_base.html', host_data = host_data,  action = action)


@main.route('/address_collect/<host_name>')
def address_collect(host_name):
    '''三层接口和静态用户IP地址采集'''
    address_data = []
    city = session.get('city')
    page = request.args.get('page', 1, type=int)
    count = AddressCollect.query.filter_by(host_name = host_name, date_time = datetime.date.today()).count()
    # count = 0 #等下去掉
    if count == 0:
        config = get_log(city, host_name)
        if not config:
            abort(404)
        res = get_address_data(config)

        for item in res:
            address_data.append([host_name] + item)

            #存入数据库
            address_collect = AddressCollect(
                host_name = host_name,
                host_ip = item[0],
                ip_type = item[1],
                function_type = item[2],
                is_use = item[3],
                ip = item[4].strNormal(0),
                gateway = item[5],
                mask = item[6],
                interface_name = item[7],
                sap_id = item[8],
                next_hop = item[9],
                ies_vprn_id = item[10],
                vpn_rd = item[11],
                vpn_rt = item[12],
                description = item[13]
            )

            db.session.add(address_collect)
        db.session.commit()


    pageination = AddressCollect.query.filter_by(host_name = host_name, date_time = datetime.date.today()).order_by(AddressCollect.date_time.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False
    )
    address_data = pageination.items


    return render_template('address_collect.html', 
        address_data = address_data, 
        action = 'address_collect', 
        host_name=host_name,
        pageination = pageination)


@main.route('/address_mk_excel/<host_name>')
def address_mk_excel(host_name):
    '''地址采集生成 excel 表格'''
    excel = openpyxl.Workbook()
    sheet = excel.active
    sheet['A1'] = '设备名'
    sheet['B1'] = '设备IP'
    sheet['C1'] = 'IP类型'
    sheet['D1'] = '网络功能类型'
    sheet['E1'] = '是否已分配'
    sheet['F1'] = 'IP'
    sheet['G1'] = '网关'
    sheet['H1'] = '掩码'
    sheet['I1'] = '逻辑接口编号'
    sheet['J1'] = 'sap-ID'
    sheet['K1'] = '下一跳IP'
    sheet['L1'] = 'IES/VPRN编号'
    sheet['M1'] = 'VPN-RD'
    sheet['N1'] = 'VPN-RT'
    sheet['O1'] = '接口或用户描述'


    sheet.column_dimensions['A'].width = 40.0
    sheet.column_dimensions['B'].width = 20.0
    # sheet.column_dimensions['N'].width = 20.0
    # sheet.column_dimensions['Q'].width = 15.0
    # sheet.column_dimensions['R'].width = 15.0
    cur_row = 2

    address_data = AddressCollect.query.filter_by(host_name = host_name, date_time = datetime.date.today()).order_by(AddressCollect.date_time.desc()).all()
    for item in address_data:
        sheet['A'+ str(cur_row)] = item.host_name.split('.')[0]
        sheet['B'+ str(cur_row)] = item.host_ip
        sheet['C'+ str(cur_row)] = item.ip_type
        sheet['D'+ str(cur_row)] = item.function_type
        sheet['E'+ str(cur_row)] = item.is_use
        sheet['F'+ str(cur_row)] = item.ip
        sheet['G'+ str(cur_row)] = item.gateway
        sheet['H'+ str(cur_row)] = item.mask
        sheet['I'+ str(cur_row)] = item.interface_name
        sheet['J'+ str(cur_row)] = item.sap_id
        sheet['K'+ str(cur_row)] = item.next_hop
        sheet['L'+ str(cur_row)] = item.ies_vprn_id
        sheet['M'+ str(cur_row)] = item.vpn_rd
        sheet['N'+ str(cur_row)] = item.vpn_rt
        sheet['O'+ str(cur_row)] = item.description

        cur_row += 1
    
    excel.save(os.path.join('app','static', 'address.xlsx'))

    return redirect(url_for('static', filename='address.xlsx'))


@main.route('/config_backup')
def config_backup():
    '''config备份（下载到本地）'''
    host_data = []
    city = session.get('city')
    if not city:
        return redirect(url_for('main.city_list'))

    host_list = get_host(city)
    today = datetime.date.today()
    date = today.strftime('%Y%m%d')
    for item in host_list:
        if get_log(city, item):
            host_data.append((item, date))
        
    return render_template('back_up/config_backup_host_list.html', host_data=host_data)

@main.route('/backup_list', methods=['POST'])
def backup_list():
    '''获取需要备份的config列表'''

    city = session.get('city')
    if request.method=='POST':
        if not os.path.exists(os.path.join('app', 'static', 'backup')):
            os.makedirs(os.path.join('app', 'static', 'backup'))

        file_name = str(time.time()) + '.zip'
        zip_name = os.path.join('app', 'static', 'backup', file_name)
        zip = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED )
        
        for name, _ in request.form.to_dict().items():
            log_str = get_log(city, name)
            log_config_str = log_str[:log_str.index('# Finished')]
            back_up_log_path = os.path.join('app', 'static', 'backup', name + '.log')
            with open(back_up_log_path, 'w') as f:
                f.write(log_config_str)
            zip.write(back_up_log_path, name + '.log')

        zip.close()

        url = url_for('static', filename = 'backup/{}'.format(file_name))
        url2 = unquote(url, encoding='utf-8')
        return redirect(url2)



@main.route('/load_statistic/<host_name>')
def load_statistic(host_name):
    '''业务负荷统计'''
    statistic_data = None
    page = request.args.get('page', 1, type=int)
    city = session.get('city')
    if not city:
        return redirect(url_for('main.city_list'))

    count = LoadStatistic.query.filter_by(host_name = host_name, date_time = datetime.date.today()).count()
    if count == 0:
        config = get_log(city, host_name)
        if not config:
            abort(404)
        res = get_statistic_data(config)
        for item in res:

            #存入数据库
            load_statistic = LoadStatistic(
                host_name = host_name,
                host_ip = item[2],
                port = item[1],
                port_dk = item[3],
                in_utilization = item[4],
                out_utilization = item[5],
                ies_3000_user_num = item[6],
                ies_3000_utilization = item[7],
                vprn_4015_user_num = item[8],
                vprn_4015_utilization = item[9]
            )

            db.session.add(load_statistic)
        db.session.commit()

    pageination = LoadStatistic.query.filter_by(host_name = host_name, date_time = datetime.date.today()).order_by(LoadStatistic.date_time.desc()).paginate(
        page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out = False
    )
    statistic_data = pageination.items


    return render_template('statistic.html',
        statistic_data = statistic_data, 
        action = 'load_statistic', 
        host_name=host_name,
        pageination = pageination)




@main.route('/load_statistic_host/<host_name>')
def load_statistic_host(host_name):
    '''按设备统计用户数量'''

    city = session.get('city')
    load_statistic_host_data = get_statistic_host_data(city)

    return render_template('statistic_host.html',
        load_statistic_host_data = load_statistic_host_data, 
        action = 'load_statistic_host', 
        host_name=host_name)
    
    

@main.route('/db_test')
def db_test():
    '''数据库测试'''
    address_collect = AddressCollect(
        host_name = 'aaaa',
        host_ip = 'sdsd',
        ip_type = 'sd',
        function_type = 'sd',
        is_use = 's',
        ip = 'sss',
        gateway = 'sss',
        mask = 'sds',
        interface_name = 'sds',
        sap_id = 'sdsd',
        next_hop = 'sdwd',
        ies_vprn_id = 'sdsd',
        vpn_rd = 'sdsds',
        vpn_rt = 'sdsxcc',
        description = 'sdasd'
    )


    db.session.add(address_collect)
    db.session.commit()


    a = AddressCollect.query.first()

    return a.host_name

