# encoding: utf-8
import os
import json
import logging
import time
from .warn import *
from .report import make_report_mob
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

#告警检查列表
warn_check = (mobile_warn1, mobile_warn2, mobile_warn3, mobile_warn4
    , mobile_warn5, mobile_warn6, mobile_warn7, mobile_warn8
    , mobile_warn9, mobile_warn11, mobile_warn12, mobile_warn13
    , mobile_warn14, mobile_warn15, mobile_warn16, mobile_warn17, mobile_warn18, mobile_warn19)

# def xj():
#     warn_res = []
#     date_path = time.strftime('%Y-%m-%d', time.localtime(time.time()))

#     if not os.path.exists(date_path):
#         logging.error('没有发现目录：' + date_path)
#     else:
#         city_list = os.listdir(date_path)
#         for city in city_list:
#             logging.debug('开始检查 {} 设备日志'.format(city))
#             warn_res = []
#             city_path = os.path.join(date_path,city)
#             if  not os.path.isfile(city_path):
#                 log_list = os.listdir(city_path)
            
#                 for log in log_list:
#                     if log == 'gz.json' or log == 'unconnect_ip.txt':
#                         continue
#                     log_path = os.path.join(city_path,log)
                    
#                     logging.debug('发现日志：%s, 字节数：%s' % (log, os.path.getsize(log_path)))
#                     f = open(log_path)
#                     f_result = f.read()
#                     for func in warn_check:
#                         info, warn = func(f_result)
#                         if info and warn:
#                             logging.debug('发现告警：' + warn)
#                             warn_item = [log, info, warn]
#                             warn_res.append(warn_item)
#                         info = ''
#                         warn = ''
#                     f.close()

#                 logging.debug('检查完毕，开始生成巡检报告')
#                 report_name = make_report_mob(warn_res, city)
#                 if report_name:
#                     logging.debug('巡检报告：{} 生成成功'.format(report_name))

#     logging.debug('工具运行结束')
#     input()

def xunjian():
    log_directory_path = os.path.join('app', 'static', 'uploads', 'log')
    if not os.path.exists(log_directory_path):
        logging.error('没有发现目录：' + log_directory_path)
        return
    warn_res = []
    log_list = os.listdir(log_directory_path)
    for log in log_list:

        log_path = os.path.join(log_directory_path,log)
                
        f = open(log_path)
        f_result = f.read()
        for func in warn_check:
            info, warn = func(f_result)
            if info and warn:
                logging.debug('发现告警：' + warn)
                warn_item = [log, info, warn]
                warn_res.append(warn_item)
            info = ''
            warn = ''
        f.close()

    return warn_res

