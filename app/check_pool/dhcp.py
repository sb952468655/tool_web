# encoding = utf-8

import re
import IPy

def dhcp_check(config):
    '''Dhcp有关地址一致性检查'''

    #地址池pool "iptv"、"pppoe"、“vippool”地址私网网段检查，私网地址段需包含在l2-aware下

    err = ''

    err += check_pool_in_l2_aware('iptv', config)
    err += check_pool_in_l2_aware('pppoe', config)
    # err += check_pool_in_l2_aware('vippool', config)
    err += check_pool_in_l2_aware('video', config)


    #地址池pool "iptv"的地址需在ies 1000下subscriber-interface 下对应配置网关地址
    #地址池pool "pppoe"、“vippool”的地址需在ies 3000下subscriber-interface 下对应配置网关地址
    err += check_pool_sub(config)

    #地址池pool "iptv"、"pppoe"、“vippool”地址公网网段检查，公网地址段需包含在prefix-list "ies2bgp"下配置
    err += check_pool_prefix_list(config)

    #如是iptv业务pool下subnet中options  default-router需配置，地址应为本subnet段第一个地址
    err +=  check_subnet(config)

    #nat outside 公网地址，对应公网地址需配置black-hole路由，需在prefix-list "ies2bgp"下配置
    err +=  check_nat(config)

    #检查static-route-entry preference iptv配置preference 240、pppoe配置preference 200
    err += check_static_route_entry(config) 

    #subscriber-interface 下gi地址应为subscriber-interface网关地址其中地址之一
    #subscriber-interface xxx下gi地址应为local-dhcp-server "server1"中，pool "iptv"下，某一subnet的default-router
    err += check_gi(config)

    if err == '':
        err = 'lDhcp有关地址一致性检查 -> OK\n\n'
    else:
        err = 'Dhcp有关地址一致性检查 -> 请进行确认\n\n' + err + '\n\n'

    return err


def is_sw(ip):
    '''判断是否是私网'''

    sw = ['10', '100', '172']

    ips = ip.split('.')
    if ips[0] in sw:
        return True
    else:
        return False

def is_include(ip1, ip2):
    '''判断ip1是否包含在ip2中'''

    ip_a = IPy.IP(ip1, make_net=1)
    ip_b = IPy.IP(ip2, make_net=1)

    if ip_a in ip_b:
        return True
    else:
        return False

def check_pool_in_l2_aware(pool, config):
    '''检查pool中的地址是否包含在l2_aware中'''

    err = ''
    p_address = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2}'
    p_pool = r'(?s)pool "'+ pool +r'" create.*?\n {16}exit'
    p_l2_aware = r'(?s)l2-aware\n.*?\n {16}exit'
    res_l2_aware = re.search(p_l2_aware, config)
    if res_l2_aware:
        res_l2_address = re.findall(p_address, res_l2_aware.group())
    else:
        return '没有找到l2_aware'
    res_pool = re.search(p_pool, config)
    if res_pool:
        res_address = re.findall(p_address, res_pool.group())

        for i in res_address:
            is_in = False
            if is_sw(i):
                for j in res_l2_address:
                    if is_include(i, j):
                        is_in = True
                        break
                if not is_in:
                    if i.startswith('100.'):
                        err += 'pool {} {} 对应在l2-aware下缺配置，请对该项人工检查复核！\n'.format(pool, i)
                    else:
                        err += 'pool {} {} 对应在l2-aware下缺配置\n'.format(pool, i)
    else:
        err = '没有找到pool {}\n'.format(pool)


    return err

def check_pool_sub(config):
    '''地址池pool "iptv"的地址需在ies 1000下subscriber-interface 下对应配置网关地址
    地址池pool "pppoe"、“vippool”的地址需在ies 3000下subscriber-interface 下对应配置网关地址'''

    err = ''
    p_ies_1000 = r'(?s)(ies 1000( name ".*?")? customer \d{1,2} create.*?\n {8}exit)'
    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create.*?\n {8}exit)'
    p_sub_inter = r'(?s)(subscriber-interface "(.*?)" create.*?\n {12}exit)'

    p_pool_iptv = r'(?s)pool "iptv" create.*?\n {16}exit'
    p_pool_pppoe = r'(?s)pool "pppoe" create.*?\n {16}exit'
    p_pool_vippool = r'(?s)pool "vippool" create.*?\n {16}exit'
    p_address = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2}'

    res_pool_iptv = re.search(p_pool_iptv, config)
    res_pool_pppoe = re.search(p_pool_pppoe, config)
    res_pool_vippool = re.search(p_pool_vippool, config)

    res_ies_1000 = re.findall(p_ies_1000, config)
    if len(res_ies_1000)!= 2:
        err = '没有找到ies 1000\n'
        return err

    res_ies_3000 = re.findall(p_ies_3000, config)
    if len(res_ies_3000)!= 2:
        err = '没有找到ies 3000\n'
        return err

    res_ies_1000_sub = re.findall(p_sub_inter, res_ies_1000[1][0])
    res_ies_3000_sub = re.findall(p_sub_inter, res_ies_3000[1][0])

    ies_1000_address = []
    for i in res_ies_1000_sub:
        res_address = re.findall(p_address, i[0])
        ies_1000_address += res_address


    ies_3000_address = []
    for i in res_ies_3000_sub:
        res_address = re.findall(p_address, i[0])
        # if not res_address:
        #     err += 'pool xxx  subnet x.x.x.0/24在ies xxxx subscriber-interface下缺网关地址配置'
        ies_3000_address += res_address


    if res_pool_iptv:
        res_address = re.findall(p_address, res_pool_iptv.group())

        for i in res_address:
            is_in = False

            for j in ies_1000_address:
                if is_include(i, j):
                    is_in = True
                    break
            if not is_in:
                err += 'pool iptv subnet {} 在ies 1000 subscriber-interface下缺少网关地址配置\n'.format(i)

    if res_pool_pppoe:
        res_address = re.findall(p_address, res_pool_pppoe.group())

        for i in res_address:
            is_in = False
            
            for j in ies_3000_address:
                if is_include(i, j):
                    is_in = True
                    break
            if not is_in:
                err += 'pool pppoe subnet {} 在ies 3000 subscriber-interface下缺少网关地址配置\n'.format(i)

    if res_pool_vippool:
        res_address = re.findall(p_address, res_pool_vippool.group())

        for i in res_address:
            is_in = False
            for j in ies_3000_address:
                if is_include(i, j):
                    is_in = True
                    break
            if not is_in:
                err += 'pool vippool subnet {} 在ies 3000 subscriber-interface下缺少网关地址配置\n'.format(i)



    return err


def check_pool_prefix_list(config):
    '''地址池pool "iptv"、"pppoe"、“vippool”地址公网网段检查，公网地址段需包含在prefix-list "ies2bgp"下配置'''

    err = ''
    p_pool_iptv = r'(?s)pool "iptv" create.*?\n {16}exit'
    p_pool_pppoe = r'(?s)pool "pppoe" create.*?\n {16}exit'
    p_pool_vippool = r'(?s)pool "vippool" create.*?\n {16}exit'
    p_pool_video = r'(?s)pool "video" create.*?\n {16}exit'
    p_address = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2}'
    p_prefix_list_ies2bgp = r'(?s)prefix-list "ies2bgp".*?\n {12}exit'

    res_pool_iptv = re.search(p_pool_iptv, config)
    res_pool_pppoe = re.search(p_pool_pppoe, config)
    res_pool_vippool = re.search(p_pool_vippool, config)
    res_pool_video = re.search(p_pool_video, config)

    res_prefix_list_ies2bgp = re.search(p_prefix_list_ies2bgp, config)
    if not res_prefix_list_ies2bgp:
        return '没有找到prefix-list "ies2bgp"\n'
    res_address_prefix_list = re.findall(p_address, res_prefix_list_ies2bgp.group())


    # if res_pool_iptv:
    #     res_address = re.findall(p_address, res_pool_iptv.group())

    #     for i in res_address:
    #         is_in = False

    #         for j in res_address_prefix_list:
    #             if is_include(i, j):
    #                 is_in = True
    #                 break
    #         if not is_in:
    #             err += 'pool iptv {} 对应在prefix-list "ies2bgp"下缺配置\n'.format(i)

    if res_pool_pppoe:
        res_address = re.findall(p_address, res_pool_pppoe.group())

        for i in res_address:
            is_in = False

            for j in res_address_prefix_list:
                if is_include(i, j):
                    is_in = True
                    break
            if not is_in:
                err += 'pool pppoe {} 对应在prefix-list "ies2bgp"下缺配置\n'.format(i)


    if res_pool_vippool:
        res_address = re.findall(p_address, res_pool_vippool.group())

        for i in res_address:
            is_in = False
            for j in res_address_prefix_list:
                if is_include(i, j):
                    is_in = True
                    break
            if not is_in:
                err += 'pool vippool {} 对应在prefix-list "ies2bgp"下缺配置\n'.format(i)

    if res_pool_video:
        res_address = re.findall(p_address, res_pool_video.group())

        for i in res_address:
            is_in = False
            for j in res_address_prefix_list:
                if is_include(i, j):
                    is_in = True
                    break
            if not is_in:
                err += 'pool video {} 对应在prefix-list "ies2bgp"下缺配置，请对该项人工检查复核！\n'.format(i)

    return err


def check_subnet(config):
    '''如是iptv业务pool下subnet中options  default-router需配置，地址应为本subnet段第一个地址
    subnet 与 address-range 在同一个网段'''

    err = ''
    p_pool = r'(?s)(pool "(.*?)" create.*?\n {16}exit)'
    p_subnet = r'(?s)(subnet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d\d) create.*?\n {20}exit)'
    p_default_router = r'default-router (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    p_address_range = r'address-range (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    res_pool = re.findall(p_pool, config)
    for i in res_pool:
        res_subnet = re.findall(p_subnet, i[0])
        for j in res_subnet:
            res_default_router = re.search(p_default_router, j[0])
            if res_default_router:
                default_router = IPy.IP(res_default_router.group(1), make_net=1)
                subnet = IPy.IP(j[1], make_net=1)
                if default_router != subnet[1]:
                    err += 'pool {} default-router {} 不是subnet {} 段第一个地址\n'.format(i[1], res_default_router.group(1), j[1])

            res_address_range = re.search(p_address_range, j[0])
            if res_address_range:
                subnet = IPy.IP(j[1], make_net=1)
                ip_b = IPy.IP(res_address_range.group(1))
                ip_e = IPy.IP(res_address_range.group(2))

                if ip_b not in subnet or ip_e not in subnet:
                    err += 'pool {} subnet {} 和 {} 不在一个网段\n'.format(i[1], j[1], res_address_range.group())


                

    return err

def check_nat(config):
    '''nat outside 公网地址，对应公网地址需配置black-hole路由，需在prefix-list "ies2bgp"下配置'''

    err = ''
    p_outside = r'(?s)outside.*?\n {12}exit'
    p_address_range = r'address-range (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    p_prefix_list_ies2bgp = r'(?s)prefix-list "ies2bgp".*?\n {12}exit'
    p_static_route_configuration = r'(?s)echo "Static Route Configuration"\n#-{50}.*?\n#-{50}'
    p_static_route = r'(?s)static-route-entry (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w\w).*?\n {8}exit'
    p_address = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2}'

    res_prefix_list_ies2bgp = re.search(p_prefix_list_ies2bgp, config)
    if not res_prefix_list_ies2bgp:
        return '没有找到prefix-list "ies2bgp"\n'
    res_static_route_configuration = re.search(p_static_route_configuration, config)
    if not res_static_route_configuration:
        return '没有找到Static Route Configuration\n'
    res_static_route = re.findall(p_static_route, res_static_route_configuration.group())
    res_address = re.findall(p_address, res_prefix_list_ies2bgp.group())
    res_outside = re.search(p_outside, config)
    if res_outside:
        res_address_range = re.findall(p_address_range, res_outside.group())
        for i in res_address_range:
            ip_b = IPy.IP(i[0])
            ip_e = IPy.IP(i[1])
            is_include = False
            for j in res_address:
                address = IPy.IP(j, make_net=1)
                if ip_b in address and ip_e in address:
                    is_include = True
                    break

            if not is_include:
                err += 'outside address-range {}-{} 没有在prefix-list "ies2bgp"下配置\n'.format(i[0], i[1])

            #nat outside 公网地址，对应公网地址需配置black-hole路由
            is_include = False
            for j in res_static_route:
                static_route = IPy.IP(j, make_net=1)
                if ip_b in static_route and ip_e in static_route:
                    is_include = True
                    break

            if not is_include:
                err += 'outside  address-range {}-{} 没有配置黑洞路由\n'.format(i[0], i[1])

    return err

def check_gi(config):
    '''subscriber-interface 下gi地址应为subscriber-interface网关地址其中地址之一
    subscriber-interface xxx下gi地址应为local-dhcp-server "server1"中，pool "iptv"下，某一subnet的default-router'''

    err = ''
    p_local_dhcp_server = r'(?s)echo "Local DHCP Server \(Base Router\) Configuration"\n#-{50}.*?\n#-{50}'
    p_ies_1000 = r'(?s)(ies 1000( name ".*?")? customer \d{1,2} create.*?\n {8}exit)'
    p_sub_inter = r'(?s)(subscriber-interface "(.*?)" create.*?\n {12}exit)'
    p_gi_address = r'gi-address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    p_address = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w{2}'
    p_local_dhcp_server_1 = r'(?s)local-dhcp-server "server1" create\n.*?\n {12}exit'
    p_default_router = r'default-router (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    p_pool_iptv = r'(?s)pool "iptv" create.*?\n {16}exit'
    p_subnet = r'(?s)(subnet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d\d) create.*?\n {20}exit)'

    res_ies_1000 = re.findall(p_ies_1000, config)
    if len(res_ies_1000)!= 2:
        err = '没有找到ies 1000\n'
        return err

    res_local_dhcp_server = re.search(p_local_dhcp_server, config)
    if not res_local_dhcp_server:
        return '没有找到Local DHCP Server (Base Router) Configuration\n'

    res_local_dhcp_server_1 = re.search(p_local_dhcp_server_1, res_local_dhcp_server.group())
    if not res_local_dhcp_server_1:
        return '没有找到local-dhcp-server "server1"\n'

    res_pool_iptv = re.search(p_pool_iptv, res_local_dhcp_server_1.group())
    if not res_pool_iptv:
        return '没有找到pool "iptv"\n'

    res_default_router = re.findall(p_default_router, res_pool_iptv.group())

    #检查所有sunnet中default_router是否缺失
    res_subnet = re.findall(p_subnet, res_pool_iptv.group())
    for i in res_subnet:
        if 'default-router' not in i[0]:
            err += 'pool "iptv" subnet {} default-router缺失\n'.format(i[1])

    res_sub_inter = re.findall(p_sub_inter, res_ies_1000[1][0])
    for i in res_sub_inter:
        res_address = re.findall(p_address, i[0])
        res_gi_address = re.search(p_gi_address, i[0])
        if not res_gi_address:
            err += 'ies 1000 subscriber-interface "{}" 中缺少gi-address\n'.format(i[1])
            continue
        gi_address = IPy.IP(res_gi_address.group(1))
        is_include = False
        if not res_address:
            err += 'ies 1000 subscriber-interface "{}" 中没有address\n'.format(i[1])
        else:
            for j in res_address:
                address = IPy.IP(j, make_net=1)
                if gi_address in address:
                    is_include = True
                    break

            if not is_include:
                err += 'ies 1000 subscriber-interface "{}" gi-address 不包含在address中\n'.format(i[1])

        if res_gi_address.group(1) not in res_default_router:
            err += 'ies 1000 subscriber-interface "{}" gi-address 没有在local-dhcp-server "server1" pool "iptv" default-router中\n'.format(i[1])


    return err


def check_static_route_entry(config):
    '''检查static-route-entry preference iptv配置preference 240、pppoe配置preference 200
    根据地址段属于哪个pool来确定， iptv配置： pool名称带iptv， pppoe配置： pool名称带pppoe'''

    err = ''
    p_static_route_configuration = r'(?s)echo "Static Route Configuration"\n#-{50}.*?\n#-{50}'
    p_static_route = r'(?s)(static-route-entry (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w\w).*?\n {8}exit)'
    p_out_side = r'(?s)outside\n.*?\n {12}exit'
    p_pool_iptv = r'(?s)pool "nat-iptv" nat-group \d{1,2} type l2-aware create.*?\n {16}exit'
    p_pool_pppoe = r'(?s)pool "nat-pppoe" nat-group \d{1,2} type l2-aware create.*?\n {16}exit'
    p_preference = r'preference (\d{3})'
    p_address_range = r'address-range (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    p_black_hole = r'black-hole\n.*?\n {12}exit'


    res_outside = re.search(p_out_side, config)
    if not res_outside:
        err = '没有找到outside\n'
        return err
    res_pool_iptv = re.search(p_pool_iptv, res_outside.group())
    res_pool_pppoe = re.search(p_pool_pppoe, res_outside.group())
    if not res_pool_iptv:
        return '没有找到pool "nat-iptv"\n'
    if not res_pool_pppoe:
        return '没有找到pool "nat-pppoe"\n'

    res_address_range_iptv = re.findall(p_address_range, res_pool_iptv.group())
    res_address_range_pppoe = re.findall(p_address_range, res_pool_pppoe.group())

    res_static_route_configuration = re.search(p_static_route_configuration, config)
    if res_static_route_configuration:
        res_static_route = re.findall(p_static_route, res_static_route_configuration.group())
        for i in res_static_route:
            entry = IPy.IP(i[1], make_net=1)
            for j in res_address_range_iptv:
                ip_b = IPy.IP(j[0])
                ip_e = IPy.IP(j[1])

                if is_include(ip_b, entry) and is_include(ip_e, entry):
                    res_preference = re.search(p_preference, i[0])
                    if not res_preference:
                        err += 'static-route-entry {} 缺少 preference 240配置\n'.format(i[1])
                    elif res_preference.group(1) != '240':
                        err += 'static-route-entry {} preference 配置错误，请对该项人工检查复核！\n'.format(i[1])
                    break

            for j in res_address_range_pppoe:
                ip_b = IPy.IP(j[0])
                ip_e = IPy.IP(j[1])

                if is_include(ip_b, entry) and is_include(ip_e, entry):
                    res_preference = re.search(p_preference, i[0])
                    if not res_preference:
                        err += 'static-route-entry {} 缺少 preference 200配置\n'.format(i[1])
                    elif res_preference.group(1) != '200':
                        err += 'static-route-entry {} preference 配置错误，请对该项人工检查复核！\n'.format(i[1])
                    break

    # return err
    return ('Dhcp相关地址一致性检查', err, '')

