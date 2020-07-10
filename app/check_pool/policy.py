# encoding = utf-8

import re
import difflib
from .config_7750 import *
from .common import *

group_inter_m = r'''                    ipv6
                        router-advertisements
                            other-stateful-configuration
                            prefix-options
                                autonomous
                            exit
                            no shutdown
                        exit
                        dhcp6
                            proxy-server
                                client-applications ppp
                                no shutdown
                            exit
                            relay
                                client-applications ppp
                                no shutdown
                            exit
                        exit
                        router-solicit
                            no shutdown
                        exit
                    exit
                    local-address-assignment
                        server "server1"
                        client-application ppp-v4
                        default-pool "pppoe" secondary "vippool"
                        ipv6
                            client-application ppp-slaac
                            server "server1-ipv6"
                        exit
                        no shutdown
                    exit
                    arp-populate
                    oper-up-while-empty
                    pppoe
                        policy "pppoe-policy-m"
                        python-policy "qu-port"
                        session-limit 32767
                        sap-session-limit 32767
                        user-db "ludb-m"
                        no shutdown
                    exit
                exit'''

group_inter_s = r'''                    ipv6
                        router-advertisements
                            other-stateful-configuration
                            prefix-options
                                autonomous
                            exit
                            no shutdown
                        exit
                        dhcp6
                            proxy-server
                                client-applications ppp
                                no shutdown
                            exit
                            relay
                                client-applications ppp
                                no shutdown
                            exit
                        exit
                        router-solicit
                            no shutdown
                        exit
                    exit
                    local-address-assignment
                        server "server1"
                        client-application ppp-v4
                        default-pool "pppoe" secondary "vippool"
                        ipv6
                            client-application ppp-slaac
                            server "server1-ipv6"
                        exit
                        no shutdown
                    exit
                    arp-populate
                    oper-up-while-empty
                    pppoe
                        policy "pppoe-policy-s"
                        python-policy "qu-port"
                        session-limit 32767
                        sap-session-limit 32767
                        user-db "ludb-s"
                        no shutdown
                    exit
                exit'''

sap_q_s = r'''                trigger-packet pppoe
                pppoe-python-policy "qu-port"
                no shutdown
            exit'''

sap_q_m = r'''                trigger-packet pppoe
                pppoe-python-policy "qu-port"
                no shutdown
            exit'''

sap_any_s = r'''                cpu-protection 32 mac-monitoring
                trigger-packet dhcp pppoe
                pppoe-python-policy "qu-port"
                ipoe-session
                    ipoe-session-policy "ipoe-policy"
                    user-db "ludb-iptv"
                    no shutdown
                exit
                no shutdown
            exit'''

sap_any_m = r'''                cpu-protection 32 mac-monitoring
                trigger-packet dhcp pppoe
                pppoe-python-policy "qu-port"
                ipoe-session
                    ipoe-session-policy "ipoe-policy"
                    user-db "ludb-iptv"
                    no shutdown
                exit
                no shutdown
            exit'''

host_default_s = r'''auth-policy "auth-pppoe-p1"
                    msap-defaults
                        group-interface "shsi-" suffix port-id
                        policy "msap-pppoe"
                        service 3000
                    exit'''
host_default_m = r'''auth-policy "auth-pppoe-p1"
                    msap-defaults
                        group-interface "mhsi-" suffix port-id
                        policy "msap-pppoe"
                        service 3000
                    exit'''


def policy_check(config):
    '''ies3000下面每个group-interface的"pppoe-policy-m"和 "ludb-m"要一致起来。
    只有"pppoe-policy-m" "ludb-m"和"pppoe-policy-s" "ludb-s"这两种组合，不能混用'''

    err = ''
    p_subscriber_mgmt = r'(?s)echo "Subscriber-mgmt \(Service Side\) Configuration"\n#-{50}.*?\n#-{50}'
    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_vpls = r'(?s)(vpls (\d{1,10})( name ".*?")? customer \d{1,3} create.*?\n {8}exit)'
    p_group_interface = PAT['group_interface']
    p_sap = r'(?s)(sap (.*?) capture-sap create.*?\n {12}exit)'
    p_system = r'(?s)interface "system".*?\n {8}exit'
    p_ipv6 = r'(([a-f0-9]{1,4}:){0,7}:[a-f0-9]{1,4})'


    res_system = re.search(p_system, config)
    if not res_system:
        return '没有找到interface "system"\n'

    res_system_ipv6 = re.search(p_ipv6, res_system.group())
    if not res_system_ipv6:
        return 'interface "system" 中没有找到ipv6\n'

    res_ies_3000 = re.findall(p_ies_3000, config)
    res_vpls = re.findall(p_vpls, config)
    if len(res_ies_3000) != 2:
        err = '没有找到ies 3000，请检查\n'
    else:
        res_group_interface = re.findall(p_group_interface, res_ies_3000[1][0])
        for i in res_group_interface:
            if i[1].startswith('mhsi'):
                #检查system地址

                p_v6_config = r'                    ipv6'
                if p_v6_config not in  i[0]:
                    err += 'ies 3000 中的 group-interface "{}" 缺少 ipv6配置\n'.format(i[1])
                else:
                    #检查dhcp6 relay server 是否存在
                    res_group_inter_ipv6 = re.search(p_ipv6, i[0])
                    if not res_group_inter_ipv6:
                        err += 'ies 3000 中的 group-interface "{}" 缺少 dhcp6 relay server\n'.format(i[1])
                    else:
                        if res_system_ipv6.group(1) not in i[0]:
                            err += 'ies 3000 中的 group-interface "{}" ipv6与system不一致\n'.format(i[1])


                #主用一致性检查
                if 'policy "pppoe-policy-m"' not in i[0] or 'user-db "ludb-m"' not in i[0]:
                    err += 'group-interface "{}" m主用一致性配置错误，请对该项人工检查复核！\n'.format(i[1])

                group_inter = i[0].replace('group-interface "{}" create\n'.format(i[1]), '')
                res_server = re.search(p_ipv6, i[0])
                if res_server:
                    group_inter = group_inter.replace('                                server ' + res_server.group() + '\n', '')
                #忽略老配置sap
                res_old_sap = re.findall(r'(?s)(                    sap [^*]*? create.*?\n {20}exit\n)', group_inter)
                for j in res_old_sap:
                    group_inter = group_inter.replace(j, '')

                #忽略描述
                p_miaoshu = r'(?s)                    description ".*?"\n'
                res_description = re.search(p_miaoshu, group_inter)
                if res_description:
                    group_inter = group_inter.replace(res_description.group(), '')
                if group_inter_m != group_inter:
                    text1_lines = group_inter.splitlines()
                    text2_lines = group_inter_m.splitlines()

                    d = difflib.Differ()
                    diff = d.compare(text1_lines, text2_lines)
                    diff_str = "\n".join(list(diff))
                    diff_str = '                group-interface "{}" create\n'.format(i[1]) + diff_str
                    p_static_sap = r'(?s)-                     sap [^*]{5,15} create\n.*?\n-                     exit'
                    res_static_sap = re.findall(p_static_sap, diff_str)
                    for j in res_static_sap:
                        new_str = ''
                        i_lines = j.splitlines()
                        for k in i_lines:
                            new_str = new_str + k.replace('- ', '-? ') + '\n'
                        diff_str = diff_str.replace(j, new_str.rstrip())

                    if res_server:
                        diff_str = diff_str.replace('relay\n', 'relay\n                                  server {}\n'.format(res_server.group()))
                    err += 'ies 3000 中的 group-interface "{}"  固定配置一致性配置错误，请对该项人工检查复核！\n{}\n'.format(i[1],diff_str)

            elif i[1].startswith('shsi'):
                #检查system地址
                p_v6_config = r'                    ipv6'
                if p_v6_config not in  i[0]:
                    err += 'ies 3000 中的 group-interface "{}" 缺少 ipv6配置\n'.format(i[1])
                else:
                    #检查dhcp6 relay server 是否存在
                    res_group_inter_ipv6 = re.search(p_ipv6, i[0])
                    if not res_group_inter_ipv6:
                        err += 'ies 3000 中的 group-interface "{}" 缺少 dhcp6 relay server\n'.format(i[1])
                    else:
                        if res_system_ipv6.group(1) not in i[0]:
                            err += 'ies 3000 中的 group-interface "{}" ipv6与system不一致\n'.format(i[1])

                #备用一致性检查
                if 'policy "pppoe-policy-s"' not in i[0] or 'user-db "ludb-s"' not in i[0]:
                    err += 'group-interface "{}" s备用一致性配置错误，请对该项人工检查复核！\n'.format(i[1])

                group_inter = i[0].replace('group-interface "{}" create\n'.format(i[1]), '')
                res_server = re.search(p_ipv6, i[0])
                if res_server:
                    group_inter = group_inter.replace('                                server ' + res_server.group() + '\n', '')
                if group_inter_s != group_inter:
                    text1_lines = group_inter.splitlines()
                    text2_lines = group_inter_s.splitlines()

                    d = difflib.Differ()
                    diff = d.compare(text1_lines, text2_lines)
                    diff_str = "\n".join(list(diff))
                    diff_str = '                group-interface "{}" create\n'.format(i[1]) + diff_str
                    p_static_sap = r'(?s)-                     sap [^*]{5,15} create\n.*?\n-                     exit'
                    res_static_sap = re.findall(p_static_sap, diff_str)
                    for j in res_static_sap:
                        new_str = ''
                        i_lines = j.splitlines()
                        for k in i_lines:
                            new_str = new_str + k.replace('- ', '-? ') + '\n'
                        diff_str = diff_str.replace(j, new_str.rstrip())
                    #忽略描述
                    p_miaoshu = r'-(                     description ".*?")'
                    diff_str = re.sub(p_miaoshu, r' \1', diff_str)
                    if res_server:
                        diff_str = diff_str.replace('relay\n', 'relay\n                                  server {}\n'.format(res_server.group()))
                    err += 'ies 3000 中的 group-interface "{}"  固定配置一致性配置错误，请对该项人工检查复核！\n{}\n'.format(i[1],diff_str)

    #vpls的capture-sap类型的sap下，pppoe-policy "pppoe-policy-s"与pppoe-user-db "ludb-s"对应配置
    all_vpls_str = ''
    for i in res_vpls:
        all_vpls_str = all_vpls_str+'\n'+i[0]
        res_sap = re.findall(p_sap, i[0])
        for j in res_sap:
            if '.*' not in j[1]:
                continue
            if 'pppoe-policy "pppoe-policy-m"' in j[0] and 'pppoe-user-db "ludb-s"' in j[0]:
                err += 'sap {} pppoe-policy 、pppoe-user-db 配置主备用不一致\n'.format(j[1])

            if 'pppoe-policy "pppoe-policy-s"' in j[0] and 'pppoe-user-db "ludb-m"' in j[0]:
                err += 'sap {} pppoe-policy 和 pppoe-user-db 配置主备用不一致\n'.format(j[1])

            if 'pppoe-policy' not in j[0]:
                err += 'sap {} 缺少pppoe-policy 配置\n'.format(j[1])
            # if 'pppoe-user-db' not in j[0]:
            #     err += 'sap {} 缺少pppoe-user-db 配置\n'.format(j[1])
            sap_str = j[0].replace('sap {} capture-sap create\n'.format(j[1]), '')
            sap_str = sap_str.replace('                pppoe-policy "pppoe-policy-m"\n', '')
            sap_str = sap_str.replace('                pppoe-policy "pppoe-policy-s"\n', '')
            
            p_pppoe_user_db = r'pppoe-user-db "(.*?)"'
            res_pppoe_user_db = re.search(p_pppoe_user_db, j[0])
            if not res_pppoe_user_db:
                err += 'sap {} 缺少pppoe-user-db 配置\n'.format(j[1])
            else:
                if res_pppoe_user_db.group(1) not in  ['ludb-m', 'ludb-s']:
                    err += 'sap {} pppoe-user-db名称与配置规范不符\n'.format(j[1])

                sap_str = sap_str.replace('                ' + res_pppoe_user_db.group() + '\n', '')
            #固定配置检查

            if '*.*' in j[1]:
                if sap_str != sap_any_s:
                    d = difflib.Differ()
                    diff = d.compare(sap_str.splitlines(), sap_any_s.splitlines())
                    diff_str = "\n".join(list(diff))
                    diff_str = '              sap {} capture-sap create\n'.format(j[1]) + diff_str
                    err += 'sap {} 下固定配置错误，请对该项人工检查复核！\n{}\n'.format(j[1], diff_str)
            elif '.*' in j[1]:
                # if sap_str != sap_q_m:
                #     d = difflib.Differ()
                #     diff = d.compare(sap_str.splitlines(), sap_q_m.splitlines())
                #     diff_str = "\n".join(list(diff))
                #     diff_str = '              sap {} capture-sap create\n'.format(j[1]) + diff_str
                #     err += 'sap {} 下固定配置错误，请对该项人工检查复核！\n{}\n'.format(j[1], diff_str)

                if 'cpu-protection 32 mac-monitoring' not in j[0]:
                    err += 'sap {} 缺少 cpu-protection 32 mac-monitoring配置\n'.format(j[1])
                if 'pppoe-python-policy "qu-port"' not in j[0]:
                    err += 'sap {} 缺少 pppoe-python-policy "qu-port"配置\n'.format(j[1])

    p_sap_any = r'(?s)(sap (lag-%lag_id%:\*\.\*) capture-sap create.*?\n {12}exit)'
    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_lag_config = r'(?s)echo "LAG Configuration"\n#-{50}.*?\n#-{50}'
    p_lag = r'(?s)lag (\d{1,3})\n'

    res_ies_3000 = re.search(p_ies_3000, config)
    # res_sap_all = re.findall(p_sap_all, all_vpls_str)
    # sap_all = list(set(res_sap_all))
    res_lag_config = re.search(p_lag_config, config)
    if not res_lag_config:
        return err + '没有找到LAG Configuration\n'

    sap_all = re.findall(p_lag, res_lag_config.group())
    
    for j in sap_all:
        res_sap_any = re.search(p_sap_any.replace('%lag_id%', j), all_vpls_str)
        if not res_sap_any:
            err += 'lag-{} 缺少 lag-{}:*.*配置\n'.format(j, j)

        #检查在ies 3000 下是否有group-interface "mhsi-lag-x" 、group-interface "shsi-lag-x"
        
        p_group_inter_mhsi = r'group-interface "mhsi-lag-{}"'.format(j)
        p_group_inter_shsi = r'group-interface "shsi-lag-{}"'.format(j)
        if res_ies_3000 and p_group_inter_mhsi not in res_ies_3000.group():
            err += '对应lag-{}，在ies 3000下缺group-interface "mhsi-lag-{}"\n'.format(j, j)
        if res_ies_3000 and p_group_inter_shsi not in res_ies_3000.group():
            err += '对应lag-{}，在ies 3000下缺group-interface "shsi-lag-{}"\n'.format(j, j)

    #p_subscriber_mgmt
    #local-user-db "ludb-m"配置检查,检查“m“一致性和host "default"固定配置检查
    res_subscriber_mgmt = re.search(p_subscriber_mgmt, config)
    if not res_subscriber_mgmt:
        err += '没有找到Subscriber-mgmt\n'
        return err

    p_ludb_m = r'(?s)local-user-db "ludb-m" create\n.*?\n {8}exit'
    p_ludb_s = r'(?s)local-user-db "ludb-s" create\n.*?\n {8}exit'
    p_host_default = r'(?s)host "default" create.*?\n {16}exit'

    p_group_interface = r'(group-interface ".*?")'
    res_ludb_m = re.search(p_ludb_m, res_subscriber_mgmt.group())
    res_ludb_s = re.search(p_ludb_s, res_subscriber_mgmt.group())
    if res_ludb_m:
        res_group_interface = re.findall(p_group_interface, res_ludb_m.group())
        for i in res_group_interface:
            if 'shsi' in i:
                err += 'local-user-db "ludb-m" m主用一致性配置错误，请对该项人工检查复核！ group-interface "{}" suffix port-id \n'.format(i)
                break

        #检查host_default是否存在
        res_host_default = re.search(p_host_default, res_ludb_m.group())
        if res_host_default:
            if host_default_m not in res_ludb_m.group():
                err += 'local-user-db "ludb-m"中 host "default"一致性配置错误，请对该项人工检查复核！\n'
        else:
            err += 'local-user-db "ludb-m"中缺少 host "default"\n'

    if res_ludb_s:
        res_group_interface = re.findall(p_group_interface, res_ludb_s.group())
        for i in res_group_interface:
            if 'mhsi' in i:
                err += 'local-user-db "ludb-s" s备用一致性配置错误，请对该项人工检查复核！ group-interface "{}" suffix port-id\n'.format(i)
                break

        #检查host_default是否存在
        res_host_default = re.search(p_host_default, res_ludb_s.group())
        if res_host_default:
            if host_default_s not in res_ludb_s.group():
                err += 'local-user-db "ludb-s"中 host "default"一致性配置错误，请对该项人工检查复核！"\n'
        else:
            err += 'local-user-db "ludb-s"中缺少 host "default"\n'


    if err == '':
        err = 'ludb和pppoe策略的主备一致性检查 -> OK\n\n'
    else:
        err = 'ludb和pppoe策略的主备一致性检查 -> 请进行确认\n\n' + err + '\n\n'

    # return err
    return ('ludb-m/s 主备一致性检查', err, '')

def ies_3000_check(config):
    '''ies3000下面每个group-interface的"pppoe-policy-m"和 "ludb-m"要一致起来。
    只有"pppoe-policy-m" "ludb-m"和"pppoe-policy-s" "ludb-s"这两种组合，不能混用'''

    err = ''
    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_group_interface = PAT['group_interface']
    p_system = r'(?s)interface "system".*?\n {8}exit'
    p_ipv6 = r'(([a-f0-9]{1,4}:){0,7}:[a-f0-9]{1,4})'

    res_system = re.search(p_system, config)
    if not res_system:
        return '没有找到interface "system"\n'

    res_system_ipv6 = re.search(p_ipv6, res_system.group())
    if not res_system_ipv6:
        return 'interface "system" 中没有找到ipv6\n'

    res_ies_3000 = re.findall(p_ies_3000, config)
    if len(res_ies_3000) != 2:
        return '没有找到ies 3000，请检查\n'

    res_group_interface = re.findall(p_group_interface, res_ies_3000[1][0])
    for i in res_group_interface:
        if i[1].startswith('mhsi') or i[1].startswith('shsi'):
            #检查system地址

            p_v6_config = r'                    ipv6'
            if p_v6_config not in  i[0]:
                err += 'ies 3000 中的 group-interface "{}" 缺少 ipv6配置\n'.format(i[1])
            else:
                #检查dhcp6 relay server 是否存在
                res_group_inter_ipv6 = re.search(p_ipv6, i[0])
                if not res_group_inter_ipv6:
                    err += 'ies 3000 中的 group-interface "{}" 缺少 dhcp6 relay server\n'.format(i[1])
                else:
                    if res_system_ipv6.group(1) not in i[0]:
                        err += 'ies 3000 中的 group-interface "{}" ipv6与system不一致\n'.format(i[1])

            if i[1].startswith('mhsi'):
                #主用一致性检查
                if 'policy "pppoe-policy-m"' not in i[0] or 'user-db "ludb-m"' not in i[0]:
                    err += 'group-interface "{}" m主用一致性配置错误，请对该项人工检查复核！\n'.format(i[1])
            else:
                #备用一致性检查
                if 'policy "pppoe-policy-s"' not in i[0] or 'user-db "ludb-s"' not in i[0]:
                    err += 'group-interface "{}" s备用一致性配置错误，请对该项人工检查复核！\n'.format(i[1])

            group_inter = i[0].replace('group-interface "{}" create\n'.format(i[1]), '')
            res_server = re.search(p_ipv6, i[0])
            if res_server:
                group_inter = group_inter.replace('                                server ' + res_server.group() + '\n', '')
            #忽略老配置sap
            res_old_sap = re.findall(r'(?s)(                    sap [^*]*? create.*?\n {20}exit {0,20}\n)', group_inter)
            for j in res_old_sap:
                group_inter = group_inter.replace(j, '')

            #忽略描述
            p_miaoshu = r'(?s)                    description ".*?"\n'
            res_description = re.search(p_miaoshu, group_inter)
            if res_description:
                group_inter = group_inter.replace(res_description.group(), '')
            if i[1].startswith('mhsi'):
                model_text = group_inter_m
            else:
                model_text = group_inter_s

            text1 = remove_right_space(group_inter)
            text2 = remove_right_space(model_text)
            if text2 != text1:
                text1_lines = text1.splitlines()
                text2_lines = text2.splitlines()

                d = difflib.Differ()
                diff = d.compare(text1_lines, text2_lines)
                diff_str = "\n".join(list(diff))
                diff_str = '                group-interface "{}" create\n'.format(i[1]) + diff_str
                p_static_sap = r'(?s)-                     sap [^*]{5,15} create\n.*?\n-                     exit'
                res_static_sap = re.findall(p_static_sap, diff_str)
                for j in res_static_sap:
                    new_str = ''
                    i_lines = j.splitlines()
                    for k in i_lines:
                        new_str = new_str + k.replace('- ', '-? ') + '\n'
                    diff_str = diff_str.replace(j, new_str.rstrip())

                if res_server:
                    diff_str = diff_str.replace('relay\n', 'relay\n                                  server {}\n'.format(res_server.group()))
                err += 'ies 3000 中的 group-interface "{}"  固定配置一致性配置错误，请对该项人工检查复核！\n{}\n'.format(i[1],diff_str)

    if err == '':
        err = 'ies3000 m/s一致性检查 -> OK\n\n'
    else:
        err = 'ies3000 m/s一致性检查 -> ERROR\n\n' + err + '\n\n'

    return ('ies3000 m/s一致性检查', err, '')

def sap_check(config):
    '''vpls的capture-sap类型的sap下，pppoe-policy "pppoe-policy-s"与pppoe-user-db "ludb-s"对应配置'''

    err = ''
    all_vpls_str = ''
    p_vpls = r'(?s)(vpls (\d{1,10})( name ".*?")? customer \d{1,3} create.*?\n {8}exit)'
    p_sap = r'(?s)(sap (.*?) capture-sap create.*?\n {12}exit)'
    p_sap_any = r'(?s)(sap (lag-%lag_id%:\*\.\*) capture-sap create.*?\n {12}exit)'
    p_ies_3000 = r'(?s)(ies 3000( name ".*?")? customer \d{1,2} create\n.+?\n {8}exit)'
    p_lag_config = r'(?s)echo "LAG Configuration"\n#-{50}.*?\n#-{50}'
    p_lag = r'(?s)lag (\d{1,3})\n'

    res_vpls = re.findall(p_vpls, config)

    for i in res_vpls:
        all_vpls_str = all_vpls_str+'\n'+i[0]
        res_sap = re.findall(p_sap, i[0])
        for j in res_sap:
            if '*.*' not in j[1]:
                continue
            if 'pppoe-policy "pppoe-policy-m"' in j[0] and 'pppoe-user-db "ludb-s"' in j[0]:
                err += 'sap {} pppoe-policy 、pppoe-user-db 配置主备用不一致\n'.format(j[1])

            if 'pppoe-policy "pppoe-policy-s"' in j[0] and 'pppoe-user-db "ludb-m"' in j[0]:
                err += 'sap {} pppoe-policy 和 pppoe-user-db 配置主备用不一致\n'.format(j[1])

            if 'pppoe-policy' not in j[0]:
                err += 'sap {} 缺少pppoe-policy 配置\n'.format(j[1])

            sap_str = j[0].replace('sap {} capture-sap create\n'.format(j[1]), '')
            sap_str = sap_str.replace('                pppoe-policy "pppoe-policy-m"\n', '')
            sap_str = sap_str.replace('                pppoe-policy "pppoe-policy-s"\n', '')
            
            p_pppoe_user_db = r'pppoe-user-db "(.*?)"'
            res_pppoe_user_db = re.search(p_pppoe_user_db, j[0])
            if not res_pppoe_user_db:
                err += 'sap {} 缺少pppoe-user-db 配置\n'.format(j[1])
            else:
                if res_pppoe_user_db.group(1) not in  ['ludb-m', 'ludb-s']:
                    err += 'sap {} pppoe-user-db名称与配置规范不符\n'.format(j[1])

                sap_str = sap_str.replace('                ' + res_pppoe_user_db.group() + '\n', '')
            #固定配置检查

            # if '*.*' in j[1]:
            text1 = remove_right_space(sap_str)
            text2 = remove_right_space(sap_any_s)
            if text1 != text2:
                d = difflib.Differ()
                diff = d.compare(text1.splitlines(), text2.splitlines())
                diff_str = "\n".join(list(diff))
                diff_str = '              sap {} capture-sap create\n'.format(j[1]) + diff_str
                err += 'sap {} 下固定配置错误，请对该项人工检查复核！\n{}\n'.format(j[1], diff_str)
            # elif '.*' in j[1]:
            #     if 'cpu-protection 32 mac-monitoring' not in j[0]:
            #         err += 'sap {} 缺少 cpu-protection 32 mac-monitoring配置\n'.format(j[1])
            #     if 'pppoe-python-policy "qu-port"' not in j[0]:
            #         err += 'sap {} 缺少 pppoe-python-policy "qu-port"配置\n'.format(j[1])

    res_ies_3000 = re.search(p_ies_3000, config)
    res_lag_config = re.search(p_lag_config, config)
    if not res_lag_config:
        return err + '没有找到LAG Configuration\n'

    lap_all = re.findall(p_lag, res_lag_config.group())
    
    for j in lap_all:
        res_sap_any = re.search(p_sap_any.replace('%lag_id%', j), all_vpls_str)
        if not res_sap_any:
            err += 'lag-{} 缺少 lag-{}:*.*配置\n'.format(j, j)

        #检查在ies 3000 下是否有group-interface "mhsi-lag-x" 、group-interface "shsi-lag-x"
        
        p_group_inter_mhsi = r'group-interface "mhsi-lag-{}"'.format(j)
        p_group_inter_shsi = r'group-interface "shsi-lag-{}"'.format(j)
        if res_ies_3000 and p_group_inter_mhsi not in res_ies_3000.group():
            err += '对应lag-{}，在ies 3000下缺group-interface "mhsi-lag-{}"\n'.format(j, j)
        if res_ies_3000 and p_group_inter_shsi not in res_ies_3000.group():
            err += '对应lag-{}，在ies 3000下缺group-interface "shsi-lag-{}"\n'.format(j, j)

    if err == '':
        err = 'sap *.* m/s一致性检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'sap *.* m/s一致性检查 -> ERROR\n\n' + err + '\n\n'

    return ('sap *.* m/s一致性检查', err, '')

def sap_q_check(config):
    '''sap Q.*检查'''

    err = ''
    p_vpls = r'(?s)(vpls (\d{1,10})( name ".*?")? customer \d{1,3} create.*?\n {8}exit)'
    p_sap = r'(?s)(sap (.*?) capture-sap create.*?\n {12}exit)'

    res_vpls = re.findall(p_vpls, config)

    for i in res_vpls:
        res_sap = re.findall(p_sap, i[0])
        for j in res_sap:
            if '*.*' not in j[1] and '.*' in j[1]:
                if 'pppoe-policy "pppoe-policy-m"' in j[0] and 'pppoe-user-db "ludb-s"' in j[0]:
                    err += 'sap {} pppoe-policy 、pppoe-user-db 配置主备用不一致\n'.format(j[1])

                if 'pppoe-policy "pppoe-policy-s"' in j[0] and 'pppoe-user-db "ludb-m"' in j[0]:
                    err += 'sap {} pppoe-policy 和 pppoe-user-db 配置主备用不一致\n'.format(j[1])

                if 'pppoe-policy' not in j[0]:
                    err += 'sap {} 缺少pppoe-policy 配置\n'.format(j[1])

                if 'pppoe-python-policy "qu-port"' not in j[0]:
                    err += 'sap {} 缺少 pppoe-python-policy "qu-port"配置\n'.format(j[1])

                sap_str = j[0].replace('sap {} capture-sap create\n'.format(j[1]), '')
                sap_str = sap_str.replace('                pppoe-policy "pppoe-policy-m"\n', '')
                sap_str = sap_str.replace('                pppoe-policy "pppoe-policy-s"\n', '')
                
                p_pppoe_user_db = r'pppoe-user-db "(.*?)"'
                res_pppoe_user_db = re.search(p_pppoe_user_db, j[0])
                if not res_pppoe_user_db:
                    err += 'sap {} 缺少pppoe-user-db 配置\n'.format(j[1])
                else:
                    if res_pppoe_user_db.group(1) not in  ['ludb-m', 'ludb-s']:
                        err += 'sap {} pppoe-user-db名称与配置规范不符\n'.format(j[1])

                    sap_str = sap_str.replace('                ' + res_pppoe_user_db.group() + '\n', '')

    if err == '':
        err = 'sap q.* m/s一致性检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'sap q.* m/s一致性检查 -> ERROR\n\n' + err + '\n\n'

    return ('sap q.* m/s一致性检查', err, '')

def sap_q_cpu_check(config):
    '''sap Q.*cpu-protection检查'''

    err = ''
    p_vpls = r'(?s)(vpls (\d{1,10})( name ".*?")? customer \d{1,3} create.*?\n {8}exit)'
    p_sap = r'(?s)(sap (.*?) capture-sap create.*?\n {12}exit)'

    res_vpls = re.findall(p_vpls, config)

    for i in res_vpls:
        res_sap = re.findall(p_sap, i[0])
        for j in res_sap:
            if '*.*' not in j[1] and '.*' in j[1]:

                #固定配置检查
                if 'cpu-protection 32 mac-monitoring' not in j[0]:
                    err += 'sap {} 缺少 cpu-protection 32 mac-monitoring配置\n'.format(j[1])

    if err == '':
        err = 'sap q.* cpu-protection检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'sap q.* cpu-protection检查 -> ERROR\n\n' + err + '\n\n'

    return ('sap q.* cpu-protection检查', err, '')


def local_user_db_check(config):
    '''local-user-db "ludb-m"配置检查,检查“m“一致性和host "default"固定配置检查'''

    err = ''
    p_subscriber_mgmt = r'(?s)echo "Subscriber-mgmt \(Service Side\) Configuration"\n#-{50}.*?\n#-{50}'
    p_ludb_m = r'(?s)local-user-db "ludb-m" create\n.*?\n {8}exit'
    p_ludb_s = r'(?s)local-user-db "ludb-s" create\n.*?\n {8}exit'
    p_host_default = r'(?s)host "default" create.*?\n {16}exit'
    res_subscriber_mgmt = re.search(p_subscriber_mgmt, config)
    if not res_subscriber_mgmt:
        err += '没有找到Subscriber-mgmt\n'
        return err

    p_group_interface = r'(group-interface ".*?")'
    res_ludb_m = re.search(p_ludb_m, res_subscriber_mgmt.group())
    res_ludb_s = re.search(p_ludb_s, res_subscriber_mgmt.group())
    if res_ludb_m:
        res_group_interface = re.findall(p_group_interface, res_ludb_m.group())
        for i in res_group_interface:
            if 'shsi' in i:
                err += 'local-user-db "ludb-m" m主用一致性配置错误，请对该项人工检查复核！ group-interface "{}" suffix port-id \n'.format(i)
                break

        #检查host_default是否存在
        res_host_default = re.search(p_host_default, res_ludb_m.group())
        if res_host_default:
            if host_default_m not in res_ludb_m.group():
                err += 'local-user-db "ludb-m"中 host "default"一致性配置错误，请对该项人工检查复核！\n'
        else:
            err += 'local-user-db "ludb-m"中缺少 host "default"\n'

    if res_ludb_s:
        res_group_interface = re.findall(p_group_interface, res_ludb_s.group())
        for i in res_group_interface:
            if 'mhsi' in i:
                err += 'local-user-db "ludb-s" s备用一致性配置错误，请对该项人工检查复核！ group-interface "{}" suffix port-id\n'.format(i)
                break

        #检查host_default是否存在
        res_host_default = re.search(p_host_default, res_ludb_s.group())
        if res_host_default:
            if host_default_s not in res_ludb_s.group():
                err += 'local-user-db "ludb-s"中 host "default"一致性配置错误，请对该项人工检查复核！"\n'
        else:
            err += 'local-user-db "ludb-s"中缺少 host "default"\n'


    if err == '':
        err = 'local-user-db 一致性检查 -> OK\n\n'
    else:
        err = add_space(err, '  ')
        err = 'local-user-db 一致性检查 -> ERROR\n\n' + err + '\n\n'

    return ('local-user-db 一致性检查', err, '')