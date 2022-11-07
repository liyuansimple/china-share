# coding:utf8

import pandas as pd
from os import listdir
from os.path import join,splitext
import time,datetime

def tm():
    return time.strftime("%Y-%m-%d %H:%M:%S") + ':'

def read_param(path):
    try:
        df = pd.read_csv(path, encoding='utf8')
    except:
        df = pd.read_csv(path, encoding='gbk')
    return df

def read_configLte(path):
    files = [i for i in listdir(path) if splitext(i)[-1]=='.xlsx']
    dfIpLayer = pd.DataFrame()
    dfSctp = pd.DataFrame()
    dfOperator = pd.DataFrame()
    dfServiceMap = pd.DataFrame()
    for file in files:
        if '$' not in file and 'Done_' not in file:
            print(tm(),f"正在解析4G参数配置文件：{file}")
            if 'IpLayerConfig' in  file:
                df = pd.read_excel(join(path, file),sheet_name=1,header=0,
                                   usecols=['MEID','IpLayerConfig','ipNo'])
                df = df.iloc[3:]
                dfIpLayer = dfIpLayer.append(df)
            elif 'Sctp' in  file:
                df = pd.read_excel(join(path, file),sheet_name=1,header=0,
                                   usecols=['MEID','localPort','Sctp','sctpNo','radioMode','refIpLayerConfig'])
                df = df.iloc[3:]
                dfSctp = dfSctp.append(df)
            elif 'Operator' in file:
                df = pd.read_excel(join(path, file),sheet_name=1,header=0,
                                   usecols=['MEID','Operator'])
                df = df.iloc[3:]
                dfOperator = dfOperator.append(df)
            elif 'ServiceMap' in file:
                df = pd.read_excel(join(path, file),sheet_name=1,header=0,
                                   usecols=['MEID','ServiceMap'])
                df = df.iloc[3:]
                dfServiceMap = dfServiceMap.append(df)
    return dfIpLayer,dfSctp,dfOperator,dfServiceMap


def makeZteScripesLte(df, dfOperator, dfIpLayer, dfSctp, dfServiceMap):
    textTDD = ''; textFDD = ''; dfNa = pd.DataFrame()
    for name, data in df.groupby(['网元ID','基站ID','制式']):
        print(tm(), f"正在配置共享共建数据：{name[1]}")
        fea_1 = data['子网'].iloc[0]
        fea_2 = data['网元ID'].iloc[0]
        fea_3 = data['基站ID'].iloc[0]
        opertor_usedList = dfOperator.loc[dfOperator['MEID']==str(fea_2),'Operator'].to_list()
        if opertor_usedList != []:
            operVal = 2
            for i in range(8):
                if str(i+1) not in opertor_usedList:
                    operVal = i+1
                    break
            if name[2] == 'TDD':
                textTDD += f'UPDATE:MOC="NEManagedElement",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)}",ATTRIBUTES="ranShareSwitch=1",EXTENDS="";\n'
                textTDD += f'CREATE:MOC="Operator",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},Operator={str(operVal)}",ATTRIBUTES="Operator={str(operVal)},userLabel=\\"\\",operatorName=中国广电",EXTENDS="";\n'
                textTDD += f'CREATE:MOC="Plmn",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},Operator={str(operVal)},Plmn=1",ATTRIBUTES="mnc=15,Plmn=1,mcc=460",EXTENDS="";\n'
                textTDD += f'UPDATE:MOC="GlobleSwitchInformationTDD",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},ENBFunctionTDD={str(fea_3)},GlobleSwitchInformationTDD=1",ATTRIBUTES="ranSharSwch=1",EXTENDS="";\n'
            elif name[2] == 'FDD':
                textFDD += f'UPDATE:MOC="NEManagedElement",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)}",ATTRIBUTES="ranShareSwitch=1",EXTENDS="";\n'
                textFDD += f'CREATE:MOC="Operator",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},Operator={str(operVal)}",ATTRIBUTES="Operator=2,userLabel=\\"\\",operatorName=中国广电",EXTENDS="";\n'
                textFDD += f'CREATE:MOC="Plmn",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},Operator={str(operVal)},Plmn=1",ATTRIBUTES="mnc=15,Plmn=1,mcc=460",EXTENDS="";\n'
                textFDD += f'UPDATE:MOC="GlobleSwitchInformation",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},ENBFunctionFDD={str(fea_3)},GlobleSwitchInformation=1",ATTRIBUTES="ranSharSwch=1",EXTENDS="";\n'
            ipflag = data['是否共享基站IP'].iloc[0]
            IpLayerConfigVal=10000000000
            ipNoVal = 10000000000
            if ipflag == '是':
                IpLayerConfigList = dfIpLayer.loc[dfIpLayer['MEID'] == str(fea_2), 'IpLayerConfig'].to_list()
                ipNoList = dfIpLayer.loc[dfIpLayer['MEID'] == str(fea_2), 'ipNo'].to_list()
                if IpLayerConfigList != [] and ipNoList != []:
                    for i in range(1,30,1):
                        if str(i + 1) not in IpLayerConfigList:
                            IpLayerConfigVal = i + 1
                            break
                    for i in range(30):
                        if str(i) not in ipNoList:
                            ipNoVal = i
                            break
                    ipadd1 = data['网关IP'].iloc[0]; ipadd2 = data['掩码'].iloc[0]; ipadd3 = data['IP地址'].iloc[0]; vlan = data['VLAN'].iloc[0]
                    if name[2] == 'TDD':
                        textTDD += f'CREATE:MOC="IpLayerConfig",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                                   f'TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)}",ATTRIBUTES="IpLayerConfig={str(IpLayerConfigVal)},' \
                                   f'gatewayIp={str(ipadd1)},networkMask={str(ipadd2)},ipField=255,' \
                                   f'ipAddr={str(ipadd3)},vid={str(vlan)},refEthernetLink=\\"SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                                   f'ConfigSet=0,TransportNetwork=1,EthernetLink=1\\",x2SelfSetup=null,' \
                                   f'refEthernetLinkGroup=null,ipNo={str(ipNoVal)},refPppLink=null",EXTENDS="";\n'
                    elif name[2] == 'FDD':
                        textFDD += f'CREATE:MOC="IpLayerConfig",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                                   f'TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)}",ATTRIBUTES="IpLayerConfig={str(IpLayerConfigVal)},' \
                                   f'gatewayIp={str(ipadd1)},networkMask={str(ipadd2)},ipField=255,' \
                                   f'ipAddr={str(ipadd3)},vid={str(vlan)},refEthernetLink=\\"SubNetwork={str(fea_1)},' \
                                   f'MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,EthernetLink=1\\",' \
                                   f'x2SelfSetup=null,refEthernetLinkGroup=null,ipNo={str(ipNoVal)},refPppLink=null",' \
                                   f'EXTENDS="";\n'
                else:
                    data.loc[:, 'Error'] = '该站点Operator未获取配置'
                    dfNa = dfNa.append(data)
            SctpList = dfSctp.loc[dfSctp['MEID'] == str(fea_2), 'Sctp'].to_list()
            sctpNoList = dfSctp.loc[dfSctp['MEID'] == str(fea_2), 'sctpNo'].to_list()
            if IpLayerConfigVal == 10000000000:
                dfGetOper = dfSctp[(dfSctp['MEID'] == str(fea_2)) & (dfSctp['localPort'] == '36412')]
                strOper = dfGetOper['refIpLayerConfig'].iloc[0]
                IpLayerConfigVal = strOper.split(';')[0].split(',')[-1].split('=')[-1]
                ipNoList = dfIpLayer.loc[dfIpLayer['MEID'] == str(fea_2), 'ipNo'].to_list()
                for i in range(30):
                    if str(i) not in ipNoList:
                        ipNoVal = i
                        break
            faripadd1 = data['远端地址'].iloc[0]
            farips = faripadd1.split(',')
            for farip in farips:
                SctpVal = 100
                for i in range(704):
                    if str(i + 1) not in SctpList:
                        SctpVal = i + 1
                        SctpList.append(str(i + 1))
                        break
                sctpNoVal = 100
                for i in range(704):
                    if str(i) not in sctpNoList:
                        sctpNoVal = i
                        sctpNoList.append(str(i))
                        break
                ipcnt = len(farip.split(';'))
                if name[2] == 'TDD':
                    textTDD += f'CREATE:MOC="Sctp",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},TransportNetwork=1,' \
                               f'Sctp={str(SctpVal)}",ATTRIBUTES="minRTO=500,userLabel=SCTP,localPort=36412,' \
                               f'maxRTO=5000,remotePort=36412,Sctp={str(SctpVal)},sctpNo={str(sctpNoVal)},maxAssoRetran=10,' \
                               f'sctpType=0,dscp=46,delayAckTime=200,refIpLayerConfig=\\"'
                    textTDD += f'SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)};' * (ipcnt-1)
                    textTDD += f'SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)}\\",' \
                               f'maxInitRetran=5,maxPathRetran=5,radioMode=32,congestEndure=null,inOutStreamNum=2,' \
                               f'hbInterval=5000,initRTO=1000,remoteAddr=\\"{str(farip)}\\",primaryPathNo=0",EXTENDS="";\n'
                elif name[2] == 'FDD':
                    textFDD += f'CREATE:MOC="Sctp",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},TransportNetwork=1,' \
                               f'Sctp={str(SctpVal)}",ATTRIBUTES="minRTO=500,userLabel=sctp,localPort=36412,' \
                               f'maxRTO=5000,remotePort=36412,Sctp={str(SctpVal)},sctpNo={str(sctpNoVal)},maxAssoRetran=10,' \
                               f'sctpType=0,dscp=46,delayAckTime=200,refIpLayerConfig=\\"'
                    textFDD += f'SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)};' * (ipcnt-1)
                    textFDD += f'SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)}\\",' \
                               f'maxInitRetran=5,maxPathRetran=5,radioMode=16,congestEndure=null,' \
                               f'inOutStreamNum=2,hbInterval=5000,initRTO=1000,remoteAddr=\\"{str(farip)}\\",' \
                               f'primaryPathNo=0",EXTENDS="";\n'
            ServiceList = dfServiceMap.loc[dfServiceMap['MEID'] == str(fea_2), 'ServiceMap'].to_list()
            ServiceMapVal = 100
            for i in range(1,32,1):
                if str(i) not in ServiceList:
                    ServiceMapVal = i
                    break
            if name[2] == 'TDD':
                textTDD += f'CREATE:MOC="ServiceMap",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},TransportNetwork=1,ServiceMap={str(ServiceMapVal)}",' \
                           f'ATTRIBUTES="tdsServiceDscpMap=null,ServiceMap={str(ServiceMapVal)},refIpLayerConfig=\\"SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                           f'ConfigSet=0,TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)}\\",refBandwidthResource=\\"SubNetwork={str(fea_1)},' \
                           f'MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,BandwidthResourceGroup=1,BandwidthResource=1\\",' \
                           f'lteServiceType=null,refOperator=\\"SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,' \
                           f'Operator={str(operVal)}\\",tddServiceDscpMap=(OBJ)' + \
                           '[{serviceDscp31=30,serviceDscp30=29,serviceDscp35=34,serviceDscp34=33,serviceDscp33=32,' \
                           'serviceDscp32=31,serviceDscp39=38,serviceDscp38=37,serviceDscp37=36,serviceDscp36=35,' \
                           'serviceDscp60=59,serviceDscp20=19,serviceDscp64=63,serviceDscp63=62,serviceDscp62=61,' \
                           'serviceDscp61=60,serviceDscp9=8,serviceDscp29=28,serviceDscp2=1,serviceDscp24=23,' \
                           'serviceDscp1=0,serviceDscp23=22,serviceDscp4=3,serviceDscp22=21,serviceDscp3=2,' \
                           'serviceDscp21=20,serviceDscp6=5,serviceDscp28=27,serviceDscp5=4,serviceDscp27=26,' \
                           'serviceDscp8=7,serviceDscp26=25,serviceDscp7=6,serviceDscp25=24,serviceDscp53=52,' \
                           'serviceDscp52=51,serviceDscp51=50,serviceDscp50=49,serviceDscp19=18,serviceDscp18=17,' \
                           'serviceDscp13=12,serviceDscp57=56,serviceDscp12=11,serviceDscp56=55,serviceDscp11=10,' \
                           'serviceDscp55=54,serviceDscp10=9,serviceDscp54=53,serviceDscp17=16,serviceDscp16=15,' \
                           'serviceDscp15=14,serviceDscp59=58,serviceDscp14=13,serviceDscp58=57,serviceDscp42=41,' \
                           'serviceDscp41=40,serviceDscp40=39,serviceDscp46=45,serviceDscp45=44,serviceDscp44=43,' \
                           'serviceDscp43=42,serviceDscp49=48,serviceDscp48=47,serviceDscp47=46}]",EXTENDS="";\n'

            elif name[2] == 'FDD':
                textFDD += f'CREATE:MOC="ServiceMap",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},TransportNetwork=1,ServiceMap={str(ServiceMapVal)}",' \
                           f'ATTRIBUTES="enableSlaveFlag=null,ServiceMap={str(ServiceMapVal)},refIpLayerConfig=\\"SubNetwork={str(fea_1)},' \
                           f'MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,IpLayerConfig={str(IpLayerConfigVal)}\\",refBandwidthResource=\\"SubNetwork={str(fea_1)},' \
                           f'MEID={str(fea_2)},ConfigSet=0,TransportNetwork=1,BandwidthResourceGroup=1,BandwidthResource=1\\",fddServiceDscpMap=(OBJ)' + \
                           '[{serviceDscp31=30,serviceDscp30=29,serviceDscp35=34,serviceDscp34=33,serviceDscp33=32,' \
                           'serviceDscp32=31,serviceDscp39=38,serviceDscp38=37,serviceDscp37=36,serviceDscp36=35,' \
                           'serviceDscp60=59,serviceDscp20=19,serviceDscp64=63,serviceDscp63=62,serviceDscp62=61,' \
                           'serviceDscp61=60,serviceDscp9=8,serviceDscp29=28,serviceDscp2=1,serviceDscp24=23,' \
                           'serviceDscp1=0,serviceDscp23=22,serviceDscp4=3,serviceDscp22=21,serviceDscp3=2,' \
                           'serviceDscp21=20,serviceDscp6=5,serviceDscp28=27,serviceDscp5=4,serviceDscp27=26,' \
                           'serviceDscp8=7,serviceDscp26=25,serviceDscp7=6,serviceDscp25=24,serviceDscp53=52,' \
                           'serviceDscp52=51,serviceDscp51=50,serviceDscp50=49,serviceDscp19=18,serviceDscp18=17,' \
                           'serviceDscp13=12,serviceDscp57=56,serviceDscp12=11,serviceDscp56=55,serviceDscp11=10,' \
                           'serviceDscp55=54,serviceDscp10=9,serviceDscp54=53,serviceDscp17=16,serviceDscp16=15,' \
                           'serviceDscp15=14,serviceDscp59=58,serviceDscp14=13,serviceDscp58=57,serviceDscp42=41,' \
                           'serviceDscp41=40,serviceDscp40=39,serviceDscp46=45,serviceDscp45=44,serviceDscp44=43,' \
                           'serviceDscp43=42,serviceDscp49=48,serviceDscp48=47,serviceDscp47=46}],' \
                           'gsmServiceDscpMap=null,nbServiceDscpMap=null,lteServiceType=null,refOperator=\\"' + \
                           f'SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,Operator={str(operVal)}\\"",EXTENDS="";\n'
            for idx,row in data.iterrows():
                fea_4 = row['小区ID']
                if name[2] == 'TDD':
                    textTDD += f'UPDATE:MOC="EUtranCellTDD",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                            f'ENBFunctionTDD={str(fea_3)},EUtranCellTDD={str(fea_4)}",ATTRIBUTES="refPlmn=\\"SubNetwork={str(fea_1)},' \
                            f'MEID={str(fea_2)},ConfigSet=0,Operator=1,Plmn=1;SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                            f'ConfigSet=0,Operator={str(operVal)},Plmn=1\\"",' \
                            f'EXTENDS="";\n'
                elif name[2] == 'FDD':
                    textFDD += f'UPDATE:MOC="EUtranCellFDD",MOI="SubNetwork={str(fea_1)},MEID={str(fea_2)},ENBFunctionFDD={str(fea_3)},' \
                            f'EUtranCellFDD={str(fea_4)}",ATTRIBUTES="refPlmn=\\"SubNetwork={str(fea_1)},MEID={str(fea_2)},' \
                            f'ConfigSet=0,Operator=1,Plmn=1;SubNetwork={str(fea_1)},MEID={str(fea_2)},ConfigSet=0,' \
                            f'Operator={str(operVal)},Plmn=1\\"",EXTENDS="";\n'
        else:
            data.loc[:,'Error'] = '该站点Operator未获取配置'
            dfNa = dfNa.append(data)
    return textTDD, textFDD, dfNa

def read_configNR(dirpath, paramDict):
    files = [i for i in listdir(dirpath) if splitext(i)[-1] == '.xlsx']
    dfRANCM_GNBCopy = pd.DataFrame()
    dfRANCM_addcellrelation = pd.DataFrame()
    for file in files:
        if '$' not in file and 'Done_' not in file:
            print(tm(), f"正在解析5G参数配置文件：{file}")
            df = pd.read_excel(join(dirpath, file), sheet_name=0, header=None, nrows=5)
            try:
                flag = df.iloc[3, 1]
            except:
                flag = ''
            if flag:
                if 'GNBCopy' in flag:
                    dfRANCM_GNBCopy = RANCM_GNBCopy_Done(dirpath, file, paramDict)
                elif 'addcellrelation_nr' in flag:
                    dfRANCM_addrt_nr = RANCM_addcellrelation_Done(dirpath, file, paramDict)
                elif 'RANCM-自定义' in flag:
                    dfRANCM_custorm = RANCM_custorm_Done(dirpath, file, paramDict)



def RANCM_GNBCopy_Done(dirpath, file, paramDict):
    path = join(dirpath, file)
    df_0 = pd.read_excel(path, sheet_name='TemplateInfo', engine='openpyxl')
    df_1 = pd.read_excel(path, sheet_name='Index', engine='openpyxl')
    df_2 = pd.read_excel(path, sheet_name='GNBCUCPFunction', header=0, engine='openpyxl')
    df_2 = RANCM_GNBCopy_Done_sht2(df_2)
    df_3 = pd.read_excel(path, sheet_name='NRCellCU', header=0, engine='openpyxl')
    df_3 = RANCM_GNBCopy_Done_sht3(df_3, paramDict)
    df_4 = pd.read_excel(path, sheet_name='GNBCUUPFunction', header=0, engine='openpyxl')
    df_4 = RANCM_GNBCopy_Done_sht4(df_4)
    df_5 = pd.read_excel(path, sheet_name='GNBDUFunction', header=0, engine='openpyxl')
    df_5 = RANCM_GNBCopy_Done_sht5(df_5)
    df_6 = pd.read_excel(path, sheet_name='SliceProfile', header=0, engine='openpyxl')
    df_6 = RANCM_GNBCopy_Done_sht6(df_6)
    try:
        df_7 = pd.read_excel(path, sheet_name='NSSAI', header=0, engine='openpyxl')
        df_7 = RANCM_GNBCopy_Done_sht7(df_7)
    except:
        df_7 = pd.DataFrame()
    df_8 = pd.read_excel(path, sheet_name='NRCellDU', header=0, engine='openpyxl')
    df_8 = RANCM_GNBCopy_Done_sht8(df_8, paramDict)
    df_9 = pd.read_excel(path, sheet_name='PlmnGroupList', header=0, engine='openpyxl')
    df_9 = RANCM_GNBCopy_Done_sht9(df_9)
    nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).\
                                      replace('-', '').replace(':', '').replace(' ','')
    xls_nm = join(dirpath, f'Done_{nowtime}_'+file)
    writer = pd.ExcelWriter(xls_nm)
    df_0.to_excel(writer, sheet_name='TemplateInfo', index=False, encoding='utf-8-sig')
    df_1.to_excel(writer, sheet_name='Index', index=False, encoding='utf-8-sig')
    df_2.to_excel(writer, sheet_name='GNBCUCPFunction', index=False, encoding='utf-8-sig')
    df_3.to_excel(writer, sheet_name='NRCellCU', index=False, encoding='utf-8-sig')
    df_4.to_excel(writer, sheet_name='GNBCUUPFunction', index=False, encoding='utf-8-sig')
    df_5.to_excel(writer, sheet_name='GNBDUFunction', index=False, encoding='utf-8-sig')
    df_6.to_excel(writer, sheet_name='SliceProfile', index=False, encoding='utf-8-sig')
    df_7.to_excel(writer, sheet_name='NSSAI', index=False, encoding='utf-8-sig')
    df_8.to_excel(writer, sheet_name='NRCellDU', index=False, encoding='utf-8-sig')
    df_9.to_excel(writer, sheet_name='PlmnGroupList', index=False, encoding='utf-8-sig')
    writer.save()

def RANCM_GNBCopy_Done_sht2(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBCUCPFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col == 'gNBIdLength':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@',''))
        elif col == 'PlmnIdListCU_pLMNId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = '460-15'
        elif col == 'assoType':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'NG/S1/Iub/Abis 偶联[1]'
    return df

def RANCM_GNBCopy_Done_sht3(df, paramDict):
    cellnameDict = {k: v[0] for k, v in paramDict.items()}
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBCUCPFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col == 'moId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@',''))
        elif col == 'userLabel':
            df.loc[df['ManagedElementType'] == 'ITBBU', col] = df[df['ManagedElementType'] == 'ITBBU'].apply(
                                                    lambda x: get_userLabel(x, cellnameDict), axis=1)
    df.loc[df['ManagedElementType'] == 'ITBBU', 'moId'] = df.loc[df['ManagedElementType'] == 'ITBBU', 'moId'].map(lambda x: str(int(x) + 70))
    return df


def RANCM_GNBCopy_Done_sht4(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBCUUPFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col == 'pLMNIdList':
            df.loc[df['ManagedElementType']=='ITBBU', col] = '460-15'
    return df


def RANCM_GNBCopy_Done_sht5(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBDUFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col == 'PlmnIdList_pLMNId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = '460-15'
    return df

def RANCM_GNBCopy_Done_sht6(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBDUFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col in ['nssiId','sliceProfileId','coverageAreaTAList']:
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@',''))
        elif col == 'pLMNIdList':
            df.loc[df['ManagedElementType'] == 'ITBBU', col] = '460-15'
    df.drop_duplicates('GNBDUFunctionMoId', keep='first', inplace=True)
    df.loc[df['ManagedElementType']=='ITBBU', 'sliceProfileId'] = '1'
    return df

def RANCM_GNBCopy_Done_sht7(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBDUFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col in ['nssiId','sliceProfileId','moId','sst','sd']:
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@',''))
        elif col == 'pLMNIdList':
            df.loc[df['ManagedElementType'] == 'ITBBU', col] = '460-15'
    df.drop_duplicates('GNBDUFunctionMoId', keep='first', inplace=True)
    for col in ['nssiId','sliceProfileId','moId','sst']:
        df.loc[df['ManagedElementType'] == 'ITBBU', col] = '1'
    return df

def get_userLabel(x, cellnameDict):
    eid = x['ManagedElement']
    moId = x['moId']
    k = str(eid) +'_' + str(moId)
    try:
        return '46015' + cellnameDict[k]
    except:
        return ''

def get_tac(x, tacDict):
    eid = x['ManagedElement']
    moId = x['moId']
    k = str(eid) +'_' + str(moId)
    try:
        return tacDict[k]
    except:
        return ''

def RANCM_GNBCopy_Done_sht8(df, paramDict):
    cellnameDict = {k:v[0] for k,v in paramDict.items()}
    tacDict = {k: v[2] for k, v in paramDict.items()}
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBDUFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col in ['nssiId','sliceProfileId','moId','sst','sd']:
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@',''))
        elif col == 'userLabel':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[df['ManagedElementType']=='ITBBU'].apply(lambda x:get_userLabel(x, cellnameDict),axis=1)
        elif col == 'tac':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df.apply(lambda x:get_tac(x, tacDict),axis=1)
    df.loc[df['ManagedElementType'] == 'ITBBU', 'moId'] = df.loc[df['ManagedElementType']=='ITBBU','moId'].map(lambda x: str(int(x) + 70))
    return df

def RANCM_GNBCopy_Done_sht9(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col == 'GNBDUFunctionMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@460-00','460-15'))
        elif col == 'refPlmnIdList':
            df.loc[df['ManagedElementType'] == 'ITBBU', col] = '460-15'
        elif col == 'NRCellDUMoId':
            df.loc[df['ManagedElementType']=='ITBBU', col] = df[col].map(lambda x:x.replace('@@',''))
    df.loc[df['ManagedElementType'] == 'ITBBU', 'NRCellDUMoId'] = df.loc[df['ManagedElementType'] == 'ITBBU', 'NRCellDUMoId'].map(
        lambda x: str(int(x) + 70))
    return df


def RANCM_addcellrelation_Done(dirpath, file, paramDict):
    path = join(dirpath, file)
    df_0 = pd.read_excel(path, sheet_name='TemplateInfo', engine='openpyxl')
    df_1 = pd.read_excel(path, sheet_name='Index', engine='openpyxl')
    df_2 = pd.read_excel(path, sheet_name='ExternalNRCellCU', header=0, engine='openpyxl')
    df_2 = RANCM_addcellrelation_Done_sht23(df_2,paramDict)
    df_3 = pd.read_excel(path, sheet_name='SsbMeasInfo', header=0, engine='openpyxl')
    df_3 = RANCM_addcellrelation_Done_sht23(df_3, paramDict)
    df_4 = pd.read_excel(path, sheet_name='CsiRsMeasInfo', header=0, engine='openpyxl')
    df_5 = pd.read_excel(path, sheet_name='NRCellRelation', header=0, engine='openpyxl')
    df_5 = RANCM_addcellrelation_Done_sht5(df_5)
    # df_6 = pd.read_excel(path, sheet_name='ExternalEutranCellTDD', header=0, engine='openpyxl')
    # df_7 = pd.read_excel(path, sheet_name='ExternalEutranCellFDD', header=0, engine='openpyxl')
    # df_8 = pd.read_excel(path, sheet_name='EutranCellRelation', header=0, engine='openpyxl')

    nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).\
                                            replace('-', '').replace(':', '').replace(' ','')
    xls_nm = join(dirpath, f'Done_{nowtime}_' + file)
    writer = pd.ExcelWriter(xls_nm)
    df_0.to_excel(writer, sheet_name='TemplateInfo', index=False, encoding='utf-8-sig')
    df_1.to_excel(writer, sheet_name='Index', index=False, encoding='utf-8-sig')
    df_2.to_excel(writer, sheet_name='ExternalNRCellCU', index=False, encoding='utf-8-sig')
    df_3.to_excel(writer, sheet_name='SsbMeasInfo', index=False, encoding='utf-8-sig')
    df_4.to_excel(writer, sheet_name='CsiRsMeasInfo', index=False, encoding='utf-8-sig')
    df_5.to_excel(writer, sheet_name='NRCellRelation', index=False, encoding='utf-8-sig')
    # df_6.to_excel(writer, sheet_name='ExternalEutranCellTDD', index=False, encoding='utf-8-sig')
    # df_7.to_excel(writer, sheet_name='ExternalEutranCellFDD', index=False, encoding='utf-8-sig')
    # df_8.to_excel(writer, sheet_name='EutranCellRelation', index=False, encoding='utf-8-sig')
    writer.save()

def filter_nr(paramDict,*args):
    for xs, ys in args:
        break
    for x, y in zip(xs.values, ys.values):
        try:
            xvalue = paramDict[str(x)][1]
            yvalue = paramDict[str(y)][1]
            if xvalue != yvalue:
                return True
            else:
                return False
        except:
            return False


def RANCM_addcellrelation_Done_sht23(df, paramDict):
    df.reset_index(drop=False,inplace=True)
    # df = df.groupby('index', as_index=True).filter(
    #     lambda x: filter_nr(paramDict, [x['sourceGNBId'], x['targetGNBId']]))
    shareDict = {k:v[-1] for k,v in paramDict.items() if v[-1]=='Y'}
    df.loc[:, '邻区是否改造'] = df.apply(lambda x:shareDict.get(x['targetGNBId']+'_'+x['targetCellLocalId']), axis=1)
    df = df[(df['邻区是否改造'] != 'Y')]
    df = df[(df['sourcePLMNId'] != '460-15') & (df['targetPLMNId'] != '460-15')]
    df.drop('邻区是否改造', axis=1, inplace=True)
    if len(df) > 0:
        for col in df.columns:
            if col in ['sourcePLMNId','targetPLMNId','pLMNIdList']:
                df.loc[df['ManagedElementType'] == 'ITBBU', col] = '460-15'
            elif col == 'targetCellLocalId':
                df.loc[df['ManagedElementType'] == 'ITBBU', col] = df.loc[
                    df['ManagedElementType'] == 'ITBBU', col].map(lambda x: str(int(x) + 70))
            elif col == 'userLabel':
                df.loc[df['ManagedElementType'] == 'ITBBU', col] = df[df['ManagedElementType'] == 'ITBBU'].apply(lambda x:f"46015{x[col]}", axis=1)
        return df
    else:
        return pd.DataFrame(columns=df.columns)

def RANCM_addcellrelation_Done_sht5(df):
    for col in df.columns:
        if col == 'MODIND':
            df.loc[df['ManagedElementType']=='ITBBU', col] = 'A'
        elif col in ['sourcePlmn', 'targetPlmn']:
            df.loc[df['ManagedElementType'] == 'ITBBU', col] = '460-15'
        elif col in ['sourceCellId', 'targetCellId']:
            df.loc[df['ManagedElementType'] == 'ITBBU', col] = df.loc[
                df['ManagedElementType'] == 'ITBBU', col].map(lambda x: str(int(x) + 70))
    return df

def RANCM_custorm_Done(dirpath, file, paramDict):
    path = join(dirpath, file)
    df_0 = pd.read_excel(path, sheet_name='TemplateInfo', engine='openpyxl')
    df_1 = pd.read_excel(path, sheet_name='Index', engine='openpyxl')
    df_2 = pd.read_excel(path, sheet_name='Sctp', header=0, engine='openpyxl')
    df_2, tranIPDict = RANCM_custorm_Done_sht2(df_2, paramDict)
    try:
        df_3 = pd.read_excel(path, sheet_name='ExternalEutranCellTDD', header=0, engine='openpyxl')
    except:
        df_3 = pd.DataFrame()
    try:
        df_4 = pd.read_excel(path, sheet_name='ExternalEutranCellFDD', header=0, engine='openpyxl')
    except:
        df_4 = pd.DataFrame()
    try:
        df_5 = pd.read_excel(path, sheet_name='NSSAI', header=0, engine='openpyxl')
        df_5 = RANCM_custorm_Done_sht5(df_5)
    except:
        df_5 = pd.DataFrame()
    try:
        df_6 = pd.read_excel(path, sheet_name='NRPhysicalCellDU', header=0, engine='openpyxl')
    except:
        df_6 = pd.DataFrame()
    # df_6 = RANCM_custorm_Done_sht6(df_6)
    df_7 = pd.read_excel(path, sheet_name='ServiceMap5g', header=0, engine='openpyxl')
    df_7 = RANCM_custorm_Done_sht7(df_7, tranIPDict)
    try:
        df_8 = pd.read_excel(path, sheet_name='NgAp', header=0, engine='openpyxl')
        df_8 = RANCM_custorm_Done_sht8(df_8, df_2)
    except:
        df_8 = pd.DataFrame()

    nowtime = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace('-', '').replace(':', '').replace(' ','')
    xls_nm = join(dirpath, f'Done_{nowtime}_' + file)
    writer = pd.ExcelWriter(xls_nm)
    df_0.to_excel(writer, sheet_name='TemplateInfo', index=False, encoding='utf-8-sig')
    df_1.to_excel(writer, sheet_name='Index', index=False, encoding='utf-8-sig')
    df_2.to_excel(writer, sheet_name='Sctp', index=False, encoding='utf-8-sig')
    if len(df_3)>0:
        df_3.to_excel(writer, sheet_name='ExternalEutranCellTDD', index=False, encoding='utf-8-sig')
    if len(df_4) > 0:
        df_4.to_excel(writer, sheet_name='ExternalEutranCellFDD', index=False, encoding='utf-8-sig')
    if len(df_5) > 0:
        df_5.to_excel(writer, sheet_name='NSSAI', index=False, encoding='utf-8-sig')
    if len(df_6) > 0:
        df_6.to_excel(writer, sheet_name='NRPhysicalCellDU', index=False, encoding='utf-8-sig')
    df_7.to_excel(writer, sheet_name='ServiceMap5g', index=False, encoding='utf-8-sig')
    df_8.to_excel(writer, sheet_name='NgAp', index=False, encoding='utf-8-sig')
    writer.save()

def RANCM_custorm_Done_sht2(dfDot, paramDict):
    ipDict = {str(k.split('_')[0]):v[-2] for k,v in paramDict.items()}
    dfRes = dfDot.iloc[:4]
    moIdDict = {}
    for a, b in dfDot.groupby('ManagedElement'):
        moIdDict[a] = b['moId'].to_list()
    dfDot = dfDot[(dfDot['localPort']=='38412') & (dfDot['remotePort']=='38412')]
    tranIPDict = {}
    for idx, df in dfDot.groupby('ManagedElement'):
        if idx in ['网元ID','string','Primary Key']:
            pass
        else:
            tranIPDict[str(idx)] = df['refIp'].iloc[0].split(';')[0]
            tranIPs = df['refIp'].iloc[0]
            try:
                ipadds = ipDict[str(idx)].split(';')
            except:
                ipadds = []
            moIdList = moIdDict[idx]
            moIds = []
            for i in range(5000):
                if str(i) not in moIdList:
                    moIds.append(str(i))
                if len(moIds) == len(ipadds):
                    break
            for c, ipadd in enumerate(ipadds):
                df1 = df.iloc[:1,:]
                df1.loc[:,'remoteIp'] = ';'.join([i for i in ipadd.split(',')])
                df1.loc[:, 'moId'] = moIds[c]
                df1.loc[:, 'ldn'] = df1['moId'].map(lambda x:f"TransportNetwork=1,Sctp={x}")
                df1.loc[:, 'refIp'] = tranIPs
                df1.loc[:, 'inOutStreamNum'] = '3'
                df1.loc[:, 'dscp']  = '46'
                df1.loc[:, 'assoType'] = df1['assoType'].map(lambda x: x.split('[')[-1].replace(']', ''))
                dfRes = dfRes.append(df1)
    dfRes.loc[dfRes['ManagedElementType'] == 'ITBBU', 'MODIND'] = 'A'
    return dfRes, tranIPDict

def get_NSSAI(x):
    eid = x['ManagedElement']
    txtList = x['ldn'].split(',')
    NetworkSliceSubnet = txtList[1].split('=')[-1]
    SliceProfile = txtList[1].split('=')[-1]
    NSSAI = txtList[1].split('=')[-1]
    txtStr = f"GNBDUFunction=460-15_{str(eid)},NetworkSliceSubnet={str(NetworkSliceSubnet)}," \
             f"SliceProfile={str(SliceProfile)},NSSAI={str(NSSAI)}"
    return txtStr

def RANCM_custorm_Done_sht5(df):
    dfRes = df.iloc[:4,:]
    df = df.loc[df['sst']=='1']
    df.loc[df['ManagedElementType'] == 'ITBBU', 'MODIND'] = 'A'
    df.loc[df['ManagedElementType'] == 'ITBBU', 'ldn'] = df[df['ManagedElementType'] == 'ITBBU'].apply(lambda x:get_NSSAI(x),axis=1)
    dfRes = dfRes.append(df)
    return dfRes

def RANCM_custorm_Done_sht6(df):
    df.loc[df['ManagedElementType'] == 'ITBBU', 'MODIND'] = 'A'
    df.loc[df['ManagedElementType'] == 'ITBBU', 'nrPhysicalCellDUId'] = \
        df.loc[df['ManagedElementType'] == 'ITBBU', 'nrPhysicalCellDUId'].map(lambda x: str(int(x) + 70))
    return df


def RANCM_custorm_Done_sht7(dfDot, tranIPDict):
    dfRes = dfDot.iloc[:4]
    for idx, df in dfDot.groupby('ManagedElement'):
        if idx in ['网元ID', 'string', 'Primary Key']:
            pass
        else:
            try:
                tranIP = tranIPDict[idx]
            except:
                tranIP = ''
            if tranIP:
                moIdList = df['moId'].to_list()
                for i in range(1,255,1):
                    if str(i) not in moIdList:
                        moIdValue = str(i)
                        break
                df1 = df.loc[df['refIp']==tranIP]
                # df1.loc[:, 'moId'] = moIdValue
                df1.loc[:, 'ldn'] = df1['moId'].map(lambda x:f"TransportNetwork=1,ServiceMap5g={x}")
                df1.loc[:, 'plmn'] = '460-00;460-15'
                df1.loc[:, 'castType'] = df1['castType'].map(lambda x:x.split('[')[-1].replace(']',''))
                dfRes = dfRes.append(df1)
    dfRes.loc[dfRes['ManagedElementType'] == 'ITBBU', 'MODIND'] = 'M'
    return dfRes

def RANCM_custorm_Done_sht8(dfDot,dfm):
    dfRes = dfDot.iloc[:4,:]
    for idx, df in dfDot.groupby('ManagedElement'):
        if idx in ['网元ID', 'string', 'Primary Key']:
            pass
        else:
            dfn = dfm[dfm['ManagedElement'] == str(idx)]
            df1 = df.iloc[:len(dfn)]
            df1.reset_index(drop=True, inplace=True)
            moIdList = df['moId'].to_list()
            moIds = []
            for i in range(1,5000,1):
                if str(i) not in moIdList:
                    moIds.append(str(i))
                if len(moIds) == len(dfn):
                    break
            for a,b in df1.iterrows():
                df1.iloc[a, 6] = moIds[a]
                df1.iloc[a ,7] = dfn['moId'].iloc[a]
                df1.iloc[a, 8] = 'true'
                df1.iloc[a, 5] = f"GNBCUCPFunction=460-15_{idx},EPNgC=1,NgAp={moIds[a]}"
            dfRes = dfRes.append(df1)
    dfRes.loc[dfRes['ManagedElementType'] == 'ITBBU', 'MODIND'] = 'A'
    return dfRes
