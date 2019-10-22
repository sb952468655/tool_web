import re

def rule3(config1, config2):
    err1 = ''
    err2 = ''

    p1 = r'''Subscriber Management Statistics for Port (.*)
Total  PPP Hosts                            ([\s0-9]{6})'''

    obj = re.compile(p1)
    res1 = obj.findall(config1)

    if res1 == []:
        err1 = '配置一Port没找到\n'
    else:
        for item in res1:
            if int(item[1]) > 0:
                temp = item[0].replace(r'(','\(')
                temp = temp.replace(r')','\)')
                p2 = '''Subscriber Management Statistics for Port %s
Total  PPP Hosts                            ([\s0-9]{6})''' % (temp)
                obj2 = re.compile(p2)
                res2 = obj2.search(config2)
                if res2:
                    if int(res2.group(1)) == 0:
                        err1 += '配置二 Port {} 与配置一不匹配\n'.format(item[0])
                else:
                    err1 += '配置二 Port {} 没找到\n'.format(item[0])

    if err1 == '':
        err1 = '● 文件对比检查 -> OK'
    else:
        err1 = '● 文件对比检查 -> ERROR\n\n' + err1

    return err1 + '\n\n' + err2