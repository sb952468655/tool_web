# encoding = utf-8
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.filedialog as filedialog
from address_pool_and_security import address_pool_and_security
from ipv6 import ipv6_check
from rule124 import rule124
from address import swfb, swbfb
from rule3 import rule3
from ftp import ftp_check
from fc import fc_check
from admin import admin_check
from jiou import jiou_check
from subnet import subnet_check
from global1 import global_check
from outside_pool import outside_pool_check
from all_check import all_check
from lag import lag_check

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.config = None
        self.config2 = None
        self.pack()
        self.create_win()

    def create_win(self):
        f1 = tk.Frame(self)
        self.kind = tk.StringVar(f1)
        self.kind2 = tk.StringVar(f1)
        self.kind.set("一键检查") # default value
        self.kind2.set("私网不发布") # default value
        # self.op = tk.OptionMenu(f1, self.kind, '地址池和业务安全配置检查', 'nat地址池及拨号配置检查', 'outside地址池检查')
        # self.op.pack(side=tk.LEFT)
        
        # self.op2 = tk.OptionMenu(f1, self.kind2, '私网不发布', '私网发布')
        # self.op2.pack(side=tk.LEFT)
        # self.op2.pack_forget()
        self.import1_btn = tk.Button(f1, text='完整配置导入', command=self.import_config)
        self.import1_btn.pack(side=tk.LEFT)
        self.import2_btn = tk.Button(f1, text='导入配置2', command=self.import2)
        self.check_btn = tk.Button(f1, text='地址池检查', command=self.check)
        self.check_btn.pack(side=tk.LEFT)
        f1.pack()

        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.res_text = tk.Text(self,width='80', borderwidth='2', yscrollcommand=self.scrollbar.set)
       
        self.res_text.pack()
        self.scrollbar.config(command=self.res_text.yview)


    # def check_op(self):
    #     if self.kind.get() == 'nat地址池及拨号配置检查':
    #         self.op2.pack(side=tk.LEFT)
    #     elif self.kind.get() == '文件对比功能':
    #         self.import2_btn.pack(side=tk.LEFT)
    #     elif self.kind.get() == 'lag检查':
    #         self.import2_btn.pack(side=tk.LEFT)

    def import_config(self):
        self.filename = filedialog.askopenfilename()
        self.res_text.delete(0.0,tk.END)
        #读取配置
        f = open(self.filename)
        self.config = f.read()
        f.close()

    def import2(self):
        self.filename = filedialog.askopenfilename()
        self.res_text.delete(0.0,tk.END)
        #读取配置
        f = open(self.filename)
        self.config2 = f.read()
        f.close()

    def check(self):
        if self.config == None:
            msg.showerror('错误', '配置未导入')
            return
        self.res_text.delete(0.0,tk.END)
        if self.kind.get() == '地址池和业务安全配置检查':
            res = address_pool_and_security(self.config)
            self.res_text.insert(tk.END, res)
            
        elif self.kind.get() == 'ipv6检查':
            self.res_text.insert(tk.END, ipv6_check(self.config))
        elif self.kind.get() == 'ipv6配置规范':
            self.res_text.insert(tk.END, rule124(self.config))
        elif self.kind.get() == 'nat地址池及拨号配置检查':
            err = ''
            if self.kind2.get() == '私网不发布':
                err = swbfb(self.config)
            else:
                err = swfb(self.config)
            self.res_text.insert(tk.END, err)
        elif self.kind.get() == '文件对比功能':
            if self.config2 == None:
                msg.showerror('错误', '配置2未导入')
                return
            self.res_text.insert(tk.END, rule3(self.config, self.config2))
        elif self.kind.get() == 'ftp检查':
            self.res_text.insert(tk.END, ftp_check(self.config))
        elif self.kind.get() == 'fc策略检查':
            self.res_text.insert(tk.END, fc_check(self.config))
        elif self.kind.get() == 'user admin检查':
            self.res_text.insert(tk.END, admin_check(self.config))
        elif self.kind.get() == 'iptv主备接口地址校验':
            self.res_text.insert(tk.END, jiou_check(self.config))
        elif self.kind.get() == 'iptv的subnet地址校验':
            self.res_text.insert(tk.END, subnet_check(self.config))
        elif self.kind.get() == 'iptv策略校验':
            self.res_text.insert(tk.END, global_check(self.config))
        elif self.kind.get() == 'outside地址池检查':
            self.res_text.insert(tk.END, outside_pool_check(self.config))
        elif self.kind.get() == 'lag检查':
            if self.config2 == None:
                msg.showerror('错误', '配置2未导入')
                return
            self.res_text.insert(tk.END, lag_check(self.config, self.config2))
        elif self.kind.get() == '一键检查':
            self.res_text.insert(tk.END, all_check(self.config))

        self.import2_btn.pack_forget()

root = tk.Tk()
root.geometry('500x300+500+200')
root.title('电信地址池配置检查_V_1.0.0')
myapp = App(master=root)
myapp.mainloop()