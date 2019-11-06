import re
import IPy
import sys
# from config_7750 import *
from .address_pool_and_security import address_range_check, address_is_include_pool, gi_address_check, pool_address_prefix_list, ies_3000_inside_check
from .address import prefix_list_include_black_hole, black_hole_address_range_check, inside_subnet_address_check
from .outside_pool import outside_pool_check
from .subnet import subnet_check
from .ipv6 import check4
from .rule124 import ipv6_address_check


def all_check(config):
    '''检查所有地址相关配置
    1.检查 address-range 范围是否正确
    2.检查 pool中的地址 是否在 address 中
    3.检查 ies, vprn 中的 gi-address 是否在 address 中
    4.检查 prefix-list 中是否包含 黑洞路由地址
    5.检查 黑洞路由与pool "nat-pppoe" 中的address-range 是否匹配
    6.检查 inside subnet address 地址是否正确
    7.检查 outside pool 中的地址是否在黑洞路由中
    8.检查 dhcp pool, 网关地址, 路由发布地址是否一致
    9.检查 ies 3000 下的sub interface下的私网地址是否与 Nat 中 inside 地址一致'''

    err = []

    err.append(('检查 address-range 范围是否正确', address_range_check(config)))
    err.append(('检查 address 是否在 pool 的网段中',address_is_include_pool(config)))
    err.append(('检查 ies 3000 sub interface下的私网地址是否与 Nat 中 inside 地址一致',ies_3000_inside_check(config)))
    err.append(('检查 dhcp pool, 网关地址, 路由发布地址是否一致',pool_address_prefix_list(config)))
    err.append(('检查 prefix-list 中是否包含 黑洞路由地址',prefix_list_include_black_hole(config)))
    err.append(('检查黑洞路由与pool "nat-pppoe" 中的address-range 是否匹配',black_hole_address_range_check(config)))
    err.append(('检查 inside subnet address 地址是否正确',inside_subnet_address_check(config)))
    err.append(('检查outside pool 中的地址是否在黑洞路由中',outside_pool_check(config)))

    return err
