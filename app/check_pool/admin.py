import re
from .config_7750 import *

def admin_check(config):
    err = ''
    if 'no optimized-mode' not in config:
        err += '没有配置 no optimized-mode\n'

    if 'no user "admin"' not in config:
        err += 'Admin 检查 -> ERROR\n\nuser 账号是 admin\n\n'
    else:
        err += 'Admin 检查 -> OK\n\n'

    return err