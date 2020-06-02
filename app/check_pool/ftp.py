def ftp_check(config):
    err = ''
    if 'ftp-server' in config:
        err = 'ftp服务被打开'
    else:
        err = 'ftp检查通过'

    return ('ftp检查', err, '')