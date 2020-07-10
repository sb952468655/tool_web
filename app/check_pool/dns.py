# encoding = utf-8

import re
from .common import add_space

def dns_check(config):
    '''dns相关检查'''

    err = ''
    err += sntp_check(config)
    err += lacp_check(config)
    err += dhcp_pool_check(config)
    err += cms_rms_check(config)
    err += ims_check(config)

    if err == '':
        err = 'dns相关检查 -> OK\n\n'
    else:
        err = 'dns相关检查 -> ERROR\n\n' + err + '\n\n'

    return err

def sntp_check(config):
    '''检查sntp固定配置，检查固定配置中1、是否两个ntp server配置，
    2、地址是否211.138.200.208、211.138.200.209，两个ntp地址先后顺序无关'''

    err = ''
    p_sntp = r'(?s)sntp\n.*?\n {12}exit'
    sntp_1 = r'''sntp
                server-address 211.138.200.208 preferred 
                server-address 211.138.200.209 
                no shutdown
            exit'''

    sntp_2 = r'''sntp
                server-address 211.138.200.209 preferred 
                server-address 211.138.200.208 
                no shutdown
            exit'''

    res_sntp = re.search(p_sntp, config)
    if res_sntp:
        if res_sntp.group() != sntp_1 and res_sntp.group() != sntp_2:
            err = 'sntp固定配置错误\n'
    else:
        err = '没有找到sntp\n'

    if err == '':
        err = 'sntp固定配置检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'sntp固定配置检查 -> ERROR\n\n' + err + '\n\n'

    return ('sntp固定配置检查', err, '')

def lacp_check(config):
    '''检查lag下是否有lacp active'''

    err = ''
    p_lag_configuration = r'(?s)echo "LAG Configuration"\n#-{50}.*?\n#-{50}'
    p_lag = r'(?s)(lag (\d{1,3})\n.*?\n {4}exit)'
    res_lag_configuration = re.search(p_lag_configuration, config)
    if res_lag_configuration:
        res_lag = re.findall(p_lag, res_lag_configuration.group())
        for i in res_lag:
            if 'lacp active' not in i[0]:
                err += 'lag {}缺少lacp 配置\n'.format(i[1])
    else:
        err = '没有找到LAG Configuration\n'


    if err == '':
        err = 'lacp active检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'lacp active检查 -> ERROR\n\n' + err + '\n\n'

    return ('lacp active检查', err, '')

def dhcp_pool_check(config):
    '''检查全局配置dhcp中每个iptv、pppoe、video 、"vippool pool中dns配置：
    1、 是否两个dns，
    2、是否正确dns地址，注意，只要pool名字中带“iptv”、“pppoe”、“video”、"vippool“就检查，如：iptv-1、pppoe-2'''

    err = ''
    p_local_dhcp_server = r'(?s)echo "Local DHCP Server \(Base Router\) Configuration"\n#-{50}.*?\n#-{50}'
    p_dhcp = r'(?s)dhcp.*?\n {8}exit'
    p_dhcp_server = r'(?s)(local-dhcp-server "(.*?)" create.*?\n {12}exit)'
    
    p_pool = r'(?s)(pool "((iptv|pppoe|video|vippool).*?)" create.*?\n {20}exit)'
    p_dns_server = r'dns-server .*?\n'
    dns_ip = ['112.4.0.55', '221.131.143.69']
    
    res_local_dhcp_server = re.search(p_local_dhcp_server, config)
    if res_local_dhcp_server:
        res_dhcp = re.search(p_dhcp, res_local_dhcp_server.group())
        if res_dhcp:
            res_dhcp_server = re.findall(p_dhcp_server, res_dhcp.group())
            for i in res_dhcp_server:
                res_pool = re.findall(p_pool, i[0])
                for j in res_pool:
                    res_dns_server = re.search(p_dns_server, j[0])
                    if res_dns_server:
                        for k in dns_ip:
                            if k not in res_dns_server.group():
                                err += 'route base dhcp server {} pool {}缺少dns地址{}配置\n'.format(i[1], j[1], k)
                    else:
                            err = 'route base dhcp server {} pool {}缺少dns配置\n'.format(i[1], j[1])

    if err == '':
        err = '全局dhcp dns配置检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = '全局dhcp dns配置检查 -> ERROR\n\n' + err + '\n\n'

    return ('全局dhcp dns配置检查', err, '')

def cms_rms_check(config):
    '''检查CMS-RMS vprn 中dns 配置，地址不分先后顺序， 检查：
    1、是否两个dns，
    2、是否在dns地址 172.42.45.4 172.42.45.5    ，地址不分先后顺序'''

    err = ''
    p_route_distinguisher = r'route-distinguisher 64800:1000000670'
    p_vprn = r'(?s)(vprn (\d{1,10})( name ".*?")? customer \d{1,3} create.*?\n {8}exit)'
    p_local_dhcp_server = r'(?s)(echo "Local DHCP Server \(Services\) Configuration"\n#-{50}.*?\n#-{50})'
    p_dhcp_server = r'(?s)(local-dhcp-server "(.*?)" create.*?\n {12}exit)'
    p_dns_server = r'dns-server .*?\n'
    p_pool = r'(?s)(pool "(.*?)" create.*?\n {20}exit)'
    dns_ip = ['172.42.45.4', '172.42.45.5']
    vprn_id = ''
    res_vprn = re.findall(p_vprn, config)
    for i in res_vprn:
        if p_route_distinguisher in i[0]:
            vprn_id = i[1]
            break

    if vprn_id:
        p_vprn = r'(?s)(vprn (%s)( name ".*?")? customer \d{1,3} create.*?\n {8}exit)' % vprn_id
        res_local_dhcp_server = re.search(p_local_dhcp_server, config)
        if res_local_dhcp_server:
            res_vprn = re.search(p_vprn, res_local_dhcp_server.group())
            if res_vprn:
                res_dhcp_server = re.findall(p_dhcp_server, res_vprn.group())
                for i in res_dhcp_server:
                    res_pool = re.findall(p_pool, i[0])
                    for j in res_pool:
                        res_dns_server = re.search(p_dns_server, j[0])
                        if res_dns_server:
                            for k in dns_ip:
                                if k not in res_dns_server.group():
                                    err += 'route vprn {} dhcp server {} pool {}缺少dns地址{}配置\n'.format(vprn_id, i[1], j[1], k)
                        else:
                            err = 'route vprn {} dhcp server {} pool {}缺少dns配置\n'.format(vprn_id, i[1], j[1])

    if err == '':
        err = 'CMS-RMS vprn dns检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'CMS-RMS vprn dns检查 -> ERROR\n\n' + err + '\n\n'

    return ('CMS-RMS vprn dns检查', err, '')


def ims_check(config):
    '''检查IMS vprn 中dns 配置，地址不分先后顺序  ，   
    1、是否两个dns，
    2、是否在dns地址 112.4.20.87 112.4.12.244，地址不分先后顺序'''

    err = ''
    p_route_distinguisher = r'route-distinguisher 64800:1000000280'
    p_vprn = r'(?s)(vprn (\d{1,10})( name ".*?")? customer \d{1,3} create.*?\n {8}exit)'
    p_local_dhcp_server = r'(?s)(echo "Local DHCP Server \(Services\) Configuration"\n#-{50}.*?\n#-{50})'
    p_dhcp_server = r'(?s)(local-dhcp-server "(.*?)" create.*?\n {12}exit)'
    p_dns_server = r'dns-server .*?\n'
    p_pool = r'(?s)(pool "(.*?)" create.*?\n {20}exit)'
    dns_ip = ['112.4.20.87', '112.4.12.244']
    vprn_id = ''
    res_vprn = re.findall(p_vprn, config)
    for i in res_vprn:
        if p_route_distinguisher in i[0]:
            vprn_id = i[1]
            break

    if vprn_id:
        p_vprn = r'(?s)(vprn (%s)( name ".*?")? customer \d{1,3} create.*?\n {8}exit)' % vprn_id
        res_local_dhcp_server = re.search(p_local_dhcp_server, config)
        if res_local_dhcp_server:
            res_vprn = re.search(p_vprn, res_local_dhcp_server.group())
            if res_vprn:
                res_dhcp_server = re.findall(p_dhcp_server, res_vprn.group())
                for i in res_dhcp_server:
                    res_pool = re.findall(p_pool, i[0])
                    for j in res_pool:
                        res_dns_server = re.search(p_dns_server, j[0])
                        if res_dns_server:
                            for k in dns_ip:
                                if k not in res_dns_server.group():
                                    err += 'route vprn {} dhcp server {} pool {}缺少dns地址{}配置\n'.format(vprn_id, i[1], j[1], k)
                        else:
                            err = 'route vprn {} dhcp server {} pool {}缺少dns配置\n'.format(vprn_id, i[1], j[1])

    if err == '':
        err = 'IMS vprn dns检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'IMS vprn dns检查 -> ERROR\n\n' + err + '\n\n'

    return ('IMS vprn dns检查', err, '')

def fc_ef_check(config):
    '''增加对所 sap-egress 12X和sap-ingress 12X的 fc "ef"调用的queue 校验
    如果fc "ef"调用queue 2则提示错误'''

    err = ''
    p_qos = r'(?s)(echo "QoS Policy Configuration"\n#-{50}.*?\n#-{50})'
    p_sap_ingress = r'(?s)(sap-ingress (12\d+?)( name ".*?") create.*?\n {8}exit)'
    p_sap_egress = r'(?s)(sap-egress (12\d+?)( name ".*?") create.*?\n {8}exit)'
    p_fc = r'(?s)fc "?ef"? create.*?\n {12}exit'
    res_qos = re.findall(p_qos, config)
    if len(res_qos) == 2:
        res_sap_ingress = re.findall(p_sap_ingress, res_qos[1])
        res_sap_egress = re.findall(p_sap_egress, res_qos[1])

        for i in res_sap_ingress:
            res_fc = re.search(p_fc, i[0])
            if res_fc:
                if 'queue 2' in res_fc.group():
                    err += 'sap-ingress {} queue错误\n'.format(i[1])

        for i in res_sap_egress:
            res_fc = re.search(p_fc, i[0])
            if res_fc:
                if 'queue 2' in res_fc.group():
                    err += 'sap-egress {} queue错误\n'.format(i[1])

    if err == '':
        err = 'sap qos 12xxx queue 1 检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'sap qos 12xxx queue 1 检查 -> ERROR\n\n' + err + '\n\n'

    return ('sap qos 12xxx queue 1 检查', err, '')
