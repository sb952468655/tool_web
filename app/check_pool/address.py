import re
from .config_7750 import *
from .common import get_ies_address, get_pool_ip, get_nat_address, nat_check, address_is_in_list, address_include_each

def get_ym(ip_begin, ip_end):
    ip1_list = ip_begin.split('.')
    ip2_list = ip_end.split('.')

    ip1_str = ''
    ip2_str = ''

    for item in ip1_list:
        bin_str = str(bin(int(item))).replace('0b','')
        while len(bin_str) < 8:
            bin_str = '0' + bin_str
        ip1_str += bin_str

    for item in ip2_list:
        bin_str = str(bin(int(item))).replace('0b','')
        while len(bin_str) < 8:
            bin_str = '0' + bin_str
        ip2_str += bin_str

    num = 0

    for index, item in enumerate(ip1_str):
        if item == ip2_str[index]:
            num += 1
        else:
            break

    return num

def compare_ip(ip, ip_range):

    ip1 = ip.split('/')[0]
    ym = ip.split('/')[1]

    ip_b = ip_range.split('-')[0]
    ip_e = ip_range.split('-')[1]

    if ym == str(get_ym(ip_b, ip_e)) and ip1[:-3] == ip_b[:-3] and ip1[-1] == '0' and ip_b[-1] == '1':
        return True
    else:
        return False

def compare_ip2(ip, ip_range):

    ip1 = ip.split('/')[0]
    ym = ip.split('/')[1]

    ip_b = ip_range.split('-')[0]
    ip_e = ip_range.split('-')[1]

    if ym == str(get_ym(ip_b, ip_e)) and ip1[:-3] == ip_b[:-3] and ip1[-1] == '0' and ip_b[-1] == '2':
        return True
    else:
        return False

def prefix_list_include_black_hole(config):
    '''检查 prefix-list 中是否包含 黑洞路由地址'''

    err = []

    p1 = r'static-route (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w\w) black-hole preference 200'
    p_static_route2 = PAT['static_route']
    p_prefix_list = r'(?s)(prefix-list "(ies2bgp|plToCR)"(\n {16}prefix \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w\w (longer|exact))+\n {12}exit)'

    p_address = r'prefix (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d\d)'

    obj1 = re.compile(p1)
    obj_static_route2 = re.compile(p_static_route2)
    obj_prefix_list = re.compile(p_prefix_list)
    obj_adress = re.compile(p_address)

    res1 = obj1.findall(config)
    res_static_route2 = obj_static_route2.findall(config)
    res_prefix_list = obj_prefix_list.search(config)

    if res1 == [] and res_static_route2 == []:
        err += '配置中没有找到 static-route 配置\n\n'
        return err
    else:
        if res_static_route2:
            res1 = [ item[1] for item in res_static_route2 ]
        if res_prefix_list == None:
            err.append('配置中没有找到 路由发布 prefix_list 配置\n\n')
            return err
        else:
            res_adress = obj_adress.findall(res_prefix_list.group())
            black_hole_address = res1
            err_ips = []
            for ip in black_hole_address:
                if not address_is_in_list(ip, res_adress):
                    err_ips.append(ip)
            if err_ips != []:
                for item in err_ips:
                    if item in res_adress:
                        err.append('路由发布 prefix-list 与 黑洞路由地址不一致\n   请检查 \"prefix-list {}\"\n'.format(item))
                    else:
                        err.append('路由发布 prefix-list 与 黑洞路由地址不一致\n   请检查 \"static-route-entry {}\"\n'.format(item))
    return err


def black_hole_address_range_check(config):
    '''检查黑洞路由与pool "nat-pppoe" 中的address-range 是否匹配'''

    err = []
    p_pool = r'(?s)( pool "nat-pppoe" nat-group 1 type l2-aware create ?\n.*?\n {16}exit)'
    p_address_range = r'address-range (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) create'

    res_black_hole = re.findall(PAT['static_route'], config)
    res_pool = re.search(p_pool, config)
    if not res_pool:
        # return '配置中没有找到 pool "nat-pppoe"\n'
        return ''

    for black_hole in res_black_hole:

        res_address_range = re.findall(p_address_range, res_pool.group())
        for item in res_address_range:
            if not compare_ip(black_hole[1],item[0] + '-' + item[1]):
                err.append('static-route-entry {} 与 address-range  {} 不匹配\n'.format(black_hole[1],item[0]+ ' ' + item[1]))

    return err

def inside_subnet_address_check(config):
    '''检查 inside subnet address 地址是否正确
    1.inside 中的私网地址必须在 subnet 和 address 中
    2.subnet 和 address 中的公网地址必须一致'''
    err = []

    subnets = get_pool_ip(config)
    addresss = get_ies_address(config)
    nat_addresss = get_nat_address(config)

    subnet_nat = []
    address_nat = []

    subnet_address = []
    if subnets == []:
        err.append('配置中没有找到pool中的subnet\n\n')
    if addresss == []:
        err.append('配置中没有找到address\n\n')

    if err != []:
        return err
    # if nat_addresss == []:
    #     err = '没有找到inside地址\n'


    for item in subnets:
        subnet_address.append(item[1])

    if nat_addresss != []:

        #获取subnet中的私网地址
        
        for subnet in subnet_address:
            if nat_check(subnet):
                subnet_nat.append(subnet)
                # subnet_address.remove(subnet)

        #获取address中的私网地址
        
        for address in addresss:
            if nat_check(address):
                address_nat.append(address)
                # addresss.remove(address)

        #subnet, address 去掉私网地址
        for item in subnet_nat:
            subnet_address.remove(item)
        for item in address_nat:
            addresss.remove(item)

        if subnet_nat == []:
            err.append('   subnet 中没有发现私网地址\n\n')
        if address_nat == []:
            err.append('   address 中没有发现私网地址\n\n')

        if err != []:
            return err

        #检查nat中的私网地址是否在subnet和address地址中
        for nat in nat_addresss:
            if not address_is_in_list(nat, subnet_nat):
                err.append('inside 地址 %s 不在 subnet 中\n   请检查 \"address  %s\"\n' % (nat, nat))
            if not address_is_in_list(nat, address_nat):
                err.append('inside 地址 %s 不在 address 中\n   请检查 \"address  %s\"\n' % (nat, nat))
    else:
        err.append('   inside 没有找到，请维护人员核查\n\n')


    #检查subnet中的公网地址和address中的公网地址是否一致
    err_ips = address_include_each(subnet_address, addresss)
    if err_ips != []:
        for item in err_ips:
            err.append('subnet中的公网地址和address中的公网地址不一致\n   请检查 \"address {}\"\n'.format(item))
    
    return err



def ludb_check(config):
    '''检查 ludb 配置是否正确'''

    err = ''
    #检查ludb-m，配置group-interface "mhsi-" suffix port-id是正确，不一样出告警
    #检查ludb-s，配置group-interface "shsi-" suffix port-id是正确，不一样出告警

    p_ludb_m = r'''local-user-db "ludb-m" create
(.* ?\n)+        exit'''

    p_ludb_s = r'''local-user-db "ludb-s" create
(.* ?\n)+        exit'''
    p_mhsi = r'''(group-interface "(mhsi-.*)" create
(.*\n)+                exit)'''

    p_shsi = r'''(group-interface "(shsi-.*)" create
(.*\n)+                exit)'''
    p_capture_sap = r'''(sap (.*) capture-sap create
(                .*\n)+            exit)'''

    obj_ludb_m = re.compile(p_ludb_m)
    obj_ludb_s = re.compile(p_ludb_s)
    obj_mhsi = re.compile(p_mhsi)
    obj_shsi = re.compile(p_shsi)
    obj_capture_sap = re.compile(p_capture_sap)

    res_ludb_m = obj_ludb_m.search(config)
    res_ludb_s = obj_ludb_s.search(config)
    res_mhsi = obj_mhsi.findall(config)
    res_shsi = obj_shsi.findall(config)
    res_capture_sap = obj_capture_sap.findall(config)

    if res_ludb_m:
        if 'group-interface "mhsi-" suffix port-id' not in res_ludb_m.group():
            err += 'ludb-m 中没有找到group-interface "mhsi-" suffix port-id\n'
    else:
        err += '没有找到ludb-m\n' 
    if res_ludb_s:
        if 'group-interface "shsi-" suffix port-id' not in res_ludb_s.group():
            err += 'ludb-m 中没有找到group-interface "mhsi-" suffix port-id\n'
    else:
        err += '没有找到ludb-s\n'

    if res_mhsi == []:
        err += '没找到以mhsi-开头的group-interface\n'
    else:
        for item in res_mhsi:
            if 'user-db "ludb-m"' not in item[0]:
                err += '{} 中没有找到 user-db "ludb-m"\n'.format('group-interface ' + item[1])

            if 'pppoe-policy-m' not in item[0]:
                err += '{} 中没有找到 pppoe-policy-m\n'.format('group-interface ' + item[1])

            if 'python-policy "qu-port"' not in item[0]:
                err += '{} 中没有找到 python-policy "qu-port"\n'.format('group-interface ' + item[1])

    if res_shsi == []:
        err += '没找到以shsi-开头的group-interface\n'
    else:
        for item in res_shsi:
            if 'user-db "ludb-s"' not in item[0]:
                err += '{} 中没有找到 user-db "ludb-s"\n'.format('group-interface ' + item[1])

            if 'pppoe-policy-s' not in item[0]:
                err += '{} 中没有找到 pppoe-policy-s\n'.format('group-interface ' + item[1])

            if 'python-policy "qu-port"' not in item[0]:
                err += '{} 中没有找到 python-policy "qu-port"\n'.format('group-interface ' + item[1])        

    if res_capture_sap == []:
        err += '没有找到capture-sap\n'
    else:
        for item in res_capture_sap:
            if 'user-db "ludb-m"' in item[0] and 'pppoe-policy-m' in item[0] and 'pppoe-python-policy "qu-port"' in item[0]:
                pass
            elif 'user-db "ludb-s"' in item[0] and 'pppoe-policy-s' in item[0] and 'pppoe-python-policy "qu-port"' in item[0]:
                pass
            else:
                err += 'sap {} 配置错误\n'.format(item[1])

    return err






#私网不发布 检查
def swbfb(config):
    err = ''
    err = prefix_list_include_black_hole(config)
    err += black_hole_address_range_check(config)

    # err += inside_subnet_address_check(config)
    # err += ludb_check(config)

    if err == '':
        err = '● 私网不发布 -> OK\n\n'
    else:
        err += '● 私网不发布 -> ERROR\n\n' + err

    return err

    

#私网发布
def swfb(config):
    #私网地址基于地址池核查，地址池有的，黑洞路由、路由发布、ies3000下应该有
    err = ''
    
    err = prefix_list_include_black_hole(config)
    err += black_hole_address_range_check(config)

    # err += inside_subnet_address_check(config)
    # err += ludb_check(config)

    if err == '':
        err = '● 私网发布 -> OK\n\n'
    else:
        err += '● 私网发布 -> ERROR\n\n' + err

    return err