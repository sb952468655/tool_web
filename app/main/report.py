import re, os
from .common import get_host, get_log
from .config_7750 import *
def get_report_data(config):
    '''从配置获取报表数据'''
    res_port = get_port(config)

    return res_port

def get_port(config):
    '''show port'''

    '''2/2/6         Down  No   Down    9212 9212    - netw null xcme   GIGE-LX  20KM'''
    p_port = r'''(\d{1,2}/\d{1,2}/\d{1,2}) {6,9}(Up|Down) {2,4}(Yes|No) {2,3}(Up|Down) {4,6}(\d{4}) (\d{4}) {2,4}(-|\d{1,3}) (accs|netw) (null|qinq) (xgige|xcme) {2,3}((10GBASE-LR|10GBASE-ER|GIGE-LX|MDX GIGE-T |MDI GIGE-T )( {2}(\d{2}KM|\*))?)?'''
    # p_port = r'''(\d{1,2}/\d{1,2}/\d{1,2}) {6,9}(Up|Down) {2,4}(Yes|No) {2,3}(Up|Down) {4,6}(\d{4}) (\d{4}) {2,4}(-|\d{1,3}) (accs|netw) (null|qinq) (xgige|xcme) {2,3}((10GBASE-（L|E）R|GIGE-LX|MDX GIGE-T |MDI GIGE-T )( {2}(\d{2}KM|\*))?)?'''
    port_data = []
    res = re.findall(p_port, config)
    device_name = get_device_name(config)

    for item in res:
        row = []
        row.append(device_name)
        row.append(item[0])
        row.append(item[1])
        row.append(item[2])
        row.append(item[3])
        row.append(item[4])
        row.append(item[5])
        row.append(item[6])
        row.append(item[7])
        row.append(item[8])
        row.append(item[9])
        row.append(item[10])

        port_data.append(row)

    return port_data

def get_port_statistic(config):
    '''端口统计'''

    port_statistic_data = []
    ge_num = 0
    ge_10_num = 0
    ge_used_num = 0
    ge_free_num = 0
    ge_10_used_num = 0
    ge_10_free_num = 0

    p_port = r'''(\d{1,2}/\d{1,2}/\d{1,2}) {6,9}(Up|Down) {2,4}(Yes|No) {2,3}(Up|Down) {4,6}(\d{4}) (\d{4}) {2,4}(-|\d{1,3}) (accs|netw) (null|qinq) (xgige|xcme) {2,3}((10GBASE-LR|10GBASE-ER|GIGE-LX|MDX GIGE-T |MDI GIGE-T )( {2}(\d{2}KM|\*))?)?'''
    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return port_statistic_data

    res_port = re.findall(p_port, config)
    for item in res_port:
        if item[10].startswith('10'):
            ge_10_num += 1
            if item[1] == 'Up' and item[2] == 'Yes' and item[3] == 'Up':
                ge_10_used_num += 1
            else:
                ge_10_free_num += 1
        elif 'GIGE' in item[10]:
            ge_num += 1
            if item[1] == 'Up' and item[2] == 'Yes' and item[3] == 'Up':
                ge_used_num += 1
            else:
                ge_free_num += 1


    port_statistic_data.append((
        host_name,
        host_ip,
        '10GE',
        ge_10_num,
        ge_10_used_num,
        ge_10_free_num
    ))

    port_statistic_data.append((
        host_name,
        host_ip,
        'GE',
        ge_num,
        ge_used_num,
        ge_free_num
    ))

    return port_statistic_data

def get_port_ggl(config):
    p_output = r'Tx Output Power \(dBm\) {8,10}([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?\nRx Optical Power \(avg dBm\) {3,5}([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?([\-\.0-9]{4,6}).*?\n'
    # p_output2 = r'Tx Output Power \(dBm\) {8,10}([\-\.0-9]{4,6}).*?\nRx Optical Power \(avg dBm\) {3,5}([\-\.0-9]{4,6}).*? '
    # p_optical = r'Rx Optical Power \(avg dBm\) {3,4}([\-\.0-9]{3,4}).*?([\-\.0-9]{3,4}).*?[\-\.0-9]{3,4}.*?[\-\.0-9]{3,4}.*?[\-\.0-9]{3,4} '

    res_output = re.findall(p_output, config)
    # res_optical = re.findall(p_optical, config)

    # print(len(res_output))
    # print(len(res_optical))

    return res_output

def get_ip(config):

    p_ip = r'''interface "system"\n {12}address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/32'''
    res_ip = re.search(p_ip, config)
    if res_ip:
        return res_ip.group(1)
    else:
        return ''

def get_host_list(city):
    '''设备清单统计'''

    host_list_data = []
    p_host_name = r'System Name            : (.*?)\n'
    p_version = r'System Version         : (.*?)\n'
    p_start_time = r' Time of last boot               : (.*?)\n'
    p_save_time = r'Time Last Saved        : (.*?)\n'

    host_list = get_host(city)
    for i in host_list:
        config = get_log(city, i)
        if not config:
            continue

        res_host_name = re.search(p_host_name, config)
        if not res_host_name:
            host_name = ''
        else:
            host_name = res_host_name.group(1)
        host_ip = get_ip(config)
        res_version = re.search(p_version, config)
        if not res_version:
            version = ''
        else:
            version = res_version.group(1)
        res_start_time = re.search(p_start_time, config)
        if not res_version:
            start_time = ''
        else:
            start_time = res_start_time.group(1)

        res_save_time = re.search(p_save_time, config)
        if not res_save_time:
            save_time = ''
        else:
            save_time = res_save_time.group(1)
        if host_name:
            host_list_data.append((
                host_name,
                host_ip,
                version,
                start_time,
                save_time
            ))

    return host_list_data

def get_card_detail(config):
    '''card 明细'''

    card_detial_data = []
    is_abnormal = '否'
    p_card = r'(?s)(Card \w{1,2}\n.*?\n    Memory capacity)'
    p_slot_type_state = r'(\w{1,2}) {8,9}([\S]{4,20}) {20,40}(up|down) {2,4}(up|down)'
    # p_operational_state = r'Operational state             : (up|down)\n'
    p_serial_number = r'Serial number                 : (.{11})\n'
    p_time_of_last_boot = r'Time of last boot             : (.*?)\n'
    p_temperature = r'Temperature                   : (.*?)\n'
    p_temperature_threshold = r'Temperature threshold         : (.*?)\n'

    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return card_detial_data

    res_card = re.findall(p_card, config)
    for item in res_card:
        res_slot_type_state = re.search(p_slot_type_state, item)
        if res_slot_type_state:
            slot = res_slot_type_state.group(1)
            card_type = res_slot_type_state.group(2)
            admin_state = res_slot_type_state.group(3)
            operational_state = res_slot_type_state.group(4)
        else:
            continue

        res_serial_number = re.search(p_serial_number, item)
        if res_serial_number:
            serial_number = res_serial_number.group(1)
        else:
            continue

        res_time_of_last_boot = re.search(p_time_of_last_boot, item)
        if res_time_of_last_boot:
            time_of_last_boot = res_time_of_last_boot.group(1)
        else:
            continue

        res_temperature_threshold = re.search(p_temperature_threshold, item)
        if res_temperature_threshold:
            temperature_threshold = res_temperature_threshold.group(1)
        else:
            continue

        res_temperature = re.search(p_temperature, item)
        if res_temperature:
            temperature = res_temperature.group(1)
        else:
            continue

        if admin_state != 'up' or operational_state != 'up':
            is_abnormal = '是'
        card_detial_data.append((
            host_name,
            host_ip,
            slot,
            card_type,
            admin_state,
            operational_state,
            serial_number,
            time_of_last_boot,
            temperature,
            temperature_threshold,
            is_abnormal
        ))

    sfm_data = get_sfm_detail(config)

    return card_detial_data + sfm_data

def get_card_statistic(config):
    '''card 统计'''
    card_statistic_data = []

    p_card_summary = r'(?s)(Card Summary\n={79}\n.*?\n=)'
    p_card_type = r'\w{1,2} {8,9}([\S]{4,20}) *?up    up'


    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return card_statistic_data

    res_card_summary = re.search(p_card_summary, config)
    if res_card_summary:
        res_card_type = re.findall(p_card_type, res_card_summary.group())
        card_type_unique = list(set(res_card_type))
        for item in card_type_unique:
            card_statistic_data.append((
                host_name,
                host_ip,
                item,
                res_card_type.count(item)
            ))

    sfm = get_sfm(config)

    return card_statistic_data + sfm

def get_sfm(config):
    '''sfm统计'''

    sfm_data = []
    sfm_list = []
    p_card_type = r'\w{1,2} {8,9}([\S]{4,20}) '
    p_fabric = r'(?s)(Fabric \d{1,2}\n={79}.*?\n={79})'

    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return sfm_data

    res_sfm = re.findall(p_fabric, config)
    for i in res_sfm:
        res_card_type = re.search(p_card_type, i)
        if res_card_type:
            sfm_list.append(res_card_type.group(1))

    sfm_unique = list(set(sfm_list))
    for item in sfm_unique:
            sfm_data.append((
                host_name,
                host_ip,
                item,
                sfm_list.count(item)
            ))

    return sfm_data


def get_sfm_detail(config):
    '''sfm明细'''

    sfm_detial_data = []
    is_abnormal = '否'
    p_fabric = r'(?s)(Fabric \d{1,2}\n={79}.*?\n={79})'

    p_slot_type_state = r'(\w{1,2}) {8,9}([\S]{4,20}) {20,40}(up|down) {2,4}(up|down)'
    p_serial_number = r'Serial number                 : (.*?)\n'
    p_time_of_last_boot = r'Time of last boot             : (.*?)\n'
    p_temperature = r'Temperature                   : (.*?)\n'
    p_temperature_threshold = r'Temperature threshold         : (.*?)\n'

    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return sfm_detial_data

    res_sfm = re.findall(p_fabric, config)
    for item in res_sfm:
        res_slot_type_state = re.search(p_slot_type_state, item)
        if res_slot_type_state:
            slot = res_slot_type_state.group(1)
            card_type = res_slot_type_state.group(2)
            admin_state = res_slot_type_state.group(3)
            operational_state = res_slot_type_state.group(4)
        else:
            continue

        res_serial_number = re.search(p_serial_number, item)
        if res_serial_number:
            serial_number = res_serial_number.group(1)
        else:
            continue

        res_time_of_last_boot = re.search(p_time_of_last_boot, item)
        if res_time_of_last_boot:
            time_of_last_boot = res_time_of_last_boot.group(1)
        else:
            continue

        res_temperature_threshold = re.search(p_temperature_threshold, item)
        if res_temperature_threshold:
            temperature_threshold = res_temperature_threshold.group(1)
        else:
            continue

        res_temperature = re.search(p_temperature, item)
        if res_temperature:
            temperature = res_temperature.group(1)
        else:
            continue
        
        if admin_state != 'up' or operational_state != 'up':
            is_abnormal = '是'
        sfm_detial_data.append((
            host_name,
            host_ip,
            slot,
            card_type,
            admin_state,
            operational_state,
            serial_number,
            time_of_last_boot,
            temperature,
            temperature_threshold,
            is_abnormal
        ))

    return sfm_detial_data

def get_mda_detail(config):
    '''mda 明细'''

    mda_detial_data = []
    is_abnormal = '否'
    p_card = r'(?s)(MDA \d{1,2}/\d detail\n.*?\n    Firmware version)'
    p_slot_type_state = r'(\w{1,2}| ) {4,5}(\d) {5}([\S]{5,20}) {20,40}(up|down) {6,8}(up|down)'
    p_serial_number = r'Serial number                 : (.*?)\n'
    p_time_of_last_boot = r'Time of last boot             : (.*?)\n'
    p_temperature = r'Temperature                   : (.*?)\n'
    p_temperature_threshold = r'Temperature threshold         : (.*?)\n'

    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return mda_detial_data

    res_card = re.findall(p_card, config)
    for item in res_card:
        res_slot_type_state = re.search(p_slot_type_state, item)
        if res_slot_type_state:
            slot = res_slot_type_state.group(1)
            mda = res_slot_type_state.group(2)
            card_type = res_slot_type_state.group(3)
            admin_state = res_slot_type_state.group(4)
            operational_state = res_slot_type_state.group(5)
        else:
            continue

        res_serial_number = re.search(p_serial_number, item)
        if res_serial_number:
            serial_number = res_serial_number.group(1)
        else:
            continue

        res_time_of_last_boot = re.search(p_time_of_last_boot, item)
        if res_time_of_last_boot:
            time_of_last_boot = res_time_of_last_boot.group(1)
        else:
            continue

        res_temperature_threshold = re.search(p_temperature_threshold, item)
        if res_temperature_threshold:
            temperature_threshold = res_temperature_threshold.group(1)
        else:
            continue

        res_temperature = re.search(p_temperature, item)
        if res_temperature:
            temperature = res_temperature.group(1)
        else:
            continue

        if admin_state != 'up' or operational_state != 'up':
            is_abnormal = '是'
        mda_detial_data.append((
            host_name,
            host_ip,
            slot,
            mda,
            card_type,
            admin_state,
            operational_state,
            serial_number,
            time_of_last_boot,
            temperature,
            temperature_threshold,
            is_abnormal
        ))

    return mda_detial_data

def get_mda_statistic(config):
    '''mda 统计'''
    mda_statistic_data = []

    p_card_summary = r'(?s)(MDA Summary\n={79}\n.*?\n=)'
    p_card_type = r'(\w{1,2}| {1,2}) {4,5}\d {5}([\S]{5,20}) '

    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return mda_statistic_data

    res_card_summary = re.search(p_card_summary, config)
    if res_card_summary:
        res_card_type = re.findall(p_card_type, res_card_summary.group())
        res_card_type = [i[1] for i in res_card_type]
        card_type_unique = list(set(res_card_type))
        for item in card_type_unique:
            mda_statistic_data.append((
                host_name,
                host_ip,
                item,
                res_card_type.count(item)
            ))

    return mda_statistic_data

def get_install_base(config):
    '''获取install_base数据'''

    host_type = ''
    host_model = ''
    version = ''
    note = ''

    p_system_type = r'System Type            : (7\d50) ([A-Z]{2,4})-(\d{2})'
    p_system_version = r'System Version         : C-((\d{1,2})\.\d\.R\d-?\d?)'

    res_system_type = re.search(p_system_type, config)
    res_system_version = re.search(p_system_version, config)

    if res_system_type:
        host_type = res_system_type.group(1) + ' ' + res_system_type.group(2)
        host_model = res_system_type.group(2) + '-' + res_system_type.group(3)

    if res_system_version:
        t = res_system_version.groups()
        version = 'R' + res_system_version.group(2)
        note = res_system_version.group(1)


    return (host_type, host_model, version, note)

def get_netflow(config):
    '''获取重要网络流量数据'''

    ge_10_num = 0
    ge_10_used_num = 0
    ge_100_num = 0
    ge_100_used_num = 0
    port_utilization_10g = 0
    port_utilization_100g = 0

    p_interface_table = r'(?s)Interface Table \(Router: Base\)\n={79}.*?\n={79}'
    p_port = r'Up        Up/Up       Network (\d{1,2}/\d{1,2}/\d{1,2})'
    p_ethernet_interface = r'(?s)Interface {10}: (\d{1,2}/\d{1,2}/\d{1,2}) {19,22}Oper Speed.*?Utilization \(300 seconds\) {24,26}(\d{1,3}\.\d{2})% {16,18}(\d{1,3}\.\d{2})%'

    res_interface_table = re.search(p_interface_table, config)
    if res_interface_table:
        res_port = re.findall(p_port, res_interface_table.group())

        res_ethernet_interface = re.findall(p_ethernet_interface, config)
        max_utilization = 0.00
        for i in res_ethernet_interface:
            if i[0] in res_port:
                if float(i[1]) > max_utilization:
                    max_utilization = float(i[1])
                if float(i[2]) > max_utilization:
                    max_utilization = float(i[2])

        
    #采集10GE, 100GE 端口使用情况
    p_port_info = r'''(\d{1,2}/\d{1,2}/\d{1,2}) {6,9}(Up|Down) {2,4}(Yes|No) {2,3}(Up|Down) {4,6}(\d{4}) (\d{4}) {2,4}(-|\d{1,3}) (accs|netw) (null|qinq) (xgige|xcme) {2,3}((10GBASE-LR|10GBASE-ER|100GBASE-LR4\*)( {2}(\d{2}KM|\*))?)?'''
    res_port = re.findall(p_port_info, config)
    for item in res_port:
        if item[10].startswith('100'):
            ge_100_num += 1
            if item[1] == 'Up' and item[2] == 'Yes' and item[3] == 'Up':
                ge_100_used_num += 1
        else:
            ge_10_num += 1
            if item[1] == 'Up' and item[2] == 'Yes' and item[3] == 'Up':
                ge_10_used_num += 1

    if ge_10_num > 0:
        port_utilization_10g = round(ge_10_used_num * 100/ge_10_num, 2)
    if ge_100_num > 0:
        port_utilization_100g = round(ge_100_used_num * 100/ge_100_num, 2)

    return (ge_10_num, str(port_utilization_10g)+'%', ge_100_num, str(port_utilization_100g)+'%', str(max_utilization)+'%')

def get_service_statistic(config):
    '''获取业务类型统计数据'''

    port_lag = {}
    data = []
    p_lag_configuration = r'(?s)echo "LAG Configuration"\n#-{50}.*?\n#-{50}'
    p_router = r'(?s)echo "Router \(Network Side\) Configuration"\n#-{50}.*?\n#-{50}'
    p_lag = generate_pat(5, 'lag', 4)
    p_port = r'port (\d{1,2}/\d{1,2}/\d{1,2})'
    p_router_inter = r'(?s)(interface "(.*?)".*?\n {8}exit)'
    p_port_configuration = r'(?s)echo "Port Configuration"\n#-{50}.*?\n#-{50}'
    p_description = r'description "(.*?)"'

    res_port_configuration = re.search(p_port_configuration, config)
    if not res_port_configuration:
        print('没有找到Port Configuration')
        return []

    res_lag_configuration = re.search(p_lag_configuration, config)
    if res_lag_configuration:
        res_lag = re.findall(p_lag, res_lag_configuration.group())
        for i in res_lag:
            port_data = []
            res_port = re.findall(p_port, i[0])
            for j in res_port:
                p_port_config = r'(?s) port %s.*?\n {4}exit' % j
                description = ''
                res_port_config = re.search(p_port_config, res_port_configuration.group())
                if res_port_config:
                    res_description = re.search(p_description, res_port_config.group())
                    if res_description:
                        description = res_description.group(1)
                port_data.append((j, description))

            port_lag[i[1]] = port_data

    config_7750 = Config_7750(config)
    service = config_7750.get_child()

    #检查vpls
    for i in service:
        if i._type == 'vpls':
            res_sap = i.get_sap()
            for j in res_sap:
                res_lag_x = re.search(r'lag-(\d{1,3})', j[1])
                if res_lag_x and res_lag_x.group(1) in port_lag:
                    for k in port_lag[res_lag_x.group(1)]:
                        data.append((k[0], k[1], res_lag_x.group(1), j[1],'n/a', i._type, i.name))
        elif i._type == 'vprn' or i._type == 'ies':
            res_interface = i.get_interface()
            for j in res_interface:
                res_sap = j.get_sap()
                for k in res_sap:
                    res_lag_x = re.search(r'lag-(\d{1,3})', k)
                    if res_lag_x and res_lag_x.group(1) in port_lag:
                        for o in port_lag[res_lag_x.group(1)]:
                            data.append(( o[0], o[1], res_lag_x.group(1), k,j.name, i._type, i.name))

            res_sub_inter = i.get_subscriber_interface()
            for j in res_sub_inter:
                res_group_inter = j.get_child()
                for k in res_group_inter:
                    res_sap = k.get_sap()
                    for o in res_sap:
                        res_lag_x = re.search(r'lag-(\d{1,3})', o)
                        if res_lag_x and res_lag_x.group(1) in port_lag:
                            for p in port_lag[res_lag_x.group(1)]:
                                data.append((p[0], p[1], res_lag_x.group(1), o,k.name, i._type, i.name))

    #检查基本配置
    res_router = re.search(p_router, config)
    if res_router:
        res_inter = re.findall(p_router_inter, res_router.group())
        for i in res_inter:
            res_port = re.search(p_port, i[0])
            if res_port:
                description = ''
                p_port_config = r'(?s) port %s.*?\n {4}exit' % res_port.group(1)
                res_port_config = re.search(p_port_config, res_port_configuration.group())
                if res_port_config:
                    res_description = re.search(p_description, res_port_config.group())
                    if res_description:
                        description = res_description.group(1)
                data.append((res_port.group(1), description, 'n/a', res_port.group(1), i[1], 'base', 'n/a'))

    return data
def get_host_name(config):
    '''获取设备名称'''

    p_host_name = r'System Name            : (.*?)\n'
    res_host_name = re.search(p_host_name, config)
    if not res_host_name:
        host_name = get_device_name(config)
    else:
        host_name = res_host_name.group(1)

    return host_name


def get_device_name(config):
    '''获取设备名称'''
    p_device = r'\*?(A|B):(.*?7750)#'

    res_device = re.search(p_device, config)
    if res_device:
        return res_device.group(2)
    else:
        return None


