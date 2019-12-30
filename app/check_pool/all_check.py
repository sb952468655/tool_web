import re, sys
import IPy
from .config_7750 import generate_pat, PAT
from .address_pool_and_security import address_range_check, address_is_include_pool, gi_address_check, pool_address_prefix_list, ies_3000_inside_check
from .address import prefix_list_include_black_hole, black_hole_address_range_check, inside_subnet_address_check
from .outside_pool import outside_pool_check
from .subnet import subnet_check
from .ipv6 import check4
from .rule124 import ipv6_address_check


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
    check_item = '''ies 1000 subscriber-interface "iptv" 下的address必须要有：
    1.gi-address必须是subscriber-interface "iptv" 下的address之一。
    2.检查server 后面的地址是否为本机system地址
    3.在pool iptv中有相应地址段即subnet
    4.subnet的default-router以及address-range必须一致
    5.nat inside的 l2-aware中必须要有相应的address'''

    err.append((ies_1000_check(config), check_item))

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
    check_item = '''ies 1000 subscriber-interface "iptv" 下的address必须要有：
    1.gi-address必须是subscriber-interface "iptv" 下的address之一。
    2.检查server 后面的地址是否为本机system地址
    3.在pool iptv中有相应地址段即subnet
    4.subnet的default-router以及address-range必须一致
    5.nat inside的 l2-aware中必须要有相应的address'''

    p_ies_1000 = r'(?s)(ies 1000( name "1000")? customer 1 create\n.+?\n {8}exit)'
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

    return err






