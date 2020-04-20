import re
from ..main.config_7750 import *

g_ies_ids = [ 2, 13, 15, 16, 17, 18, 19, 25, 33, 
1000, 2281, 4019, 4020, 4021, 6000, 9000, 9010, 
9997, 9998, 9999, 101104, 101106, 101203, 
102103, 102105, 102106, 300011, 1011010, 5179000 ]

g_vprn_ids = [ 40, 41, 42, 43, 517, 1101, 1201, 1501, 1601, 
1701, 1801, 1901, 2001, 2101, 2102, 2201, 2501, 2601, 2801, 
2901, 3001, 3101, 3301, 3501, 3601, 3701, 3901, 4301, 4101, 
4401, 4601, 4701, 4801, 4901, 5001, 5101, 5201, 5301, 5401, 
5501, 5601, 5701, 5801, 5901, 6001, 6101, 6501, 6601, 6701, 
9998, 64800990, 1000000820, 305173951, 517000110, 517000500, 
517000110, 1000000630, 1000000500, 1000000670, 1000000700, 
1000000861, 1000000890 ]

p_sap = generate_pat(4, 'sap', 16)
p_sap_2 = generate_pat(4, 'sap', 20)
p_description = r'^            description "(.*?)"'
p_inter_description = r'^                description "(.*?)"'
p_gruop_inter_description = r'^                    description "(.*?)"'
p_qos_id = r'qos (\d{1,6})'
p_rate = r'rate (\d{1,10})'
# p_arp_table = r'(?s)ARP Table \(Router: Base\)\n={79}.*?\n={79}'
p_sap_arp = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) {1,9}(([A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}) \d{2}h\d{2}m\d{2}s (Dyn|Oth)\[I\] sap '
p_vrrp = r'(?s) vrrp \d{1,3}\n.*?\n {16}exit'
p_vrrp_instances = r'(?s)VRRP Instances.*?\n={79}.*?\n={79}'
p_sap_state = r'(.{32}) \d{1,2} {3,5}(No|Yes)  (Up|Down) {1,3}([a-zA-Z]{2,6}) '

def get_saps(config):
    '''获取所有sap信息'''

    return get_ies_saps(config) + get_vprn_saps(config)

def get_ies_saps(config):
    '''获取ies中的sap信息'''

    saps = []
    for i in g_ies_ids:
        p_ies = generate_pat(0, 'ies', 8, str(i))
        res_ies = re.findall(p_ies, config)
        if len(res_ies) == 2:
            res_ies_des = re.search(p_description, res_ies[1][0])
            res_interface = re.findall(PAT['interface'], res_ies[1][0])
            for j in res_interface:
                res_inter_des = re.search(p_inter_description, j[0])
                if res_ies_des:
                    ies_des = res_ies_des.group(1)
                else:
                    ies_des = ''
                if res_inter_des:
                    inter_des = res_inter_des.group(1)
                else:
                    inter_des = ''
                #判断是否有vrrp
                res_vrrp = re.search(p_vrrp, j[0])
                if res_vrrp:
                    #检查sap 在show router vrrp instance中的状态是否为Master ，如果是，获取sap用户信息
                    res_sap = re.search(p_sap, j[0])
                    if res_sap:
                        res_vrrp_instances = re.search(p_vrrp_instances, config)
                        if res_vrrp_instances:
                            res_sap_state = re.findall(p_sap_state, res_vrrp_instances.group())
                            for k in res_sap_state:
                                a = res_sap.groups()
                                sap = res_sap.group(2).replace('"', '')
                                if sap in k[0] and k[3] == 'Master':
                                    p = p_sap_arp + sap
                                    res_sap_arp = re.search(p, config)
                                    if res_sap_arp:
                                        ip = res_sap_arp.group(1)
                                        mac = res_sap_arp.group(2)
                                    if ip:
                                        saps.append((i, ies_des, j[1], inter_des, sap , ip, mac, qos_id, band_width))
                else:
                    res_sap = re.findall(p_sap, j[0])
                    for sap in res_sap:
                        band_width = ''
                        qos_id = ''
                        ip = ''
                        mac = ''

                        res_qos_id = re.search(p_qos_id, sap[0])
                        if res_qos_id:
                            qos_id = res_qos_id.group(1)
                            p_sap_egress = r'sap-egress %s name ".*?" create.*?\n {8}exit' % res_qos_id.group(1)
                            res_sap_egress = re.search(p_sap_egress, config)
                            if res_sap_egress:
                                res_rate = re.findall(p_rate, res_sap_egress.group())
                                res_rate = [int(i) for i in res_rate]
                                res_rate.sort()
                                band_width = res_rate[-1]/1000

                        p = p_sap_arp + sap[1]
                        res_sap_arp = re.search(p, config)
                        if res_sap_arp:
                            print(res_sap_arp.groups())
                            ip = res_sap_arp.group(1)
                            mac = res_sap_arp.group(2)
                        if ip:
                            saps.append((i, ies_des, j[1], inter_des, sap[1] , ip, mac, qos_id, band_width))


    return saps

def get_vprn_saps(config):
    '''获取vprn中的sap信息'''

    saps = []
    for i in g_vprn_ids:
        p_vprn = generate_pat(0, 'vprn', 8, str(i))
        res_vprn = re.findall(p_vprn, config)
        if len(res_vprn) == 2:
            res_vprn_des = re.search(p_description, res_vprn[1][0])
            res_group_interface = re.findall(PAT['group_interface'], res_vprn[1][0])
            for j in res_group_interface:
                res_group_inter_des = re.search(p_gruop_inter_description, j[0])
                if res_vprn_des:
                    vprn_des = res_vprn_des.group(1)
                else:
                    vprn_des = ''
                if res_group_inter_des:
                    group_inter_des = res_group_inter_des.group(1)
                else:
                    group_inter_des = ''

 
                res_sap = re.findall(p_sap_2, j[0])
                for sap in res_sap:
                    band_width = ''
                    qos_id = ''
                    ip = ''
                    mac = ''

                    res_qos_id = re.search(p_qos_id, sap[0])
                    if res_qos_id:
                        qos_id = res_qos_id.group(1)
                        p_sap_egress = r'sap-egress %s name ".*?" create.*?\n {8}exit' % res_qos_id.group(1)
                        res_sap_egress = re.search(p_sap_egress, config)
                        if res_sap_egress:
                            res_rate = re.findall(p_rate, res_sap_egress.group())
                            res_rate = [int(i) for i in res_rate]
                            res_rate.sort()
                            band_width = res_rate[-1]/1000

                    p = p_sap_arp + sap[1]
                    res_sap_arp = re.search(p, config)
                    if res_sap_arp:
                        print(res_sap_arp.groups())
                        ip = res_sap_arp.group(1)
                        mac = res_sap_arp.group(2)
                    if ip:
                        saps.append((i, vprn_des, j[1], group_inter_des, sap[1] , ip, mac, qos_id, band_width))

    return saps