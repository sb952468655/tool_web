import re

def admin_check(config):
    err = ''
    if 'no user "admin"' not in config:
        err = '存在user admin账号\n'

    if err == '':
        err = 'user admin检查 -> OK\n\n无 user admin账号\n\n'
    else:
        err = 'user admin检查 -> ERROR\n\n{}\n\n'.format(err)

    return ('user admin检查', err, '')