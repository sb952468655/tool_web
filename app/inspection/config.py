# 跳板配置
g_tb_config = [
    ('202.102.19.253', '9527', 'alang1', 'jsdx!2O19#Ala!*'), # 电信
    ('202.102.19.254', '9527', 'alang1', 'jsdx!2O19#Ala!*'), # 电信教育网
    ('202.102.19.253', '9527', 'alang1', 'jsdx!2O19#Ala!*',  # CE
        ('telnet 59.43.5.135',
        'jiangsu', 'Noc@1304!@',
        'telnet 115.168.128.180 /source-interface loopback0',
        'jiangsu', 'Noc@1304!@'))
]

#超时配置
g_timeout = 60

#登陆关键字

g_login = [
    'Login:',
    'login:',
    'username:',
    'Username:',
    'UserName:'
]

g_password = [
    'password:',
    'Password:'
]

g_login_ok = [
    '7750',
    '7950',
    'CDMA'
]
