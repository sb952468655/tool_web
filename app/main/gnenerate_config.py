import re
from .config import g_config_model, g_port_10ge, g_port_ge
def parse_model(model_text):
    '''解析模板'''

    titles = []
    p_symbol = r'(@.*?@|%.*?%|\$.*?\$)'

    res = re.findall(p_symbol, model_text)
    unique = []
    for item in res:
        if item not in unique:
            unique.append(item)

    for item in unique:
        if item[0] == '@':
            if '10ge_port_id' in item or '10ge_port_description' in item or 'ge_port_id' in item or 'ge_port_description' in item:
                titles.append('@ ' + item[1:-1] + ' (多个用;隔开)')
            else:
                titles.append('@ ' + item[1:-1])
        elif item[0] == '%':
            titles.append('% ' + item[1:-1] + ' (多个用;隔开)')
        elif item[0] == '$':
            titles.append('$ ' + item[1:-1] + ' 是否保留(y/n)?')
        
    #特殊处理
    #server name
    # res_server = re.search(r'server "(.*?)"', self.model_text)
    # if res_server:
    #     self.model_form.formLayout_2.addRow(QLabel('server_name'), QLineEdit(res_server.group(1)))

    return titles


def generate_config(model_text, inputs):
    '''根据用户输入的参数生成配置'''

    config = model_text
    s10ge_ports = []
    s10ge_ports_description = []
    for item in inputs:
        if item[0].startswith('@ '):

            if('10ge_port_id' in item[0] or 'ge_port_id' in item[0]):
                s10ge_ports = item[1].split(';')
                continue
            elif('10ge_port_description' in item[0]):
                s10ge_ports_description = item[1].split(';')
                
                temp = ''
                for i, item in enumerate(s10ge_ports):
                    temp += g_port_10ge.replace('@10ge_port_id@', item).replace('@10ge_port_description@', s10ge_ports_description[i])+'\n    '
                config = config.replace(g_port_10ge, temp)
            elif('ge_port_description' in item[0]):
                s10ge_ports_description = item[1].split(';')
                
                temp = ''
                for i, item in enumerate(s10ge_ports):
                    temp += g_port_ge.replace('@ge_port_id@', item).replace('@ge_port_description@', s10ge_ports_description[i])+'\n    '
                config = config.replace(g_port_ge, temp)
            else:
                config = config.replace('@'+item[0].split(' ')[1]+'@', item[1])
        elif(item[0].startswith('% ')):
            port_text = ''
            r = item[0].split('_')
            ips = item[1].split(';')
            for i in ips:
                port_text += 'port {}\n{}'.format(i, ' '* int(r[-2]))
                port_text = port_text
            port_text = port_text.strip()

            config = config.replace('%'+item[0].split(' ')[1]+'%', port_text)
        elif(item[0].startswith('$ ')):
            t = item[0].replace('$ ', '')
            t = t.replace(' 是否保留(y/n)?', '')
            if item[1] in ['y', 'Y']:
                config = config.replace('$' + t + '$', t)
            else:
                config = config.replace('$' + t + '$', '')

        # elif(item[0] == 'server_name'):
        #     res_server = re.findall(r'server "(.*?)"', model_text)
        #     for i in res_server:
        #         if 'ipv6' in i:
        #             config = config.replace('server "{}"'.format(i), 'server "{}-ipv6"'.format(item[1]))
        #         else:
        #             config = config.replace('server "{}"'.format(i), 'server "{}"'.format(item[1]))


    return config
