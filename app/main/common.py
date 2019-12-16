import os, datetime, logging, re
from .config import CITY, g_log_path

def get_host(city):
    '''获取设备列表'''

    host_data = []
    for _,dirs,_ in os.walk(os.path.join(g_log_path, city)):
        host_data = dirs
        break

    return host_data

def get_log(city, host):
    '''根据节点，设备名称， 日期获取log'''

    log_str = ''
    logs = []

    logs = get_host_logs(city, host)

    for i in logs:
        if is_today_log(i):
            log_str = open(os.path.join(g_log_path, city, host, i)).read()
            break
    
    if not log_str:
        logging.error('host: {} today log not found'.format(host))

    return log_str

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