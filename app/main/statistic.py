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
        statistic_data.append(
            [item[0], item[1], res_ip, port_type, res_utilization[i][0], res_utilization[i][1], user_num, utilization, '', '']
        )

    return statistic_data