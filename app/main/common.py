import os, datetime, logging, re
import openpyxl
from openpyxl.styles import Alignment, PatternFill
from .config import g_log_path
from .ftp import myFtp

def get_host(city):
    '''获取设备列表'''

    host_data = []
    for _,dirs,_ in os.walk(os.path.join(g_log_path, city)):
        host_data = dirs
        break

    return host_data

def get_log_from_ftp(host_name, save_path):
    '''从ftp服务器获取log'''
    ftp = myFtp('211.138.102.229')
    ftp.Login('ftp-asb', 'Asb201730')
    log_name = ftp.DownLoadFileFromName(host_name, save_path, '/home/ftp-asb/js/')  # 从目标目录下载到本地目录d盘
    return log_name


def get_log(city, host, date = None):
    '''根据节点，设备名称， 日期获取log'''

    log_str = ''
    logs = []

    logs = get_host_logs(city, host)

    for i in logs:
        if date != None:
            if is_yesday_log(i):
                log_str = open(os.path.join(g_log_path, city, host, i)).read()
                if len(log_str) < 100:
                    log_str = ''
                else:
                    break
        else:
            if is_today_log(i):
                log_str = open(os.path.join(g_log_path, city, host, i)).read()
                if len(log_str) < 100:
                    log_str = ''
                else:
                    break
    
    if not log_str and not date:
        logging.error('host: {} today log not found'.format(host))
        logging.error('begin download log from ftp server')

        save_path = os.path.join(os.getcwd() ,'app', 'static', 'logs', city, host)
        log_name = get_log_from_ftp(host, save_path)
        if log_name:
            log_str = open(os.path.join(g_log_path, city, host, log_name)).read()

    return log_str

def get_log_from_date(city, host, date):
    '''根据设备名和日期获取log'''

    p_log_datetime = r'7750_(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-UTC'
    logs = get_host_logs(city, host)
    
    for i in logs:
        res = re.search(p_log_datetime, i)
        real_date_time = datetime.datetime(int(res.group(1)), int(res.group(2)), int(res.group(3)), \
            int(res.group(4)), int(res.group(5)), int(res.group(6))) + datetime.timedelta(hours=8)

        real_date_str = real_date_time.strftime('%Y-%m-%d')
        if real_date_str == date:
            log_str = open(os.path.join(g_log_path, city, host, i)).read()
            return log_str

    return ''

def get_today_log_name(city, host):
    '''根据设备名称生成当天log名称'''

    today = datetime.date.today()
    date = today.strftime('%Y%m%d')
    logs = get_host_logs(city, host)
    for i in logs:
        if date in i:
            return i

    return None

def get_host_logs(city, host):
    '''获取指定设备的所有log'''

    logs = []
    for _, _, files in os.walk(os.path.join(g_log_path, city, host)):
        logs = files
        break

    return logs

def get_city_list():
    '''获取城市列表'''
    city_list = []
    for _, dirs, _ in os.walk(g_log_path):
        city_list = dirs
        break

    return city_list

def is_today_log(log_name):
    '''判断Log日期是否为今天
    将当前日期加八个小时'''

    p_log_datetime = r'7750_(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-UTC'
    res = re.search(p_log_datetime, log_name)
    real_date_time = datetime.datetime(int(res.group(1)), int(res.group(2)), int(res.group(3)), \
        int(res.group(4)), int(res.group(5)), int(res.group(6))) + datetime.timedelta(hours=8)

    today_time = datetime.datetime.now()

    if today_time.strftime('%y/%m/%d') == real_date_time.strftime('%y/%m/%d'):
        return True
    else:
        return False

def is_yesday_log(log_name):
    '''判断Log日期是否为昨天
    将当前日期加八个小时'''

    p_log_datetime = r'7750_(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})-UTC'
    res = re.search(p_log_datetime, log_name)
    real_date_time = datetime.datetime(int(res.group(1)), int(res.group(2)), int(res.group(3)), \
        int(res.group(4)), int(res.group(5)), int(res.group(6))) + datetime.timedelta(hours=8) + datetime.timedelta(days=1)

    today_time = datetime.datetime.now()

    if today_time.strftime('%y/%m/%d') == real_date_time.strftime('%y/%m/%d'):
        return True
    else:
        return False


def make_excel(file_name, labels, data):
    '''根据参数生成表格'''

    letters = [
        'A','B','C','D','E','F','G','H','I',
        'J','K','L','M','N','O','P''Q','R',
        'S','T','U','V','W','X','Y','Z'
    ]
    excel = openpyxl.Workbook()
    sheet = excel.active
    for index, label in enumerate(labels):
        sheet['{}1'.format(letters[index])] = label

    # sheet.column_dimensions['A'].width = 40.0
    cur_row = 2

    for item in data:
        for index, j in enumerate(item):
            sheet[letters[index] + str(cur_row)] = j

        cur_row += 1
    
    excel.save(file_name)
