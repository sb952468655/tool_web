# encoding = utf-8

import re
import difflib

model_str = r'''log
        file-id 1 
            location cf3: 
            rollover 720 retention 72 
        exit 
        filter 92 
            default-action drop
            description "for pppoe & dhcp subscriber"
            entry 10 
                action forward
                match
                    application eq "svcmgr"
                    number eq 2213
                exit 
            exit 
            entry 15 
                action forward
                match
                    application eq "svcmgr"
                    number eq 2214
                exit 
            exit 
            entry 20 
                action forward
                match
                    application eq "svcmgr"
                    number eq 2500
                exit 
            exit 
            entry 25 
                action forward
                match
                    application eq "svcmgr"
                    number eq 2501
                exit 
            exit 
            entry 30                  
                action forward
                match
                    application eq "pppoe"
                exit 
            exit 
            entry 35 
                action forward
                match
                    application eq "svcmgr"
                    number eq 2206
                exit 
            exit 
            entry 40 
                action forward
                match
                    application eq "svcmgr"
                    number eq 2207
                exit 
            exit 
            entry 45 
                action forward
                match
                    application eq "nat"
                    number eq 2012
                exit 
            exit 
            entry 50 
                action forward
                match
                    application eq "nat"
                    number eq 2013
                exit 
            exit 
        exit 
        filter 99                     
            default-action forward
            entry 4
                action forward
                match
                    application eq "pppoe"
                    number eq 2001
                    message eq pattern "audited"
                exit            
            exit
            entry 5 
                action drop
                match
                    application eq "system"
                    subject eq "DHCPS"
                exit 
            exit 
            entry 10 
                action drop
                match
                    application eq "svcmgr"
                    number eq 2213
                exit 
            exit 
            entry 15 
                action drop
                match
                    application eq "svcmgr"
                    number eq 2214
                exit 
            exit 
            entry 20 
                action drop
                match
                    application eq "svcmgr"
                    number eq 2500
                exit 
            exit 
            entry 25 
                action drop
                match
                    application eq "svcmgr"
                    number eq 2501
                exit                  
            exit 
            entry 30 
                action drop
                match
                    application eq "pppoe"
                exit 
            exit 
            entry 35 
                action drop
                match
                    application eq "system"
                    subject eq "SUBMGR"
                exit 
            exit 
            entry 40 
                action drop
                match
                    application eq "nat"
                    number eq 2012
                exit 
            exit 
            entry 45 
                action drop
                match
                    application eq "nat"
                    number eq 2013
                exit 
            exit 
            entry 900 
                action drop
                match
                    application eq "mirror"
                exit 
            exit 
            entry 901 
                action drop
                match                 
                    application eq "li"
                exit 
            exit 
            entry 902 
                action drop
                match
                    message eq pattern "tli"
                exit 
            exit             
        exit 
        filter 100 
            default-action drop
            description "Collect events for Serious Errors Log"
            entry 5 
                action drop
                match                 
                    application eq "system"
                    subject eq "DHCPS"
                exit 
            exit 
            entry 10 
                action drop
                match
                    application eq "system"
                    subject eq "SUBMGR"
                exit 
            exit 
            entry 100 
                action forward
                match
                    severity gte major
                exit 
            exit 
        exit 
        event-control "chassis" 2058 generate major
        event-control "chassis" 2059 generate major
        event-control "chassis" 2063 generate major
        event-control "chassis" 2076 generate major
        event-control "chassis" 2098 generate major
        event-control "chassis" 2099 generate major
        event-control "chassis" 2101 generate major
        event-control "chassis" 2102 generate major
        event-control "chassis" 2103 generate major
        event-control "chassis" 2104 generate
        event-control "chassis" 2105 generate
        event-control "chassis" 2110 generate major
        event-control "chassis" 2129 generate
        event-control "dhcp" 2002 suppress
        event-control "dhcp" 2004 suppress
        event-control "dhcp" 2005 suppress
        event-control "dhcp" 2010 suppress
        event-control "dhcps" 2001 suppress
        event-control "dhcps" 2003 suppress
        event-control "dhcps" 2004 suppress
        event-control "dhcps" 2017 suppress
        event-control "dhcps" 2018 suppress
        event-control "dhcps" 2019 suppress
        event-control "dhcps" 2034 suppress
        event-control "dhcps" 2035 suppress
        event-control "dhcps" 2036 suppress
        event-control "li" 2001 generate
        event-control "li" 2011 generate
        event-control "li" 2012 generate
        event-control "li" 2013 generate
        event-control "li" 2014 generate
        event-control "li" 2018 generate
        event-control "li" 2019 generate
        event-control "li" 2020 generate
        event-control "li" 2021 generate
        event-control "li" 2022 generate
        event-control "li" 2023 generate
        event-control "li" 2026 generate
        event-control "li" 2027 generate
        event-control "li" 2028 generate
        event-control "li" 2029 generate
        event-control "li" 2030 generate
        event-control "li" 2031 generate
        event-control "li" 2032 generate
        event-control "li" 2033 generate
        event-control "li" 2034 generate
        event-control "li" 2035 generate
        event-control "li" 2036 generate
        event-control "li" 2037 generate specific-throttle-rate 2000 interval 20
        event-control "li" 2101 generate
        event-control "li" 2102 generate
        event-control "li" 2103 generate
        event-control "li" 2104 generate
        event-control "li" 2105 generate
        event-control "li" 2106 generate
        event-control "li" 2107 generate
        event-control "li" 2108 generate
        event-control "li" 2109 generate
        event-control "li" 2110 generate
        event-control "li" 2111 generate
        event-control "li" 2112 generate
        event-control "li" 2113 generate
        event-control "li" 2114 generate
        event-control "li" 2115 generate
        event-control "li" 2116 generate
        event-control "li" 2117 generate
        event-control "li" 2118 generate
        event-control "li" 2119 generate
        event-control "li" 2120 generate
        event-control "li" 2121 generate
        event-control "li" 2123 generate
        event-control "li" 2124 generate
        event-control "li" 2202 generate
        event-control "li" 2203 generate
        event-control "li" 2206 generate
        event-control "li" 2207 generate
        event-control "li" 2208 generate
        event-control "li" 2209 generate
        event-control "li" 2212 generate
        event-control "li" 2213 generate
        event-control "li" 2300 generate
        event-control "logger" 2002 suppress
        event-control "logger" 2006 suppress
        event-control "logger" 2008 suppress
        event-control "logger" 2009 suppress
        event-control "mirror" 2001 generate
        event-control "mirror" 2002 generate
        event-control "mirror" 2003 generate
        event-control "mirror" 2004 generate
        event-control "mirror" 2006 generate
        event-control "mirror" 2007 generate
        event-control "mirror" 2008 generate
        event-control "mirror" 2009 generate
        event-control "mirror" 2022 generate
        event-control "nat" 2012 generate
        event-control "nat" 2013 generate
        event-control "security" 2001 generate warning
        event-control "security" 2002 generate warning
        event-control "security" 2032 suppress
        event-control "svcmgr" 2108 suppress
        event-control "svcmgr" 2203 generate warning
        event-control "svcmgr" 2206 suppress
        event-control "svcmgr" 2210 suppress
        event-control "svcmgr" 2513 suppress
        event-control "system" 2002 suppress
        event-control "system" 2003 suppress
        event-control "system" 2006 suppress
        event-control "system" 2007 suppress
        event-control "system" 2009 suppress
        event-control "system" 2011 suppress
        event-control "user" 2001 generate warning
        event-control "user" 2002 generate warning
        event-control "user" 2011 generate warning
        syslog 1
            description "To_Syslog-Server_1"
            address 211.103.0.14
            level warning
        exit 
        syslog 2
            description "To_Syslog-Server_2"
            address 211.103.0.24
            level warning
        exit 
        syslog 8
            description "to CIOMOSS"
            address 117.134.47.81
            facility local2
        exit   
        snmp-trap-group 97            
            trap-target "CIOMSS1" address 117.134.47.1 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS10" address 117.134.47.10 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS11" address 117.134.47.11 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS12" address 117.134.47.12 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS13" address 117.134.47.13 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS14" address 117.134.47.14 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS15" address 117.134.47.15 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS16" address 117.134.47.16 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS17" address 117.134.47.17 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS18" address 117.134.47.18 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS19" address 117.134.47.19 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS2" address 117.134.47.2 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS20" address 117.134.47.20 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS21" address 117.134.47.21 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS22" address 117.134.47.22 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS23" address 117.134.47.23 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS24" address 117.134.47.24 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS25" address 117.134.47.25 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS3" address 117.134.47.3 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS4" address 117.134.47.4 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS5" address 117.134.47.5 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS6" address 117.134.47.6 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS7" address 117.134.47.7 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS8" address 117.134.47.8 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS9" address 117.134.47.9 snmpv2c notify-community "n1j0J2S5"
        exit               
        snmp-trap-group 98
            trap-target "TRAP-STATION-1" address 211.103.0.24 snmpv2c notify-community "n0j0J2S5"
            trap-target "TRAP-STATION-2" address 211.103.0.14 snmpv2c notify-community "n0j0J2S"
            trap-target "CIOMSS26" address 117.134.47.26 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS27" address 117.134.47.27 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS28" address 117.134.47.28 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS29" address 117.134.47.29 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS30" address 117.134.47.30 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS31" address 117.134.47.31 snmpv2c notify-community "n1j0J2S5"
            trap-target "CIOMSS32" address 117.134.47.32 snmpv2c notify-community "n1j0J2S5"            
        exit 
        log-id 1
            time-format local
            from main security change 
            to syslog 1
            no shutdown
        exit
        log-id 2
            time-format local
            from main security change 
            to syslog 2
            no shutdown
        exit
        log-id 8
            time-format local
            from main security change 
            to syslog 8
            no shutdown
        exit        
        log-id 20
            filter 99
            time-format local
            from main security change 
            to file 1
            no shutdown
        exit
        log-id 33
            from debug-trace 
            to memory
            no shutdown
        exit
        log-id 92
            description "for pppoe & dhcp subscriber"
            filter 92
            time-format local
            from main 
            to memory 1024
            no shutdown
        exit
        log-id 97
            filter 99
            time-format local
            from main security change 
            to snmp 1024
            no shutdown
        exit         
        log-id 98
            time-format local
            from main security 
            to snmp 1024
            no shutdown
        exit
        log-id 99
            filter 99
            no shutdown
        exit
    exit'''

def check_log_warn(config):
    '''与log 告警有关配置检查'''

    err = ' '
    p_log_configuration = r'(?s)echo "Log Configuration"\n#-{50}.*?\n#-{50}'
    p_config_log = r'(?s)log.*?\n {4}exit'

    res_log_configuration = re.search(p_log_configuration, config)
    if not res_log_configuration:
        return '没有找到Log Configuration\n'

    
    res_config_log = re.search(p_config_log, res_log_configuration.group())
    if not res_config_log:
        err += '没有找到config log\n'
        return err

    config_log_lines = res_config_log.group().splitlines()
    model_lines = model_str.splitlines()
    config_log = ''
    model_log = ''
    for i in config_log_lines:
        config_log += i.rstrip() + '\n'

    for i in model_lines:
        model_log += i.rstrip() + '\n'

    if config_log != model_log:
        text1_lines = config_log.splitlines()
        text2_lines = model_log.splitlines()

        d = difflib.Differ()
        diff = d.compare(text1_lines, text2_lines)
        diff_str = "\n".join(list(diff))
        diff_str = re.sub(r'- ', r'-? ', diff_str)
        err = 'log config 配置错误，请对该项人工检查复核！\n{}\n'.format(diff_str)

    if err == '':
        err = '与log 告警有关配置检查 -> OK\n\n'
    else:
        err = '与log 告警有关配置检查 -> 请进行确认\n\n' + err + '\n\n'

    # return err
    return ('log规范性检查', err, '')
    