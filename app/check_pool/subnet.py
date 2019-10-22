# encoding = utf-8

import re
from .config_7750 import *

p_pool = generate_pat(1, 'pool', 16, 'iptv')
p_sub_inter = generate_pat(1, 'subscriber-interface', 12, 'iptv')

p_subnet = r'''subnet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2}) create'''
p_address = r'address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2})'
p_gi_address = r'gi-address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

def subnet_check(config):
    '''检查 pool "iptv" 中 subnet 与 subscriber-interface "iptv" 中 address 是否一致'''

    err = ''
    obj_pool = re.compile(p_pool)
    obj_sub_inter = re.compile(p_sub_inter)
    obj_subnet = re.compile(p_subnet)
    obj_address = re.compile(p_address)
    obj_gi_address = re.compile(p_gi_address)

    res_pool = obj_pool.search(config)
    if res_pool == None:
        err = '没有找到 pool "iptv"\n'
    else:
        res_subnet = obj_subnet.findall(res_pool.group())
        if res_subnet == []:
            err += '没有找到subnet\n'
        else:
            res_sub_inter = obj_sub_inter.findall(config)
            if len(res_sub_inter) != 2:
                err += '没有找到 subscriber-interface "iptv"\n'
            else:
                res_address = obj_address.findall(res_sub_inter[1][0])
                if res_address == []:
                    err += '没有找到address\n'
                else:
                    res_address = [item.replace('.1/', '.0/') for item in res_address]
                    res_gi_address = obj_gi_address.search(res_sub_inter[1][0])
                    
                    if res_gi_address == None:
                        err += '没有找到 gi-address\n\n'
                    else:
                        if res_gi_address.group(1)[-1] != '1':
                            err += 'gi_address 最后一位不为1\n'
                        else:
                            gi_address = res_gi_address.group(1)[:-1] + '0'
                            if sorted(res_subnet) != sorted(res_address):
                                err += 'pool "iptv" 中 subnet 与 subscriber-interface "iptv" 中 address 不一致\n\nsubnet\n{}\naddress\n{}\n'.format('\n'.join(res_subnet), '\n'.join(res_address))
                            b_in_subnet = False
                            for item in res_subnet:
                                if gi_address in item:
                                    b_in_subnet = True
                                    break
                            if not b_in_subnet:
                                err += 'pool "iptv" 中 subnet 与 subscriber-interface "iptv" 中 gi_address 不一致\nsubnet\n{}\ngi_address\n{}\n'.format('\n'.join(res_subnet), gi_address)
    if err == '':
        err = 'subnet地址校验 -> OK\n\n'
    else:
        err = 'subnet地址校验 -> ERROR\n\n' + err

    return err