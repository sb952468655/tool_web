import re
PAT = {
    'ies': r'(?s)(ies (\d{2,6})( name "\d{2,6}")? customer \d{1,2} create.*?\n {8}exit)',
    'group_interface': r'(?s)(group-interface "(.*?)" create.*?\n {16}exit)',
    'interface': r'(?s)( interface "(.*?)" create.*?\n {12}exit)',
    'subscriber_interface': r'(?s)(subscriber-interface "(.*?)" create.*?\n {12}exit)',
    'sap': r'(?s)(    sap (.*?)( capture-sap)? create.*?\n {12}exit)',
    'ipv4': r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}/\w{2}',
    'ipv6': r'(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}',
    'pim': r'(?s)(pim\n.*?\n {8}exit)',
    'address': r'address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d\d)',
    'address2': r'address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/\d\d',
    'gi-address': r'gi-address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    'subnet': r'(?s)(subnet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d\d) create\n.*?address-range (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))',
    'pool': r'(?s)( pool "(.*?)".*?create ?\n.*?\n {16}exit)',
    'address_range': r'address-range (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    'static_route': r'(?s)(static-route-entry (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w\w).*?\n {8}exit)',
    'description': r'description "(.*?)"\n',
    'prefix_list': r'(?s)(prefix-list "(ies2bgp|plToCR)"(\n {16}prefix \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\w\w (longer|exact))+\n {12}exit)'
}
#根据参数生成正则表达式
def generate_pat(_type, head, space_num, name=None):
    if _type == 0:
        pat = r'(?s)(%(head)s (\d{1,10})( name ".{1,30}")? customer \d{1,6} create.*?\n%(space)sexit)'
    elif _type == 1:
        pat = r'(?s)(%(head)s "(.*?)" create.*?\n%(space)sexit)'
    elif _type == 2:
        pat = r'(?s)(%(head)s\n.*?\n%(space)sexit)'
    elif _type == 3:
        pat = r'(?s)(echo "%(head)s"\n.*?\n%(space)sexit)'
    elif _type == 4:
        pat = r'(?s)(%(head)s (.*?) create.*?\n%(space)sexit)'
    elif _type == 5:
        pat = r'(?s)(%(head)s (.*?)\n.*?\n%(space)sexit)'

    pat = pat % {'head': head, 'space': ' '*space_num}
    if name != None and name != '':
            pat = pat.replace('(.*?)', '({})'.format(name))
            pat = pat.replace(r'\d{1,10}', name)

    return pat

class Business(object):
    def __init__(self, _type, name, config):
        self._type = _type
        self.name = name
        self.config = config

    def get_child(self):
        return self.get_interface() + self.get_subscriber_interface()

    def get_sap(self, port=None):
        pat_sap = PAT['sap']
        if port and port != '':
            pat_sap = pat_sap.replace('(.*?)', '({})'.format(port))
        res_sap = re.findall(pat_sap, self.config)

        return res_sap

    def get_interface(self):
        pat_inter = PAT['interface']
        res_inter = re.findall(pat_inter, self.config)
        return [ Interface(item[1], item[0]) for item in res_inter ]

    def get_subscriber_interface(self):
        pat_sub_inter = PAT['subscriber_interface']
        res_sub_inter = re.findall(pat_sub_inter, self.config)
        return [ SubscriberInterface(item[1], item[0]) for item in res_sub_inter ]

    def is_empty(self):
        return self.config.count('\n') == 1

class Ies(Business):
    def __init__(self, name, config):
        self.name = name
        self.config = config

    def get_child(self):
        return self.get_interface() + self.get_subscriber_interface()

    def get_interface(self):
        pat_inter = PAT['interface']
        res_inter = re.findall(pat_inter, self.config)
        return [ Interface(item[1], item[0]) for item in res_inter ]

    def get_subscriber_interface(self):
        pat_sub_inter = PAT['subscriber_interface']
        res_sub_inter = re.findall(pat_sub_inter, self.config)
        return [ SubscriberInterface(item[1], item[0]) for item in res_sub_inter ]

class Interface(Ies):
    def get_address(self):
        pat_address_v4 = PAT['ipv4']
        res_address_v4 = re.search(pat_address_v4, self.config)
        if res_address_v4:
            return res_address_v4.group()
        return None

    def get_sap(self, port=None):
        pat_sap = generate_pat(4, '    sap', 16, port)
        res_sap = re.findall(pat_sap, self.config)
        return [ item[1] for item in res_sap ]

    def get_group_interface(self):
        pat_group_interface = PAT['group_interface']
        res_group_interface = re.findall(pat_group_interface, self.config)
        return [ GroupInterface(item[1], item[0]) for item in res_group_interface ]

class SubscriberInterface(Ies):
    def get_child(self):
        pat_group_interface = PAT['group_interface']
        res_group_interface = re.findall(pat_group_interface, self.config)
        return [ GroupInterface(item[1], item[0]) for item in res_group_interface ]
        
class GroupInterface(SubscriberInterface):
    def get_sap(self, port=None):
        pat_sap = generate_pat(4, '    sap', 20, port)
        res_sap = re.findall(pat_sap, self.config)
        return [ item[1] for item in res_sap ]

class Config_7750(object):
    def __init__(self, config):
        self.config = config
    def get_ies(self, name=None):
        pat = generate_pat(0, 'ies', 8, name)
        ies = re.findall(pat, self.config)
        self.ies = ies[int(len(ies)/2):]
        return [ Ies(item[1], item[0]) for item in self.ies ]

    def get_child(self, name=None):
        pat = generate_pat(0, r'(\w{3,4})', 8, name)
        child = re.findall(pat, self.config)
        return [ Business(item[1], item[2], item[0]) for item in child ]

    def get_echo(self, name):
        pat = generate_pat(3, name, 4)
        res = re.search(pat, self.config)
        if res:
            return res.group()
        return None

    def from_ies_get_ip(self):
        obj_ipv4 = re.compile(PAT['ipv4'])
        obj_ipv6 = re.compile(PAT['ipv6'])

        ip = []
        for ies in self.ies:
            res_ipv4 = obj_ipv4.findall(ies[0])
            res_ipv6 = obj_ipv6.findall(ies[0])
            ip += res_ipv4
            ip += res_ipv6

        return ip
    
