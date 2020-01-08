from .check import *
from .output import make_xlsx

def zuxun_check(config):

    file_data = []
    system_name = get_system_name(config)
    system_ip = get_system_ip(config)
    radius_ip = get_radius_ip(config)
    port_and_description = get_port_and_description(config)

    res_radius_check = radius_check(config)
    if not res_radius_check:
        res_radius_check = '正常'
    res_video_check = video_check(config)
    if not res_video_check:
        res_video_check = '正常'
    
    res_lag_check = lag_check(config)
    res_lag_check += lag_check_2(config)
    if not res_lag_check:
        res_lag_check = '正常'
    res_local_dhcp_server_check = local_dhcp_server_check(config)
    if not res_local_dhcp_server_check:
        res_local_dhcp_server_check = '正常'
    res_config_check = config_check(config)
    if not res_config_check:
        res_config_check = '正常'
    res_get_pppoe = get_pppoe(config)

    res_bras_check = bras_check(config)
    if not res_config_check:
        res_bras_check = '正常'

    file_data.append((
        system_name,
        system_ip,
        radius_ip,
        port_and_description,
        res_radius_check,
        res_video_check,
        res_lag_check,
        res_local_dhcp_server_check,
        res_config_check,
        res_get_pppoe,
        res_bras_check
    ))

    err =  '1、Bras设备信息输出\n' + system_name + '\n' + system_ip + '\n' + radius_ip + '\n' + port_and_description + '\n'
    err += '2、Radius服务器配置合规性\n'
    if res_radius_check != '正常':
        err += 'Radius服务器配置合规性检查异常，异常说明\n' + res_radius_check + '\n'
    else:
        err += 'Radius服务器配置合规性检查正常' + '\n\n'

    if res_video_check != '正常':
        err += '3、video配置合规性:\nvideo配置合规性检查异常，异常说明\n' + res_video_check + '\n'
    else:
        err += '3、video配置合规性:\nvideo配置合规性检查正常\n\n'

    if res_lag_check != '正常':
        err += '4、与ies3000接口业务对应的HGU管理配置和IMS配置检查:\n' + res_lag_check + '\n'
    else:
        err += '4、与ies3000接口业务对应的HGU管理配置和IMS配置检查:\nHGU管理配置合规性检查正常, IMS配置合规性检查正常\n\n'

    if res_local_dhcp_server_check != '正常':
        err += '5、Dns检查：\n' + res_local_dhcp_server_check + '\n'
    else:
        err += '5、Dns检查：\npppoe DNS配置合规性检查正常,cms DNS配置合规性检查正常,ims DNS配置合规性检查正常\n\n'

    if res_config_check != '正常':
        err += '6、telnet acl白名单检查：\n' + res_config_check + '\n'
    else:
        err += '6、telnet acl白名单检查：\ntelnet acl白名单配置合规性检查正常\n\n'

    if res_get_pppoe:
        err += '7、PPPoE业务本地默认速率检查：\n' + res_get_pppoe + '\n'

        err += '8、urpf检查：\n' + res_bras_check + '\n'
    else:
        err += '8、urpf配置检查：\nbras配置检查正常\n\n'

    return err