#coding: utf-8
import os
CITY = 'changzhou'
g_log_path = os.path.join('app', 'static', 'logs')
g_backup_path = os.path.join('app', 'static', 'backup')

g_city_to_name = {
    'changzhou': '常州',
    'suzhou': '苏州',
    'wuxi': '无锡',
    'huaian': '淮安',
    'lianyungang': '连云港',
    'nanjing': '南京',
    'nantong': '南通',
    'suqian': '宿迁',
    'taizhou': '泰州',
    'yancheng': '盐城',
    'yangzhou': '扬州',
    'zhenjiang': '镇江',
    'xuzhou': '徐州'
}

g_config_model = [
    ('10GE', '''/config
    port @10ge_port_id@
        description "@10ge_port_description@"
        ethernet
            mode access
            encap-type qinq
        exit
        no shutdown
    exit
'''),
    ('GE', '''/config
    port @ge_port_id@
        description "@ge_port_description@"
        ethernet
            mode access
            encap-type qinq
            no autonegotiate
        exit
        no shutdown
    exit
'''),
    ('Lag', '''/config
    lag @Lag_id@
        description "@Lag_description@"
        mode access
        encap-type qinq
        access
            adapt-qos link 
            per-fp-ing-queuing
        exit
        %Lag_port_id_8_space%
$        lacp active$
        no shutdown
    exit all
'''),
    ('Ies 3000', '''configure service ies 3000 subscriber-interface "pppoe"
                group-interface "mhsi-lag-@Lag_id@" create
                    ipv6
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
                                server @Ies_3000_dhcp6_server_address@
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
                exit
                group-interface "shsi-lag-@Lag_id@" create
                    ipv6
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
                                server @Ies_3000_dhcp6_server_address@
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
                exit all
'''),
    ('Ies 1000', '''config service ies 1000
            subscriber-interface "iptv"
                group-interface "iptv-lag-@Lag_id@" create
                    dhcp
                        server @Ies_1000_dhcp_server_address@
                        trusted
                        lease-populate 32767
                        no shutdown
                    exit
                    host-connectivity-verify action remove
                    ipoe-session
                        ipoe-session-policy "ipoe-policy"
                        sap-session-limit 30000
                        user-db "ludb-iptv"
                        no shutdown
                    exit
                exit all
'''),
    ('主用vpls', '''vpls XXxxxx  #主用
            sap lag-@Lag_id@:32.* capture-sap create    
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:34.* capture-sap create
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:36.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:38.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:40.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:42.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:44.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:46.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:48.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:50.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:52.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:54.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:56.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:58.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:60.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:62.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:64.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:66.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:68.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:70.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:72.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:74.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:76.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:78.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:80.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:82.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:84.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:86.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:88.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:90.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:92.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:94.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:96.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:98.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:100.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:102.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:104.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:106.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:108.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:110.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:112.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:114.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:116.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:118.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:120.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:122.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:124.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:126.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:128.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:130.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:132.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:134.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:136.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:138.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:140.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:142.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:144.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:146.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:148.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:150.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:152.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:154.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:156.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:158.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:160.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:162.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:164.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:166.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:168.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:170.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:172.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:174.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:176.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:178.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:180.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:182.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:184.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:186.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:188.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:190.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:192.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:194.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:196.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:198.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:200.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:202.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:204.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:206.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:208.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:210.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:212.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:214.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:216.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:218.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:220.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:222.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:224.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:226.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:228.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:230.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:232.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:234.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:236.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:238.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:240.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:242.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:244.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:246.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:248.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:250.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:252.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:254.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:256.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:258.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:260.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:262.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:264.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:266.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:268.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:270.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:272.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:274.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:276.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:278.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:280.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:282.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:284.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:286.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:288.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:290.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:292.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:294.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:296.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:298.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:300.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:302.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:304.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:306.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:308.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:310.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:312.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:314.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:316.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:318.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:320.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:322.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:324.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:326.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:328.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:330.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:332.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:334.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:336.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:338.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:340.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:342.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:344.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:346.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:348.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:350.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                no shutdown
            exit
            sap lag-@Lag_id@:*.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet dhcp pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                ipoe-session
                    ipoe-session-policy "ipoe-policy"
                    user-db "ludb-iptv"
                    no shutdown
                exit
                no shutdown
            exit all
'''),
    ('备用vpls', '''vpls XXxxxx  #备用
            sap lag-@Lag_id@:32.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:34.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:36.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:38.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:40.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:42.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:44.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:46.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:48.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:50.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:52.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:54.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:56.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:58.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:60.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:62.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:64.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:66.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:68.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:70.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:72.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:74.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:76.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:78.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:80.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:82.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:84.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:86.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:88.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:90.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:92.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:94.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:96.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:98.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:100.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:102.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:104.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:106.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:108.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:110.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:112.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:114.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:116.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:118.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:120.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:122.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:124.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:126.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:128.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:130.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:132.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:134.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:136.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:138.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:140.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:142.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:144.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:146.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:148.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:150.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:152.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:154.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:156.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:158.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:160.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:162.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:164.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:166.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:168.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:170.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:172.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:174.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:176.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:178.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:180.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:182.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:184.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:186.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:188.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:190.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:192.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:194.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:196.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:198.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:200.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:202.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:204.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:206.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:208.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:210.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:212.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:214.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:216.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:218.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:220.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:222.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:224.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:226.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:228.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:230.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:232.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:234.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:236.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:238.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:240.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:242.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:244.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:246.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:248.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:250.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:252.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:254.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:256.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:258.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:260.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:262.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:264.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:266.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:268.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:270.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:272.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:274.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:276.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:278.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:280.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:282.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:284.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:286.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:288.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:290.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:292.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:294.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:296.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:298.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:300.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:302.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:304.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:306.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:308.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:310.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:312.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:314.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:316.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:318.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:320.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:322.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:324.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:326.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:328.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:330.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:332.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:334.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:336.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:338.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:340.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:342.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:344.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:346.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:348.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:350.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                no shutdown
            exit
            sap lag-@Lag_id@:*.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet dhcp pppoe
                pppoe-policy "pppoe-policy-s"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-s"
                ipoe-session
                    ipoe-session-policy "ipoe-policy"
                    user-db "ludb-iptv"
                    no shutdown
                exit
                no shutdown
            exit all
'''),
    ('不分主备用vpls', '''vpls XXxxxx #不分主备用vpls
            sap lag-@Lag_id@:*.* capture-sap create
                cpu-protection 32 mac-monitoring
                trigger-packet dhcp pppoe
                pppoe-policy "pppoe-policy-m"
                pppoe-python-policy "qu-port"
                pppoe-user-db "ludb-m"
                ipoe-session
                    ipoe-session-policy "ipoe-policy"
                    user-db "ludb-iptv"
                    no shutdown
                exit
                no shutdown
            exit all
'''),
    ('Igmp', '''config service ies 1000
            interface "iptv-lag-@Lag_id@:4021.0" create
                address @igmp_ies_1000_interface_address@/30
                bfd 500 receive 500 multiplier 3 type cpm-np
                sap lag-@Lag_id@:4021.0 create
                exit
            exit all

config router
        pim
            interface "iptv-lag-@Lag_id@:4021.0"
                bfd-enable
                priority @pim_priority@
            exit all

config router
        igmp
            interface "iptv-lag-@Lag_id@:4021.0"
                version 2
                no subnet-check
                no shutdown
            exit all
'''),
    ('跨区县', '''configure subscriber-mgmt
        local-user-db "ludb-m"
            ppp
                host "@ludb_host_name@__OLT" create
                    host-identification
                        derived-id "lag-@Lag_id@"
                    exit
                    auth-policy "auth-pppoe-p1"
                    msap-defaults
                        group-interface "mhsi-" suffix port-id
                        policy "msap-pppoe"
                        service 3000
                    exit
                    ipv6-delegated-prefix-pool "@delegated_pool_name@"
                    ipv6-slaac-prefix-pool "@slaac_pool_name@"
                    no shutdown
                exit
            exit
        exit
        local-user-db "ludb-s"
            ppp
                host "@ludb_host_name@_OLT" create
                    host-identification
                        derived-id "lag-@Lag_id@"
                    exit
                    auth-policy "auth-pppoe-p1"
                    msap-defaults
                        group-interface "shsi-" suffix port-id
                        policy "msap-pppoe"
                        service 3000
                    exit
                    ipv6-delegated-prefix-pool "@delegated_pool_name@"
                    ipv6-slaac-prefix-pool "@slaac_pool_name@"
                    no shutdown
                exit all
''')
]