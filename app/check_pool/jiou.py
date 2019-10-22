# encoding = utf-8

import re
from .config_7750 import *

def jiou_check(config):
    err = ''
    inter_pri = []

    config_7750 = Config_7750(config)
    ies = config_7750.get_ies('1000')
    if ies == []:
        err += '没有找到ies 1000'

    interface = ies[0].get_interface()
    if interface == []:
        err += '没有找到interface'

    #获取pim中的interface
    res_pim = re.findall(PAT['pim'], config)
    if res_pim == []:
        err += '没有找到pim'

    pat_inter_in_pim = r'(?s)(interface "(.*?)"\n.*?\n {12}exit)'
    res_inter_in_pim = re.findall(pat_inter_in_pim, res_pim[1])
    for inter in res_inter_in_pim:
        priority = re.search(r'priority (\d{3})', inter[0])
        if priority:
            inter_pri.append((inter[1],priority.group(1)))

    if err != '':
        return err
    else:
        for inter in interface:
            address = inter.get_address()
            address_last = address.split('/')[0].split('.')[-1]
            for inter_name, priority in inter_pri:
                if inter.name == inter_name:
                    if (int(address_last)%2 == 0 and priority != '100') or (int(address_last)%2 != 0 and priority != '150'):
                        err += 'interface "{}"\n{}\npriority {}\n\n'.format(inter_name, address_last, priority)
                    break

    if err == '':
        err = '● iptv主备接口地址校验 -> OK\n\n'
    else:
        err = '● iptv主备接口地址校验 -> ERROR\n\n' + err + '\n\n'

    return err

