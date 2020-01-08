import unittest # 单元测试用例
import os
import re
import sys
from ftplib import FTP # 定义了FTP类，实现ftp上传和下载


class myFtp:
    ftp = FTP()
 
    def __init__(self, host, port=21):
        self.ftp.connect(host, port)
 
    def Login(self, user, passwd):
        self.ftp.login(user, passwd)
        print(self.ftp.welcome)
 
    def DownLoadFile(self, LocalFile, RemoteFile):# 下载当个文件
        file_handler = open(LocalFile, 'wb')
        print(file_handler)
        # self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)#接收服务器上文件并写入本地文件
        self.ftp.retrbinary('RETR ' + RemoteFile, file_handler.write)
        file_handler.close()
        return True
 
    def DownLoadFileTree(self, LocalDir, RemoteDir):  # 下载整个目录下的文件
        print("remoteDir:", RemoteDir)
        if not os.path.exists(LocalDir):
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        print("RemoteNames", RemoteNames)
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            print(self.ftp.nlst(file))
            if file.find(".") == -1:
                if not os.path.exists(Local):
                    os.makedirs(Local)
                self.DownLoadFileTree(Local, file)
            else:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def DownLoadFileFromName(self, file_name, LocalDir, RemoteDir):
        if not os.path.exists(LocalDir):
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        print("RemoteNames", RemoteNames)
        for file in RemoteNames:
            if file_name in file:
                Local = os.path.join(LocalDir, file)
                print(self.ftp.nlst(file))
                if file.find(".") == -1:
                    if not os.path.exists(Local):
                        os.makedirs(Local)
                    self.DownLoadFileTree(Local, file)
                else:
                    self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def close(self):
        self.ftp.quit()
 
if __name__ == "__main__":
    ftp = myFtp('211.138.102.229')
    ftp.Login('ftp-asb', 'Asb201730')
    ftp.DownLoadFileFromName('JSCZ-MC-CMNET-BAS06-LYND_7750', 'E:/PythonStudy/zuxun/log', '/home/ftp-asb/js/')  # 从目标目录下载到本地目录d盘
    ftp.close()