import re, os
from .common import get_host, get_log
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
        if item[10].startswith('GIGE'):
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
    p_card = r'(?s)(Card \w{1,2}\n.*?\n    Memory capacity)'
    p_slot_type_state = r'(\w{1,2}) {8,9}([\S]{5,20}) {20,40}(up|down) {2,4}(up|down)'
    # p_operational_state = r'Operational state             : (up|down)\n'
    p_serial_number = r'Serial number                 : (.*?)\n'
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
            '否'
        ))

    return card_detial_data

def get_card_statistic(config):
    '''card 统计'''
    card_statistic_data = []

    p_card_summary = r'(?s)(Card Summary\n={79}\n.*?\n=)'
    p_card_type = r'\w{1,2} {8,9}([\S]{5,20}) '

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

    return card_statistic_data


def get_mda_detail(config):
    '''mda 明细'''

    mda_detial_data = []
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
            '否'
        ))

    return mda_detial_data

def get_mda_statistic(config):
    '''mda 统计'''
    mda_statistic_data = []

    p_card_summary = r'(?s)(MDA Summary\n={79}\n.*?\n=)'
    p_card_type = r'\w{1,2} {4,5}\d {5}([\S]{5,20}) '

    host_name = get_host_name(config)
    host_ip = get_ip(config)

    if not host_name or not host_ip:
        return mda_statistic_data

    res_card_summary = re.search(p_card_summary, config)
    if res_card_summary:
        res_card_type = re.findall(p_card_type, res_card_summary.group())
        card_type_unique = list(set(res_card_type))
        for item in card_type_unique:
            mda_statistic_data.append((
                host_name,
                host_ip,
                item,
                res_card_type.count(item)
            ))

    return mda_statistic_data

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


