import re, sys
import IPy
from .config_7750 import generate_pat, PAT
from .address_pool_and_security import address_range_check, address_is_include_pool, gi_address_check, pool_address_prefix_list, ies_3000_inside_check
from .address import prefix_list_include_black_hole, black_hole_address_range_check, inside_subnet_address_check
from .outside_pool import outside_pool_check
from .subnet import subnet_check
from .ipv6 import check4, ipv6_check
from .rule124 import rule124
from .policy import policy_check
from .dhcp import dhcp_check
from .log_warn import check_log_warn
from .ftp import ftp_check
from .fc import fc_check
from .admin import admin_check
from .jiou import jiou_check
from .global1 import global_check
from .common import *


def all_check(config):
    '''检查所有地址相关配置
    1.检查 address-range 范围是否正确
    2.检查 pool中的地址 是否在 address 中
    3.检查 ies, vprn 中的 gi-address 是否在 address 中
    4.检查 prefix-list 中是否包含 黑洞路由地址
    5.检查 黑洞路由与pool "nat-pppoe" 中的address-range 是否匹配
    6.检查 inside subnet address 地址是否正确
    7.检查 outside pool 中的地址是否在黑洞路由中
    8.检查 dhcp pool, 网关地址, 路由发布地址是否一致
    9.检查 ies 3000 下的sub interface下的私网地址是否与 Nat 中 inside 地址一致'''

    # check_item = r''''''
    err = []

    # err.append(('检查 address-range 范围是否正确', address_range_check(config)))
    # err.append(('检查 address 是否在 pool 的网段中',address_is_include_pool(config)))
    # err.append(('检查 ies 3000 sub interface下的私网地址是否与 Nat 中 inside 地址一致',ies_3000_inside_check(config)))
    # err.append(('检查 dhcp pool, 网关地址, 路由发布地址是否一致',pool_address_prefix_list(config)))
    # err.append(('检查 prefix-list 中是否包含 黑洞路由地址',prefix_list_include_black_hole(config)))
    # err.append(('检查黑洞路由与pool "nat-pppoe" 中的address-range 是否匹配',black_hole_address_range_check(config)))
    # err.append(('检查 inside subnet address 地址是否正确',inside_subnet_address_check(config)))
    # err.append(('检查outside pool 中的地址是否在黑洞路由中',outside_pool_check(config)))


    err.append(ies_1000_check(config))
    err.append(ies_3000_check(config))
    err.append(nat_inside_check(config))
    err.append(ies_1000_3000_outside_check(config))
    err.append(policy_check(config))

    err.append(policy_check(config))
    err.append(dhcp_check(config))
    err.append(check_log_warn(config))

    err.append(ipv6_check(config))
    err.append(rule124(config))
    err.append(ftp_check(config))
    err.append(fc_check(config))
    err.append(admin_check(config))
    err.append(jiou_check(config))
    err.append(global_check(config))

    return err

def ies_1000_check(config):
    '''ies 1000 subscriber-interface "iptv" 下的address必须要有：
    1.gi-address必须是subscriber-interface "iptv" 下的address之一。
    2.检查server 后面的地址是否为本机system地址
    3.在pool iptv中有相应地址段即subnet
    4.subnet的default-router以及address-range必须一致
    5.nat inside的 l2-aware中必须要有相应的address'''

    err = ''
    msg = ''
    check_item = '''检查ies 1000 subscriber-interface "iptv" 的地址是否与dhcp中地址一致'''

    p_ies_1000 = r'(?s)(ies 1000( name "1000")? customer \d{1,2} create\n.+?\n {8}exit)'
    # p_ies_1000 = generate_pat(0, 'ies', 8, '1000')
    
    p_system_address = r'(?s)interface "system"\n {12}address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})'
    # p_system_address = generate_pat(5, 'interface', 8, '"system"')
    p_sub_interface_iptv = r'(?s)subscriber-interface "iptv" create\n.+?\n {12}exit'
    # p_sub_interface_iptv = generate_pat(1, 'subscriber-interface', 12, 'iptv')
    p_pool_iptv = r'(?s)pool "iptv" create\n.+?\n {16}exit'
    # p_pool_iptv = generate_pat(1, 'pool', 16, 'iptv')
    p_default_router = r'default-router (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    res_ies_1000 = re.findall(p_ies_1000, config)
    if res_ies_1000:
        temp = res_ies_1000[1][0]
        res_sub_interface_iptv = re.search(p_sub_interface_iptv, res_ies_1000[1][0])
        if not res_sub_interface_iptv:
            err += '没有找到subscriber-interface "iptv" '
            return err
        temp = res_sub_interface_iptv.group()
        res_ies_1000_address = re.findall(PAT['address2'], res_sub_interface_iptv.group())

        #gi-address必须是subscriber-interface "iptv" 下的address之一
        res_gi_address = re.search(PAT['gi-address'], res_sub_interface_iptv.group())
        if res_gi_address and res_gi_address.group(1) not in res_ies_1000_address:
            err += 'gi-address {} 不在 subscriber-interface "iptv" address 中\n'
            msg += 'address {}\ngi-address {}\n'.format(res_ies_1000_address.group(), res_gi_address.group())

        #检查server 后面的地址是否为本机system地址
        res_system_address = re.search(p_system_address, config)
        if res_system_address:
            msg += 'interface "system" address {}'.format(res_system_address.group(1))
            system_address = IPy.IP(res_system_address.group(1))
            res_server = re.findall(PAT['server'], res_sub_interface_iptv.group())
            for i in res_server:
                if i not in system_address:
                    err += 'dhcp server {} 不是本机system地址\n'.format(i)

        #在pool iptv中有相应地址段即subnet
        #subnet的address-range必须一致
        res_pool_iptv = re.search(p_pool_iptv, config)
        if res_pool_iptv:
            res_subnnet = re.findall(PAT['subnet'], res_pool_iptv.group())
            ies_1000_address = re.findall(PAT['address'], res_sub_interface_iptv.group())
            address = []
            for i in ies_1000_address:
                ip = i.split('/')
                ips = ip[0].split('.')
                ip_str = '.'.join(ips[:-1]) +'.' + str(int(ips[-1]) - 1)
                address.append('{}/{}'.format(ip_str, ip[1]))

            subnet_address = [i[1] for i in res_subnnet]
            for i in subnet_address:
                msg += 'pool "iptv" subnet\n' + '\n'.join(subnet_address)
            for index, i in enumerate(address):
                if i not in subnet_address:
                    err += 'pool "iptv" 中没有 ies 1000 subscriber-interface "iptv" 对应地址段 {}\n'.format(res_ies_1000_address[index])

            for i in res_subnnet:
                subnet = IPy.IP(i[1], make_net=True)
                res_default_router = re.search(p_default_router, i[0])
                temp = subnet[1].strNormal(0)
                if res_default_router and res_default_router.group(1) != subnet[1].strNormal(0):
                    err += 'subnet {} 和 default-router {} 不一致\n'.format(i[1], res_default_router.group(1))

                if IPy.IP(i[2]) != subnet[2] or IPy.IP(i[3]) != subnet[-2]:
                    err += 'subnet {} 和 address-range {} {} 不一致\n'.format(i[1], i[2], i[3])

    else:
        print('not found ies 1000')


    if err == '':
        err = '检查通过\n'

    return (check_item, err, msg)


def ies_3000_check(config):
    '''检查ies 3000 subscriber-interface "pppoe" 的地址是否与dhcp中地址一致'''

    err = ''
    msg = ''
    check_item = '检查ies 3000 subscriber-interface "pppoe" 的地址是否与dhcp中地址一致'

    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_sub_interface_pppoe = r'(?s)subscriber-interface "pppoe" create\n.+?\n {12}exit'

    res_ies_3000 = re.findall(p_ies_3000, config)
    if res_ies_3000:
        temp = res_ies_3000[1][0]
        res_sub_interface_pppoe = re.search(p_sub_interface_pppoe, res_ies_3000[1][0])
        if not res_sub_interface_pppoe:
            err += '没有找到subscriber-interface "pppoe" '
            return err
        temp = res_sub_interface_pppoe.group()
        res_ies_3000_address = re.findall(PAT['address'], temp)
        res_dhcp_address = get_pool_ip(config)
        res_ies_3000_address = [ i.replace('.1/', '.0/') for i in res_ies_3000_address ]

        if sorted(res_ies_3000_address) != sorted(res_dhcp_address):
            diff = list(set(res_ies_3000_address) - set(res_dhcp_address)) + list(set(res_dhcp_address) - set(res_ies_3000_address))
            err += 'ies 3000 subscriber-interface "pppoe" 的地址与dhcp中地址不一致，请检查'
            msg = '不一致地址\n{}\n\n'.format('\n'.join(diff))
    else:
        err += '没有找到ies 3000\n'
    if err == '':
        err = '检查通过\n'

    return (check_item, err, msg)

def nat_inside_check(config):
    '''检查nat inside地址是否有缺漏
    1.inside 中的私网地址必须在 subnet 和 address 中
    2.subnet 和 address 中的公网地址必须一致'''

    err = ''
    msg = ''
    check_item = '''检查nat inside地址是否有缺漏'''

    subnets = get_pool_ip(config)
    addresss = get_ies_address(config)
    nat_addresss = get_nat_address(config)

    subnet_nat = []
    address_nat = []

    subnet_address = []
    if subnets == []:
        err += '配置中没有找到pool中的subnet\n'
    if addresss == []:
        err += '配置中没有找到address\n\n'

    if err != '':
        return err

    for item in subnets:
        subnet_address.append(item)

    if nat_addresss != []:

        #获取subnet中的私网地址
        
        for subnet in subnet_address:
            if nat_check(subnet):
                subnet_nat.append(subnet)

        #获取address中的私网地址
        
        for address in addresss:
            if nat_check(address):
                address_nat.append(address)

        #subnet, address 去掉私网地址
        for item in subnet_nat:
            subnet_address.remove(item)
        for item in address_nat:
            addresss.remove(item)

        if subnet_nat == []:
            err += '   subnet 中没有发现私网地址\n\n'
        if address_nat == []:
            err += '   address 中没有发现私网地址\n\n'

        if err != '':
            return err

        #检查nat中的私网地址是否在subnet和address地址中
        for nat in nat_addresss:
            if not address_is_in_list(nat, subnet_nat):
                err += 'inside 地址 %s 不在 subnet 中\n   请检查 \"address  %s\"\n' % (nat, nat)
            if not address_is_in_list(nat, address_nat):
                err += 'inside 地址 %s 不在 address 中\n   请检查 \"address  %s\"\n' % (nat, nat)
    else:
        err += 'inside 没有找到，请维护人员核查\n\n'


    #检查subnet中的公网地址和address中的公网地址是否一致
    err_ips = address_include_each(subnet_address, addresss)
    if err_ips != []:
        for item in err_ips:
            err += 'subnet中的公网地址和address中的公网地址不一致\n   请检查 \"address {}\"\n'.format(item)
    
    if err == '':
        err = '检查通过\n'

    return (check_item, err, msg)

def ies_1000_3000_outside_check(config):
    '''检查ies1000、3000公网地址是否正常发布'''

    err = ''
    msg = ''
    check_item = '''检查ies1000、3000公网地址是否正常发布'''

    p_ies_1000 = r'(?s)(ies 1000( name "1000")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_ies_3000 = r'(?s)(ies 3000( name "3000")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_out_side = r'(?s)outside.*?\n {12}exit'
    # p_in_side = r'(?s)inside.*?\n {12}exit'
    p_address_range = PAT['address_range']
    p_address = PAT['address']

    res_ies_1000 = re.findall(p_ies_1000, config)
    res_ies_3000 = re.findall(p_ies_3000, config)
    # res_inside = re.search(p_in_side, config)
    res_outside = re.search(p_out_side, config)

    # if res_inside:
    #     res_inside_address = re.findall(p_address, res_inside.group())
    # else:
    #     err += '没有找到inside请检查\n'
    if res_outside:
        res_outside_address = re.findall(p_address_range, res_outside.group())
    else:
        err += '没有找到outside请检查\n'

    

    if res_ies_1000:
        res_address = re.findall(p_address, res_ies_1000[1][0])
        for address in res_address:
            if not nat_check(address):
                b_include = False
                address_ip = IPy.IP(address, make_net=1)
                for item in res_outside_address:
                    ip_begin = '.'.join(item[0].split('.')[:-1]) + '.0'
                    # ip_end = '.'.join(item[1].split('.')[:-1]) + '.' +str(int(item[1].split('.')[-1]) + 1)
                    ip_end = '.'.join(item[1].split('.')[:-1]) + '.255'
                    outside_ip = IPy.IP(ip_begin+'-'+ip_end, make_net=1)
                    # outside_ip = IPy.IP(item[0]+'-'+item[1], make_net=1)
                    if address_ip in outside_ip:
                        b_include = True
                        break

                if b_include == False:
                    err += 'ies 1000 address {} 没有发布\n'.format(address)

    if res_ies_3000:
        res_address = re.findall(p_address, res_ies_3000[1][0])
        for address in res_address:
            if not nat_check(address):
                b_include = False
                address_ip = IPy.IP(address, make_net=1)
                for item in res_outside_address:
                    ip_begin = '.'.join(item[0].split('.')[:-1]) + '.0'
                    ip_end = '.'.join(item[1].split('.')[:-1]) + '.255'
                    outside_ip = IPy.IP(ip_begin+'-'+ip_end, make_net=1)
                    if address_ip in outside_ip:
                        b_include = True
                        break

                if b_include == False:
                    err += 'ies 3000 address {} 没有发布\n'.format(address)

    if err == '':
        err = '检查通过\n'

    return (check_item, err, msg)


def policy_check(config):
    '''ies3000下面每个group-interface的"pppoe-policy-m"和 "ludb-m"要一致起来。
    只有"pppoe-policy-m" "ludb-m"和"pppoe-policy-s" "ludb-s"这两种组合，不能混用'''

    err = ''
    msg = ''
    check_item = '''检查ies3000 group-interface中的pppoe-policy, user-db 是否正确'''
    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_group_interface = PAT['group_interface']

    res_ies_3000 = re.findall(p_ies_3000, config)
    if len(res_ies_3000) != 2:
        err = '没有找到ies 3000，请检查\n'
    else:
        res_group_interface = re.findall(p_group_interface, res_ies_3000[1][0])
        for i in res_group_interface:
            if ('pppoe-policy-m' in i[0] and 'ludb-s' in i[0]) or ('pppoe-policy-s' in i[0] and 'ludb-m' in i[0]):
                err += 'ies 3000 中的 group-interface "{}" pppoe-policy, user-db错误，请检查\n'.format(i[1])
                msg += i[0] + '\n'


    if err == '':
        err = '检查通过\n'

    return (check_item, err, msg)






