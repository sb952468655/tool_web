# encoding: utf-8
import os
import json
import logging
import time
from .warn import *
from .report import make_report_mob
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

#告警检查列表
warn_check = (mobile_warn9, mobile_warn11, mobile_warn13\
    , mobile_warn14, mobile_warn15, mobile_warn16, mobile_warn17, mobile_warn20\
    , mobile_warn21, mobile_warn24, mobile_warn26, mobile_warn27\
    , mobile_warn28, mobile_warn29, mobile_warn30, mobile_warn31, mobile_warn33)


def xunjian(config, config_old):
    warn_res = []
    

    warn_res.append(mobile_warn1(config))
    warn_res.append(mobile_warn2(config))
    warn_res.append(mobile_warn3(config))
    warn_res.append(mobile_warn4(config))
    warn_res.append(mobile_warn5(config))

    warn_res.append(mobile_warn22(config, config_old))
    warn_res.append(mobile_warn23(config, config_old))
    warn_res.append(mobile_warn25(config, config_old))
    warn_res.append(mobile_warn32(config_old, config))

    for func in warn_check:
        msg, err, check_item = func(config)
        
        warn_item = [msg, err, check_item]
        warn_res.append(warn_item)

    return warn_res

