import re
import os

c = r'''ies 3000 name "3000" customer 1 create
            subscriber-interface "pppoe" create
                address 100.126.112.1/22
                address 10.132.60.1/22
                address 10.222.128.1/21
                address 10.32.80.1/21
                address 100.72.72.1/21
                address 100.74.112.1/22
                address 10.222.192.1/20
                address 100.77.96.1/21
                address 100.77.160.1/20
                address 100.72.32.1/20
                address 100.78.112.1/20
                address 183.211.68.201/29
                address 100.79.16.1/20
                address 100.79.112.1/20
                address 183.206.225.129/28
                address 183.206.228.129/28
                address 10.133.126.1/23
                address 10.132.196.1/22
                address 10.162.76.1/22
                address 10.162.188.1/22
                address 10.162.192.1/22
                address 10.162.196.1/22
                address 10.162.200.1/22
                address 100.96.128.1/18
                address 100.96.192.1/18
                ipv6
                    delegated-prefix-len 60
                    subscriber-prefixes
                        prefix 2409:8a20:5607::/48 wan-host
                        prefix 2409:8a20:5670::/44 pd
                        prefix 2409:8a22:5607::/48 wan-host
                        prefix 2409:8a22:5670::/44 pd
                    exit
                exit'''

with open(os.path.join('app','static','1.log')) as f:
    c = f.read()

p = r'address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d\d)'
interface = r'(?s)(interface "(.*?)" create.*?\n {12}exit)'
ies = r'(?s)(ies (\d{2,6})( name "\d{2,6}")? customer \d{1,2} create.*?\n {8}exit)'

res_ies = re.findall(ies, c)
for item in res_ies:
    res_interface = re.findall(interface, item[0])
    for item2 in res_interface:
        res_address = re.findall(p, item2[0])
        if res_address:
            for item3 in res_address:
                print(item3[0] + '/' + item3[1])