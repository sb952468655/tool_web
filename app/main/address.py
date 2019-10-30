import re, os
from .config_7750 import *
from .report import get_ip
import IPy

def get_address_data(config):
    '''获取地址采集数据'''
    address = []
    address_data = []
    ip = get_ip(config)
    config_7750 = Config_7750(config)

    ies = config_7750.get_ies()
    for item in ies:
        interface = item.get_interface()
        p_address = r'address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d\d)'

        for item2 in interface:
            sap_name = ''
            description = ''

            #判断是否有sap
            p_sap = PAT['sap']
            res_sap = re.search(p_sap, item2.config)
            if res_sap:
                sap_name = res_sap.group(2)
                print(sap_name)
            
            #获取描述
            res_description = re.search(PAT['description'], item2.config)
            if res_description:
                description = res_description.group(1)
            res_address = re.findall(p_address, item2.config)
            address.append(res_address)
            for item3 in res_address:
                ips = IPy.IP(item3[0] + '/' + item3[1], make_net=1)
                for item4 in ips:
                    ip_type = '业务侧'
                    if item4 == ips[0]:
                        ip_type = '网号'
                    elif item4 == ips[-1]:
                        ip_type = '广播'
                    elif item4.strNormal(0) == item3[0]:
                        ip_type = '接口'

                    address_data.append(
                        [ ip, 'interfaceip（三层用户接口）', ip_type, '是', item4, '', item3[1], item2.name, sap_name, '', item.name, '', '', description ]
                    )

    return address_data