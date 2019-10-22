# encoding = utf-8
import re
import IPy
from .config_7750 import *

def outside_pool_check(config):
    '''检查outside pool 中的地址是否在黑洞路由中'''

    err = []
    pat_outside = generate_pat(2,'outside', 12)
    res_outside = re.search(pat_outside, config)
    res_static_route = re.findall(PAT['static_route'], config)
    if res_static_route == []:
        err.append('nat outside 地址池检查->ERROR\n没有找到黑洞路由配置\n')
        return err
    if res_outside:
        res_pool = re.findall(PAT['pool'], res_outside.group())
        if res_pool:
            #检查pool中的ip是否包含在黑洞路由中
            for pool in res_pool:
                res_address_range = re.findall(PAT['address_range'], pool[0])
                if not res_address_range:
                    # err += 'pool "%s" 中没有找到 address_range\n' % pool[1]
                    continue
                for item in res_address_range:
                    b_include = False
                    ip_begin = IPy.IP(item[0])
                    ip_end = IPy.IP(item[1])
                    for ip in res_static_route:
                        static_route = IPy.IP(ip[1])
                        if item[0] == '200.200.254.1' and item[1] == '200.200.254.254':
                            print('1')
                        if ip_begin in static_route and ip_end in static_route:
                            b_include = True
                            break

                    if b_include == False:
                        err.append('pool "{}" 中的 address range: {}-{} 没有包含在黑洞路由中\n   请检查 address-range {} {}\n'.format(pool[1],
                                item[0], item[1], item[0], item[1]))

        else:
            err.append('配置中没有找到 outside 中的 pool 配置\n')
    else:
        err.append('配置中没有找到 outside 配置 请维护人员进行设备配置核实\n')

    return err

if __name__ == '__main__':
    with open('苏州金鸡湖') as f:
        config = f.read()
        res = outside_pool_check(config)

        print(res)