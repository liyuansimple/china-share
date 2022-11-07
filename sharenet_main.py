# coding:utf8
from sharenet_form import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow,  QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal,  QThread
from PyQt5.QtGui import QTextCursor
from sqlalchemy import create_engine
from os.path import exists, dirname
import nokiatool as nt
from FunZteScripts import *
from ericssonscript import *
from FunHwScripts import *
import sys
def tm():
    return time.strftime("%Y-%m-%d %H:%M:%S") + ':'

class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str) #定义一个发送str的信号
    def write(self, text):
        self.textWritten.emit(str(text))

#主窗体类
class ShareNetMain(QMainWindow,Ui_MainWindow):
    context = ''; contextList = []; HwScriptsDict={}
    def __init__(self,username):
        super(ShareNetMain, self).__init__()
        self.setupUi(self)

        # 设置主要按钮样式
        self.pushButton_2.setStyleSheet(self.button_style_x())
        self.pushButton_6.setStyleSheet(self.button_style_x())
        self.pushButton_10.setStyleSheet(self.button_style_x())
        self.pushButton_12.setStyleSheet(self.button_style_y())
        self.pushButton_13.setStyleSheet(self.button_style_x())
        self.pushButton_16.setStyleSheet(self.button_style_x())

        # 设置选择按钮样式
        self.pushButton_5.setStyleSheet(self.button_style_y())
        self.pushButton_7.setStyleSheet(self.button_style_y())
        self.pushButton_8.setStyleSheet(self.button_style_y())
        self.pushButton_9.setStyleSheet(self.button_style_y())
        self.pushButton_11.setStyleSheet(self.button_style_y())
        self.pushButton_14.setStyleSheet(self.button_style_y())
        self.pushButton.setStyleSheet(self.button_style_x())

        self.actionhelp.triggered.connect(self.helpForm)

        self.pushButton_8.clicked.connect(self.pushButton8_click)
        self.pushButton_9.clicked.connect(self.pushButton9_click)
        self.pushButton_10.clicked.connect(self.pushButton10_click)
        self.pushButton_11.clicked.connect(self.pushButton11_click)
        self.pushButton_13.clicked.connect(self.pushButton13_click)
        self.pushButton_2.clicked.connect(self.getMmlScripts)

        self.pushButton_12.clicked.connect(self.pushButton12_click)

        self.pushButton_14.clicked.connect(self.pushButton14_click)
        self.pushButton_16.clicked.connect(self.pushButton16_click)

        self.pushButton_5.clicked.connect(self.pushButton5_click)
        self.pushButton_6.clicked.connect(self.pushButton6_click)
        self.pushButton_7.clicked.connect(self.pushButton7_click)

        self.radioButton_3.toggled.connect(self.zteRadioChangeLte)
        self.radioButton_4.toggled.connect(self.zteRadioChangeNr)
        self.radioButton_5.toggled.connect(self.nokiaRadioChangeLte)
        self.radioButton_6.toggled.connect(self.nokiaRadioChangeNr)
        self.radioButton_7.toggled.connect(self.ericRadioChangeLte)
        self.radioButton_8.toggled.connect(self.ericRadioChangeNr)
        self.lineEdit_12.setPlaceholderText('工单分割站点数')
        self.lineEdit_12.setText("500")
        today = datetime.datetime.today()
        timeItems = []
        for i in range(60):
            after = today + datetime.timedelta(days=i)
            timeItems.append(str(after).split(' ')[0])
        self.comboBox_3.addItems(timeItems)
        self.radioButton.setChecked(True)
        self.radioButton_3.setChecked(True)
        self.radioButton_5.setChecked(True)
        self.radioButton_7.setChecked(True)
        # self.lineEdit.setEnabled(False)
        # self.lineEdit_2.setEnabled(False)
        # self.pushButton_5.setEnabled(False)
        # self.pushButton_6.setEnabled(False)
        # self.pushButton_7.setEnabled(False)

        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)

        # 全局变量
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(":/cmcc.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.engine = create_engine("postgresql://postgres:1234Qwer@114.215.176.170:5432/mdt")
        self.engineParam = create_engine("postgresql://postgres:root@121.41.168.99:5432/sharenet")
        self.default_path = ''
        self.paramPath = ''
        self.configPath = ''
        self.username = username
        self.nokiaPath = ''
        self.neiborPath = ''
        self.HwparamPath = ''
        self.HwconfigPath = ''
        print(tm(), f"{self.username}，欢迎登录使用！")

        # 隐藏NR控件
        self.label_12.hide()
        self.lineEdit_10.hide()
        self.pushButton_12.hide()
        self.pushButton.hide()
        self.pushButton_10.setText('中兴LTE共享共建脚本生成')

    def zteRadioChangeLte(self):
        if self.radioButton_3.isChecked():
            self.lineEdit_3.setText('')
            self.lineEdit_4.setText('')
            self.paramPath = ''
            self.configPath = ''
            # self.label_12.hide()
            # self.lineEdit_10.hide()
            # self.pushButton_12.hide()
            # self.pushButton.hide()
            self.pushButton_10.setText('中兴LTE共享共建脚本生成')

    def zteRadioChangeNr(self):
        if self.radioButton_4.isChecked():
            self.lineEdit_3.setText('')
            self.lineEdit_4.setText('')
            self.paramPath = ''
            self.configPath = ''
            # self.label_12.show()
            # self.lineEdit_10.show()
            # self.pushButton_12.show()
            # self.pushButton.show()
            self.pushButton_10.setText('中兴NR共享共建脚本生成')
            # self.pushButton.setText('STEP2：NR邻区脚本生成')

    def nokiaRadioChangeLte(self):
        if self.radioButton_5.isChecked():
            self.comboBox.setEnabled(True)
            self.comboBox_2.setEnabled(False)
            self.comboBox_2.clear()
            self.lineEdit_5.setText('')
            self.nokiaPath = ''
            self.pushButton_13.setText('诺基亚LTE共享共建脚本生成')

    def nokiaRadioChangeNr(self):
        if self.radioButton_6.isChecked():
            self.lineEdit_5.setText('')
            self.nokiaPath = ''
            self.comboBox.clear()
            # self.comboBox_2.setEnabled(True)
            self.comboBox.setEnabled(False)
            self.pushButton_13.setText('诺基亚NR共享共建脚本生成')
            nokiaItemsNr = ['全部', '添加广电AMF', '添加广电PLMN', '添加IP和VLAN', '添加广电路由',
                            '更新切片中广电的PLMN', '添加NGUplane地址并关联PLMN', '添加NGCplan地址',
                            '更新XNCplan地址', '更新XNUplan地址',
                            '打开RanShraing开关', '打开传输RanShraing开关', '添加小区下面新的PLMN', '关联跟踪区']
            for a, b in enumerate(nokiaItemsNr):
                if b in ['添加广电AMF', '添加广电PLMN','更新切片中广电的PLMN','打开RanShraing开关',
                         '打开传输RanShraing开关', '添加小区下面新的PLMN', '关联跟踪区']:
                    self.comboBox_2.qCheckBox.append(b)
                    self.comboBox_2.qCheckBox[a].setChecked(True)

    def ericRadioChangeLte(self):
        if self.radioButton_7.isChecked():
            self.lineEdit_6.setPlaceholderText('')
            self.lineEdit_7.setPlaceholderText('')
            self.lineEdit_8.setPlaceholderText('')
            self.lineEdit_9.setPlaceholderText('')
            self.lineEdit_6.setEnabled(False)
            self.lineEdit_7.setEnabled(False)
            self.lineEdit_8.setEnabled(False)
            self.lineEdit_9.setEnabled(False)
            self.pushButton_16.setText('爱立信LTE共享共建脚本生成')

    def ericRadioChangeNr(self):
        if self.radioButton_8.isChecked():
            self.lineEdit_6.setPlaceholderText("exam:10.68.219.3")
            self.lineEdit_7.setPlaceholderText("exam:10.68.219.18")
            self.lineEdit_8.setPlaceholderText("exam:10.68.219.34")
            self.lineEdit_9.setPlaceholderText("exam:10.68.219.50")
            self.lineEdit_6.setStyleSheet("background-color: rgb(226, 226, 226);\n"
                                          "color: rgb(0, 0, 255);")
            self.lineEdit_7.setStyleSheet("background-color: rgb(226, 226, 226);\n"
                                          "color: rgb(0, 0, 255);")
            self.lineEdit_8.setStyleSheet("background-color: rgb(226, 226, 226);\n"
                                          "color: rgb(0, 0, 255);")
            self.lineEdit_9.setStyleSheet("background-color: rgb(226, 226, 226);\n"
                                          "color: rgb(0, 0, 255);")
            self.lineEdit_6.setEnabled(True)
            self.lineEdit_7.setEnabled(True)
            self.lineEdit_8.setEnabled(True)
            self.lineEdit_9.setEnabled(True)
            self.pushButton_16.setText('爱立信NR共享共建脚本生成')

    def button_style_x(self):
        button_style = (
            "QPushButton{background-color:Gainsboro;color:black; font:bold 10pt '微软雅黑';}"
            "QPushButton:hover{background-color:blue; color: white;font:bold 10pt '微软雅黑';}"
            "QPushButton:pressed{background-color:orange;font:bold 10pt '微软雅黑';}"
        )
        return button_style

    def button_style_y(self):
        button_style = (
            "QPushButton{background-color:GhostWhite;color:black; font:9pt '微软雅黑';}"
            "QPushButton:hover{background-color:PapayaWhip; color: black;font:9pt '微软雅黑';}"
            "QPushButton:pressed{background-color:CornflowerBlue;font:bold 10pt '微软雅黑';}"
        )
        return button_style

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def helpForm(self):
        def dialog_click():
            sending_button = dialog.sender()
            changjia = sending_button.objectName()
            if changjia == '中兴':
                dialog.accept()
                print(tm(),'选取中兴数据模板保存路径')
                configPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
                if exists(configPath):
                    print(tm(), f'选取路径：{configPath}')
                    print(tm(), f'中兴模板文件下载中.....')
                    df1 = pd.read_sql_table('zteParamLte',con=self.engineParam)
                    df2 = pd.read_sql_table('zteParamNr', con=self.engineParam)
                    xls_nm = join(configPath, f'中兴共享共建模板.xlsx')
                    writer = pd.ExcelWriter(xls_nm)
                    df1.to_excel(writer, sheet_name='4G模板', index=False, encoding='utf-8-sig')
                    df2.to_excel(writer, sheet_name='5G模板', index=False, encoding='utf-8-sig')
                    writer.save()
                    print(tm(), f'中兴模板文件下载完成，已保存至{xls_nm}')
            elif changjia == '诺基亚4G':
                dialog.accept()
                print(tm(),'选取诺基亚数据模板保存路径')
                configPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
                if exists(configPath):
                    print(tm(), f'选取路径：{configPath}')
                    print(tm(), f'诺基亚模板文件下载中.....')
                    df1 = pd.read_sql_table('nokiaParamLte1',con=self.engineParam)
                    df2 = pd.read_sql_table('nokiaParamLte2', con=self.engineParam)
                    df3 = pd.read_sql_table('nokiaParamLte3', con=self.engineParam)
                    df4 = pd.read_sql_table('nokiaParamLte4', con=self.engineParam)
                    df5 = pd.read_sql_table('nokiaParamLte5', con=self.engineParam)
                    df6 = pd.read_sql_table('nokiaParamLte6', con=self.engineParam)
                    df7 = pd.read_sql_table('nokiaParamLte7', con=self.engineParam)
                    xls_nm = join(configPath, '诺基亚4G共享共建模板.xlsx')
                    writer = pd.ExcelWriter(xls_nm)
                    df1.to_excel(writer, sheet_name='LTE基站共享数据', index=False, encoding='utf-8-sig')
                    df2.to_excel(writer, sheet_name='LTE小区共享数据', index=False, encoding='utf-8-sig')
                    df3.to_excel(writer, sheet_name='现网LNMME配置', index=False, encoding='utf-8-sig')
                    df4.to_excel(writer, sheet_name='现网VLAN配置', index=False, encoding='utf-8-sig')
                    df5.to_excel(writer, sheet_name='现网IP配置', index=False, encoding='utf-8-sig')
                    df6.to_excel(writer, sheet_name='现网路由配置', index=False, encoding='utf-8-sig')
                    df7.to_excel(writer, sheet_name='现网moprMappingList配置', index=False, encoding='utf-8-sig')
                    writer.save()
                    print(tm(), f'诺基亚4G共享共建模板文件下载完成，已保存至{xls_nm}')
            elif changjia == '诺基亚5G':
                dialog.accept()
                print(tm(),'选取诺基亚数据模板保存路径')
                configPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
                if exists(configPath):
                    print(tm(), f'选取路径：{configPath}')
                    print(tm(), f'诺基亚模板文件下载中.....')
                    df1 = pd.read_sql_table('nokiaParamNr1',con=self.engineParam)
                    df2 = pd.read_sql_table('nokiaParamNr2', con=self.engineParam)
                    df3 = pd.read_sql_table('nokiaParamNr3', con=self.engineParam)
                    df4 = pd.read_sql_table('nokiaParamNr4', con=self.engineParam)
                    df5 = pd.read_sql_table('nokiaParamNr5', con=self.engineParam)
                    df6 = pd.read_sql_table('nokiaParamNr6', con=self.engineParam)
                    df7 = pd.read_sql_table('nokiaParamNr7', con=self.engineParam)
                    df8 = pd.read_sql_table('nokiaParamNr8', con=self.engineParam)
                    xls_nm = join(configPath, '诺基亚5G共享共建模板.xlsx')
                    writer = pd.ExcelWriter(xls_nm)
                    df1.to_excel(writer, sheet_name='LTE基站共享数据', index=False, encoding='utf-8-sig')
                    df2.to_excel(writer, sheet_name='LTE小区共享数据', index=False, encoding='utf-8-sig')
                    df3.to_excel(writer, sheet_name='现网LNMME配置', index=False, encoding='utf-8-sig')
                    df4.to_excel(writer, sheet_name='现网VLAN配置', index=False, encoding='utf-8-sig')
                    df5.to_excel(writer, sheet_name='现网IP配置', index=False, encoding='utf-8-sig')
                    df6.to_excel(writer, sheet_name='现网路由配置', index=False, encoding='utf-8-sig')
                    df7.to_excel(writer, sheet_name='现网NRADJNRCELL', index=False, encoding='utf-8-sig')
                    df8.to_excel(writer, sheet_name='现网NRREDRT', index=False, encoding='utf-8-sig')
                    writer.save()
                    print(tm(), f'诺基亚5G共享共建模板文件下载完成，已保存至{xls_nm}')
            elif changjia == '华为':
                dialog.accept()
                print(tm(),'选取华为数据模板保存路径')
                configPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
                if exists(configPath):
                    print(tm(), f'选取路径：{configPath}')
                    print(tm(), f'华为模板文件下载中.....')
                    df1 = pd.read_sql_table('hwParamLte',con=self.engineParam)
                    df2 = pd.read_sql_table('hwParamNr', con=self.engineParam)
                    xls_nm = join(configPath, '华为共享共建模板.xlsx')
                    writer = pd.ExcelWriter(xls_nm)
                    df1.to_excel(writer, sheet_name='华为4G模板', index=False, encoding='utf-8-sig')
                    df2.to_excel(writer, sheet_name='华为5G模板', index=False, encoding='utf-8-sig')
                    writer.save()
                    print(tm(), f'华为模板文件下载完成，已保存至{xls_nm}')
        dialog = QDialog()
        dialog.resize(200, 150)
        dialog.setMaximumSize(QtCore.QSize(200, 700))
        dialog.setWindowIcon(self.icon)
        font = QtGui.QFont()
        font.setFamily('微软雅黑')
        font.setBold(True)
        font.setPointSize(14)
        i = 10
        for c, name in enumerate(['华为','中兴','诺基亚4G','诺基亚5G']):
            btn = QPushButton(str(name) + '模板下载', dialog)
            btn.setFont(font)
            btn.setGeometry(20, i, 160, 20)
            btn.setFlat(False)
            btn.setStyleSheet(self.button_style_y())
            btn.setObjectName(str(name))
            btn.clicked.connect(dialog_click)
            i += 25
            if name in ['爱立信']:
                btn.setEnabled(False)
        dialog.setWindowTitle("help")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        dialog.exec_()
    # 中兴选择文件1
    def pushButton8_click(self):
        print(tm(), "选择中兴共享共建改造站点明细")
        paramPath, filetype = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", self.default_path,"csv Files (*.csv)")
        if exists(paramPath):
            self.default_path = dirname(paramPath)
            self.paramPath = paramPath
            self.lineEdit_3.setText(paramPath)
            print(tm(), f'中兴共享共建改造明细设置成功！')

    def pushButton11_click(self):
        print(tm(), "选择诺基亚共享共建改造参数文件")
        nokiaPath, filetype = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", self.default_path,
                                                          "Excel Files (*.xlsx)")
        if exists(nokiaPath):
            self.default_path = dirname(nokiaPath)
            self.nokiaPath = nokiaPath
            self.lineEdit_5.setText(nokiaPath)
            print(tm(), f'诺基亚共享共建改造明细设置成功！')

    def pushButton12_click(self):
        print(tm(), "选择中兴共享共建改造邻区数据文件")
        neiborPath, filetype = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", self.default_path,
                                                                    "Excel Files (*.xlsx)")
        if exists(neiborPath):
            self.default_path = dirname(neiborPath)
            self.neiborPath = neiborPath
            self.lineEdit_5.setText(neiborPath)
            print(tm(), f'中兴共享共建改造邻区配置数据已选择！')

    # 诺基亚生成脚本
    def pushButton13_click(self):
        if self.radioButton_5.isChecked():
            MyThread.net_check = 'LTE'
            print(tm(), "当前待生成脚本网络类型为4G")
        elif self.radioButton_6.isChecked():
            MyThread.net_check = 'NR'
            print(tm(), "当前待生成脚本网络类型为5G")
        if exists(dirname(self.nokiaPath)):
            if MyThread.net_check == 'LTE':
                items = ['配置IP和VLAN', '配置广电路由', '配置广电用户面控制面IP地址', '添加广电LTAC',
                         '添加广电LNMME', '基站共享开关', '移动策略MODPR', '切换策略', '重选策略4G',
                         '重选策略5G', '重定向策略', '添加广电小区PLMN和移动策略组']
                selectitems = self.comboBox.getCheckItems()
                if selectitems:
                    PlmnDict = {}
                    for i in items:
                        if i in selectitems:
                            PlmnDict[i] = True
                        else:
                            PlmnDict[i] = False
                    MyThread.sending_button = self.sender()
                    MyThread.nokiaPath = self.nokiaPath
                    MyThread.default_path = self.default_path
                    MyThread.PlmnDict = PlmnDict
                    self.geThreads()
                else:
                    QMessageBox.information(self, "提示", "请选择诺基亚共享共建改造参数配置选项!")
            elif MyThread.net_check == 'NR':
                items = ['添加广电AMF', '添加广电PLMN', '添加IP和VLAN', '添加广电路由',
                            '更新切片中广电的PLMN', '添加NGUplane地址并关联PLMN', '添加NGCplan地址',
                            '更新XNCplan地址', '更新XNUplan地址',
                            '打开RanShraing开关', '打开传输RanShraing开关', '添加小区下面新的PLMN', '关联跟踪区']
                selectitems = self.comboBox_2.getCheckItems()
                if selectitems:
                    PlmnDict = {}
                    for i in items:
                        if i in selectitems:
                            PlmnDict[i] = True
                        else:
                            PlmnDict[i] = False
                    MyThread.sending_button = self.sender()
                    MyThread.nokiaPath = self.nokiaPath
                    MyThread.default_path = self.default_path
                    MyThread.PlmnDict = PlmnDict
                    self.geThreads()
                else:
                    QMessageBox.information(self, "提示", "请选择诺基亚共享共建改造参数配置选项!")
        else:
            QMessageBox.information(self, "提示", "未选择有效数据路径!")


    # 中兴选择文件2
    def pushButton9_click(self):
        print(tm(), "选择中兴现网配置信息明细")
        configPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
        if exists(configPath):
            self.default_path = configPath
            self.configPath = configPath
            self.lineEdit_4.setText(configPath)
            print(tm(), f'中兴现网配置信息明细文件选取成功！')

    # 中兴生成脚本
    def pushButton10_click(self):
        if self.radioButton_3.isChecked():
            MyThread.net_check = 'LTE'
            print(tm(), "当前待生成脚本网络类型为4G")
        elif self.radioButton_4.isChecked():
            MyThread.net_check = 'NR'
            print(tm(), "当前待生成脚本网络类型为5G")
        if exists(dirname(self.paramPath)) and exists(self.configPath):
            MyThread.sending_button = self.sender()
            MyThread.paramPath = self.paramPath
            MyThread.configPath = self.configPath
            MyThread.default_path = self.default_path
            self.geThreads()
        else:
            QMessageBox.information(self, "提示", "未选择有效数据路径!")

    # 爱立信选择文件
    def pushButton14_click(self):
        print(tm(), "选择爱立信脚本保存路径")
        configPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
        if exists(configPath):
            self.default_path = configPath
            self.configPath = configPath
            self.lineEdit_11.setText(configPath)
            print(tm(), f'爱立信参数脚本保存路径已选择！')

    # 爱立信生成脚本文件
    def pushButton16_click(self):
        ericTPadd1 = self.lineEdit_6.text().strip()
        ericTPadd2 = self.lineEdit_7.text().strip()
        ericTPadd3 = self.lineEdit_8.text().strip()
        ericTPadd4 = self.lineEdit_9.text().strip()
        print(ericTPadd1, ericTPadd2, ericTPadd3, ericTPadd4)
        if self.radioButton_7.isChecked():
            MyThread.net_check = 'LTE'
            print(tm(), "当前待生成脚本网络类型为4G")
        elif self.radioButton_8.isChecked():
            MyThread.net_check = 'NR'
            print(tm(), "当前待生成脚本网络类型为5G")
        if MyThread.net_check == 'LTE':
            nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '').replace(':',
                                                                                                          '').replace(
                ' ', '')
            MakeEricssonLTEScript(join(self.configPath, f"爱立信5G共享共建改造脚本_{nowtime}.amos"))
            print(tm(), f"爱立信4G脚本已生成，文件位于{self.configPath}")
            QMessageBox.information(self, "提示", "已完成!")
        else:
            if ericTPadd1 != None and ericTPadd2 != None and ericTPadd3 != None and ericTPadd4 != None:
                pars = [ericTPadd1, ericTPadd2, ericTPadd3, ericTPadd4]
                nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '').replace(':',
                       '').replace(' ', '')
                MakeEricssonNRScript(join(self.configPath, f"爱立信4G共享共建改造脚本_{nowtime}.amos"), pars)
                print(tm(), f"爱立信5G脚本已生成，文件位于{self.configPath}")
                QMessageBox.information(self, "提示", "已完成!")
            else:
                QMessageBox.information(self, "提示", "请设置共享共建远端IP!")

    # 华为选择模板文件
    def pushButton7_click(self):
        print(tm(), "选择华为待共享共建改造站点信息明细")
        HwparamPath, filetype = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", self.default_path,
                                                                    "csv Files (*.csv)")
        if exists(dirname(HwparamPath)):
            self.default_path = dirname(HwparamPath)
            self.HwparamPath = HwparamPath
            self.lineEdit.setText(HwparamPath)
            print(tm(), f'华为共享共建改造站点明细已选择！')

    # 华为选择配置文件路径
    def pushButton5_click(self):
        print(tm(), "选择华为现网配置MML结果查询文件路径")
        HwconfigPath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
        if exists(HwconfigPath):
            self.default_path = HwconfigPath
            self.HwconfigPath = HwconfigPath
            self.lineEdit_2.setText(HwconfigPath)
            print(tm(), f'华为现网配置MML结果查询文件路径选取成功！')

    # 华为脚本制作入口
    def pushButton6_click(self):
        if self.radioButton.isChecked():
            MyThread.net_check = 'LTE'
            print(tm(), "当前待生成脚本网络类型为4G")
        elif self.radioButton_2.isChecked():
            MyThread.net_check = 'NR'
            print(tm(), "当前待生成脚本网络类型为5G")
        try:
            splitNum = int(self.lineEdit_12.text().strip())
        except:
            splitNum = 0
        if splitNum > 0:
            if exists(dirname(self.HwparamPath)) and exists(self.HwconfigPath):
                MyThread.sending_button = self.sender()
                MyThread.paramPath = self.HwparamPath
                MyThread.configPath = self.HwconfigPath
                MyThread.default_path = self.default_path
                MyThread.splitNum = int(self.lineEdit_12.text().strip())
                MyThread.sDay = self.comboBox_3.currentText().strip().replace('-', '')
                self.geThreads()
            else:
                QMessageBox.information(self, "提示", "未选择有效数据路径!")
        else:
            QMessageBox.information(self, "提示", "请输入正确的脚本分割数量！!")

    def getMmlScripts(self):
        if exists(dirname(self.HwparamPath)):
            dfDot = read_param(self.HwparamPath)
            dirpath = QFileDialog.getExistingDirectory(self, "选择文件夹", self.default_path)
            if exists(dirpath):
                nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).\
                    replace('-', '').replace(':','').replace(' ', '')
                cnt = 0
                if self.radioButton.isChecked():
                    for idx, df in dfDot.groupby(['地市','OMC归属']):
                        city = idx[0]; omc = idx[1]
                        enbList = list(df['基站名称'].unique())
                        txtScripts = ''
                        for enb in enbList:
                            txtScripts += 'LST CNOPERATOR:;{' + str(enb) + '}\n'
                            txtScripts += 'LST CNOPERATORTA:;{' + str(enb) + '}\n'
                            txtScripts += 'LST EPGROUP:;{' + str(enb) + '}\n'
                            txtScripts += 'LST SCTPPEER:;{' + str(enb) + '}\n'
                            txtScripts += 'LST SCTPHOST:;{' + str(enb) + '}\n'
                            txtScripts += 'LST USERPLANEHOST:;{' + str(enb) + '}\n'
                            txtScripts += 'LST EUTRANEXTERNALCELL:;{' + str(enb) + '}\n'
                            txtScripts += 'LST NREXTERNALCELL:;{' + str(enb) + '}\n'
                            txtScripts += 'LST X2:;{' + str(enb) + '}\n'
                            txtScripts += 'LST S1:;{' + str(enb) + '}\n'
                            txtScripts += 'LST APP:;{' + str(enb) + '}\n'
                        fname = f"{city}_华为_LTE_{omc}_站点数量{len(enbList)}_MML查询脚本_{nowtime}.txt"
                        with open(join(dirpath, fname), 'w') as f:
                            f.write(txtScripts)
                        cnt += 1
                elif self.radioButton_2.isChecked():
                    for idx, df in dfDot.groupby(['地市','OMC归属']):
                        city = idx[0]; omc = idx[1]
                        enbList = list(df['基站名称'].unique())
                        txtScripts = ''
                        for enb in enbList:
                            txtScripts += 'LST GNBOPERATOR:;{' + str(enb) + '}\n'
                            txtScripts += 'LST GNBCUNG:;{' + str(enb) + '}\n'
                            txtScripts += 'LST EPGROUP:;{' + str(enb) + '}\n'
                            txtScripts += 'LST SCTPPEER:;{' + str(enb) + '}\n'
                            txtScripts += 'LST SCTPHOST :;{' + str(enb) + '}\n'
                            txtScripts += 'LST USERPLANEHOST:;{' + str(enb) + '}\n'
                            txtScripts += 'LST NREXTERNALNCELL  :;{' + str(enb) + '}\n'
                            txtScripts += 'LST GNBEUTRAEXTERNALCELL:;{' + str(enb) + '}\n'
                            txtScripts += 'LST GNBCUXN:;{' + str(enb) + '}\n'
                            txtScripts += 'LST APP:;{' + str(enb) + '}\n'
                        fname = f"{city}_华为_NR_{omc}_站点数量{len(enbList)}_MML查询脚本_{nowtime}.txt"
                        with open(join(dirpath, fname), 'w') as f:
                            f.write(txtScripts)
                        cnt += 1
                print(tm(), f"MML查询脚本保存在{dirpath}，共计{cnt}个文件!")
                QMessageBox.information(self, "成功", f"MML查询脚本保存在{dirpath}!")
        else:
            QMessageBox.information(self, "提示", "请先选择华为共建共享改造数据文件!")

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '共享共建',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.close()
        else:
            event.ignore()

    def geThreads(self):
        self.threadJob = MyThread()
        self.threadJob.my_signal.connect(self.getSingles)
        self.threadJob.start()

    def getSingles(self, i):
        if i == -1:
            QMessageBox.information(self, "提示", "已完成!")
        elif i == -2:
            print(tm(), "选择诺基亚脚本保存路径")
            filepath, type = QFileDialog.getSaveFileName(self, "脚本保存路径", self.default_path, 'xml(*.xml)')
            if exists(dirname(filepath)):
                if MyThread.net_check == 'LTE':
                    f = open(filepath, 'wb+')
                    f.write(self.context)
                    f.close()
                    print(tm(), f"诺基亚脚本已保存至{filepath}")
                    QMessageBox.information(self, "提示", "已完成!")
                else:
                    for i, conetex in enumerate(self.contextList):
                        f = open(splitext(filepath)[0] + f'_STEP_{i+1}'+ splitext(filepath)[1], 'wb+')
                        f.write(conetex)
                        f.close()
                    print(tm(), f"诺基亚脚本已保存至{filepath}")
                    QMessageBox.information(self, "提示", "已完成!")
        elif i == -3:
            print(tm(), "选择华为脚本保存路径")
            dirpath = QFileDialog.getExistingDirectory(self, "脚本保存路径", self.default_path)
            if exists(dirpath):
                if MyThread.net_check == 'LTE':
                    for k, v in self.HwScriptsDict.items():
                        if '未输出脚本异常明细' in k:
                            v.to_csv(join(dirpath, k), encoding='utf-8-sig', index=False)
                        else:
                            f = open(join(dirpath, k), 'w')
                            f.write(v)
                            f.close()
                    print(tm(), f"华为LTE共享共建脚本已保存至{dirpath}")
                    QMessageBox.information(self, "提示", "已完成!")
                else:
                    for k, v in self.HwScriptsDict.items():
                        if '未输出脚本异常明细' in k:
                            v.to_csv(join(dirpath, k), encoding='utf-8-sig', index=False)
                        else:
                            f = open(join(dirpath, k), 'w')
                            f.write(v)
                            f.close()
                    print(tm(), f"华为NR共享共建脚本已保存至{dirpath}")
                    QMessageBox.information(self, "提示", "已完成!")

class MyThread(QThread):
    my_signal = pyqtSignal(int)
    sending_button=paramPath=configPath=net_check=default_path=nokiaPath=''
    PlmnDict = '';splitNum=500;sDay=''

    def __init__(self):
        super(MyThread, self).__init__()

    def run(self):
        if self.sending_button.objectName() == 'pushButton_10':
            print(tm(), '开始生成中兴共享共建脚本.....')
            self.zteMakeScripts()
        elif self.sending_button.objectName() == 'pushButton_13':
            print(tm(), '开始生成诺基亚共享共建脚本.....')
            self.NokiaMakeScripts()
        elif self.sending_button.objectName() == 'pushButton_6':
            print(tm(), '开始生成华为共享共建脚本.....')
            self.HwMakeScripts()

    def zteMakeScripts(self):
        dfParam = read_param(self.paramPath)
        if self.net_check == 'LTE':
            dfIpLayer,dfSctp,dfOperator,dfServiceMap = read_configLte(self.configPath,)
            textTDD, textFDD, dfNa = makeZteScripesLte(dfParam,dfOperator,dfIpLayer,dfSctp,dfServiceMap)
            nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '').replace(':', '').replace(' ', '')
            if textTDD != '':
                with open(join(self.default_path,f'中兴共享共建改造脚本TDD_{nowtime}.txt'),'w') as f:
                    f.write(textTDD)
            if textFDD != '':
                with open(join(self.default_path,f'中兴共享共建改造脚本FDD_{nowtime}.txt'),'w') as f:
                    f.write(textFDD)
            if len(dfNa)>0:
                dfNa.to_excel(join(self.default_path,f'中兴未生成脚本站点明细_{nowtime}.xlsx'),encoding='utf-8-sig',index=False)
            print(tm(), '中兴共享共建脚本制作完成！')
            self.my_signal.emit(-1)
        elif self.net_check == 'NR':
            dfParam = read_param(self.paramPath)
            paramDict = {str(str(x)+'_'+str(y)):[str(b),str(c),str(d),str(e),str(f)] for x,y,b,c,d,e,f in zip(dfParam.iloc[:,0],dfParam.iloc[:,1],
                    dfParam.iloc[:,2],dfParam.iloc[:,3],dfParam.iloc[:,4],dfParam.iloc[:,5],dfParam.iloc[:,6])}
            read_configNR(self.configPath,paramDict)
            print(tm(), '中兴共享共建脚本制作完成！')
            self.my_signal.emit(-1)


    def NokiaMakeScripts(self):
        if self.net_check == 'LTE':
            nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '').replace(':', '').replace(
                ' ', '')
            context = nt.MakeNokiaLTEScript(self.nokiaPath,join(self.default_path,f'诺基亚4G共享共建改造脚本plan_{nowtime}.xml'),self.PlmnDict)
            ShareNetMain.context = context
            print(tm(), '诺基亚4G共享共建脚本制作完成！')
            self.my_signal.emit(-2)
        elif self.net_check == 'NR':
            nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '').replace(':',
                                                    '').replace(' ', '')
            contextList = nt.MakeNokiaNRScript(self.nokiaPath, join(self.default_path, f'诺基亚5G共享共建改造脚本plan_{nowtime}.xml'),self.PlmnDict)
            ShareNetMain.contextList = contextList
            print(tm(), '诺基亚5G共享共建脚本制作完成！')
            self.my_signal.emit(-2)

    def HwMakeScripts(self):
        dfParam = read_param(self.paramPath)
        dfParam.columns = ['地市', '基站名称', '本地小区标识', 'OMC归属', 'AMF01_ipv4Address01', 'AMF01_ipv4Address02',
                           'AMF02_ipv4Address01', 'AMF02_ipv4Address02']
        if self.net_check == 'LTE':
            ShareNetMain.HwScriptsDict = makeHwScripesLte(dfParam, self.configPath, self.splitNum, self.sDay)
            print(tm(), f"华为LTE共享共建脚本已生成，下一步保存到本地")
            self.my_signal.emit(-3)
        elif self.net_check == 'NR':
            ShareNetMain.HwScriptsDict = makeHwScripesNr(dfParam, self.configPath, self.splitNum, self.sDay)
            print(tm(), f"华为NR共享共建脚本已生成，下一步保存到本地")
            self.my_signal.emit(-3)

