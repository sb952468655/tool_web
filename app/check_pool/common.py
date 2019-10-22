#一些通用的方法
import re
import IPy
from .config_7750 import *

def address_check(pool, inside, subnet):
    '''pool, inside, subnet 地址检查
    1.判断inside中的私网地址是否在pool和subnet中
    2.去掉pool,subnet中的私网地址
    3.判断pool中的地址是否和subnet一致'''

    #先判断inside中的私网地址是否在pool和subnet中
    for item in inside:
        if item not in pool:
            return 'inside 中的：{} 不在pool中'
        else:
            pool.remove(item)
        if item not in subnet:
            return 'inside 中的：{} 不在subnet中'
        else:
            subnet.remove(item)

    #判断pool中的地址是否和subnet一致

    if pool != subnet:
        return 'pool中的地址是和subnet不一致'

def compare_ip(ip, ip_range):
    '''检查ip range 是否在正确范围内'''

    ip_b = IPy.IP(ip_range.split('-')[0])
    ip_e = IPy.IP(ip_range.split('-')[1])

    ip = IPy.IP(ip)
    ip = ip[2:-1]
    if ip_b not in ip or ip_e not in ip:
        return False
    else:
        return True


def get_pool_ip(config):
    p_dhcp = r'(?s)(echo "Local DHCP Server \(Base Router\) Configuration"\n.*?\n {4}exit)'
    p_pool = generate_pat(1, 'pool', 16)
    p_subnet = PAT['subnet']
    ips = []
    res_dhcp = re.search(p_dhcp, config)
    if res_dhcp:
        res_pool = re.findall(p_pool, res_dhcp.group())
        for item in res_pool:
            res_subnet = re.findall(p_subnet, item[0])
            ips += res_subnet

    return ips

def get_nat_address(config):
    res = []
    p_nat = generate_pat(2, 'l2-aware', 16)
    res_nat = re.search(p_nat, config)

    if res_nat:
        res = re.findall(PAT['address'], res_nat.group())

    return res


def get_vprn_pool_ip(config):
    p_dhcp = r'(?s)(echo "Local DHCP Server \(Services\) Configuration"\n.*?\n {4}exit)'
    p_vprn = generate_pat(0, 'vprn', 8)
    p_pool = generate_pat(1, 'pool', 20)
    p_subnet = PAT['subnet']
    res = []
    res_dhcp = re.search(p_dhcp, config)
    if res_dhcp:
        res_vprn = re.findall(p_vprn, res_dhcp.group())
        for vprn in res_vprn:
            subnet = []
            res_pool = re.findall(p_pool, vprn[0])
            for item in res_pool:
                res_subnet = re.findall(p_subnet, item[0])
                subnet += res_subnet

            res.append((vprn[1], subnet))


    return res

def get_ies_address(config):
    '''获取ies subscriber_interface 中的 address'''

    config_7750 = Config_7750(config)
    p_sub_inter = PAT['subscriber_interface']
    res = []
    ies = config_7750.get_ies()
    for item in ies:
        res_sub_inter = re.findall(p_sub_inter, item.config)
        if res_sub_inter:
            for sub_inter in res_sub_inter:
                res += re.findall(PAT['address'], sub_inter[0])

    return res

def get_vprn_address(config):
    '''获取vprn subscriber_interface 中的 address'''

    config_7750 = Config_7750(config)
    p_sub_inter = PAT['subscriber_interface']
    res = []
    business = config_7750.get_child()
    for item in business:
        if item._type != 'vprn':
            continue

        address = []
        res_sub_inter = re.findall(p_sub_inter, item.config)
        if res_sub_inter:
            for sub_inter in res_sub_inter:
                address += re.findall(PAT['address'], sub_inter[0])
        if address != []:
            res.append((item.name, address))


    return res


def is_include(a, b):
    '''判断b是否包含a'''
    res = []
    for item in a:
        if item not in b:
            res.append(item)

    return res


def get_prefix_list(config):
    ips = []
    res_prefix_list = re.search(PAT['prefix_list'], config)
    if res_prefix_list:
        res_ip = re.findall(PAT['ipv4'], res_prefix_list.group())

        for ip in res_ip:
            ips.append(ip)

    return ips


def oct2bin(num):
    res = bin(int(num)).replace('0b', '')
    while len(res) != 8:
        res = '0' + res

    return res


def address_is_in_one_net(add1, add2):
    add1_ip = add1.split('/')[0]
    ym = add1.split('/')[1]

    add2_ip = add2.split('/')[0]
    ym2 = add2.split('/')[1]

    if ym != ym2:
        return False

    add1_list = add1_ip.split('.')
    add2_list = add2_ip.split('.')

    add1_bin_str = ''
    add2_bin_str = ''
    for i in add1_list:
        add1_bin_str += oct2bin(int(i))

    for i in add2_list:
        add2_bin_str += oct2bin(int(i))

    if add1_bin_str[:int(ym)-1] == add2_bin_str[:int(ym)-1]:
        return True
    else:
        return False


def address_include_each(addr1, addr2):
    '''检查两组地址是否在一个网段'''

    err_ips = []

    for addr1_ip in addr1:
        is_in = False
        for addr2_ip in addr2:
            if address_is_in_one_net(addr1_ip, addr2_ip):
                is_in = True
        if not is_in:
            err_ips.append(addr1_ip)


    for addr2_ip in addr2:
        is_in = False
        for addr1_ip in addr1:
            if address_is_in_one_net(addr1_ip, addr2_ip):
                is_in = True
        if not is_in:
            err_ips.append(addr2_ip)


    return err_ips

def address_is_in_list(addr, ip_list):
    '''检查ip网段 是否在 一组ip的网段中'''
    
    for ip in ip_list:
        if address_is_in_one_net(addr, ip):
            return True

    return False

def nat_check(ip):
    '''判断地址是否为私网'''

    ip_nums = ip.split('.')
    if ip_nums[0] == '100' and (42 <= int(ip_nums[1]) <= 113):
        return True
    else:
        return False


def get_outside_pool(config):
    '''获取outside pool 中的 address-range'''

    p_outside = generate_pat(2, 'outside', 12)
    res_outside = re.search(p_outside, config)

    res_address_range = []
    if res_outside:
        res_address_range = re.findall(PAT['address_range'], res_outside.group())


    return res_address_range


def get_static_route(config):
    '''获取静态路由'''

    res_static_route = re.findall(PAT['static_route'], config)
    return [item[1] for item in res_static_route]




