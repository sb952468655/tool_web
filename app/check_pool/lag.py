# encoding = utf-8
import re
from .config_7750 import generate_pat

def lag_check(config1, config2):
    '''lag检查
    1.检查config文件修改前后lag数量以及lag号是否一致
    2.检查修改后config文件的lag配置中是否缺少adapt-qos link和per-fp-ing-queuing'''

    err = ''
    p_lag_config = r'''(?s)(echo "LAG Configuration".*?echo "Redundancy Configuration")'''
    p_lag = generate_pat(5, 'lag', 4)


    res_lag_config_1 = re.search(p_lag_config, config1)
    res_lag_config_2 = re.search(p_lag_config, config2)

    if res_lag_config_1 and res_lag_config_2:
        res_lag_1 = re.findall(p_lag, res_lag_config_1.group())
        res_lag_2 = re.findall(p_lag, res_lag_config_2.group())

        lag_id_1 = [ item[1] for item in res_lag_1 ]
        lag_id_2 = [ item[1] for item in res_lag_2 ]

        #检查config文件修改前后lag数量以及lag号是否一致
        same_id = set(lag_id_1) & set(lag_id_2)

        for item in same_id:
            lag_id_1.remove(item)
            lag_id_2.remove(item)
        
        res_lag = lag_id_1 + lag_id_2

        if res_lag:
            err += '配置修改后lag数量或lag号不一致\n不一致lag号：\n{}\n'.format('\n'.join(res_lag))

        #检查修改后config文件的lag配置中是否缺少adapt-qos link和per-fp-ing-queuing
        for item in res_lag_2:
            if 'adapt-qos link' not in item[0]:
                err += '配置修改后lag {} 中缺少 adapt-qos link\n'.format(item[1])
            if 'per-fp-ing-queuing' not in item[0]:
                err += '配置修改后lag {} 中缺少 per-fp-ing-queuing\n'.format(item[1])
    else:
        err = '没有找到 LAG Configuration 配置，请检查\n'

    if err == '':
        err = 'lag检查 -> OK\n\n'
    else:
        err = 'lag检查 -> ERROR\n\n' + err


    return err


if __name__ == '__main__':
    config1 = open('沈浒路.log').read()
    config2 = open('苏州金鸡湖').read()

    res = lag_check(config1, config2)
    print(res)




