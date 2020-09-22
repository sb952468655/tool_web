from datetime import datetime, date
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from flask_login import UserMixin

class AddressCollect(db.Model):
    '''地址采集表'''

    __tablename__ = 'address_collects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
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
    '''端口明细表'''

    __tablename__ = 'card_port1'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
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

class PortStatistic(db.Model):
    '''端口统计表'''

    __tablename__ = 'port_statistic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    port_type = db.Column(db.String(64)) #端口类型
    port_num = db.Column(db.String(64)) #端口数量
    used_num = db.Column(db.String(64)) #已使用数量
    unused_num = db.Column(db.String(64)) #未使用数量
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<PortStatistic %r>' % self.host_name


class CardDetail(db.Model):
    '''Card明细表'''

    __tablename__ = 'card_detail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    slot = db.Column(db.String(64)) #槽位
    card_type = db.Column(db.String(64)) #板卡类型
    admin_state = db.Column(db.String(64)) #admin状态
    operational_state = db.Column(db.String(64)) #operational状态
    serial_number = db.Column(db.String(64)) #串口数量
    time_of_last_boot = db.Column(db.String(64)) #上次启动时间
    temperature = db.Column(db.String(64)) #温度
    temperature_threshold = db.Column(db.String(64)) #温度阈值
    is_abnormal = db.Column(db.String(64)) #是否异常
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<CardDetail %r>' % self.host_name

class CardStatistic(db.Model):
    '''Card统计表'''

    __tablename__ = 'card_statistic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    card_type = db.Column(db.String(64)) #card类型
    card_num = db.Column(db.String(64)) #card数量
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<CardStatistic %r>' % self.host_name


class MdaDetail(db.Model):
    '''Mda明细表'''

    __tablename__ = 'mda_detail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    slot = db.Column(db.String(64)) #槽位
    mda = db.Column(db.String(64))
    equipped_type = db.Column(db.String(64)) #mda类型
    admin_state = db.Column(db.String(64)) #admin状态
    operational_state = db.Column(db.String(64)) #operational状态
    serial_number = db.Column(db.String(64)) #串口数量
    time_of_last_boot = db.Column(db.String(64)) #上次启动时间
    temperature = db.Column(db.String(64)) #温度
    temperature_threshold = db.Column(db.String(64)) #温度阈值
    is_abnormal = db.Column(db.String(64)) #是否异常
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<MdaDetail %r>' % self.host_name


class MdaStatistic(db.Model):
    '''Mda统计表'''

    __tablename__ = 'mda_statistic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    card_type = db.Column(db.String(64)) #card类型
    card_num = db.Column(db.String(64)) #card数量
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<MdaStatistic %r>' % self.host_name


class LoadStatistic(db.Model):
    '''业务负荷统计表-按端口统计用户数量'''

    __tablename__ = 'load_statistic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
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

class LoadStatisticHost(db.Model):
    '''业务负荷统计表-按设备统计用户数量'''

    __tablename__ = 'load_statistic_host'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    ies_3000_num = db.Column(db.String(64)) #ies 3000 用户数量
    ies_3000_pool_utilization = db.Column(db.String(64)) #ies 3000 地址池利用率
    vprn_4015_num = db.Column(db.String(64)) #vprn 4015 用户数量
    vprn_4015_pool_utilization = db.Column(db.String(64)) #vprn 4015 地址池利用率
    date_time = db.Column(db.Date, default = date.today()) #采集时间

    def __repr__(self):
        return '<LoadStatisticHost %r>' % self.host_name

class XunJian(db.Model):
    '''巡检表'''

    __tablename__ = 'xunjian'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    check_item = db.Column(db.String(128)) #检查项
    err = db.Column(db.Text) #错误提示
    msg = db.Column(db.Text) #关键信息
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<XunJian %r>' % self.host_name

class ConfigCheck(db.Model):
    '''配置检查表'''

    __tablename__ = 'config_check'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    check_item = db.Column(db.String(128)) #设备名
    err = db.Column(db.Text) #错误提示
    msg = db.Column(db.Text) #关键信息
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<ConfigCheck %r>' % self.host_name

class CaseLib(db.Model):
    '''案例库表'''

    __tablename__ = 'case_lib'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    describe = db.Column(db.Text) #文件描述
    file_url = db.Column(db.String(128)) #文件路径
    file_name = db.Column(db.String(128)) #文件名
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<CaseLib %r>' % self.file_name

class ZuXun(db.Model):
    '''组巡表'''

    __tablename__ = 'zuxun'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市名
    host_name = db.Column(db.String(64)) #设备名
    err = db.Column(db.Text) #错误提示
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<ZuXun %r>' % self.host_name

class GenerateConfig(db.Model):
    '''脚本自动生成表'''

    __tablename__ = 'generate_config'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64)) #模板名称
    content = db.Column(db.Text) #模板内容
    model_type = db.Column(db.Integer) #模板类型（0 内置模板， 1 自定义模板， 2 模板组）
    date_time = db.Column(db.Date, default = date.today()) #保存日期

    @staticmethod
    def save_default_model():
        '''保存内置模板'''
        from .main.config import g_config_model
        today = date.today()
        for i in g_config_model:
            generate_config = GenerateConfig(
                name = i[0],
                content = i[1],
                model_type = 0,
                date_time = today
            )

            db.session.add(generate_config)

        db.session.commit()
        db.session.close()

    def __repr__(self):
        return '<GenerateConfig %r>' % self.name

class InstallBase(db.Model):
    '''InstallBase表'''

    __tablename__ = 'install_base'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    province = db.Column(db.String(64)) #省份
    operator = db.Column(db.String(64)) #运营商
    busines_type = db.Column(db.String(64)) #业务类型
    net_type = db.Column(db.String(64)) #网络类型
    host_type = db.Column(db.String(64)) #设备类型
    host_model = db.Column(db.String(64)) #设备型号
    version = db.Column(db.String(64)) #版本
    number = db.Column(db.Integer) #数量
    note = db.Column(db.String(64)) #备注
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<InstallBase %r>' % self.host_type

class NetFlow(db.Model):
    '''重要网络流量统计表'''

    __tablename__ = 'net_flow'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrier = db.Column(db.String(64)) #Carrier
    province = db.Column(db.String(64)) #省份
    city = db.Column(db.String(64)) #地市
    network = db.Column(db.String(64)) #网络
    site_name = db.Column(db.String(64)) #设备名称
    port_num_10g = db.Column(db.Integer) #10GE端口数量
    port_utilization_10g = db.Column(db.String(64)) #10GE端口已用数量百分比
    port_num_100g = db.Column(db.Integer) #100GE端口数量
    port_utilization_100g = db.Column(db.String(64)) #100GE端口已用数量百分比
    pea_uplink_throughput_utilization = db.Column(db.String(64)) #流量峰值利用率中选取最大的值。
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<NetFlow %r>' % self.site_name



class SpecialLine(db.Model):
    '''专线统计表'''

    __tablename__ = 'special_line'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
    host_name = db.Column(db.String(64)) #设备名
    service = db.Column(db.String(64)) #业务名称
    service_id = db.Column(db.String(64)) #业务编号
    ies_describe = db.Column(db.String(64)) #ies 描述
    gi_name = db.Column(db.String(64)) #group-interface 端口名称
    gi_describe = db.Column(db.String(64)) #group-interface 端口描述
    sap_name = db.Column(db.String(64)) # sap名称
    ip = db.Column(db.String(64)) #ip 地址
    mac = db.Column(db.String(64)) #mac 地址
    egress_id = db.Column(db.String(64)) #qos sap-egress编号
    rate = db.Column(db.String(64)) #带宽值 rate值/1000
    date_time = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return '<SpecialLine %r>' % self.ip


class HostList(db.Model):
    '''设备清单'''

    __tablename__ = 'host_list'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
    host_name = db.Column(db.String(64)) #设备名
    host_ip = db.Column(db.String(64)) #设备ip
    version = db.Column(db.String(64)) #版本
    boot_time = db.Column(db.String(64)) #设备启动时间
    config_save_time = db.Column(db.String(64)) #设备配置保存时间
    date_time = db.Column(db.Date, default = date.today())

class ServiceStatistic(db.Model):
    '''业务统计'''

    __tablename__ = 'service_statistic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
    host_name = db.Column(db.String(64)) #设备名
    port = db.Column(db.String(64)) #端口
    lag = db.Column(db.String(64)) #lag
    sap = db.Column(db.String(64)) #sap/port
    interface = db.Column(db.String(64)) #interface
    service = db.Column(db.String(64)) #service
    service_id = db.Column(db.String(64)) #service_id
    date_time = db.Column(db.Date, default = date.today())

class NatPort(db.Model):
    '''Nat Port 流量表'''

    __tablename__ = 'nat_port'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(64)) #地市
    host_name = db.Column(db.String(64)) #设备名
    port = db.Column(db.String(64)) #端口
    utilization = db.Column(db.String(64)) #利用率
    date_time = db.Column(db.Date, default = date.today())

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def insert_default_users():
        changzhou = User(username='changzhou', password='changzhou')
        huaian = User(username='huaian', password='huaian')
        lianyungang = User(username='lianyungang', password='lianyungang')
        nanjing = User(username='nanjing', password='nanjing')
        nantong = User(username='nantong', password='nantong')
        suqian = User(username='suqian', password='suqian')
        suzhou = User(username='suzhou', password='suzhou')
        taizhou = User(username='taizhou', password='taizhou')
        wuxi = User(username='wuxi', password='wuxi')
        xuzhou = User(username='xuzhou', password='xuzhou')
        yancheng = User(username='yancheng', password='yancheng')
        yangzhou = User(username='yangzhou', password='yangzhou')
        zhenjiang = User(username='zhenjiang', password='zhenjiang')

        #内部账号
        nokia = User(username='nokia', password='nokia2020')
        #省公司
        shenggonsi = User(username='shenggonsi', password='shenggonsi')

        db.session.add(changzhou)
        db.session.add(huaian)
        db.session.add(lianyungang)
        db.session.add(nanjing)
        db.session.add(nantong)
        db.session.add(suqian)
        db.session.add(suzhou)
        db.session.add(taizhou)
        db.session.add(wuxi)
        db.session.add(xuzhou)
        db.session.add(yancheng)
        db.session.add(yangzhou)
        db.session.add(zhenjiang)
        db.session.add(nokia)
        db.session.add(shenggonsi)

        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))