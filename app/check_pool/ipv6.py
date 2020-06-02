# encoding = utf-8
import re
from .config_7750 import *

p1 = r'''(pool "(.*)" create
                    options
                        dns-server \d{4}:\d{4}:\d{4}::\d{2} \d{4}:\d{4}:\d{4}::\d
                    exit
                    prefix [0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/(\d\d) (wan-host|pd) create
                    exit
                exit)'''

p2 = r'''(interface "system"
(            .*\n)+        exit)'''

p3 = r'''(isis 0
(            .*\n)+        exit)'''

p4_1 = r'''pool ".*" create
                    options
                        dns-server \d{4}:\d{4}:\d{4}::\d{1,2} \d{4}:\d{4}:\d{4}::\d{1,2}
                    exit
                    prefix ([0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/\d\d) (wan-host|pd) create
                    exit
                exit'''

p4_2 = r'''            prefix-list ".*"
(                prefix ([0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/\d\d) exact\n)+            exit'''

p4_3 = r'''subscriber-prefixes
(                        prefix [0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/\d\d (wan-host|pd)\n)+                    exit'''

p_prefix = r'[0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/\d\d'

p5_1 = r'ipv6-slaac-prefix-pool "(.*)"'
p5_2 = r'ipv6-delegated-prefix-pool "(.*)"'

p6_2 = r'\d{4}:\d{4}:\d{4}::[0-9a-fA-F]{2}'
p_relay = r'''(relay
(                                .*\n)+                            exit)'''

#pool 检测  nd 对应 48 wan-host， pd 对应 44 pd
def check1(config):
    p_dhcp6 = r'(?s)(dhcp6\n {12}local-dhcp-server "server1-ipv6" create\n.*?\n {8}exit)'
    obj = re.compile(p1)
    res = obj.findall(config)
    err = ''

    res_dhcp6 = re.findall(p_dhcp6, config)
    if len(res_dhcp6) != 2:
        err = '没有找到dhcp6'
        return err

    res_pool = re.findall(PAT['pool'], res_dhcp6[1])

    if res_pool == []:
        err = 'pool没有找到'
        return err
    else:
        for item in res_pool:
            p_prefix = r'prefix [0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/(\d\d) (wan-host|pd)'
            res_prefix = re.search(p_prefix, item[0])
            if res_prefix:
                if '_nd_' in item[0] and (res_prefix.group(1) != '48' or res_prefix.group(2) != 'wan-host'):
                    err += res_prefix.group()
                if '_pd_' in item[1] and (res_prefix.group(1) != '44' or res_prefix.group(2) != 'pd'):
                    err += res_prefix.group()
    return err

#interface "system" 下必须有 local-dhcp-server "server1-ipv6"
def check2(config):
    obj = re.compile(p2)
    res = obj.search(config)
    err = ''
    
    if res:
        if 'local-dhcp-server "server1-ipv6"' not in res.group():
            err = 'interface "system" 中没有 local-dhcp-server "server1-ipv6"\n' + res.group()
    else:
        err = '没有找到interface "system"'
    return err
        
#isis0 下必须有 ipv6-routing mt 、ipv6-unicast
def check3(config):
    obj = re.compile(p3)
    res = obj.findall(config)
    err = ''

    if len(res) != 2:
        err += '没有找到isis 0 配置\n'
    else:
        if 'ipv6-routing mt' not in res[0][0]:
            err += 'isis 中没有 ipv6-routing mt 配置\n'
        elif 'ipv6-unicast' not in res[0][0]:
            err += 'isis 中没有 ipv6-unicast 配置\n'

    return err
#prefix 对比三个地方一致 dhcp6 local-dhcp-server，isis 0 policy-options prefix-list，ies 3000 ipv6
def check4(config):
    '''prefix 对比三个地方一致 dhcp6 local-dhcp-server，isis 0 policy-options prefix-list，ies 3000 ipv6'''

    err = ''
    prefix1 = []
    prefix2 = []
    prefix3 = []
    res_pool = []
    p_dhcp6 = r'(?s)(dhcp6\n {12}local-dhcp-server "server1-ipv6" create\n.*?\n {8}exit)'
    p_prefix = r'[0-9a-fA-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{4}::/\d\d'
    obj1 = re.compile(p4_1)
    res_dhcp6 = re.findall(p_dhcp6, config)
    if len(res_dhcp6) != 2:
        err = '没有找到dhcp6'
        return err

    res_pool = re.findall(PAT['pool'], res_dhcp6[1])

    if res_pool == []:
        err = 'pool没有找到'
        return err
    else:
        for pool in res_pool:
            res_prefix = re.search(p_prefix, pool[0])
            if res_prefix:
                prefix1.append(res_prefix.group())
    obj_prefix = re.compile(p_prefix)
    obj2 = re.compile(p4_2)
    res2 = obj2.search(config)
    obj3 = re.compile(p4_3)
    res3 = obj3.search(config)
    if res2:
        prefix2 = obj_prefix.findall(res2.group())
    else:
        err = '没有找到prefix-list'
        return err
    if res3:
        prefix3 = obj_prefix.findall(res3.group())
    else:
        err = '没有找到subscriber-prefixes'
        return err

    if set(prefix1) != set(prefix2) or set(prefix1)!= set(prefix3):
        err = 'prefix对比失败\n{},{},{}\n对比不一致'.format(set(prefix1), set(prefix2), set(prefix3))

    return err

# config = open('周家村（跨区域）.txt').read()
#ipv6-slaac-prefix-pool，ipv6-delegated-prefix-pool 与名称对应 slaac 对应 nd，delegated 对应 pd
def check5(config):
    err = ''
    obj1 = re.compile(p5_1)
    res1 = obj1.findall(config)
    obj2 = re.compile(p5_2)
    res2 = obj2.findall(config)
    if res1 == []:
        err = 'ipv6-slaac-prefix-pool没找到'
    else:
        for item in res1:
            if '_nd_' not in item:
                err += 'ipv6-slaac-prefix-pool "{}"'.format(item)

    if res2 == []:
        err = 'ipv6-delegated-prefix-pool没有找到'
    else:
        for item in res2:
            if '_pd_' not in item:
                err += 'ipv6-delegated-prefix-pool "{}"'.format(item)
    
    return err

#dhcp6 relay server的地址和interface "system"下的ipv6地址一致
def check6(config):
    err = ''
    obj_relay = re.compile(p_relay)
    obj_system = re.compile(p2)
    obj_server = re.compile(p6_2)
    res_relay = obj_relay.search(config)
    res_system = obj_system.search(config)
    if res_relay == None:
        err += '没有找到 dhcp6 relay 配置\n'
    elif res_system == None:
        err += '没有找到 system 配置\n'
    else:
        res_ip1 = obj_server.findall(res_relay.group())
        res_ip2 = obj_server.findall(res_system.group())
        
        for item in res_ip2:
            if item not in res_ip1:
                err = 'relay中的ipv6地址：{} 和interface "system"中的ipv6地址：{} 不一致'.format(res_ip1, res_ip2)
                break
    return err



def ipv6_check(config):
    c1 = check1(config)
    c2 = check2(config)
    c3 = check3(config)
    c4 = check4(config)
    c5 = check5(config)
    c6 = check6(config)
    errs = ''
    if c1 != '':
        errs += 'pool 检查错误\n\n' + check1(config) + '\n\n'
    else:
        errs += 'pool 检查 -> 通过\n\n'
    if c2 != '':
        errs += 'local-dhcp-server检查 -> 错误\n\n' + check2(config) + '\n\n'
    else:
        errs += 'local-dhcp-server检查 -> 通过\n\n'
    if c3 != '':
        errs += 'ipv6-routing mt，ipv6-unicast检查 -> 错误\n\n' + check3(config) + '\n\n'
    else:
        errs += 'ipv6-routing mt，ipv6-unicast检查 -> 通过\n\n'
    if c4 != '':
        errs += 'prefix一致性检查 -> 错误\n\n' + check4(config) + '\n\n'
    else:
        errs += 'prefix一致性检查 -> 通过\n\n'
    if c5 != '':
        errs += 'ipv6-slaac-prefix-pool，ipv6-delegated-prefix-pool检查 -> 错误\n\n' + check5(config) + '\n\n'
    else:
        errs += 'ipv6-slaac-prefix-pool，ipv6-delegated-prefix-pool检查 -> 通过\n\n'
    if c6 != '':
        errs += 'ipv6地址一致性检查 -> 错误\n\n' + check6(config) + '\n\n'
    else:
        errs += 'ipv6地址一致性检查 -> 通过\n\n'

    # return errs
    return ('ipv6检查', errs, '')