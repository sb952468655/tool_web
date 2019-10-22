def ftp_check(config):
    err = ''
    if 'ftp-server' in config:
        err = '● FTP检查 -> ERROR\n\nftp服务被打开\n\n'
    else:
        err = '● FTP检查 -> OK\n\n'
    return err