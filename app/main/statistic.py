import re
from .report import get_port, get_ip

def get_statistic_data(config):
    '''获取业务负荷数据'''

    statistic_data = []
    #按端口统计用户数量

    p_utilization = r'Utilization \(300 seconds\) {24,26}(\d{1,3}\.\d{2})% {16,18}(\d{1,3}\.\d{2})%'

    res_utilization = re.findall(p_utilization, config)
    res_port = get_port(config)
    res_ip = get_ip(config)

    #ies 3000 用户数
    p_subscriber_management_statistics = r'Subscriber Management Statistics for Port (\d{1,2}/\d{1,2}/\d{1,2})'

    p_ppp = r'IPv4   PPP Hosts        - IPCP {14,19}(\d{1,5}) '
    res_subscriber_management_statistics = re.findall(p_subscriber_management_statistics, config)
    res_ppp = re.findall(p_ppp, config)

    for i, item in enumerate(res_port):
        
        #判断ge或10ge
        port_type = ''
        if item[-1].startswith('10'):
            port_type = '10GE'
        elif item[-1].startswith('GIGE'):
            port_type = 'GE'
        else:
            continue

        #查找ies 3000 用户数
        user_num = ''
        index = -1
        try:
            index = res_subscriber_management_statistics.index(item[1])
        except ValueError:
            print('{} is not in list'.format(item[1]))
        
        if index != -1:
            user_num = res_ppp[index]

        #地址池总数
        pool_num = ''
        p_provisioned_addresses = r'Provisioned Addresses {3,8}(\d{1,6}) '
        res_provisioned_addresses = re.search(p_provisioned_addresses, config)
        if res_provisioned_addresses:
            pool_num = res_provisioned_addresses.group(1)

        utilization = ''
        if user_num and pool_num:
            utilization = str(round(int(user_num)/int(pool_num),2) * 10) + ' %'

        #vprn 4015用户数，地址池利用率
        #获取4015对应lag的用户数

        p_4015_lag = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} {2,9}\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2} lag-(\d{1,3}):4015.0.*?DHCP '

        res_4015_lag = re.findall(p_4015_lag, config)

        lag_num = []
        lag_set = set(res_4015_lag)
        for item1 in lag_set:
            lag_num.append((item1, res_4015_lag.count(item1)))

        #找到lag下绑定的端口
        p_lag_port = r'''(?s)((\d{1,3})\((e|d)\) {16,18}up             (up|down)[^\(\)]*?
(       (\d{1,2}/\d{1,2}/\d{1,2}) {7,10}up    active   (up|down) .*?\n)+)'''
        p_port = r'(\d{1,2}/\d{1,2}/\d{1,2})'

        res_lag_port = re.findall(p_lag_port, config)
        lag_port = []

        for item1 in res_lag_port:
            res_port = re.findall(p_port, item1[0])
            lag_port.append((item1[1], res_port))


        #计算每个端口的用户数
        port_user_num = []
        for item1 in lag_port:
            for item2 in lag_num:
                if item1[0] == item2[0]:
                    for item3 in item1[1]:
                        port_user_num.append((item3, int(int(item2[1])/len(item1[1]))))

        user_num_4015 = ''
        for item1 in port_user_num:
            if item1[0] == item[1]:
                user_num_4015 = item1[1]

        #查找4015地址池利用率
        p_stable_leases = r'(?s)(Stable Leases *?(\d{1,10}) *?(\d{1,10}).*?Provisioned Addresses *?(\d{1,10}) )'
        res_stable_leases = re.search(p_stable_leases, config)
        lyl_4015 = ''
        if res_stable_leases:
            lyl_4015 = str(round(int(res_stable_leases.group(3))/int(res_stable_leases.group(4)),2) * 100) + ' %'
        statistic_data.append(
            [item[0], item[1], res_ip, port_type, res_utilization[i][0], res_utilization[i][1], user_num, utilization, user_num_4015, lyl_4015]
        )

    return statistic_data