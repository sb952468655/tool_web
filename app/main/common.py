import os, datetime, logging
from .config import CITY

def get_node():
    '''获取节点列表'''

    node_data = []
    for _,dirs,_ in os.walk(os.path.join('app','static','logs', CITY)):
        node_data = dirs
        break

    return node_data


def get_host(node):
    '''获取设备列表'''

    host_data = []
    for _,dirs,_ in os.walk(os.path.join('app','static','logs', CITY, node)):
        host_data = dirs
        break

    return host_data

def get_log(node, host, date=None):
    '''根据节点，设备名称， 日期获取log'''

    if date == None:
        today = datetime.date.today()
        date = today.strftime('%Y-%m-%d')


    log_path = os.path.join('app','static','logs', CITY, node, host, '{}_{}.log'.format(host, date))
    if os.path.exists(log_path):
        return open(log_path).read()
    else:
        logging.error('host: {} today log not found'.format(host))

    return None

def get_today_log_name(host):
    '''根据设备名称生成当天log名称'''

    today = datetime.date.today()
    date = today.strftime('%Y-%m-%d')

    log_path = '{}_{}.log'.format(host, date)

    return log_path