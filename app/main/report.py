import re, os

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


def get_port_detail(config):
    '''show port detail'''

def get_lag(config):
    '''show lag'''

def get_lag_detail(config):
    '''show lag detail'''

def get_lag_des(config):
    '''show lag des'''


def get_router_interface(config):
    '''show router interface'''

def get_router_arp(config):
    '''show router arp'''

def get_router_dhcp_servers(config):
    '''show router dhcp servers'''

def get_router_dhcp_local_dhcp_server(config):
    '''show router dhcp local-dhcp-server "dhcp-s1" summary'''

def get_admin_display_config(config):
    '''show admin display-config'''

def get_show_service(config):
    '''show show service service-using ies'''

def get_service_using_vprn(config):
    '''show service service-using vprn '''

def get_service_sap_using(config):
    '''show service sap-using '''

def get_lag_description(config):
    '''show lag description '''

def get_device_name(config):
    '''获取设备名称'''
    p_device = r'(\*?(A|B):.*?7750#)'

    res_device = re.search(p_device, config)
    if res_device:
        return res_device.group()
    else:
        return None


