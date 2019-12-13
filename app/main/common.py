import os, datetime, logging, re
from .config import CITY, g_log_path

def get_node(city):
    '''获取节点列表'''

    node_data = []
    for _,dirs,_ in os.walk(os.path.join(g_log_path, city)):
        node_data = dirs
        break

    return node_data


def get_host(city, node):
    '''获取设备列表'''

    host_data = []
    for _,dirs,_ in os.walk(os.path.join(g_log_path, city, node)):
        host_data = dirs
        break

    return host_data

def get_log(city, node, host, date=None):
    '''根据节点，设备名称， 日期获取log'''

    log_str = ''
    logs = []
    if date == None:
        today = datetime.date.today()
        date = today.strftime('%Y%m%d')

    p_host_log = host + '_' + date
    for _, _, files in os.walk(os.path.join(g_log_path, city, node, host)):
        logs = files
        break

    for i in logs:
        if p_host_log in i:
            log_str = open(os.path.join(g_log_path, city, node, host, i)).read()
            break
    
    if not log_str:
        logging.error('host: {} today log not found'.format(host))

    return log_str

def get_today_log_name(host):
    '''根据设备名称生成当天log名称'''

    today = datetime.date.today()
    date = today.strftime('%Y-%m-%d')

    log_path = '{}_{}.log'.format(host, date)

    return log_path

def get_city_list():
    '''获取城市列表'''
    city_list = []
    for _, dirs, _ in os.walk(g_log_path):
        city_list = dirs
        break

    return city_list