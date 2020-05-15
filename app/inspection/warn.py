# -*- coding: utf-8 -*-
import datetime, time
import re
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

def warn_find_all(res, re_str):
    re_obj = re.compile(re_str)
    result = re_obj.findall(res)
    return result

def mobile_warn1(res):
    '''风扇SPEED巡检'''

    err = ''
    msg = ''
    check_item = '风扇SPEED巡检'

    re_str = r'''(Fan tray number                   : (\d)
    Speed                           : (\d{1,3} %|\w{3,4} speed( \(0-\d\d%\))?)
    Status                          : (\w{2,5}))'''

    p_fan_info = r'(?s)Environment Information\n.*?\n-'

    re_obj = re.compile(re_str)
    
    res_fan_info = re.search(p_fan_info, res)

    if res_fan_info:
        result = re_obj.findall(res_fan_info.group())
        if result:
            for item in result:
                try:
                    if item[2] == 'full speed':
                        err += '风扇%s全转速，建议清洗滤尘网。\n' % item[1]
                    elif 'speed' not in item[2]:
                        if int(item[2][:-2]) >= 50:
                            err += '风扇%s转速大于50。\n' % item[1]
                    elif int(item[3][-4:-2]) >= 50:
                        msg += 'Fan tray number: %s\nSpeed: %s\n' % (item[1], item[2])
                        err += '风扇%s转速大于50。\n' % item[1]
                    elif item[4] != 'up':
                        err += '风扇%s状态不正常。\n' % item[1]
                except Exception:
                    pass
                msg += item[0] + '\n'
                
        else:
            logging.error('没有找到风扇信息')
    else:
        logging.error('没有找到Environment Information')

    if err == '':
        err = '风扇SPEED正常'

    return(msg, err, check_item)

def mobile_warn2(res):
    '''电源状态巡检'''

    re_str = r'''(Power supply number               : (\d)
    Defaulted power supply type     : .{2,10}
    Power supply model              : .{2,10}
    Status                          : (.{2,10}))'''

    re_obj = re.compile(re_str)
    result = re_obj.findall(res)

    msg = ''
    err = ''
    check_item = '电源状态巡检'
    if result:
        for item in result:
            msg += item[0] + '\n'
            if item[2] != 'up':
                err += '电源状态异常，Power supply number {} Status {}\n'.format(item[1], item[2])
    else:
        logging.error('没有找到电源信息')

    if err == '':
        err = '电源模块状态正常'

    return (msg, err, check_item)

def mobile_warn3(res):
    '''系统LED状态巡检'''

    re_str = r'''Critical LED state                : (.{2,10})
  Major LED state                   : (.{2,10})
  Minor LED state                   : (.{2,10})'''

    re_obj = re.compile(re_str)
    result = re_obj.search(res)

    msg = ''
    err = ''
    check_item = '系统LED状态巡检'
    if result:
        msg = result.group()
        if result.group(1) != 'Off':
            err += 'Critical 告警指示灯亮\n'
        if result.group(2) != 'Off':
            err += 'Major 告警指示灯亮\n'
        if result.group(3) != 'Off':
            err += 'Minor 告警指示灯亮\n'
    else:
        logging.error('没有找到主控指示灯信息')

    if err == '':
        err = '系统LED状态正常'

    return (msg, err, check_item)

def mobile_warn4(res):
    '''系统CPU状态巡检'''

    err = ''
    msg = ''
    check_item = '系统CPU状态巡检'

    re_str = r'''Total {30,41}[,0-9]{1,11} {9,11}\d{1,3}\.\d\d%                
   Idle {30,41}[,0-9]{1,11} {9,11}\d{1,3}\.\d\d%                
   Usage {30,41}[,0-9]{1,11} {9,11}(\d{1,3})\.\d\d%'''

    re_obj = re.compile(re_str)
    result = re_obj.search(res)

    if result:
        if int(result.group(1)) > 80:
            err = 'cpu利用率高，利用率：{}%'.format(result.group(1))
        msg = result.group()
    else:
        logging.error('没有找到系统cpu状态')

    if err == '' and result:
        err = 'cpu利用率正常，利用率：{}%'.format(result.group(1))

    return (msg, err, check_item)

def mobile_warn5(res):
    '''系统Memory状态巡检'''

    err = ''
    msg = ''
    check_item = '系统Memory状态巡检'

    re_str = r'''Current Total Size :    (.{10,15}) bytes
Total In Use       :    (.{10,15}) bytes
Available Memory   :   (.{10,15}) bytes'''

    re_obj = re.compile(re_str)
    result = re_obj.search(res)
    ziyuan = ''
    if result:
        msg = result.group()
        current_sotal_size = int(result.group(1).replace(',', ''))
        available_memory = int(result.group(3).replace(',', ''))

        ziyuan = current_sotal_size/(current_sotal_size + available_memory)
        if ziyuan >= 0.8:
            err = '系统Memory资源消耗高，资源消耗：{}%'.format(int(ziyuan * 100))
    else:
        logging.error('warn5 没有找到系统Memory状态')

    if err == '' and ziyuan:
        err = '系统Memory正常，资源消耗：{}%'.format(int(ziyuan * 100))

    return (msg, err, check_item)


def mobile_warn6(res):
    '''空闲队列资源检查'''

    err = ''
    msg = ''
    check_item = '空闲队列资源检查'

    p_hardware_resource_ssage = r'(?s)(Hardware Resource Usage for Slot.*?Egress TLS Mcast Entries \|[ 0-9]{11}\|[ 0-9]{11}\|[ 0-9]{11}\n)'
    re_str = r'''((Dynamic|Ingress|Egress) Queues (\+|\|)\s{1,11}\d{2,10}\|\s{1,11}(\d{2,10})\|\s{1,11}(\d{2,10}))'''
    re_obj = re.compile(re_str)
    

    res_hardware_resource_ssage = re.findall(p_hardware_resource_ssage, res)
    for i in res_hardware_resource_ssage:
        result = re_obj.search(i)
        if result:
            msg += i + '\n'
            a = result.group(4)
            b = result.group(5)
            if int(result.group(5)) < int(result.group(4)):
                err += '空闲队列资源不足：{}\n'.format(result.group())
        else:
            logging.error('warn6没有找到空闲队列资源')

    if err == '':
        err = '空闲队列资源正常'

    return (msg, err, check_item)


def mobile_warn7(res):

    re_str = '''FCS Errors'''

    re_obj = re.compile(re_str)
    result = re_obj.findall(res)
    
    if result:
        return('FCS Errors', 'FCS Errors告警。', '', 'FCS Errors')
    else:
        return ('','','','')


def mobile_warn8(res):
    '''mda温度巡检'''

    err = ''
    msg = ''
    check_item = 'mda温度巡检'
    p_mda = r'(?s)(MDA (\d/\d) detail\n.*?(\w{2,4}-\w{2,4}-\w{2,4}) .*?Temperature                   : (\d{1,3})C)'
    res_mda = re.findall(p_mda, res)

    if res_mda:
        for item in res_mda:
            msg += item[0] + '\n'
            if int(item[3]) > 75:
                err = '板卡温度高，建议清洗防尘网，若清洗之后还没变化或建议降低机房环境温度'
                break
    else:
        logging.error('warn8没有找到板卡温度')

    if err == '':
        err = 'mda温度正常，无Errors告警'

    return (msg, err, check_item)



def mobile_warn9(res):
    '''CF卡状态巡检'''

    err = ''
    msg = ''
    check_item = 'CF卡状态巡检'

    re_str = r'''Flash - cf3:
    Administrative State          : [a-zA-Z]{2,4}
    (Operational state             : ([a-zA-Z]{2,4}))'''

    re_obj = re.compile(re_str)
    result = re_obj.findall(res)
    if result:
        for index, item in enumerate(result):
            msg += item[0] + '\n'
            if item[1] != 'up':
                card_id = 'A'
                if index == 1:
                    card_id = 'B'
                msg += item[0] + '\n'
                err += '%s槽位CF卡退服。\n' % card_id
    else:
        logging.error('warn9没有找到CF卡信息')

    if err == '':
        err = 'CF卡状态正常'

    return (msg, err, check_item)

def mobile_warn11(res):
    '''地址池空闲值巡检'''

    err = ''
    msg = ''
    check_item = '地址池空闲值巡检'

    re_str = r'''(?s)(Pool name : (.*?)\n.*?Totals for pool\s{1,9}\d{2,5}\s{1,8}(\d{1,3})%)'''
    p_global_pool = r'(?s)DHCP server .{2,8}  router Base\n={79}.*?='
    p_vprn_pool = r'(?s)(DHCP server (\w{2,8})  router (\d{3,11})\n={79}.*?=)'
    p_totals = r'Totals for pool\s{1,9}\d{2,5}\s{1,8}(\d{1,3})%'
    p_pool_name = r'Pool name : (.*?)\n'
    re_obj = re.compile(re_str)

    res_vprn_pool = re.findall(p_vprn_pool, res)
    res_global_pool = re.search(p_global_pool, res)

    if res_global_pool:
        result = re_obj.findall(res_global_pool.group())

        for item in result:
            msg += item[0] + '\n'
            if int(item[2]) <= 20:
                err += '全局dhcp pool {} 地址池空闲值低于20%，空闲值：{}%\n'.format(item[1], int(item[2]))
            else:
                err += '全局dhcp pool {} 地址池空闲值正常\n'.format(item[1])

    for i in res_vprn_pool:
        msg += i[0] + '\n'
        res_pool_name = re.search(p_pool_name, i[0])
        res_totals = re.search(p_totals, i[0])
        if res_pool_name and res_totals:
            if int(res_totals.group(1)) <= 20:
                err += 'vprn {} server {} pool {} 地址池空闲值低于20%，空闲值：{}%\n'.format(i[2], i[1], res_pool_name.group(1), res_totals.group(1))
            else:
                err += 'vprn {} server {} pool {} 地址池空闲值正常\n'.format(i[2], i[1], res_pool_name.group(1))

    return (msg, err, check_item)

def mobile_warn12(res):
    '''NAT公网地址池空闲值巡检'''

    err = ''
    msg = ''
    check_item = 'NAT公网地址池空闲值巡检'

    re_str = r'''Block usage \(\%\)                       : (\d{1,3})'''
    re_obj = re.compile(re_str)
    result = re_obj.search(res)
    if result:
        msg = result.group()
        if int(result.group(1)) >= 90:
            err = 'NAT公网地址池空闲值低于10%，空闲值：{}%'.format(result.group(1))
    else:
        logging.error('warn12没有找到NAT公网地址池空闲值')

    if err == '' and result:
        err = 'NAT公网地址池空闲值巡检正常，空闲值：{}%'.format(result.group(1))

    return (msg, err, check_item)
def mobile_warn13(res):
    '''FTP状态检查'''

    err = ''
    msg = ''
    check_item = 'FTP状态检查'

    p_ftp_admin = r'Tel/Tel6/SSH/FTP Admin : (.*)\n'
    p_ftp_oper = r'Tel/Tel6/SSH/FTP Oper  : (.*)\n'
    obj_ftp_admin = re.compile(p_ftp_admin)
    obj_ftp_oper = re.compile(p_ftp_oper)

    res_ftp_admin = obj_ftp_admin.search(res)
    res_ftp_oper = obj_ftp_oper.search(res)

    if res_ftp_admin and res_ftp_oper:
        msg = res_ftp_admin.group() + '\n' + res_ftp_oper.group()

        admin_status = res_ftp_admin.group(1).split('/')
        oper_status = res_ftp_oper.group(1).split('/')

        if admin_status[-1] != 'Disabled' or oper_status[-1] != 'Down':
            err = 'FTP状态异常\n{}{}'.format(res_ftp_admin.group(), res_ftp_oper.group())

    if err == '':
        err = 'FTP关闭状态正常'

    return (msg, err, check_item)

def mobile_warn14(res):
    '''设备admin账号巡检'''

    err = ''
    msg = ''
    check_item = '设备admin账号巡检'
    if 'no user "admin"' not in res:
        err = '设备存在admin账号'

    if err == '':
        err = '巡检正常，admin账号不存在'

    return (msg, err, check_item)

def mobile_warn15(res):
    '''sfm检查
    状态应该都是UP'''

    err = ''
    msg = ''
    check_item = 'sfm检查'

    p_sfm = r'''(?s)(SFM Summary\n={79}.*?\n={79})'''
    p_sfm_state = r'(\d{1,2}         [-0-9a-z]{7,11} {30,35}([a-z]{2,5}) {1,4}([a-z]{2,5}))'

    res_sfm = re.search(p_sfm, res)
    if res_sfm:
        msg= res_sfm.group()
        res_sfm_state = re.findall(p_sfm_state, res)
        for item in res_sfm_state:
            if item[1] != 'up' or item[2] != 'up':
                err = 'sfm 状态异常'
                break
    else:
        logging.error('warn15没有找到sfm信息')

    if err == '':
        err = 'sfm 状态正常'

    return (msg, err, check_item)

def mobile_warn16(res):
    '''Subscriber Host超预警线检查
    检查tools dump system-resources命令输出结果
    中的Subscriber Hosts行，
    对应的Allocated值大于100K时，提示“Subscriber Host超预警线，需优化”'''

    err = ''
    msg = ''
    check_item = 'Subscriber Host超预警线检查'

    p_hardware_resource_sage = r'(?s)(Hardware Resource Usage for Slot #(\d{1,2}),.*?Egress TLS Mcast Entries \|[ 0-9]{11}\|[ 0-9]{11}\|[ 0-9]{11}\n)'
    p_hosts = r'(Subscriber Hosts - {1,10}\d{1,7}\| {5,10}(\d{1,6})\| {1,10}\d{1,7})'
    res_hardware_resource_sage = re.findall(p_hardware_resource_sage, res)
    # res_hosts = re.findall(p_hosts, res)

    for item in res_hardware_resource_sage:
        msg += item[0] + '\n'
        res_hosts = re.search(p_hosts, item[0])
        if res_hosts and int(res_hosts.group(2)) > 100000:
            err += 'tools dump system-resources Slot #{} Subscriber Host超预警线，需优化，Allocated：{}\n'.format(item[1] ,int(res_hosts.group(2)))
    else:
        logging.error('warn16没有找到Subscriber Hosts信息')

    if err == '':
        err = 'tools dump system-resources Subscriber Host 状态正常'

    return (msg, err, check_item)



def mobile_warn17(res):
    '''Total Subscribers 超预警线检查
    检查show subscriber-mgmt statistics iom all命令输出结果
    Total  Subscribers行中的，对应的Current值大于58K时，
    提示“Total Subscribers超预警线，需优化”'''

    err = ''
    msg = ''
    check_item = 'Total Subscribers 超预警线检查'

    p_iom = r'(Subscriber Management Statistics for IOM (\d{1,2}).*?Total  Subscribers {24,31}(\d{1,8}) .*?\n)'
    # p_total_subscribers = r'(Total  Subscribers {24,31}(\d{1,8}) )'
    res_total_subscribers = re.findall(p_iom, res)

    if res_total_subscribers == []:
        logging.error('warn17没有找到Total Subscribers信息')

    for item in res_total_subscribers:
        msg += item[0] + '\n'
        if int(item[2]) > 58000:
            err = 'show subscriber-mgmt statistics iom all IOM {} Total Subscribers超预警线，需优化，'\
                'Total Subscribers Current：{}\n'.format(item[1], int(item[2]))
            break
    
    if err == '':
        err = 'show subscriber-mgmt statistics iom all Subscriber Host 状态正常'

    return (msg, err, check_item)

def mobile_warn18(res):
    '''mda cpu利用率检查
    超过30%告警'''

    err = ''
    msg = ''
    check_item = 'mda cpu利用率检查'

    p_performance = r'(?s)(tools dump nat isa performance mda (\d/\d) last \d{1,3} hrs.*?Timestamp            \|     Wait     Idle     Work \| Total jobs \|    Total data.*?={79})'
    p_cpu = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})  \| {2,4}\d{1,3}\.\d{2}% {2,4}\d{1,3}\.\d{2}% {2,4}(\d{1,3}\.\d{2})%'

    res_performance = re.search(p_performance, res)
    if res_performance:
        res_cpu = re.findall(p_cpu, res_performance.group())
        for item in res_cpu:
            msg += item[0] + '\n'
            if float(item[1]) > 30:
                err = 'mda cpu 利用率高于30%，利用率高：{}'.format(float(item[1]))
    else:
        logging.error('warn18没有找到tools dump nat isa performance mda信息')
    
    if err == '':
        err = 'mda cpu 利用率正常'

    return (msg, err, check_item)

def mobile_warn19(res):
    '''检查nat Discards是否非0'''

    err = ''
    msg = ''
    check_item = 'nat Discards检查'
    p_out = r'(?s)(show port (\d{1,2}/\d{1,2})/nat\-in\-l2 detail .*?(Discards {34,47}(\d{1,14}) {9,22}(\d{1,14})))'
    p_in = r'(?s)(show port (\d{1,2}/\d{1,2})/nat\-out\-ip detail .*?(Discards {34,47}(\d{1,14}) {9,22}(\d{1,14})))'

    res_out = re.findall(p_out, res)
    res_in = re.findall(p_in, res)

    
    for item in res_out:
        msg += item[0] + '\n'
        if item[3] != '0' or item[4]!= '0':
            # msg += 'nat {} Discards {}     {}\n'.format(item[1], item[3], item[4])
            err = 'nat discards 不为0'
    for item in res_in:
        msg += item[0] + '\n'
        if item[3] != '0' or item[4]!= '0':
            # msg += 'nat {} Discards {}     {}\n'.format(item[1], item[3], item[4])
            err = 'nat discards 不为0'

    if err == '':
        err = 'nat discards正常'

    return (msg, err, check_item)

def mobile_warn20(res):
    '''config.cfg上次修改后是否为保存状态检查'''

    msg = ''
    err = ''
    check_item = 'config.cfg上次修改后是否为保存状态检查'

    p_save_time = r'Time Last Saved        : (.*?)\n'
    p_modified_time = r'Time Last Modified     : (.*?)\n'

    res_save_time = re.search(p_save_time, res)
    res_modified_time = re.search(p_modified_time, res)

    if res_save_time and res_modified_time:
        msg = res_save_time.group() + '\n' + res_modified_time.group()
        time_array = time.strptime(res_save_time.group(1), "%Y/%m/%d %H:%M:%S")
        save_time_timestamp = int(time.mktime(time_array))
        time_array = time.strptime(res_modified_time.group(1), "%Y/%m/%d %H:%M:%S")
        modified_time_timestamp = int(time.mktime(time_array))

        if modified_time_timestamp > save_time_timestamp:
            err = 'config.cfg上次修改后未做保存\n{}{}'.format(res_save_time.group(), res_modified_time.group())

    if err == '':
        err = 'config.cfg保存状态正常'

    return (msg, err, check_item)

def mobile_warn21(res):
    '''show time时间检查'''

    msg = ''
    err = ''
    check_item = 'show time时间检查'

    p_show_time = r'show time ?\n(.*?)\n'

    res_show_time = re.search(p_show_time, res)
    if res_show_time:
        msg = res_show_time.group()
        # gmt_format = '%a %b %d %H:%M:%S GMT8 %Y'
        # log_time = datetime.datetime.strptime(res_show_time.group(1), gmt_format)
        # now_time = datetime.datetime.now()

        # if (now_time - log_time).seconds > 300:
        #     err = '设备时间异常，设备时间：{}'.format(res_show_time.group(1))
        err = '设备时间正常：{}'.format(res_show_time.group(1))
    if err == '':
        err = '没有设备时间'

    return (msg, err, check_item)


def mobile_warn22(res, res_old):
    '''card状态巡检'''

    msg = ''
    err = ''
    check_item = 'card状态巡检'

    p_card = r'(?s)(={79}\nCard (\d{1,2})\n={79}.*?\n    Memory capacity {15}: [0-9,]{1,6} MB(.+?)\n=)'
    p_trap_raised = r'Trap raised (\d{1,7}) times;'
    p_temperature = r'Temperature                   : (\d{1,3})C'

    res_card = re.findall(p_card, res)
    res_card_old = re.findall(p_card, res_old)

    for i in zip(res_card, res_card_old):
        msg += i[0][0] + '\n'

        res_trap_raised = re.search(p_trap_raised, i[0][0])
        res_trap_raised_old = re.search(p_trap_raised, i[1][0])

        res_temperature = re.search(p_temperature, i[0][0])

        if res_trap_raised and res_trap_raised_old:
            if int(res_trap_raised.group(1)) > int(res_trap_raised_old.group(1)):
                err += 'Card {} 状态异常,比上一日增加{}次\n'.format(i[0][1], int(res_trap_raised.group(1)) - int(res_trap_raised_old.group(1)))


        res_temperature = re.search(p_temperature, i[0][0])
        if res_temperature and int(res_temperature.group(1)) >= 75:
            err += 'Card {} {}\n'.format(i[1], res_temperature.group())

    if err == '':
        err = '板卡状态正常，无板卡Errors告警'

    return (msg, err, check_item)

def mobile_warn23(res, res_old):
    '''MDA状态巡检'''

    msg = ''
    err = ''
    check_item = 'MDA状态巡检'

    if res_old == '':
        res_old = res

    p_mda = r'(?s)(={79}\nMDA (\d{1,2}/\d{1,2}) detail\n={79}.*?\n)='
    p_trap_raised = r'(?s)([ a-zA-Z]{3,12}) Errors:   Trap raised (\d{1,7}) times;'

    p_temperature = r'Temperature                   : (\d{1,3})C'

    res_mda = re.findall(p_mda, res)
    res_mda_old = re.findall(p_mda, res_old)

    for i in zip(res_mda, res_mda_old):
        msg += i[0][0] + '\n'

        res_trap_raised = re.search(p_trap_raised, i[0][0])
        res_trap_raised_old = re.search(p_trap_raised, i[1][0])

        res_temperature = re.search(p_temperature, i[0][0])

        if res_trap_raised and res_trap_raised_old:
            if int(res_trap_raised.group(2)) > int(res_trap_raised_old.group(2)):
                err += 'MDA {} 状态异常,{} Errors 比上一日增加{}次\n'.format(i[0][1], res_trap_raised.group(1), int(res_trap_raised.group(2)) - int(res_trap_raised_old.group(2)))

        if res_temperature and int(res_temperature.group(1)) > 75:
            err += 'MDA {} {}\n'.format(i[0][1], res_temperature.group())

    if err == '':
        err = 'MDA状态正常，无Errors告警'

    return (msg, err, check_item)

def mobile_warn24(res):
    '''路由器全局interface状态巡检'''

    msg = ''
    err = ''
    check_item = '路由器全局interface状态巡检'

    p_interface_table = r'(?s)Interface Table \(Router: Base\)\n={79}.*?\n='
    p_interface_state = r'((.*?)  (Up|Down) {6,8}(Up|Down)/(Up|Down) .*?\n)'

    res_interface_table = re.search(p_interface_table, res)
    if res_interface_table:
        msg = res_interface_table.group()
        res_interface_state = re.findall(p_interface_state, res_interface_table.group())

        for i in res_interface_state:
            if i[2] != 'Up' or i[3] != 'Up':
                err += 'interface {} 状态异常\n{}\n'.format(i[1], i[0])
    else:
        logging.error('没有找到Interface Table')

    if err == '':
        err = 'interface 状态正常'

    return (msg, err, check_item)

def mobile_warn25(res, res_old):
    '''port状态巡检'''

    msg = ''
    err = ''
    check_item = 'port状态巡检'

    if res_old == '':
        res_old = res

    p_interface = r'Interface {10}: (\d{1,2}/\d{1,2}/\d{1,2}) '
    p_tx_rx = r'Tx Output Power \(dBm\) {8,10}([+\-\.0-9]{4,6}).*?[+\-\.0-9]{4,6}.*?([+\-\.0-9]{4,6}).*?([+\-\.0-9]{4,6}).*?[+\-\.0-9]{4,6}.*?\nRx Optical Power \(avg dBm\)'\
    r' {3,5}([+\-\.0-9]{4,6}).*?[+\-\.0-9]{4,6}.*?([+\-\.0-9]{4,6}).*?([+\-\.0-9]{4,6}).*?[+\-\.0-9]{4,6}.*?\n'
    p_queue_statistics = r'(?s)Queue Statistics\n={79}.*?\n='
    p_per_threshold_mda_discard_statistics = r'(?s)Per Threshold MDA Discard Statistics\n={79}.*?\n='
    p_ethernet_like_medium_statistics = r'(?s)Ethernet-like Medium Statistics\n={79}.*?\n='
    ddm = r'                              Value High Alarm  High Warn   Low Warn  Low Alarm'
    p_traffic_statistics = r'(?s)Traffic Statistics\n={79}.*?\n={79}'
    p_utilization = r'Utilization \(300 seconds\) {24,26}(\d{1,3}\.\d{2})% {16,18}(\d{1,3}\.\d{2})%'

    #找到所有 Ethernet Interface
    start = 0
    indexs = []
    while start != -1:
        try:
            start = res.index('Ethernet Interface', start + 1)
            indexs.append(start)
        except ValueError:
            break

    if len(indexs) < 2:
        res_ethernet_interface = None
    else:
        res_ethernet_interface = res[indexs[0]:indexs[-1]].split('Ethernet Interface')[1:]

    start = 0
    indexs = []
    while start != -1:
        try:
            start = res_old.index('Ethernet Interface', start + 1)
            indexs.append(start)
        except ValueError:
            break

    if len(indexs) < 2:
        res_ethernet_interface_old = None
    else:
        res_ethernet_interface_old = res_old[indexs[0]:indexs[-1]].split('Ethernet Interface')[1:]

    if res_ethernet_interface and res_ethernet_interface_old:

        res_ethernet_interface_zip = zip(res_ethernet_interface, res_ethernet_interface_old)
        for i in res_ethernet_interface_zip:
            if 'Admin State        : up' not in i[0]:
                continue
            res_interface = re.search(p_interface, i[0])
            res_tx_rx = re.search(p_tx_rx, i[0])
            if res_tx_rx and res_interface:
                if float(res_tx_rx.group(1)) > float(res_tx_rx.group(2)) or float(res_tx_rx.group(1)) < float(res_tx_rx.group(3)):
                    err += 'port {} Tx Output Power 超限\n{}\n{}\n'.format(res_interface.group(1), ddm, res_tx_rx.group())
                    msg += 'port {} Tx Output Power Value: {}, High Warn: {}, Low Warn: {}\n'.format(res_interface.group(1),
                        res_tx_rx.group(1), res_tx_rx.group(2), res_tx_rx.group(3))
                if float(res_tx_rx.group(4)) > float(res_tx_rx.group(5)) or float(res_tx_rx.group(4)) < float(res_tx_rx.group(6)):
                    err += 'port {} Rx Optical Power 超限\n{}\n{}\n'.format(res_interface.group(1), ddm, res_tx_rx.group())
                    msg += 'port {} Tx Output Power Value: {}, High Warn: {}, Low Warn: {}\n'.format(res_interface.group(1),
                        res_tx_rx.group(4), res_tx_rx.group(5), res_tx_rx.group(6))
            else:
                logging.error('没有找到光功率信息')
                continue

            #检查 Ethernet-like Medium Statistics
            res_ethernet_like_medium_statistics = re.search(p_ethernet_like_medium_statistics, i[0])
            res_ethernet_like_medium_statistics_old = re.search(p_ethernet_like_medium_statistics, i[1])
            if res_ethernet_interface and res_ethernet_interface_old:
                p_ethernet_like = r' :([ 0-9]{20})'
                res_ethernet_like = re.findall(p_ethernet_like, res_ethernet_like_medium_statistics.group())
                res_ethernet_like_old = re.findall(p_ethernet_like, res_ethernet_like_medium_statistics_old.group())
                for j in zip(res_ethernet_like, res_ethernet_like_old):
                    if int(j[0].strip()) - int(j[1].strip()) > 0:
                        err += 'port {} Ethernet-like Medium Statistics 状态异常\n'.format(res_interface.group(1))
                        msg += 'port {}\n{}\n'.format(res_interface.group(1), res_ethernet_like_medium_statistics.group())
                        break
            else:
                logging.error('没有找到Ethernet-like Medium Statistics')
            
            #检查 Per Threshold MDA Discard Statistics
            res_per_threshold_mda_discard_statistics = re.search(p_per_threshold_mda_discard_statistics, i[0])
            res_per_threshold_mda_discard_statistics_old = re.search(p_per_threshold_mda_discard_statistics, i[1])
            if res_per_threshold_mda_discard_statistics and res_per_threshold_mda_discard_statistics_old:
                p_per_threshold = r'Threshold \d{1,2} Dropped : {2,11}(\d{1,9}) {13,23}(\d{1,10}) '

                res_per_threshold = re.findall(p_per_threshold, res_per_threshold_mda_discard_statistics.group())
                res_per_threshold_old = re.findall(p_per_threshold, res_per_threshold_mda_discard_statistics_old.group())

                for j in zip(res_per_threshold, res_per_threshold_old):
                    if int(j[0][0].strip()) - int(j[1][0].strip()) > 0 or int(j[0][1].strip()) - int(j[1][1].strip()) > 0:
                        err += 'port {} Per Threshold MDA Discard Statistics 状态异常\n'.format(res_interface.group(1))
                        msg += 'port {}\n{}\n'.format(res_interface.group(1), res_per_threshold_mda_discard_statistics.group())
                        break
            else:
                logging.error('没有找到Per Threshold MDA Discard Statistics')

            #检查 Queue Statistics
            res_queue_statistics = re.search(p_queue_statistics, i[0])
            res_queue_statistics_old = re.search(p_queue_statistics, i[1])
            if res_queue_statistics and res_queue_statistics_old:
                p_profile_dropped = r'In Profile dropped    : {1,4}(\d{1,3}) {13,23}\d{1,10}'
                p_prof_dropped = r'In/Inplus Prof dropped: {1,4}(\d{1,3}) {13,23}\d{1,10}'

                res_profile_dropped = re.findall(p_profile_dropped, res_queue_statistics.group())
                res_profile_dropped_old = re.findall(p_profile_dropped, res_queue_statistics_old.group())

                res_prof_dropped = re.findall(p_prof_dropped, res_queue_statistics.group())
                res_prof_dropped_old = re.findall(p_prof_dropped, res_queue_statistics_old.group())

                for j in zip(res_profile_dropped, res_profile_dropped_old):
                    if int(j[0].strip()) - int(j[1].strip()) > 0:
                        err += 'port {} In Profile dropped 状态异常\n'.format(res_interface.group(1))
                        msg += 'port {}\n{}\n'.format(res_interface.group(1), res_queue_statistics.group())
                        break

                for j in zip(res_prof_dropped, res_prof_dropped_old):
                    if int(j[0].strip()) - int(j[1].strip()) > 0:
                        err += 'port {} In/Inplus Prof dropped 状态异常\n'.format(res_interface.group(1))
                        msg += 'port {}\n{}\n'.format(res_interface.group(1), res_queue_statistics.group())
                        break

            #检查Traffic Statistics 端口流量占用率
            res_traffic_statistics = re.search(p_traffic_statistics, i[0])
            if res_traffic_statistics:
                res_utilization = re.search(p_utilization, res_traffic_statistics.group())
                if res_utilization:
                    if float(res_utilization.group(1)) > 60 or float(res_utilization.group(2)) > 60:
                        err += 'port {} Input/Output”占用率超60%\n'.format(res_interface.group(1))

    if err == '':
        err = 'port状态正常'

    return (msg, err, check_item)

def mobile_warn26(res):
    '''isis路由邻居状态巡检'''

    msg = ''
    err = ''
    check_item = 'isis路由邻居状态巡检'

    p_isis = r'(?s)Rtr Base ISIS Instance 0 Adjacency \n={79}\n.*?='
    p_state = r'((.*?) \w{2}    (Up|Down) .*?\n)'

    res_isis = re.search(p_isis, res)
    if res_isis:
        msg = res_isis.group()
        res_state = re.findall(p_state, res_isis.group())
        for i in res_state:
            if i[2] != 'Up':
                err += 'isis路由邻居状态异常：{}\n'.format(i[0])
                break
    else:
        logging.error('没有找到Rtr Base ISIS Instance 0 Adjacency')

    if err == '':
        err = 'isis路由邻居状态正常'

    return (msg, err, check_item)


def mobile_warn27(res):
    '''缺省路由状态巡检'''

    msg = ''
    err = ''
    check_item = '缺省路由状态巡检'

    p_route_table = r'(?s)show router route-table 0\.0\.0\.0\n.*?\n\*'
    p_state = r'(0\.0\.0\.0/0 {36,40}([a-zA-Z]{3,10})  ([A-Z]{3,5}) {5,7}\w{9}  (\d{2,4}))'

    res_route_table = re.search(p_route_table, res)
    if res_route_table:
        msg = res_route_table.group()
        res_state = re.findall(p_state, res_route_table.group())
        for i in res_state:
            if i[1] != 'Remote' or i[2] != 'BGP' or i[3] != '100':
                err = '缺省路由状态异常：{}\n'.format(i[0])
                break
    else:
        logging.error('没有找到route-table')

    if err == '':
        err = '缺省路由状态正常，由BGP协议获取'

    return (msg, err, check_item)


def mobile_warn28(res):
    '''BGP邻居状态巡检'''

    msg = ''
    err = ''
    check_item = 'BGP邻居状态巡检'

    p_bgp_neighbor = r'(?s)BGP Neighbor\n={79}.*?\n='
    p_state = r'(State                : ([a-zA-Z]{2,15}) )'

    res_bgp_neighbor = re.search(p_bgp_neighbor, res)
    if res_bgp_neighbor:
        msg = res_bgp_neighbor.group()
        res_state = re.findall(p_state, res_bgp_neighbor.group())
        for i in res_state:
            if i[1] != 'Established':
                err += 'BGP邻居状态异常：{}\n'.format(i[0])
                break
    else:
        logging.error('没有找到BGP Neighbor')

    if err == '':
        err = 'BGP邻居状态正常'

    return (msg, err, check_item)


def mobile_warn29(res):
    '''mpls interface状态巡检'''

    msg = ''
    err = ''
    check_item = 'mpls interface状态巡检'

    p_mpls_interfaces = r'(?s)MPLS Interfaces\n={79}.*?\n='
    p_state = r'((.*?) .{3,8} {8,15}(Up|Down)     (Up|Down) )'

    res_mpls_interfaces = re.search(p_mpls_interfaces, res)
    if res_mpls_interfaces:
        msg = res_mpls_interfaces.group()
        res_state = re.findall(p_state, res_mpls_interfaces.group())
        for i in res_state:
            if i[2] != 'Up' or i[3] != 'Up':
                err = 'mpls interface状态异常：{}\n'.format(i[0])
                break
    else:
        logging.error('没有找到mpls interface')

    if err == '':
        err = 'mpls interface状态正常'

    return (msg, err, check_item)

def mobile_warn30(res):
    '''ldp session状态巡检'''

    msg = ''
    err = ''
    check_item = 'ldp session状态巡检'

    p_ldp_session = r'(?s)Peer LDP Id         Adj Type  State         Msg Sent  Msg Recv  Up Time\n-{78}.*?-'
    p_state = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,3} {2,11}(Targeted|Link) {2,6}(\w{3,12}) .*?\n)'

    res_ldp_session = re.search(p_ldp_session, res)
    if res_ldp_session:
        msg = res_ldp_session.group()
        res_state = re.findall(p_state, res_ldp_session.group())
        for i in res_state:
            if i[2] != 'Established':
                err = 'ldp session状态异常：{}\n'.format(i[0])
                break
    else:
        logging.error('没有找到ldp session')

    if err == '':
        err = 'ldp session状态正常'

    return (msg, err, check_item)

def mobile_warn31(res):
    '''system-resources巡检'''

    msg = ''
    err = ''
    check_item = 'system-resources巡检'

    # p_hardware_resource_sage = r'(?s)(Hardware Resource Usage for Slot.*?Egress TLS Mcast Entries \|[ 0-9]{11}\|[ 0-9]{11}\|[ 0-9]{11}\n)'
    p_hardware_resource_sage = r'(?s)(Hardware Resource Usage for Slot #(\d{1,2}),.*?Egress TLS Mcast Entries \|[ 0-9]{11}\|[ 0-9]{11}\|[ 0-9]{11}\n)'
    p_dynamic_queues = r'Dynamic Queues \+ {2,10}(\d{1,7})\| {3,9}(\d{1,7})\| '
    p_subscriber_hosts = r'Subscriber Hosts - {2,10}(\d{1,7})\| {3,11}(\d{1,7})\| '
    p_ingress_policer_stats = r'Ingress Policer Stats \|([ 0-9]{11})\|([ 0-9]{11})\|'
    p_egress_policer_stats = r'Egress Policer Stats \|([ 0-9]{11})\|([ 0-9]{11})\|'


    res_hardware_resource_sage = re.findall(p_hardware_resource_sage, res)

    for i in res_hardware_resource_sage:

        res_dynamic_queues = re.search(p_dynamic_queues, i[0])
        res_subscriber_hosts = re.search(p_subscriber_hosts, i[0])
        res_ingress_policer_stats = re.search(p_ingress_policer_stats, i[0])
        res_egress_policer_stats = re.search(p_egress_policer_stats, i[0])

        if res_dynamic_queues and int(res_dynamic_queues.group(2))/int(res_dynamic_queues.group(1)) >= 0.8:
            msg = i[0] + '\n'
            err = 'system-resources Slot #{} Dynamic Queues 资源状态异常：{}%\n'.format(i[1] ,res_dynamic_queues.group())

        if res_subscriber_hosts and int(res_subscriber_hosts.group(2))/int(res_subscriber_hosts.group(1)) >= 0.8:
                err = 'system-resources Slot #{} Subscriber Hosts 资源状态异常：{}\n'.format(i[1] ,res_subscriber_hosts.group())

        if res_ingress_policer_stats and int(res_ingress_policer_stats.group(2))/int(res_ingress_policer_stats.group(1)) >= 0.8:
            err += 'system-resources Slot #{} Ingress Policer Stats 资源状态异常：{}\n'.format(i[1], res_ingress_policer_stats.group())

        if res_egress_policer_stats and int(res_egress_policer_stats.group(2))/int(res_egress_policer_stats.group(1)) >= 0.8:
            err += 'system-resources Slot #{} Egress Policer Stats 资源状态异常：{}\n'.format(i[1], res_egress_policer_stats.group())

    if err == '':
        err = 'system-resources状态正常'

    return (msg, err, check_item)

def mobile_warn32(config, config_old):

    msg = ''
    err = ''
    check_item = 'pppoe端口用户数比上一日异常检查'

    p_total = r'(?s)(Subscriber Management Statistics for Port (\d{1,2}/\d{1,2}/\d{1,2}).*?Total  PPP Hosts([ 0-9]{34})([ 0-9]{9}) .*?\n'\
        ' {7}IPOE Hosts([ 0-9]{33})([ 0-9]{9}) .*?\n'\
        ' {7}IPv4 Hosts([ 0-9]{33})([ 0-9]{9}) .*?\n'\
        ' {7}IPv6 Hosts([ 0-9]{33})([ 0-9]{9}) )'

    res_total = sorted(list(set(re.findall(p_total, config))))

    for i in res_total:
        port = i[1]
        p_port_total = r'(?s)(Subscriber Management Statistics for Port @@.*?Total  PPP Hosts([ 0-9]{34})([ 0-9]{9}) .*?\n'\
        ' {7}IPOE Hosts([ 0-9]{33})([ 0-9]{9}) .*?\n'\
        ' {7}IPv4 Hosts([ 0-9]{33})([ 0-9]{9}) .*?\n'\
        ' {7}IPv6 Hosts([ 0-9]{33})([ 0-9]{9}) )'.replace('@@', port)

        res_port_total = re.search(p_port_total, config_old)
        if res_port_total and i[2] != '0' and res_port_total.group(1) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[3] != '0' and res_port_total.group(2) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[4] != '0' and res_port_total.group(3) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[5] != '0' and res_port_total.group(4) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[6] != '0' and res_port_total.group(5) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[7] != '0' and res_port_total.group(6) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[8] != '0' and res_port_total.group(7) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue

        if res_port_total and i[9] != '0' and res_port_total.group(8) == '0':
            err += 'port {} 下ppp 用户数异常，请检查核实\n'.format(port)
            continue


    if err == '':
        err = 'PPP 用户数正常'

    return (msg, err, check_item)


def mobile_warn33(config):
    msg = ''
    err = ''
    check_item = 'Nat地址资源利用率状态'

    p_nat_pppoe= r'(?s)NAT Pool nat-pppoe\n={79}.*?='
    p_nat_iptv= r'(?s)NAT Pool nat-iptv\n={79}.*?='
    p_usage = r'Block usage \(%\)                       : (< )?(\d{1,3})'

    res_nat_pppoe = re.search(p_nat_pppoe, config)
    res_nat_iptv = re.search(p_nat_iptv, config)

    if res_nat_pppoe:
        msg += res_nat_pppoe.group() + '\n'
        res_usage = re.search(p_usage, res_nat_pppoe.group())

        if res_usage and int(res_usage.group(2)) >= 60:
            err += 'nat pool "nat-pppoe" 地址利用率大于60%：{}\n'.format(res_usage.group())
        else:
            err += 'nat pool "nat-pppoe" 地址利用率状态正常：{}\n'.format(res_usage.group())

    if res_nat_iptv:
        msg += res_nat_iptv.group() + '\n'
        res_usage = re.search(p_usage, res_nat_iptv.group())

        if res_usage and int(res_usage.group(2)) >= 60:
            err += 'nat pool "nat-iptv" 地址利用率大于60%：{}\n'.format(res_usage.group())
        else:
            err += 'nat pool "nat-iptv" 地址利用率状态正常：{}\n'.format(res_usage.group())

    return (msg, err, check_item)

 