import re
def ruler4(config):
    err = ''

    #pool 检测  nd 对应 48 wan-host， pd 对应 44 pd
    p1 = r'''(pool "(.*)" create
                    options
                        dns-server \d{4}:\d{4}:\d{4}::\d{1,2} \d{4}:\d{4}:\d{4}::\d{1,2}
                    exit
                    prefix [0-9A-F]{3,4}:[0-9A-Fa-f]{3,4}:[0-9A-Fa-f]{3,4}::/(\d\d) (wan-host|pd) create
                    exit
                exit)'''

    #prefix 对比 
    p4_1 = r'''pool ".*" create
                    options
                        dns-server \d{4}:\d{4}:\d{4}::\d{1,2} \d{4}:\d{4}:\d{4}::\d{1,2}
                    exit
                    prefix ([0-9A-F]{3,4}:[0-9A-Fa-f]{3,4}:[0-9A-Fa-f]{3,4}::/\d\d) (wan-host|pd) create
                    exit
                exit'''

    p4_2 = r'''prefix-list "plToRR_IPV6"
(                prefix ([0-9A-F]{4}:[0-9A-Fa-f]{4}:[0-9A-Fa-f]{3,4}::/\d\d) exact\n)+            exit'''

    #prefix 对比 
    p4_3 = r'''subscriber-prefixes
(                        prefix [0-9A-F]{3,4}:[0-9A-Fa-f]{3,4}:[0-9A-Fa-f]{3,4}::/\d\d (wan-host|pd)\n)+                    exit'''

    p_prefix = r'[0-9A-F]{3,4}:[0-9A-Fa-f]{3,4}:[0-9A-Fa-f]{3,4}::/\d\d'

    #检测  nd 对应 48 wan-host， pd 对应 44 pd
    p_prefix_dy = r'(prefix [0-9A-F]{3,4}:[0-9A-Fa-f]{3,4}:[0-9A-Fa-f]{3,4}::/(\d\d) (wan-host|pd))'
    
    #ipv6-slaac-prefix-pool，ipv6-delegated-prefix-pool 与名称对应 slaac 对应 nd，delegated 对应 pd
    p5_1 = r'ipv6-slaac-prefix-pool "(.*)"'
    p5_2 = r'ipv6-delegated-prefix-pool "(.*)"'

    obj = re.compile(p1)
    res = obj.findall(config)

    pools = [item[1] for item in res]

    if res == []:
        err += '没有找到pool配置\n'
        return err
    else:
        for item in res:
            if '_nd_' in item[1] and (item[2] != '48' or item[3] != 'wan-host'):
                err += 'pool {} 地址池掩码错误\n'.format(item[1])
            if '_pd_' in item[1] and (item[2] != '44' or item[3] != 'pd'):
                err += 'pool {} 地址池掩码错误\n'.format(item[1])


    obj1 = re.compile(p5_1)
    res1 = obj1.findall(config)
    obj2 = re.compile(p5_2)
    res2 = obj2.findall(config)

    if res1 == []:
        err += 'ipv6-slaac-prefix-pool没找到\n'
    else:
        for item in res1:
            if '_nd_' not in item:
                err += 'ipv6-slaac-prefix-pool "{}" 配置错误\n'.format(item)
            if item not in pools:
                err += 'ipv6 pool {} 不存在\n'.format(item)

    if res2 == []:
        err += 'ipv6-delegated-prefix-pool没有找到\n'
    else:
        for item in res2:
            if '_pd_' not in item:
                err += 'ipv6-delegated-prefix-pool "{}" 配置错误\n'.format(item)

            if item not in pools:
                err += 'ipv6 pool {} 不存在\n'.format(item)

    prefix1 = []
    prefix2 = []
    prefix3 = []
    obj4_1 = re.compile(p4_1)
    res4_1 = obj4_1.findall(config)
    obj4_2 = re.compile(p4_2)
    res4_2 = obj4_2.search(config)

    if res4_1 == []:
        err += 'pool没有找到\n'
    else:
        prefix1 = [i[0] for i in res4_1]

    obj_prefix = re.compile(p_prefix)
    obj4_3 = re.compile(p4_3)
    obj_prefix_dy = re.compile(p_prefix_dy)

    res4_3 = obj4_3.search(config)

    if res4_2:
        prefix2 = obj_prefix.findall(res4_2.group())
    else:
        err += 'prefix-list "plToRR_IPV6" 没有找到\n'
        return err

    if res4_3:
        prefix3 = obj_prefix.findall(res4_3.group())
        res_prefix_dy = obj_prefix_dy.findall(res4_3.group())
        if res_prefix_dy == []:
            err += 'subscriber-prefixes 中没有找到prefix\n'
        else:
            for item in res_prefix_dy:
                if item[1] == '48' and item[2] != 'wan-host':
                    err += '{} 配置错误\n'.format(item[0])
                elif item[1] == '44' and item[2] != 'pd':
                    err += '{} 配置错误\n'.format(item[0])
    else:
        err += '没有找到subscriber-prefixes\n'
        return err

    if set(prefix1) != set(prefix2) or set(prefix1)!= set(prefix3):
        err += 'prefix对比失败\n\npool {}\nsubscriber-prefixes {}\nprefix-list "plToRR_IPV6" {}\n\n对比不一致\n'.format(set(prefix1), set(prefix2), set(prefix3))

    return err

def ipv6_address_check(config):
    '''检查 group-interface 中 server 与 ipv6 address 是否匹配'''

    err = ''
    p2_1 = r'''(ipv6
(                address \w{4}:\w{4}:\w{4}::\w{1,3}/128 ?\n)+                local-dhcp-server "server1-ipv6"
            exit)'''

    p_address = r'''address (\w{4}:\w{4}:\w{4}::\w{1,3})/128'''

    p2_2 = r'''(group-interface "(.*)" create
                    ipv6
                        router-advertisements
                            (dns-options
                                include-dns
                            exit\n                            )?other-stateful-configuration
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
                                server \w{3,4}:\w{3,4}:\w{3,4}::\w{1,2}
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
(                   .*\n)+                exit)'''

    p_inter = r'''(group-interface "(.*)" create
(                    description ".*"\n)?                    ipv6
                        router-advertisements
(                            .*?\n)+                            no shutdown
                        exit
                        dhcp6
                            proxy-server
                                client-applications ppp
                                no shutdown
                            exit
                            relay
(                                server \w{3,4}:\w{3,4}:\w{3,4}::\w{1,3}\n)+                                client-applications ppp
                                no shutdown
                            exit
                        exit
                        router-solicit
                            no shutdown
                        exit
                    exit
                    local-address-assignment
(                        .*\n)+                        no shutdown
                    exit
(                    .*\n)+                    pppoe
(                        .*?\n)+                        no shutdown
                    exit
                exit)'''

    p_server = r'''server (\w{3,4}:\w{3,4}:\w{3,4}::\w{1,3})'''

    obj2_1 = re.compile(p2_1)
    obj2_2 = re.compile(p2_2)
    obj_inter = re.compile(p_inter)
    obj_server = re.compile(p_server)
    obj_address = re.compile(p_address)
    res2_1 = obj2_1.search(config)
    res_inter = obj_inter.findall(config)

    #规则二
    if res2_1 == None:
        err = '没有找到ipv6 address\n'
    else:
        #提取ipv6 address
        res_address = obj_address.findall(res2_1.group())

        if res_inter == []:
            err = '没有找到group-interface 或者配置不完善\n'
        else:
            for item in res_inter:
                res_server = obj_server.findall(item[0])

                #检查server 是否与 ipv6 address 匹配
                if set(res_server) != set(res_address):
                    err += 'group-interface {} 中server 与 ipv6 address 不匹配\n'.format(item[1])

                #检查 group-interface 配置是否 完整
                res_wzx = obj2_2.search(item[0])
                if res_wzx == None:
                    err += 'group-interface {} 配置不完整\n'.format(item[1])

                #判断 group-interface pppoe 中是否有 python-policy "qu-port"
                if '                        python-policy "qu-port"' not in item[0]:
                    err += 'group-interface {} pppoe 中没有 python-policy "qu-port"\n'.format(item[1])


    return err

def rule124(config):
    err1 = ''
    err2 = ''
    err4 = ''
    p1 = r'''(sap (.*) capture-sap create
(                .*\n)+            exit)'''

    p2_1 = r'''(ipv6
(                address \w{4}:\w{4}:\w{4}::\w{1,3}/128 ?\n)+                local-dhcp-server "server1-ipv6"
            exit)'''

    p_address = r'''address (\w{4}:\w{4}:\w{4}::\w{1,3})/128'''

    p2_2 = r'''(group-interface "(.*)" create
                    ipv6
                        router-advertisements
                            (dns-options
                                include-dns
                            exit\n                            )?other-stateful-configuration
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
                                server \w{3,4}:\w{3,4}:\w{3,4}::\w{1,2}
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
(                   .*\n)+                exit)'''

    p_inter = r'''(group-interface "(.*)" create
(                    description ".*"\n)?                    ipv6
                        router-advertisements
(                            .*?\n)+                            no shutdown
                        exit
                        dhcp6
                            proxy-server
                                client-applications ppp
                                no shutdown
                            exit
                            relay
(                                server \w{3,4}:\w{3,4}:\w{3,4}::\w{1,3}\n)+                                client-applications ppp
                                no shutdown
                            exit
                        exit
                        router-solicit
                            no shutdown
                        exit
                    exit
                    local-address-assignment
(                        .*\n)+                        no shutdown
                    exit
(                    .*\n)+                    pppoe
(                        .*?\n)+                        no shutdown
                    exit
                exit)'''

    p_server = r'''server (\w{3,4}:\w{3,4}:\w{3,4}::\w{1,3})'''

    obj = re.compile(p1)
    obj2_1 = re.compile(p2_1)
    obj2_2 = re.compile(p2_2)
    obj_inter = re.compile(p_inter)
    obj_server = re.compile(p_server)
    obj_address = re.compile(p_address)
    res = obj.findall(config)
    res2_1 = obj2_1.search(config)
    # res2_2 = obj2_2.findall(config)
    res_inter = obj_inter.findall(config)

    #规则一
    if res == []:
        err1 = '没有找到capture-sap\n'
    else:
        for item in res:
            if 'pppoe-python-policy "qu-port"' not in item[0]:
                err1 += '{} 中没有pppoe-python-policy "qu-port"\n'.format(item[1])

    #规则二
    if res2_1 == None:
        err2 = '没有找到ipv6 address\n'
    else:
        #提取ipv6 address
        res_address = obj_address.findall(res2_1.group())

        if res_inter == []:
            err2 = '没有找到group-interface 或者配置不完善\n'
        else:
            for item in res_inter:
                res_server = obj_server.findall(item[0])

                #检查server 是否与 ipv6 address 匹配
                if set(res_server) != set(res_address):
                    err2 += 'group-interface {} 中server 与 ipv6 address 不匹配\n'.format(item[1])

                #检查 group-interface 配置是否 完整
                res_wzx = obj2_2.search(item[0])
                if res_wzx == None:
                    err2 += 'group-interface {} 配置不完整\n'.format(item[1])

                #判断 group-interface pppoe 中是否有 python-policy "qu-port"
                if '                        python-policy "qu-port"' not in item[0]:
                    err2 += 'group-interface {} pppoe 中没有 python-policy "qu-port"\n'.format(item[1])

    #规则四
    err4 = ruler4(config)

    if err1 == '':
        err1 = '规则一检查 -> 通过'
    else:
        err1 = '规则一检查 -> 错误\n\n' + err1

    if err2 == '':
        err2 = '规则二检查 -> 通过'
    else:
        err2 = '规则二检查 -> 错误\n\n' + err2

    if err4 == '':
        err4 = '规则四检查 -> 通过'
    else:
        err4 = '规则四检查 -> 错误\n\n' + err4

    return ('ipv6配置规范检查', err1 + '\n\n' + err2 + '\n\n' + err4, '')