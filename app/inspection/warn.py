# -*- coding: utf-8 -*-
import datetime
import re
import logging

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

def warn_find_all(res, re_str):
    re_obj = re.compile(re_str)
    result = re_obj.findall(res)
    return result

def mobile_warn1(res):
    # re_str = r'''(Fan tray number                   : (\d)
    # Speed                           : (\w{3,4} speed( \(0-\d\d%\))?)
    # Status                          : (\w{2,5}))'''

    re_str = r'''(Fan tray number                   : (\d)
    Speed                           : (\d{1,3} %|\w{3,4} speed( \(0-\d\d%\))?)
    Status                          : (\w{2,5}))'''

    re_obj = re.compile(re_str)
    result = re_obj.findall(res)

    msg = ''
    atn = ''
    if result:
        for item in result:
            if item[2] == 'half speed':
                pass
            elif item[2] == 'full speed':
                msg += 'Fan tray number: %s\nSpeed: full speed\n' % item[1]
                atn += '风扇%s全转速，建议清洗滤尘网。' % item[1]
            elif 'speed' not in item[2]:
                if int(item[2][:-2]) >= 50:
                    msg += 'Fan tray number: %s\nSpeed: %s\n' % (item[1], item[2])
                    atn += '风扇%s转速大于50。' % item[1]
            elif int(item[3][-4:-2]) >= 50:
                msg += 'Fan tray number: %s\nSpeed: %s\n' % (item[1], item[2])
                atn += '风扇%s转速大于50。' % item[1]
            elif item[4] != 'up':
                msg += 'Fan tray number: %s\nStatus: %s\n' % item[4]
                atn += '风扇%s状态不正常。' % item[1]
        return(msg, atn)
    else:
        logging.error('没有找到风扇信息')
        return ('','')

def mobile_warn2(res):
    re_str = r'''(Power supply number               : \d
    Defaulted power supply type     : .{2,10}
    Power supply model              : .{2,10}
    Status                          : (.{2,10}))'''

    re_obj = re.compile(re_str)
    result = re_obj.findall(res)

    msg = ''

    if result:
        for item in result:
            if item[1] != 'up':
                msg += item[0] + '\n'
        
        return(msg, '电源异常。')
    else:
        logging.error('没有找到电源信息')
        return ('','')

def mobile_warn3(res):
    re_str = r'''(Critical LED state                : (.{2,10})
  Major LED state                   : (.{2,10})
  Minor LED state                   : (.{2,10}))'''

    re_obj = re.compile(re_str)     
    result = re_obj.findall(res)

    msg = ''

    if result:
        for item in result:
            if item[1] != 'Off' or item[2] != 'Off' or item[3] != 'Off':
                msg += item[0] + '\n'
        
        return(msg, '主控指示灯告警')
    else:
        logging.error('没有找到主控指示灯信息')
        return ('','')

def mobile_warn4(res):
    re_str = r'''Total {30,41}[,0-9]{1,11} {9,11}\d{1,3}\.\d\d%                
   Idle {30,41}[,0-9]{1,11} {9,11}(\d{1,3})\.\d\d%                
   Usage {30,41}[,0-9]{1,11} {9,11}\d{1,3}\.\d\d%'''
    re_obj = re.compile(re_str)
    result = re_obj.search(res)
    msg = ''
    if result:
        if int(result.group(1)) < 50:
            msg += result.group() + '\n'

        return (msg, 'cpu利用率高。')
    else:
        logging.error('warn4没有找到cpu利用率')
        return ('','')

def mobile_warn5(res):
    re_str = '''Current Total Size :    (.{10,15}) bytes
Total In Use       :    (.{10,15}) bytes
Available Memory   :   (.{10,15}) bytes'''
    re_obj = re.compile(re_str)
    result = re_obj.search(res)
    msg = ''
    if result:
        current_sotal_size = int(result.group(1).replace(',', ''))
        total_in_use = int(result.group(2).replace(',', ''))
        available_memory = int(result.group(3).replace(',', ''))
        logging.debug('current_sotal_size=%s, total_in_use=%s, available_memory=%s' % (current_sotal_size, total_in_use, available_memory))
        if available_memory < 2*(current_sotal_size + total_in_use):
            msg += result.group() + '\n'

        return (msg, '内存利用率高。')
    else:
        logging.error('warn5没有找到内存利用率')
        return ('','')


def mobile_warn6(res):
    re_str = r'''((Dynamic|Ingress|Egress) Queues (\+|\|)\s{1,11}\d{2,10}\|\s{1,11}(\d{2,10})\|\s{1,11}(\d{2,10}))'''
    re_obj = re.compile(re_str)     
    result = re_obj.findall(res)
    msg = ''
    if result:
        for item in result:
            if int(item[4]) < int(item[3]):
                msg += item[0] + '\n'
        
        return (msg, '空闲队列资源不足。')
    else:
        logging.error('warn6没有找到空闲队列资源')
        return ('','')



def mobile_warn7(res):
    re_str = '''FCS Errors'''

    re_obj = re.compile(re_str)     
    result = re_obj.findall(res)
    
    if result:
        return('FCS Errors', 'FCS Errors告警。')
    else:
        return ('','')


def mobile_warn8(res):
    # re_str = r'''(Temperature                   : (\d\d)C)'''
    p_mda = r'(?s)(MDA (\d/\d) detail\n.*?(\w{2,4}-\w{2,4}-\w{2,4}) .*?Temperature                   : (\d{1,3})C)'
    res_mda = re.findall(p_mda, res)
    msg = ''
    if res_mda:
        for item in res_mda:
            if int(item[3]) > 62:
                msg += 'MDA {} {} Temperature                   : {}C\n'.format(item[1], item[2], item[3])
        
        return (msg, '板卡温度高，建议清洗防尘网，若清洗之后还没变化或建议降低机房环境温度。')
    else:
        logging.error('warn8没有找到板卡温度')
        return ('','')



def mobile_warn9(res):
    re_str = r'''Flash - cf3:
    Administrative State          : [a-zA-Z]{2,4}
    (Operational state             : ([a-zA-Z]{2,4}))'''

    re_obj = re.compile(re_str)     
    result = re_obj.findall(res)
    msg = ''
    atn = '注：'
    if result:
        for index, item in enumerate(result):
            if item[1] != 'up':
                card_id = 'A'
                if index == 1:
                    card_id = 'B'
                msg += item[0] + '\n'
                atn += '%s槽位CF卡退服。' % card_id
        return (msg, atn)
    else:
        logging.error('warn9没有找到CF卡信息')
        return ('','')

def mobile_warn11(res):
    re_str = r'''(Totals for pool\s{1,9}\d{2,5}\s{1,8}(\d{1,3})%)'''

    re_obj = re.compile(re_str)     
    result = re_obj.findall(res)
    msg = ''
    if result:
        for item in result:
            if int(item[1]) <= 20:
                msg += item[0] + '\n'
        
        return (msg, '地址池空闲值低于20%。')
    else:
        logging.error('warn11没有找到地址池空闲值')
        return ('','')

def mobile_warn12(res):
    re_str = r'''Block usage \(\%\)                       : (\d{1,3})'''
    re_obj = re.compile(re_str)
    result = re_obj.search(res)
    msg = ''
    if result:
        if int(result.group(1)) >= 90:
            msg += result.group() + '\n'

        return (msg, 'NAT公网地址池空闲值低于10%。')
    else:
        logging.error('warn12没有找到NAT公网地址池空闲值')
        return ('','')

def mobile_warn13(res):
    p_ftp = r'Tel/Tel6/SSH/FTP Admin : (.*)\n'
    obj_ftp = re.compile(p_ftp)

    res_ftp = obj_ftp.search(res)
    if res_ftp == None:
        logging.error('warn13没有找到ftp配置')
    else:
        res = res_ftp.group(1).split('/')
        if len(res) != 4:
            logging.error('ftp配置解析错误')
        else:
            if 'Disabled' not in res[-1]:
                logging.debug(res_ftp.group())
                return (res_ftp.group(), '注释：ftp没有关闭')

    return ('', '')

def mobile_warn14(res):
    if 'no user "admin"' not in res:
        return (' ', '设备存在admin账号')

    return ('', '')

def mobile_warn15(res):
    '''sfm检查
    状态应该都是UP'''

    msg = ''
    p_sfm = r'''(?s)(SFM Summary\n={79}.*?\n={79})'''
    p_sfm_state = r'(\d{1,2}         [-0-9a-z]{7,11} {30,35}([a-z]{2,5}) {1,4}([a-z]{2,5}))'

    res_sfm = re.search(p_sfm, res)
    if res_sfm:
        res_sfm_state = re.findall(p_sfm_state, res)
        for item in res_sfm_state:
            if item[1] != 'up' or item[2] != 'up':
                msg += item[0] + '\n'
    else:
        logging.error('warn15没有找到sfm信息')
        return ('','')

    if msg != '':
        return (msg, 'sfm 状态异常')

    return ('', '')

def mobile_warn16(res):
    '''Subscriber Host超预警线检查
    检查tools dump system-resources命令输出结果
    中的Subscriber Hosts行，
    对应的Allocated值大于100K时，提示“Subscriber Host超预警线，需优化”'''

    msg = ''
    p_hosts = r'(Subscriber Hosts - {1,10}\d{1,7}\| {5,10}(\d{1,6})\| {1,10}\d{1,7})'
    res_hosts = re.findall(p_hosts, res)
    if res_hosts:
        for item in res_hosts:
            if int(item[1]) > 100000:
                msg += item[0] + '\n'
    else:
        logging.error('warn16没有找到Subscriber Hosts信息')

    if msg != '':
        return (msg, 'Subscriber Host超预警线，需优化')

    return ('', '')


def mobile_warn17(res):
    '''Total Subscribers 超预警线检查
    检查show subscriber-mgmt statistics iom all命令输出结果
    Total  Subscribers行中的，对应的Current值大于58K时，
    提示“Total Subscribers超预警线，需优化”'''

    msg = ''
    p_total_subscribers = r'(Total  Subscribers {24,31}(\d{1,8}) )'
    res_total_subscribers = re.findall(p_total_subscribers, res)

    if res_total_subscribers == []:
        logging.error('warn17没有找到Total Subscribers信息')

    for item in res_total_subscribers:
        if int(item[1]) > 58000:
            msg += item[0] + '\n'
    
    if msg != '':
        return (msg, 'Total Subscribers超预警线，需优化')

    return ('', '')

def mobile_warn18(res):
    '''检查mda cpu利用率
    超过30%告警'''

    msg = ''
    p_performance = r'(?s)(tools dump nat isa performance mda (\d/\d) last \d{1,3} hrs.*?Timestamp            \|     Wait     Idle     Work \| Total jobs \|    Total data.*?={79})'
    p_cpu = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})  \| {2,4}\d{1,3}\.\d{2}% {2,4}\d{1,3}\.\d{2}% {2,4}(\d{1,3}\.\d{2})%'

    res_performance = re.search(p_performance, res)
    if res_performance:
        res_cpu = re.findall(p_cpu, res_performance.group())
        for item in res_cpu:
            if float(item[1]) > 30:
                msg += 'nat {} {} cpu 使用率 {}%\n'.format(res_performance.group(2), item[0], item[1])
    else:
        logging.error('warn18没有找到tools dump nat isa performance mda信息')
    
    if msg != '':
        return (msg, 'mda cpu 利用率高于30%')

    return ('', '')

def mobile_warn19(res):
    '''检查nat Discards是否非0'''

    msg = ''
    p_out = r'(?s)(show port (\d{1,2}/\d{1,2})/nat\-in\-l2 detail .*?(Discards {34,47}(\d{1,14}) {9,22}(\d{1,14})))'
    p_in = r'(?s)(show port (\d{1,2}/\d{1,2})/nat\-out\-ip detail .*?(Discards {34,47}(\d{1,14}) {9,22}(\d{1,14})))'

    res_out = re.findall(p_out, res)
    res_in = re.findall(p_in, res)

    
    for item in res_out:
        if item[3] != '0' or item[4]!= '0':
            msg += 'nat {} Discards {}     {}\n'.format(item[1], item[3], item[4])

    for item in res_in:
        if item[3] != '0' or item[4]!= '0':
            msg += 'nat {} Discards {}     {}\n'.format(item[1], item[3], item[4])

    if msg != '':
        return (msg, 'nat discards 不为0')

    return ('', '')


def warn1(res):
    str1 = ''
    str2 = ''
    b = res.split('-------------------------------------------------------------------------------')
    if len(b) < 2:
        logging.error('warn1没有找到风扇信息')
        return ('', '')
    re_obj = re.compile(r'Fan tray number                   : (\d)')
    result = re_obj.findall(b[1])
    re_obj2 = re.compile(r'Speed                           : (.*)\n')
    result2 = re_obj2.findall(b[1])

    if not result or not result2:
        return ('', '')

    fan_list = []
    for i in range(len(result2)):
        if result2[i].strip('\r\n') == 'full speed':
            fan_list.append(result[i])
    if fan_list:
        str1 = '1.Environment Information\nFan tray number ：' + ','.join(fan_list) + ' full speed'
        str2 = '%s个风扇满运行，建议降低机房温度或更换增强型风扇' % str(len(result))

    return (str1, str2)


def warn2(res):

    #先判断是否为mda卡
    mda_obj = re.compile(r'MDA (.*) detail')
    result_mda = mda_obj.findall(res)

    result1 = None
    result2 = None
    if result_mda:
        re_obj1 = re.compile(r'(\d?\d)?\s{4,5}(\d)\s{5}(.*)\s+up        up')
    else:
        re_obj1 = re.compile(r'(\w?\w)?\s{5,6}(.*)\s+up    up')

    result1 = re_obj1.findall(res)
    re_obj2 = re.compile(r'Temperature                   : (\d\d)C')
    result2 = re_obj2.findall(res)

    if not result1 or not result2:
        logging.error('warn2没有找到板卡温度')
        return ('', '')

    dict1 = dict(zip(result2, result1))
    str1 = ''

    for key,val in dict1.items():
        if int(key) >= 63:
            if result_mda:
                if ('imm12' in val[2] or 'imm48' in val[2]) and int(key) < 65:
                    continue
                str1 += 'mda %s/%s     %s\nTemperature        : %sC\n' % (val[0], val[1], val[2].strip(), key)
            else:
                if ('imm12' in val[1] or 'imm48' in val[1]) and int(key) < 65:
                    continue
                str1 += 'Card %s     %s\nTemperature        : %sC\n' % (val[0], val[1].strip(), key)

    str2 = '注释：板卡温度过高，建议清洗滤网。'
    if result_mda:
        str2 = 'mda' + str2 
    
    return (str1, str2)

def warn3(res):
    err_sum = 0
    re_obj1 = re.compile(r'(XPL Errors:   Trap raised \d{1,6} times;   Last Trap (\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}))')
    result1 = re_obj1.findall(res)
    if not result1:
        return ('', '')
    str1 = ''
    datetime_15d_ago = datetime.datetime.now() - datetime.timedelta(days=15)
    for item in result1:
        datetime_befor = datetime.datetime(int(item[3]), int(item[1]), 
            int(item[2]), int(item[4]), int(item[5]), int(item[6]))

        if datetime_befor > datetime_15d_ago:
            err_sum += 1
            str1 += item[0] + '\n'
    #告警在5次以内忽略
    if str1 and err_sum > 5:
        return (str1, '注释：XPL 告警，建议拔插处理，如继续存在，建议更换板卡')
   
    return ('', '')

def warn4(res):
    re_obj2 = re.compile(r'(\d{6} (\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})\.\d{2} GMT8 MINOR: PORT #\d{4} Base Port (\d/\d/\d)\s+"SFF DDM \(rxOpticalPower-(low|high)-alarm\) \w+")')
    result2 = re_obj2.findall(res)

    if not result2:
        return ('', '')
    
    # str1 = '高' if result1.group(0) == 'high' else '低'
    str2 = ''
    datetime_15d_ago = datetime.datetime.now() - datetime.timedelta(days=15)

    port = []
    for item in result2:
        datetime_befor = datetime.datetime(int(item[1]), int(item[2]), 
            int(item[3]), int(item[4]), int(item[5]), int(item[6]))
            
        if datetime_befor > datetime_15d_ago and item[7] not in port:
            str2 += item[0] + '\n'
            port.append(item[7])

    return(str2, '注释：端口收光告警,建议检查光路')

def warn5(res):
    err_sum = 0
    re_obj1 = re.compile(r'((Q|P)chip Errors Detected\n\s{4}Complex \d \(parity error\): Trap raised \d{1,6} times; Last Trap (\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2}))')
    result1 = re_obj1.findall(res)
    if not result1:
        return ('', '')
    str1 = ''
    warn_type = 'P'
    datetime_15d_ago = datetime.datetime.now() - datetime.timedelta(days=15)
    for item in result1:
        datetime_befor = datetime.datetime(int(item[4]), int(item[2]), 
            int(item[3]), int(item[5]), int(item[6]), int(item[7]))

        if datetime_befor > datetime_15d_ago:
            str1 += item[0] + '\n'
            err_sum += 1
        warn_type = item[1]

    if str1 and err_sum > 5:
        return (str1, '注释：%schip 告警，建议拔插处理，如继续存在，建议更换板卡' % warn_type)
   
    return ('', '')

def warn6(res):
    p_ftp = r'Tel/Tel6/SSH/FTP Admin : (.*)\n'
    obj_ftp = re.compile(p_ftp)

    res_ftp = obj_ftp.search(res)
    if res_ftp == None:
        logging.debug('warn6没有找到ftp配置')
    else:
        res = res_ftp.group(1).split('/')
        if len(res) != 4:
            logging.debug('ftp配置解析错误')
        else:
            if 'Disabled' not in res[-1]:
                logging.debug(res_ftp.group())
                return (res_ftp.group(), '注释：ftp没有关闭')

    return ('', '')

def warn7(res):
    if 'no user "admin"' not in res:
        return (' ', '注释：user 账号是 admin')

    return ('', '')

def warn8(res):
    '''sfm检查
    状态应该都是UP'''

    return mobile_warn15(res)

def warn9(res):
    '''Subscriber Host超预警线检查'''

    return mobile_warn16(res)

def warn10(res):
    '''Total Subscribers超预警线检查'''

    return mobile_warn17(res)

def warn11(res):
    '''mda cpu利用率检查'''

    return mobile_warn8(res)

def warn12(res):
    '''nat discards检查'''

    return mobile_warn19(res)