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


def xunjian(config):
    warn_res = []
    for func in warn_check:
        info, warn, all_text, check_item = func(config)
        if all_text:
            warn_item = [info, warn, all_text, check_item]
            warn_res.append(warn_item)
        info = ''
        warn = ''
        all_text = ''


    return warn_res

