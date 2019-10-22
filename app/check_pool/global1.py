# encoding = utf-8

import re

p_subscriber_mgmt = r'''(subscriber-mgmt
(        .*\n)+    exit)'''

obj_subscriber_mgmt = re.compile(p_subscriber_mgmt)

template_nat_policy = r'''nat-policy "nat-iptv" create
                alg
                    rtsp
                    sip
                    pptp
                exit
                pool "nat-iptv" router Base
                port-limits
                    watermarks high 90 low 30
                exit
                session-limits
                    watermarks high 90 low 30
                exit
                timeouts
                    tcp-established min 15 
                exit
            exit'''

template_ingress = r'''sap-ingress 3030 create
            description "IPTV"
            queue 1 create
            exit
            queue 11 multipoint create
            exit
            policer 1 create
                rate 100000 cir 100000
                mbs 8192 kilobytes
                cbs 8192 kilobytes
            exit
            fc "af" create
                policer 1
            exit
            fc "be" create
                policer 1
            exit
            fc "ef" create
                policer 1
            exit
            fc "h1" create
                policer 1
            exit
            fc "h2" create
                policer 1
                in-remark dscp af41
            exit
            fc "l1" create
                policer 1
            exit
            fc "l2" create
                policer 1
            exit
            fc "nc" create
                policer 1
            exit
            dot1p 4 fc "h2"
            dscp af41 fc "h2"
            default-fc "h2"
            default-priority high
        exit'''


template_egress = r'''sap-egress 3030 create
            description "IPTV"
            queue 1 create
            exit
            policer 1 create
                rate 100000 cir 100000
                mbs 8192 kilobytes
                cbs 8192 kilobytes
            exit
            fc af create
                policer 1
            exit 
            fc be create
                policer 1
            exit 
            fc ef create
                policer 1
            exit 
            fc h1 create
                policer 1
            exit 
            fc h2 create
                policer 1
            exit 
            fc l1 create
                policer 1
            exit 
            fc l2 create
                policer 1
            exit 
            fc nc create
                policer 1
            exit 
        exit'''
subscriber_mgmt_ipoe_policy = r'''ipoe-session-policy "ipoe-policy" create
        exit'''

subscriber_mgmt_auth_iptv = r'''authentication-policy "auth-iptv-p1" create
            fallback-action user-db "no-auth"
            accept-authorization-change
            include-radius-attribute
                circuit-id
                remote-id
                nas-port-id  suffix circuit-id
                nas-identifier
                dhcp-vendor-class-id
                mac-address
            exit
            radius-server-policy "iptv-radius-p1"
        exit'''

subscriber_mgmt_acc_iptv = r'''radius-accounting-policy "acc-iptv-p1" create
            no queue-instance-accounting
            host-accounting interim-update
            update-interval 30
            include-radius-attribute
                framed-ip-addr
                framed-ip-netmask
                mac-address
                nas-identifier
                nas-port-id  suffix circuit-id
                nat-port-range
                user-name
                all-authorized-session-addresses
                no detailed-acct-attributes
                std-acct-attributes
            exit
            session-id-format number
            radius-server-policy "iptv-radius-p1"
        exit'''

subscriber_mgmt_sla_iptv = r'''sla-profile "sla-iptv" create
            ingress
                qos 3030 shared-queuing
                exit
                ip-filter 6050
            exit
            egress
                qos 3030 
                exit
            exit
        exit'''

subscriber_mgmt_sub_iptv = r'''sub-profile "sub-iptv" create
            nat-policy "nat-iptv"
            radius-accounting
                policy "acc-iptv-p1"
            exit
        exit'''

subscriber_mgmt_msap_iptv = r'''msap-policy "msap-iptv" create
            cpu-protection 30 mac-monitoring
            sub-sla-mgmt
                def-sub-id use-auto-id
                def-sub-profile "sub-iptv"
                def-sla-profile "sla-iptv"
                sub-ident-policy "sub-ident-local"
                multi-sub-sap limit 30000
                single-sub-parameters
                    profiled-traffic-only
                exit
            exit
        exit'''

subscriber_mgmt_msap_pppoe = r'''msap-policy "msap-pppoe" create
            cpu-protection 30 mac-monitoring
            sub-sla-mgmt
                def-sub-profile "sub-no-auth"
                def-sla-profile "sla-pppoe"
                sub-ident-policy "sub-ident-local"
                multi-sub-sap limit 20000
                single-sub-parameters
                    profiled-traffic-only
                exit
            exit
        exit'''

template_sub = r'''local-user-db "ludb-iptv" create
            ipoe
                match-list encap-tag-range 
                host "iptv" create
                    host-identification
                        encap-tag-range start-tag *.1031 end-tag *.1031
                    exit
                    auth-policy "auth-iptv-p1"
                    msap-defaults
                        group-interface "iptv-" suffix port-id
                        policy "msap-iptv"
                        service 1000
                    exit
                    no shutdown
                exit
            exit
            no shutdown
        exit'''


def global_check(config):
    err = ''
    if template_nat_policy not in config:
        err += 'nat-policy "nat-iptv" 配置错误\n'
    if template_ingress not in config:
        err += 'sap-ingress 3030 配置错误\n'
    if template_egress not in config:
        err += 'sap-egress 3030 配置错误\n'
    if template_sub not in config:
        err += 'ludb-iptv 配置错误\n'


    #开始检测subscriber_mgmt配置

    res = obj_subscriber_mgmt.findall(config)

    if len(res) != 2:
        err += '没有找到subscriber-mgmt配置\n'
    else:
        if subscriber_mgmt_acc_iptv not in res[0][0]:
            err += 'subscriber_mgmt_acc_iptv 配置错误\n'
        elif subscriber_mgmt_auth_iptv not in res[0][0]:
            err += 'subscriber_mgmt_auth_iptv 配置错误\n'
        elif subscriber_mgmt_ipoe_policy not in res[0][0]:
            err += 'subscriber_mgmt_ipoe_policy 配置错误\n'
        elif subscriber_mgmt_msap_pppoe not in res[0][0]:
            err += 'subscriber_mgmt_msap_pppoe 配置错误\n'
        elif subscriber_mgmt_sla_iptv not in res[0][0]:
            err += 'subscriber_mgmt_sla_iptv 配置错误\n'
        elif subscriber_mgmt_sub_iptv not in res[0][0]:
            err += 'subscriber_mgmt_sub_iptv 配置错误\n'


        #单独检查msap-policy "msap-iptv"

        p_msap_iptv = r'''msap-policy "msap-iptv" create
(            .*\n)+        exit'''
        obj_msap_iptv = re.compile(p_msap_iptv)

        res_msap_iptv = obj_msap_iptv.search(res[0][0])
        if res_msap_iptv:
            msap_iptv_lines1 = res_msap_iptv.group().split('\n')
            msap_iptv_lines2 = subscriber_mgmt_msap_iptv.split('\n')
            if sorted(msap_iptv_lines1) != sorted(msap_iptv_lines2):
                err += 'subscriber_mgmt_msap_iptv 配置错误\n'
        else:
            err += '没有找到 subscriber_mgmt_msap_iptv 配置\n'
    if err == '':
        err = '全局校验 -> OK\n\n'
    else:
        err = '全局校验 -> ERROR\n\n' + err

    return err
