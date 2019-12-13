from . import db
from datetime import datetime, date

class AddressCollect(db.Model):
    '''地址采集表'''
    __tablename__ = 'address_collects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    ip_type = db.Column(db.String(64))
    function_type = db.Column(db.String(64)) #网络功能类型
    is_use = db.Column(db.String(64)) #是否已分配
    ip = db.Column(db.String(64))
    gateway = db.Column(db.String(64)) #网关
    mask = db.Column(db.String(64)) #掩码
    interface_name = db.Column(db.String(64)) #逻辑接口编号
    sap_id = db.Column(db.String(64))
    next_hop = db.Column(db.String(64)) #下一跳ip
    ies_vprn_id = db.Column(db.String(64)) #IES/VPRN编号
    vpn_rd = db.Column(db.String(64)) #VPN-RD
    vpn_rt = db.Column(db.String(64)) #VPN-RT
    description = db.Column(db.String(128)) #接口或用户描述
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def count_table():
        return AddressCollect.query.count()

    def __repr__(self):
        return '<AddressCollect %r>' % self.host_name


class CardPort1(db.Model):
    '''板卡端口统计表'''
    __tablename__ = 'card_port1'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    port = db.Column(db.String(64)) #端口号
    port_dk = db.Column(db.String(64)) #端口带宽（GE/10GE）
    admin_state = db.Column(db.String(64)) #Admin State
    link_state = db.Column(db.String(64)) #Link State
    port_state = db.Column(db.String(64)) #Port State
    cfg_mtu = db.Column(db.String(64)) #CfgMTU
    oper_mtu = db.Column(db.String(64)) #OperMTU
    lag = db.Column(db.String(64)) #LAG
    port_mode = db.Column(db.String(64)) #PortMode
    port_encp = db.Column(db.String(64)) #PortEncp
    port_type = db.Column(db.String(64)) #PortType
    c_qs_s_xfp_mdimdx = db.Column(db.String(64)) #C/QS/S/XFP/MDIMDX
    optical_power = db.Column(db.String(64)) #收光功率
    output_power = db.Column(db.String(64)) #发光功率
    optical_warn = db.Column(db.String(64)) #收光门限
    output_warn = db.Column(db.String(64)) #发光门限
    is_abnormal = db.Column(db.String(64)) #是否存在异常
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<CardPort1 %r>' % self.host_name


class LoadStatistic(db.Model):
    '''业务负荷统计表-按端口统计用户数量'''
    __tablename__ = 'card_port'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    port = db.Column(db.String(64)) #端口号
    port_dk = db.Column(db.String(64)) #端口带宽（GE/10GE）
    in_utilization = db.Column(db.String(64)) #带宽in利用率
    out_utilization = db.Column(db.String(64)) #带宽out利用率
    ies_3000_user_num = db.Column(db.String(64)) #ies 3000用户数量
    ies_3000_utilization = db.Column(db.String(64)) #ies 3000地址池利用率
    vprn_4015_user_num = db.Column(db.String(64)) #vprn 4015用户数量
    vprn_4015_utilization = db.Column(db.String(64)) #vprn 4015地址池利用率
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<LoadStatistic %r>' % self.host_name