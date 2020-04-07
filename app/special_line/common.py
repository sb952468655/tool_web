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

def get_saps(config):
    '''获取所有sap信息'''

    saps = []
    p_sap = generate_pat(4, 'sap', 16)
    p_qos_id = r'qos (\d{1,6})'
    p_rate = r'rate (\d{1,10})'
    for i in g_ies_ids:
        p_ies = generate_pat(0, 'ies', 8, i)
        res_ies = re.findall(p_ies, config)
        if len(res_ies) == 2:
            res_interface = re.findall(PAT['interface'], res_ies[1][0])
            for j in res_interface:
                res_sap = re.findall(p_sap, j[0])
                for sap in res_sap:
                    res_qos_id = re.search(p_qos_id, sap[0])
                    if res_qos_id:
                        p_sap_egress = r'sap-egress %s name ".*?" create.*?\n {8}exit' % res_qos_id.group(1)
                        res_sap_egress = re.search(p_sap_egress, config)
                        if res_sap_egress:
                            res_rate = re.findall(p_rate, res_sap_egress.group())
                            res_rate = [int(i) for i in res_rate]
                            res_rate.sort()
                            band_width = res_rate[-1]/1000
