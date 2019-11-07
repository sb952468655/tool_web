import re
import math
import IPy
import sys
from .config_7750 import *
from .common import compare_ip, get_ies_address, get_pool_ip,\
    get_vprn_pool_ip, get_vprn_address, get_prefix_list, \
    address_is_in_one_net, address_include_each, \
    get_nat_address, nat_check, get_outside_pool, get_static_route
from .address import inside_subnet_address_check
def get_ip(config):
    p_pool = generate_pat(1, 'pool', 16)
    p_subnet = PAT['subnet']

    res = re.findall(p_pool, config)
    ips = []
    if res:
        for item in res:
            res_subnet = re.findall(p_subnet, item[0])
            ips += res_subnet

    return ips


def check_arp_anti(config):
    errors = []
    p_group_empty = r'group-interface ".+?" create\s{17}exit'
    obj_group_empty = re.compile(p_group_empty)

    ########
    config_obj = Config_7750(config)
    business = config_obj.get_child()
    if business == []:
        errors.append('未找到业务配置！')

    sub_inter = []
    for item in business:
        sub_inter += item.get_subscriber_interface()
    if sub_inter == []:
        errors.append('未找到 subscriber-interface 配置！')

    group_inter = []
    for item in sub_inter:
        group_inter += item.get_child()
    if group_inter == []:
        errors.append('未找到 group-interface 配置！')

    for item in group_inter:
        #跳过空的group
        group_empty = obj_group_empty.search(item.config)
        if group_empty:
            continue

        pat_dhcp = generate_pat(2, 'dhcp', 20)
        dhcp = re.search(pat_dhcp, item.config)

        #含有dhcp配置不需要检查
        #不含有static-host ip配置不需要检查
        #含有local-address-assignment配置不需要检查
        #配置索引不检查
        if dhcp or 'static-host ip' not in item.config \
                or 'local-address-assignment' in item.config:
            continue
        if 'arp-populate' in item.config or ('anti-spoof' not in item.config \
            and 'urpf-check' not in item.config):
            errors.append('group-interface "{}" arp anti 检查错误'.format(item.name))

    return errors

def check_security(config):
    err = ''
    security_err = []

    config_obj = Config_7750(config)
    res1 = config_obj.get_echo('System Security Configuration')
    res2 = config_obj.get_echo('System Security Cpm Hw Filters, PKI, TLS and LDAP Configuration')
    if res1:
        security_config = res1
        p_ssh = r'''ssh\s(.+\s)+?\s{12}exit'''
        ssh_res = re.search(p_ssh, security_config)
        if not ssh_res:
            security_err.append('System Security Configuration ssh 配置未找到\n\n')
        else:
            if 'server-shutdown' not in ssh_res.group():
                security_err.append('System Security Configuration ssh 配置错误\n\n')
        
        if 'ftp-server' in security_config:
            security_err.append('System Security Configuration 请关闭ftp服务\n\n')
    else:
        security_err.append('没有找到System Security Configuration配置\n\n')

    if res2:
        security_config = res2
        p_ip_filter = r'''ip-filter\s(.+\s)+?\s{16}exit'''
        p_mac_filter = r'''mac-filter\s(.+\s)+?\s{16}exit'''

        ip_filter_res = re.search(p_ip_filter, security_config)
        mac_filter_res = re.search(p_mac_filter, security_config)
        if not ip_filter_res:
            security_err.append('System Security Configuration ip-filter 配置未找到\n\n')
        else:
            if 'no shutdown' not in ip_filter_res.group():
                security_err.append('System Security Configuration 请开启访问控制ip-filter\n\n')

        if not mac_filter_res:
            security_err.append('System Security Configuration mac-filter 配置未找到\n\n')
        else:
            if 'no shutdown' not in mac_filter_res.group():
                security_err.append('System Security Configuration 请开启访问控制mac-filter\n\n')
    else:
        security_err.append('没有找到System Security Cpm Hw Filters and PKI Configuration配置\n\n')


    if security_err == []:
        err = '安全检查 -> OK\n\n'
    else:
        err += '安全检查 -> ERROR\n\n'
        for i in security_err:
            err += i + '\n\n'

    return err

def address_range_check(config):
    '''检查 address-range 范围是否正确'''

    err  = []
    ips = get_pool_ip(config)
    for item in ips:
        wg = item[1]
        ip_range = '{}-{}'.format(item[2], item[3])

        #检查subnet地址分配范围
        if not compare_ip(wg, ip_range):
            err_info = '   subnet {}\n   address-range {} {}\n'.format(item[1], item[2], item[3])
            err.append('地址范围错误\n\n' + err_info + '\n   请检查 address-range ' +  item[2] + ' ' + item[3] + '\n')

    return err

def address_is_include_pool(config):
    '''检查 address 是否在 pool 的网段中'''

    err  = []

    ips = get_pool_ip(config)
    wgs = get_ies_address(config)

    if not ips:
        err.append('配置中 pool subnet 没有找到\n\n')
        return err
    if not wgs:
        err.append('配置中 address 没有找到\n\n')
        return err

    err_ips = []

    for wg in wgs:
        is_in = False
        for ip in ips:
            if address_is_in_one_net(ip[1], wg):
                is_in == True

        if not is_in:
            err_ips.append(wg)


    #vprn 检查
    vprn_address = get_vprn_address(config)
    vprn_pool_subnet = get_vprn_pool_ip(config)

    if not vprn_pool_subnet:
        err.append('配置中 vprn 没有 subnet 请维护人员进行设备配置核实\n\n')
        return err
    if not vprn_address:
        err.append('配置中 vprn 没有 address 请维护人员进行设备配置核实\n\n')
        return err

    for address in vprn_address:
        for subnet in vprn_pool_subnet:
            if address[0] == subnet[0]:
                is_in = False
                for address_ip in address[1]:
                    for subnet_ip in subnet[1]:
                        if address_is_in_one_net(address_ip, subnet_ip[1]):
                            is_in = True
                            break

                if not is_in:
                    err.append('vprn %s address %s 不在 pool 的网段中\n   请检查 \"%s\" 配置\n' % (address[0], address_ip, address_ip))
    return err


def gi_address_check(config):
    #判断 ies, vprn 中的 gi-address 是否在 address 中

    err = ''
    cofig_7750 = Config_7750(config)
    bussness = cofig_7750.get_child()
    for item in bussness:
        if item._type == 'ies' or item._type == 'vprn':
            sub_inters = item.get_subscriber_interface()
            for sub_inter in sub_inters:
                res_addresss = re.findall(PAT['address2'], sub_inter.config)
                res_gi_addresss = re.findall(PAT['gi-address'], sub_inter.config)
                for res_gi_address in res_gi_addresss:
                    if res_gi_address not in res_addresss:
                        err += 'gi-address %s 不在 address 中\n\n' % res_gi_address


    return err


def pool_address_prefix_list(config):
    '''检查 dhcp pool, 网关地址, 路由发布地址是否一致'''

    err = []

    subnets = get_pool_ip(config)
    address = get_ies_address(config)
    prefixs = get_prefix_list(config)

    if subnets == []:
        err.append('配置中没有找到 subnet\n\n')
    if address == []:
        err.append('配置中没有找到 address\n\n')
    if prefixs == []:
        err.append('配置中没有找到路由发布 prefix-list\n\n')

    if err != []:
        return err

    subnets_ips = []
    for subnet in subnets:
        subnets_ips.append(subnet[1])

    err_ips = address_include_each(subnets_ips, address)
    err_ips += address_include_each(subnets_ips, prefixs)

    #如果 address 有静态路由、有路由发布，没有在网关中，但在公网nat地址池中，也算正常
    outside_pool = get_outside_pool(config)
    static_route = get_static_route(config)

    if outside_pool != [] and static_route != []:
        ips = []
        for err_ip in err_ips:
            if err_ip in static_route:
                for addr in outside_pool:
                    err_ip_split = err_ip.split('.')
                    addr_split = addr[0].split('.')
                    if err_ip_split[0] == addr_split[0] \
                        and err_ip_split[1] == addr_split[1] \
                        and err_ip_split[2] == addr_split[2]:
                        ips.append(err_ip)

        for item in ips:
            err_ips.remove(item)
    if err_ips != []:
        
        for item in err_ips:
            err.append('dhcp pool, 网关地址, 路由发布地址不一致\n   请检查 \"address {}\" 配置\n'.format(item))
    return err


def address_pool_and_security(config):
    '''
    地址核对
    1.检查 address-range 范围是否正确
    2.检查 pool中的地址 是否在 address 中
    ies 和 vprn 对应不同的 pool
    '''
    err  = ''
    
    range_err = ''
    wg_contain_err = ''
    arp_anti_err = ''


    range_err = address_range_check(config)
    # wg_contain_err = address_is_include_pool(config)
    wg_contain_err += inside_subnet_address_check(config)
    wg_contain_err += ies_3000_inside_check(config)
    range_err += gi_address_check(config)
    wg_contain_err  += pool_address_prefix_list(config)

    #检查arp-populate，anti-spoof ip
    arp_anti_err = check_arp_anti(config)

    if range_err == '':
        err += "● address range检查 -> OK\n\n"
    else:
        err += "● address range检查 -> ERROR\n\n"
        err += range_err

    if wg_contain_err == '':
        err += "● 地址一致性检查 -> OK\n\n"
    else:
        err += "● 地址一致性检查 -> ERROR\n\n"
        err += wg_contain_err

    if arp_anti_err == []:
        err += "● arp-populate, anti-spoof, urpf-check检测 -> OK\n\n"
    else:
        err += "● arp-populate, anti-spoof, urpf-check检测 -> ERROR\n\n"
        for err1 in arp_anti_err:
            err += err1 + '\n\n'

    #安全检查
    err += check_security(config)

    return err

def ies_3000_inside_check(config):
    '''检查 ies 3000 sub interface下的私网地址是否与 Nat 中 inside 地址一致'''

    err = []
    ies_1000_address = []
    address_nat = []
    p_ies_3000 = generate_pat(0, 'ies', 8, '3000')
    p_ies_1000 = generate_pat(0, 'ies', 8, '1000')
    res_ies_3000 = re.findall(p_ies_3000, config)
    res_ies_1000 = re.findall(p_ies_1000, config)
    if len(res_ies_1000) != 2:
        return err

    res_ies_1000_address = re.findall(PAT['address'], res_ies_1000[1][0])
    if len(res_ies_3000) != 2:
        return err
    else:
        res_address = re.findall(PAT['address'], res_ies_3000[1][0])
        inside_addresss = get_nat_address(config)

        if res_address == []:
            err.append('ies 3000 中没有找到address\n\n')
        if inside_addresss == []:
            err.append('ies 3000 中没有找到inside\n\n')

        if err != []:
            return err
        #获取addres中的私网地址
        for add in res_address:
            if nat_check(add):
                address_nat.append(add)


        err_ips = address_include_each(address_nat, inside_addresss)

        for item in err_ips:
            if item not in res_ies_1000_address:
                err.append('ies 3000 sub interface下的私网地址与 Nat 中 inside 地址不一致\n   请检查 \"address {}\"\n'.format(item))
    return err