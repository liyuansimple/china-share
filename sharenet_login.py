# coding:utf8
from PyQt5 import QtGui,QtCore,QtWidgets
from sharenet_login_form import *
from sharenet_main import *
from PyQt5.QtWidgets import *
import os,sys,time,pickle
from PyQt5.QtWidgets import QApplication, QMainWindow,  QFileDialog, QColorDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt, pyqtSignal,  QThread,QSettings
from PyQt5.QtGui import QCursor,QMovie
import pandas as pd
import datetime
from os import makedirs,removedirs
from os.path import exists,dirname
import numpy as np
from sqlalchemy import create_engine
import uuid,hashlib,pickle,datetime,base64,os


class ShareNetLogin(QMainWindow,Ui_Login):
    def __init__(self):
        super(ShareNetLogin, self).__init__()
        self.setupUi(self)

        # self.lineEdit.setText('xixiaoyang')
        # self.lineEdit_2.setText('123qwe')
        self.pushButton.setStyleSheet(self.button_style_z())
        self.pushButton.clicked.connect(self.LoginUp)
        # self.pushButton_2.clicked.connect(self.Registion)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.engine = create_engine("postgresql://postgres:1234Qwer@114.215.176.170:5432/mdt")

    def button_style_z(self):
        button_style = (
            "QPushButton{background-color:DeepSkyBlue;color:white; font:bold 10pt '微软雅黑';}"
            "QPushButton:hover{background-color:green; color: black;font:bold 10pt '微软雅黑';}"
            "QPushButton:pressed{background-color:PeachPuff;font:bold 10pt '微软雅黑';}"
        )
        return button_style

    def save_pkl(self, pick_path, **k):
        address = hex(uuid.getnode())[2:]
        mac_ads = '-'.join(address[i:i + 2] for i in range(0, len(address), 2))
        with open(pick_path, 'wb') as user_file:
            user_info = {self.get_secort('Project'): k['proj'],
                         self.get_secort('name'): k['user'],
                         # self.get_secort('phone'):k['phone'],
                         self.get_secort('uid'): mac_ads.strip()}
            pickle.dump(user_info, user_file)

    def get_secort(self, s):
        md5 = hashlib.md5()
        md5.update(s.encode("utf-8"))
        return md5.hexdigest()


    # 用户注册模块,根据用户PC机MAC地址生成加密授权码，进行权限验证
    def Registion(self):
        save_path = QFileDialog.getExistingDirectory(self, "ESN保存路径", 'c:/')
        if save_path:
            proj, is_ok_1 = QInputDialog.getText(self, "ESN生成", "请输入项目:", QLineEdit.Normal, "河南省移动")
            if is_ok_1:
                user, is_ok_2 = QInputDialog.getText(self, "ESN生成", "请输入姓名:", QLineEdit.Normal, "张三")
                if is_ok_2:
                    pick_path = os.path.join(save_path, f"{proj}_{user}.key")
                    self.save_pkl(pick_path, proj=proj, user=user)
                    QMessageBox.information(self, "提示", f"ESN文件已生成，位于{pick_path}")

                else:
                    QMessageBox.information(self, "提示", "未输入项目人员姓名!")
            else:
                QMessageBox.information(self, "提示", "未输入项目名称!")
        else:
            QMessageBox.information(self, "提示", "未指定保存路径!")


    def LoginUp(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        address = hex(uuid.getnode())[2:]
        mac_addrs = '-'.join(address[i:i + 2] for i in range(0, len(address), 2))
        mac_addrs = self.get_secort(mac_addrs)
        query = "select * from sharenetusers where username = '%s';" % username
        isNet = False
        try:
            df = pd.read_sql_query(query, con=self.engine)
            isNet = True
        except:
            pass
        if isNet:
            if len(df) > 0:
                self.user = df['username'].iloc[0]
                self.password = df['password'].iloc[0]
                self.logintimes = df['logintimes'].iloc[0]
                self.lastlogintime = df['lastlogintime'].iloc[0]
                try:
                    self.macs = df['macs'].iloc[0].split(',')
                except:
                    self.macs = []
                self.licnum = df['licnum'].iloc[0]
                if username == self.user and password == self.password:
                    if mac_addrs in self.macs:
                        self.loginSuccess(username,self.logintimes+1,mac_addrs)
                    else:
                        if len(self.macs) < self.licnum:
                            self.loginSuccess(username, self.logintimes + 1, mac_addrs)
                            self.macs.append(mac_addrs)
                            ddl = "update sharenetusers set macs = '%s' where username='%s';" %(','.join(self.macs), self.user)
                            self.engine.execute(ddl)
                        else:
                            QMessageBox.information(self, "提示", "配额已满，请联系河南移动!")
                else:
                    QMessageBox.information(self, "提示", "用户或密码输入错误，请重新输入!")
            else:
                QMessageBox.information(self, "提示", "用户未注册，请联系河南移动!")
        else:
            QMessageBox.information(self, "提示", "网络异常，请重试!")

    def loginSuccess(self,name,v,v1):
        self.close()
        self.mainui = ShareNetMain(name)
        self.mainui.show()
        last_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        ddl = "update sharenetusers set logintimes = %d,lastlogintime='%s',last_mac='%s' where username='%s';" % (
        v, last_time, v1, name)
        self.engine.execute(ddl)



if __name__ == '__main__':
    import sys
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    logintools = ShareNetLogin()
    logintools.show()
    sys.exit(app.exec_())