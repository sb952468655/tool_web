import re
from .config_7750 import *

def fc_check(config):
    err = ''
    p_egress = r'''        sap-egress 3010 create
(            .*\n)+        exit'''
    p_ingress = r'''        sap-ingress 3010 create
(            .*\n)+        exit'''

    p_fc = r'''fc "?(.{2})"? create
                (.*)
            exit ?'''
    obj_egress = re.compile(p_egress)
    obj_ingress = re.compile(p_ingress)
    obj_fc = re.compile(p_fc)

    res_egress = obj_egress.search(config)
    res_ingress = obj_ingress.search(config)

    res_fc_egress = obj_fc.findall(res_egress.group())
    res_fc_ingress = obj_fc.findall(res_ingress.group())

    if res_fc_egress == [] or res_fc_ingress == []:
        err += 'fc策略检查->ERROR\n没有找到fc\n'
        return err

    if res_egress and res_ingress:
        for item in res_fc_egress:
            if item[1] != 'policer 1':
                err += 'sap-egress 3010 fc {} policer 策略错误\n'.format(item[0])

        for item in res_fc_ingress:
            if item[1] != 'policer 1':
                err += 'sap-ingress 3010 fc {} policer 策略错误\n'.format(item[0])
        
    else:
        err = 'sap-egress 3010 或者sap-ingress 3010没有找到\n'


    if err == '':
        err = 'fc策略检查 -> OK\n\n'
    return err

if __name__ == '__main__':
    with open('苏州金鸡湖') as f:
        config = f.read()
        res = fc_check(config)

        print(res)