import re, logging

def generate_p(key):
    '''生产正则规则'''
    key = key.replace('(', '\(').replace(')', '\)')
    return r'(?s)(echo "key"\n.*?#.*?\n#)'.replace('key', key)

def get_system_name(config):
    '''获取设备名称'''
    sys_name = ''
    p = generate_p('System Configuration')
    p_sys_name = r'name "(.*?)"'
    res = re.search(p, config)
    if res:
        res_sys_name = re.search(p_sys_name, res.group())
        if res_sys_name:
            sys_name = res_sys_name.group(1)
        else:
            sys_name = '缺设备名称配置'


    return sys_name

def get_system_ip(config):
    '''获取system ip'''

    ipv4 = ''
    ipv6 = ''
    p = generate_p('Router (Network Side) Configuration')
    p_ipv4 = r'(?s) interface "system"\n {12}address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})'
    p_ipv6 = r'(?s) ipv6\n {16}address (.*?/\d{1,3})'

    res = re.search(p, config)
    if res:
        res_ipv4 = re.search(p_ipv4, res.group())
        res_ipv6 = re.search(p_ipv6, res.group())

        if res_ipv4:
            ipv4 = res_ipv4.group(1)
        else:
            ipv4 = '缺ipv4配置'
        if res_ipv6:
            ipv6 = res_ipv6.group(1)
        else:
            ipv6 = '缺ipv6配置'
    else:
        err = '没有找到Router (Network Side) Configuration\n'

    return '{};{}'.format(ipv4, ipv6)


def get_radius_ip(config):
    '''与radius交互的ip'''

    radius_ip = ''
    p = generate_p('AAA Configuration')
    p_radius_server_policy = r'(?s)radius-server-policy "pppoe-radius-p1" create.*?\n {8}exit'
    p_source_address = r'source-address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    res = re.search(p, config)
    if res:
        res_radius_server_policy = re.search(p_radius_server_policy, res.group())
        if res_radius_server_policy:
            res_source_address = re.search(p_source_address, res_radius_server_policy.group())
            if res_source_address:
                radius_ip = res_source_address.group(1)
            else:
                radius_ip = '缺少与radius交互的ip配置'
    else:
        radius_ip = '没有找到AAA Configuration\n'

    return '{}\n'.format(radius_ip)


def get_port_and_description(config):
    '''上行接口的端口号及描述'''

    port_data = []
    port_str = ''
    p = generate_p('Router (Network Side) Configuration')
    p_port = generate_p('Port Configuration')
    p_port_port = r'(?s)(port (\d{1,2}/\d{1,2}/\d{1,2}).*?\n {4}exit)'
    p_port_description = r'description "(.*?)"'
   
    res = re.search(p, config)
    if res:
        res_router_port = re.findall('port (\d{1,2}/\d{1,2}/\d{1,2})', res.group())
        res_port = re.search(p_port, config)
        if res_port:
            res_port_port = re.findall(p_port_port, res_port.group())
            for i in res_router_port:
                for j in res_port_port:
                    if i == j[1]:
                        res_port_description = re.search(p_port_description, j[0])
                        if res_port_description:
                            port_data.append((i, res_port_description.group(1)))
                        else:
                            port_data.append((i, ''))
    else:
        err = '没有找到Router (Network Side) Configuration\n'

    for i in port_data:
        if not i[1]:
            port_str += '{} description "{}"\n'.format(i[0], '缺少描述，请确认')
        else:
            port_str += '{} description "{}"\n'.format(i[0], i[1])

    return port_str


def radius_check(config):
    '''1.aaa配置下的radius-server-policy "pppoe-radius-p1"应包含  server 2 name "pppoe-radius-s184"
    server 4 name "pppoe-radius-s18"
    2.radius-server下包含下面标黄色配置'''

    err = ''
    p = generate_p('AAA Configuration')
    p_radius_server = generate_p('RADIUS Server Configuration')
    p_subscriber_mgmt = generate_p('Subscriber-mgmt Configuration')
    p_subscriber_mgmt_service_side = generate_p('Subscriber-mgmt (Service Side) Configuration')
    p_radius_server_policy = r'(?s)radius-server-policy "pppoe-radius-p1" create.*?\n {8}exit'
    p_authentication_policy = r'(?s)authentication-policy "auth-pppoe-p1" create.*?\n {8}exit'
    res = re.search(p, config)
    res_radius_server = re.search(p_radius_server, config)
    res_subscriber_mgmt = re.search(p_subscriber_mgmt, config)
    res_subscriber_mgmt_service_side = re.search(p_subscriber_mgmt_service_side, config)

    if res:
        res_server_policy = re.search(p_radius_server_policy, res.group())
        if res_server_policy:

            if 'server 2 name "pppoe-radius-s184"' not in res_server_policy.group():
                err += 'aaa 中没有server 2 name "pppoe-radius-s184\n'
            if 'server 4 name "pppoe-radius-s18"' not in res_server_policy.group():
                err += 'aaa 中没有server 4 name "pppoe-radius-s18"\n'
    else:
        err += '没有找到AAA Configuration\n'
    

    if res_radius_server:
        if 'server "pppoe-radius-s18" address 211.138.200.18' not in res_radius_server.group():
            err += 'RADIUS Server 中没有 server "pppoe-radius-s18" address 211.138.200.18\n'

        if ' server "pppoe-radius-s184" address 221.131.129.184' not in res_radius_server.group():
            err += 'RADIUS Server 中没有  server "pppoe-radius-s184" address 221.131.129.184\n'
    else:
        err += '没有找到RADIUS Server Configuration\n'


    if res_subscriber_mgmt:
        res_authentication_policy = re.search(p_authentication_policy, res_subscriber_mgmt.group())
        if not res_authentication_policy:
            err += 'Subscriber-mgmt 中没有 authentication-policy "auth-pppoe-p1"\n'
        else:
            if 'fallback-action user-db "no-auth"' not in res_authentication_policy.group():
                err += 'Subscriber-mgmt 中没有 fallback-action user-db "no-auth"\n'
    else:
        err += '没有找到Subscriber-mgmt Configuration\n'

    if res_subscriber_mgmt_service_side:
        if 'local-user-db "no-auth"' not in res_subscriber_mgmt_service_side.group():
            err += 'Subscriber-mgmt (Service Side) 中没有 local-user-db "no-auth"'
    else:
        err += '没有找到Subscriber-mgmt (Service Side) Configuration\n'

    return err

def video_check(config):
    '''检查设备上video局数据及接口数据配置规范性与配置覆盖率，若存在不符合配置规范或配置缺失
    local-user-db "ludb-m"和local-user-db "ludb-s"的ppp中包含如下host "video"配置'''

    err = ''
    p = generate_p('Subscriber-mgmt (Service Side) Configuration')
    p_ludb_m = r'(?s)local-user-db "ludb-m" create.*?\n {8}exit'
    p_ludb_s = r'(?s)local-user-db "ludb-s" create.*?\n {8}exit'
    p_host_video = r'(?s)host "video" create.*?\n {16}exit'

    str1 = r'''host-identification
                        username "VIDEO" domain-only
                    exit'''

    str2 = r'''address pool "video"'''
    str3 = r'''ipv6-delegated-prefix-pool'''
    str4 = r'''ipv6-slaac-prefix-pool'''

    res = re.search(p, config)
    if res:
        
        res_ludb_m = re.search(p_ludb_m, res.group())
        res_ludb_s = re.search(p_ludb_s, res.group())

        if res_ludb_m:
            res_host_video = re.search(p_host_video, res_ludb_m.group())
            if res_host_video:
                if str1 not in res_host_video.group():
                    err += 'local-user-db "ludb-m" host-identification 配置错误\n'
                if str2 not in res_host_video.group():
                    err += 'local-user-db "ludb-m" 缺少 address pool "video"\n'
                if str3 not in res_host_video.group():
                    err += 'local-user-db "ludb-m" 缺少 ipv6-delegated-prefix-pool\n'
                if str4 not in res_host_video.group():
                    err += 'local-user-db "ludb-m" 缺少 ipv6-slaac-prefix-pool\n'
            else:
                err += 'local-user-db "ludb-m" 缺少 host "video" 配置，请检查确认\n'
        else:
            err += '没有找到local-user-db "ludb-m"\n'

        if res_ludb_s:
            res_host_video = re.search(p_host_video, res_ludb_s.group())
            if res_host_video:
                if str1 not in res_host_video.group():
                    err += 'local-user-db "ludb-s" host-identification 配置错误\n'
                if str2 not in res_host_video.group():
                    err += 'local-user-db "ludb-s" 缺少 address pool "video"\n'
                if str3 not in res_host_video.group():
                    err += 'local-user-db "ludb-s" 缺少 ipv6-delegated-prefix-pool\n'
                if str4 not in res_host_video.group():
                    err += 'local-user-db "ludb-s" 缺少 ipv6-slaac-prefix-pool\n'
            else:
                err += 'local-user-db "ludb-s" 缺少 host "video" 配置，请检查确认\n'
        else:
            err += '没有找到local-user-db "ludb-s"\n'
    else:
        err += '没有找到Subscriber-mgmt (Service Side) Configuration\n'


    return err


def lag_check(config):
    '''从ies 3000中读取subscriber-interface "pppoe"下的group-interface的lag信息，作为下一步的比对参照
    检索到subscriber-interface "VPN_JS_JMCC_IMS"后，检查其下group-interface中包含的lag信息是否与上一步作为比对信息的lag信息是否有缺少'''

    err = ''
    lags_cms = []
    lags_ims = []
    saps_cms = []
    p = generate_p('Service Configuration')
    p_ies_3000 = r'(?s) ies 3000 name "3000" customer 10 create.*?\n {8}exit'
    p_lag = r'group-interface "(s|m)hsi-(lag-\d{1,2})" create'
    p_vrf_target = r'vrf-target target:64800:1000000670'
    p_vprn = r'(?s)(vprn (\d{4,11}) name ".*?" customer \d{1,2} create.*?\n {8}exit)'
    p_subscriber_interface_vprn_cms = r'(?s)subscriber-interface "VPRN_CMS" create.*?\n {12}exit'
    p_subscriber_interface_vprn_ims = r'(?s)subscriber-interface "VPN_JS_JMCC_IMS" create.*?\n {12}exit'
    p_group_interface = r'(?s)(group-interface ".*?" create.*?\n {16}exit)'
    p_sap = r'sap (.*?) create'
    res = re.search(p, config)

    if res:
        res_ies_3000 = re.search(p_ies_3000, res.group())
        if res_ies_3000:
            res_lag = re.findall(p_lag, res_ies_3000.group())

            res_vprn = re.findall(p_vprn, config)
            is_true = False
            for i in res_vprn:
                if p_vrf_target in i[0]:
                    is_true = True
                    
                    res_group_interface = re.findall(p_group_interface, i[0])
                    for i in res_group_interface:
                        res_sap = re.search(p_sap, i)
                        if res_sap:
                            saps_cms.append(res_sap.group(1).split(':')[0])

                    break

            for j in res_lag:
                    if j[1] not in saps_cms:
                        lags_cms.append(j[1])
            if lags_cms:
                err = 'cms group-interface请确认该设备是否为主用bras或配置缺失\n'
                for i in set(lags_cms):
                    err += i + '\n'
                
            if not is_true:
                err += '该设备没有cms vprn配置\n'
    else:
        err += '没有找到 Service Configuration\n'

    return err

def lag_check_2(config):
    '''从ies 3000中读取subscriber-interface "pppoe"下的group-interface的lag信息，作为下一步的比对参照
    检索到subscriber-interface "VPN_JS_JMCC_IMS"后，检查其下group-interface中包含的lag信息是否与上一步作为比对信息的lag信息是否有缺少'''

    err = ''
    lags_ims = []
    saps_ims = []
    p = generate_p('Service Configuration')
    p_ies_3000 = r'(?s) ies 3000 name "3000" customer 10 create.*?\n {8}exit'
    p_lag = r'group-interface "(s|m)hsi-(lag-\d{1,2})" create'
    p_vrf_target = r'vrf-target target:64800:1000000280'
    p_vprn = r'(?s)(vprn (\d{4,11}) name ".*?" customer \d{1,2} create.*?\n {8}exit)'
    p_subscriber_interface_vprn_ims = r'(?s)subscriber-interface "VPN_JS_JMCC_IMS" create.*?\n {12}exit'
    p_group_interface = r'(?s)(group-interface ".*?" create.*?\n {16}exit)'
    p_sap = r'sap (.*?) create'
    res = re.search(p, config)

    if res:
        res_ies_3000 = re.search(p_ies_3000, res.group())
        if res_ies_3000:
            res_lag = re.findall(p_lag, res_ies_3000.group())

            res_vprn = re.findall(p_vprn, config)
            is_true = False
            for i in res_vprn:
                if p_vrf_target in i[0]:
                    is_true = True
                    res_group_interface = re.findall(p_group_interface, i[0])
                    for i in res_group_interface:
                        res_sap = re.search(p_sap, i)
                        if res_sap:
                            saps_ims.append(res_sap.group(1))

                    break

            for j in res_lag:
                    if j[1] not in saps_ims:
                        lags_ims.append(j[1])
            if lags_ims:
                err = 'ims group-interface请确认该设备是否为主用bras或配置缺失\n'
                for i in set(lags_ims):
                    err += i + '\n'

                
            if not is_true:
                err += '该设备没有ims vprn配置\n'
    else:
        err += '没有找到 Service Configuration\n'

    return err


def local_dhcp_server_check(config):
    '''检查local-dhcp-server "server1"中dns地址是否为221.131.143.69 112.4.0.55'''

    err = ''
    p = generate_p('Local DHCP Server (Base Router) Configuration')
    p_dhcp = generate_p('Local DHCP Server (Services) Configuration')
    p_dns_server = r'(?s)dns-server (.*?)\n'
    p_pool = r'(?s)pool "pppoe" create.*?\n {16}exit'
    p_pool_ipv6 = r'(?s)(pool "(pppoe_ipv6_.*?)" create.*?\n {16}exit)'
    p_pool_vprn = r'(?s)pool "vprn_cms" create.*?\n {20}exit'
    p_pool_vprn_ims = r'(?s)pool "vprn_ims" create.*?\n {20}exit'
    p_sub_inter = r'(?s)(subscriber-interface "VPN_JS_JMCC_IMS" create.+?\n {12}exit)'
    p_vprn = r'(?s)(vprn (\d{4,11}) name ".*?" customer \d{1,2} create.*?\n {8}exit)'
    p_rt = r'vrf-target target:64800:1000000280'
    p_rt_cms = r'vrf-target target:64800:1000000670'

    res = re.search(p, config)
    res_dhcp = re.search(p_dhcp, config)
    if res:
        res_pool = re.search(p_pool, res.group())
        if res_pool:
            res_dns_server = re.search(p_dns_server, res_pool.group())
            if res_dns_server:
                if res_dns_server.group(1) not in ['221.131.143.69 112.4.0.55', '112.4.0.55 221.131.143.69']:
                    err += 'pppoe dns地址: {} 不为221.131.143.69 112.4.0.55\n'.format(res_dns_server.group(1))
                else:
                    err += 'pppoe dns地址: {} 正常\n'.format(res_dns_server.group(1))
        else:
            err += '没有找到pool "pppoe"\n'

        res_pool_ipv6 = re.findall(p_pool_ipv6, res.group())
        if not res_pool_ipv6:
            err += '没有找到pool "pppoe_ipv6_xxx"\n'
        for i in res_pool_ipv6:
            res_dns_server = re.search(p_dns_server, i[0])
            if res_dns_server:
                if res_dns_server.group(1) not in ['2409:8020:2000::8 2409:8020:2000::88', '2409:8020:2000::88 2409:8020:2000::8']:
                    err += 'pppoe_ipv6 dns地址: {} 不为221.131.143.69 112.4.0.55\n'.format(res_dns_server.group(1))
                else:
                    err += 'pppoe_ipv6 dns地址: {} 正常\n'.format(res_dns_server.group(1))
                
            
        vprns = re.findall(p_vprn, config)
        vprn_id = ''
        for i in vprns:
            if p_rt_cms in i[0]:
                vprn_id = i[1]
                break

        if vprn_id:
            p_vprn = r'(?s)vprn {} name ".*?" customer \d{1,2} create.*?\n {8}exit'.replace('{}',vprn_id)
            res_vprn = re.search(p_vprn, res_dhcp.group())
            if res_vprn:
                res_dns_server = re.search(p_dns_server, res_vprn.group())
                if res_dns_server:
                    if res_dns_server.group(1) not in ['172.42.45.4 172.42.45.5', '172.42.45.5 172.42.45.4']:
                        err += 'cms dns地址 {} 不为“112.4.20.87 112.4.12.244”\n'.format(res_dns_server.group(1))
                    else:
                        err += 'cms dns地址: {} 正常\n'.format(res_dns_server.group(1))
            else:
                err += 'cms 没有配置dns\n'
        else:
            err += '没有找到含cms vrf-target的vprn\n'

        # res_vprn = re.findall(p_vprn, config)
        vprn_id = ''
        for i in vprns:
            if p_rt in i[0]:
                vprn_id = i[1]
                break

        if vprn_id:
            p_vprn = r'(?s)vprn {} name ".*?" customer \d{1,2} create.*?\n {8}exit'.replace('{}',vprn_id)
            if res_dhcp:
                res_vprn = re.search(p_vprn, res_dhcp.group())
                if res_vprn:
                    res_dns_server = re.search(p_dns_server, res_vprn.group())
                    if res_dns_server:
                        if res_dns_server.group(1) not in ['112.4.20.87 112.4.12.244', '112.4.12.244 112.4.20.87']:
                            err += 'ims dns地址 {} 不为“112.4.20.87 112.4.12.244”\n'.format(res_dns_server.group(1))
                        else:
                            err += 'ims dns地址: {} 正常\n'.format(res_dns_server.group(1))
                else:
                    err += 'ims 没有配置dns\n'
            else:
                err += '缺少 Local DHCP Server (Services) Configuration\n'
        else:
            err += '没有找到含 ims vrf-target的vprn\n'
        
    else:
        err += '没有找到 Local DHCP Server (Base Router) Configuration\n'

    return err

def config_check(config):
    '''检查7750设备CMS配置、telnet acl白名单、PPPoE业务本地默认速率等，若存在不符合配置规范或配置缺失'''

    err = ''
    p = generate_p('Filter Match lists Configuration')
    p_ip_prefix_list = r'(?s)ip-prefix-list "telnet" create.*?\n{12}exit'
    p_qos = generate_p('QoS Policy Configuration')
    p_sap_ingress = r'(?s)sap-ingress 3010 name "3010" create.*?\n {8}exit'
    p_sap_egress = r'(?s)sap-egress 3010 name "3010" create.*?\n {8}exit'
    p_rate = r'(?s)policer 1 create\n {16}rate (\d{4,8})'

    res = re.search(p, config)
    if res:
        if '183.207.194.220/32' not in res.group():
            err += 'telnet acl白名单缺少183.207.194.220\n'
        if '183.207.194.222/32' not in res.group():
            err += 'telnet acl白名单缺少183.207.194.222\n'
    else:
        err += '没有找到Filter Match lists Configuration\n'

    return err

def get_pppoe(config):
    '''检查7750设备CMS配置、telnet acl白名单、PPPoE业务本地默认速率等，若存在不符合配置规范或配置缺失'''

    err = ''
    p = generate_p('Filter Match lists Configuration')
    p_ip_prefix_list = r'(?s)ip-prefix-list "telnet" create.*?\n{12}exit'
    p_qos = generate_p('QoS Policy Configuration')
    p_sap_ingress = r'(?s)sap-ingress 3010 name "3010" create.*?\n {8}exit'
    p_sap_egress = r'(?s)sap-egress 3010 name "3010" create.*?\n {8}exit'
    p_rate = r'(?s)policer 1 create\n {16}rate (\d{4,8})'

    # res = re.search(p, config)
    res_qos = re.findall(p_qos, config)

    if len(res_qos) == 2:
        res_sap_ingress = re.search(p_sap_ingress, res_qos[1])
        res_sap_egress = re.search(p_sap_egress, res_qos[1])

        if res_sap_ingress:
            res_rate = re.search(p_rate, res_sap_ingress.group())
            err += 'pppoe 本地默认速率，ingress方向为{} Mbps\n'.format(float(int(res_rate.group(1))/1000))
        else:
            err += '没有找到sap-ingress 3010\n'

        if res_sap_egress:
            res_rate = re.search(p_rate, res_sap_egress.group())
            err += 'pppoe 本地默认速率，egress方向为{} Mbps\n'.format(float(int(res_rate.group(1))/1000))
        else:
            err += '没有找到sap-egress 3010\n'
    else:
        err = '缺少QoS Policy Configuration\n'

    return err




def urpf_check(config):
    '''vprn 、Ies下的普通Interface和group-interface都应配置urpf'''

    err = ''
    p = generate_p('Service Configuration')
    p_interface = r'(?s)( interface "(.*?)" create\n.+?\n {12}exit)'
    p_group_interface = r'(?s)(group-interface "(.*?)" create\n.+?\n {16}exit)'
    p_ies = r'(?s)(ies (\d{4,6}) name "\d{4,6}" customer \d{1,2} create\n.+?\n {8}exit)'
    p_vprn = r'(?s)(vprn \d{4,6} name ".*?" customer \d{1,2} create\n.+?\n {8}exit)'

    res = re.search(p, config)
    if res:
        res_ies = re.findall(p_ies, res.group())
        res_ies = res_ies[int(len(res_ies)/2):]
        res_vprn = re.findall(p_vprn, res.group())
        res_vprn = res_vprn[int(len(res_vprn)/2):]

        for i in res_ies:
            if i[1] == '1000' or i[1] == '3000':
                continue
            res_interface = re.findall(p_interface, i[0])
            res_group_interface = re.findall(p_group_interface, i[0])

            for j in res_interface:
                if 'urpf-check' not in j[0]:
                    err += 'interface "{}"  缺少urpf配置\n'.format(j[1])
            
            for j in res_group_interface:
                if 'urpf-check' not in j[0]:
                    err += 'group-interface "{}"  缺少urpf配置\n'.format(j[1])

        for i in res_vprn:
            res_interface = re.findall(p_interface, i)
            res_group_interface = re.findall(p_group_interface, i)

            for j in res_interface:
                if 'urpf-check' not in j[0]:
                    err += 'interface "{}"  缺少urpf配置\n'.format(j[1])
            
            for j in res_group_interface:
                if 'urpf-check' not in j[0]:
                    err += 'group_interface "{}"  缺少urpf配置\n'.format(j[1])
    else:
        err += '没有找到Service Configuration\n'


    return err

def bras_check(config):
    '''检查Bras每个上行接口egress方向是否配置filter ip 3100
    ip-filter 3100下不配置    default-action forward 报错
    包含src-ip ip-prefix-list "anti-out-spoofing"的 action为forward的entry条目'''

    err = ''
    p_router = generate_p('Router (Network Side) Configuration')
    p_filter = generate_p('Filter Configuration')
    p_interface = r'(?s)( interface "(.*?)"\n.+?\n {8}exit)'
    p_ip_filter_3100 = r'(?s)ip-filter 3100 name "3100" create.*?\n {8}exit'
    key_words = r'''match 
                    src-ip ip-prefix-list "anti-out-spoofing"
                exit 
                action
                    forward
                exit'''

    res_router = re.search(p_router, config)
    if res_router:
        res_interface = re.findall(p_interface, res_router.group())
        for i in res_interface:
            if 'loopback' in i[0] or i[1] == 'system':
                continue
            if 'egress\n                filter ip 3100' not in i[0]:
                err += 'interface "{}" 中缺少 egress filter ip 3100\n'.format(i[1])
    else:
        err += '缺少Router (Network Side) Configuration\n'
    
    res_filter = re.search(p_filter, config)
    if res_filter:
        res_ip_filter_3100 = re.search(p_ip_filter_3100, res_filter.group())
        if res_ip_filter_3100:
            if 'default-action forward' in res_ip_filter_3100.group():
                err += 'ip-filter 3100 存在 default-action forward\n'
            if key_words not in res_ip_filter_3100.group():
                err += 'ip-filter 3100 缺少 src-ip ip-prefix-list "anti-out-spoofing"\n'
        else:
            err += '缺少 ip-filter 3100 配置\n'
    else:
        err += '缺少 Filter Configuration\n'

    return err







