# coding:utf8

import pandas as pd
from os import listdir
from os.path import join,splitext,dirname
import time,datetime
from hwmmlTool import mml_jx

def tm():
    return time.strftime("%Y-%m-%d %H:%M:%S") + ':'


def read_param(path):
    try:
        df = pd.read_csv(path, encoding='utf8')
    except:
        df = pd.read_csv(path, encoding='gbk')
    return df

def getDistNum(dataList, *args):
    dataList = [int(i) for i in dataList]
    start, end, step, num = args
    res = []
    for i in range(start, end, step):
        if i not in dataList:
            res.append(str(i))
            if len(res) == num:
                return res

#按1000行进行数据切片拆分
def df_yield(df,number=500):
    y = number
    x = 0
    while x<df.shape[0]:
        df_t = df.iloc[x:y,]
        yield df_t
        x = y
        y = y + number

def DfError(df, fea):
    if len(df)>0:
        df.loc[:, '参数命令'] = fea
        return df
    else:
        return pd.DataFrame(columns=['站名','异常类型','参数命令'])

def makeHwScripesLte(dfParam,configPath,splitNum,sDay):
    ScriptsDict = {} ; dferror = pd.DataFrame()
    dfCNOPERATOR,dferr = mml_jx(configPath, r'LST CNOPERATOR:;', ['站名','运营商索引值'])
    dferr = DfError(dferr, 'LST CNOPERATOR')
    dferror = dferror.append(dferr)
    dfCNOPERATORTA,dferr = mml_jx(configPath, r'LST CNOPERATORTA:;', ['站名','本地跟踪区域标识','跟踪区域码'])
    dferr = DfError(dferr, 'LST CNOPERATORTA')
    dferror = dferror.append(dferr)
    dfEPGROUP,dferr = mml_jx(configPath, r'LST EPGROUP:;', ['站名','端节点对象归属组标识'])
    dferr = DfError(dferr, 'LST EPGROUP')
    dferror = dferror.append(dferr)
    dfSCTPPEER,dferr = mml_jx(configPath, r'LST SCTPPEER:;', ['站名','SCTP对端标识'])
    dferr = DfError(dferr, 'LST SCTPPEER')
    dferror = dferror.append(dferr)
    dfSCTPHOST,dferr = mml_jx(configPath, r'LST SCTPHOST:;', ['站名','SCTP本端标识','本端SCTP端口号'])
    dferr = DfError(dferr, 'LST SCTPHOST')
    dferror = dferror.append(dferr)
    dfUSERPLANEHOST,dferr = mml_jx(configPath, r'LST USERPLANEHOST:;', ['站名','用户面本端标识'])
    dferr = DfError(dferr, 'LST USERPLANEHOST')
    dferror = dferror.append(dferr)
    dfS1,dferr = mml_jx(configPath, r'LST S1:;', ['站名','S1对象标识'])
    dferr = DfError(dferr, 'LST S1')
    dferror = dferror.append(dferr)
    dfX2,dferr = mml_jx(configPath, r'LST X2:;', ['站名','X2对象标识'])
    dferr = DfError(dferr, 'LST X2')
    dferror = dferror.append(dferr)
    dfAPP,dferr = mml_jx(configPath, r'LST APP:;', ['站名', '应用ID'])
    dferr = DfError(dferr, 'LST APP')
    dferror = dferror.append(dferr)
    dflteNcell,dferr = mml_jx(configPath, r'LST EUTRANEXTERNALCELL:;', ['站名', '基站标识','小区标识'])
    dferr = DfError(dferr, 'LST EUTRANEXTERNALCELL')
    dferror = dferror.append(dferr)
    dfnrNcell,dferr = mml_jx(configPath, r'LST NREXTERNALCELL:;', ['站名', '基站标识', '小区标识'])
    dferr = DfError(dferr, 'LST NREXTERNALCELL')
    dferror = dferror.append(dferr)
    error_enbs = []
    if len(dferror)>0:
        error_enbs = list(dferror['站名'].unique())
    dfna = pd.DataFrame()
    for idxDot,dfDot in dfParam.groupby(['地市', 'OMC归属']):
        eomc = str(idxDot[1]); ecity = str(idxDot[0])
        dfSiteDups = dfDot.drop_duplicates('基站名称',keep='first')
        dfy = df_yield(dfSiteDups, splitNum)
        icnt = 1
        for dft in dfy:
            enbs = list(set(dft['基站名称'].to_list()))
            dfs = dfDot.loc[dfDot['基站名称'].isin(enbs)]
            texScriptsRes = ''
            backScriptsRes = ''
            neiborScriptsRes = ''
            rebootScriptsRes = ''
            neiborBackScriptsRes = ''
            enbNum = len(list(dfs['基站名称'].unique()))
            fname_1 = f"{idxDot[0]}_华为_LTE_{idxDot[1]}_{enbNum}_{sDay}_改造脚本无复位-{icnt}.txt"
            fname_2 = f"{idxDot[0]}_华为_LTE_{idxDot[1]}_{enbNum}_{sDay}_改造回退脚本-{icnt}.txt"
            fname_3 = f"{idxDot[0]}_华为_LTE_{idxDot[1]}_{enbNum}_{sDay}_邻区脚本-{icnt}.txt"
            fname_4 = f"{idxDot[0]}_华为_LTE_{idxDot[1]}_{enbNum}_{sDay}_邻区回退脚本-{icnt}.txt"
            fname_5 = f"{idxDot[0]}_华为_LTE_{idxDot[1]}_{enbNum}_{sDay}_复位脚本-{icnt}.txt"
            fname_6 = f"华为LTE未输出脚本异常明细_{sDay}.csv"
            for ename, df in dfs.groupby('基站名称'):
                if ename not in error_enbs:
                    texScripts = ''
                    backScripts = ''
                    neiborScripts = ''
                    rebootScripts = ''
                    neiborBackScripts = ''
                    print(tm(), f"正在配置共享共建数据：{ename}")
                    texScripts += 'MOD ENODEBSHARINGMODE:ENODEBSHARINGMODE=SHARED_FREQ;{' + ename + '}\n'
                    texScripts += 'ADD CNOPERATOR:CNOPERATORID=1,CNOPERATORNAME="CBN",CNOPERATORTYPE=CNOPERATOR_SECONDARY,MCC="460",MNC="15";{' + ename + '}\n'
                    TRACKINGAREAIDList = dfCNOPERATORTA.loc[dfCNOPERATORTA['站名'] == ename, '本地跟踪区域标识'].to_list()
                    if len(TRACKINGAREAIDList)>0:
                        TACList = dfCNOPERATORTA.loc[dfCNOPERATORTA['站名'] == ename, '跟踪区域码'].to_list()
                        res = getDistNum(TRACKINGAREAIDList, 200,1000,100,1)
                        TRACKINGAREAID = res[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST CNOPERATORTA']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD CNOPERATORTA:TRACKINGAREAID=%s,CNOPERATORID=1,TAC=%s;{' %(TRACKINGAREAID,TACList[0]) + ename + '}\n'
                    EPGROUPIDList = dfEPGROUP.loc[dfEPGROUP['站名'] == ename, '端节点对象归属组标识'].to_list()
                    if len(EPGROUPIDList) > 0:
                        resEpgroupid = getDistNum(EPGROUPIDList, 111,1000,1,2)
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST EPGROUP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    backScripts += 'RMV EPGROUP:EPGROUPID=%s;{' % resEpgroupid[0] + ename + '}\n'
                    texScripts += 'ADD EPGROUP:EPGROUPID=%s,USERLABEL="CBN",IPPMSWITCH=DISABLE,APPTYPE=NULL;{' % resEpgroupid[0] + ename + '}\n'
                    ipGroups = []; ipg = []
                    for colIdx, col in enumerate(list(df.columns)):
                        if colIdx > 3:
                            ipg.append(df[col].iloc[0])
                            if len(ipg) == 2:
                                ipGroups.append(ipg)
                                ipg = []
                    SCTPPEERIDList = dfSCTPPEER.loc[dfSCTPPEER['站名'] == ename, 'SCTP对端标识'].to_list()
                    if len(SCTPPEERIDList) > 0:
                        resSctpList = getDistNum(SCTPPEERIDList, 10, 1000, 1, len(ipGroups))
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST SCTPPEER']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    for ipIdx, ip in enumerate(ipGroups):
                        SCTPPEERID = resSctpList[ipIdx]
                        texScripts += 'ADD SCTPPEER:SCTPPEERID=%s,IPVERSION=IPv4,SIGIP1V4="%s",SIGIP1SECSWITCH=DISABLE,SIGIP2V4="%s",' \
                                      'SIGIP2SECSWITCH=DISABLE,PN=36412,SIMPLEMODESWITCH=SIMPLE_MODE_OFF,' \
                                      'USERLABEL="CBN-MME";{' %(SCTPPEERID,ip[0],ip[1])  + ename + '}\n'
                        backScripts += 'RMV SCTPPEER:SCTPPEERID=%s;{' %SCTPPEERID  + ename + '}\n'
                    SCTPHOSTIDList = dfSCTPHOST.loc[(dfSCTPHOST['站名'] == ename) & (dfSCTPHOST['本端SCTP端口号'] == '36412'), 'SCTP本端标识'].to_list()
                    if len(SCTPHOSTIDList)>0:
                        SCTPHOSTID = SCTPHOSTIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST SCTPHOST2EPGRP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD SCTPHOST2EPGRP:EPGROUPID=%s,SCTPHOSTID=%s;{' % (resEpgroupid[0], SCTPHOSTID)  + ename + '}\n'
                    backScripts += 'RMV EPGROUP:EPGROUPID=%s;{'  % resEpgroupid[0]  + ename + '}\n'
                    for i in range(len(resSctpList)):
                        texScripts += 'ADD SCTPPEER2EPGRP:EPGROUPID=%s,SCTPPEERID=%s;{' % (resEpgroupid[0], resSctpList[i])  + ename + '}\n'
                    UPHOSTIDList = dfUSERPLANEHOST.loc[(dfUSERPLANEHOST['站名'] == ename), '用户面本端标识'].to_list()
                    if len(UPHOSTIDList)>0:
                        UPHOSTID = UPHOSTIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST UPHOST2EPGRP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD UPHOST2EPGRP:EPGROUPID=%s,UPHOSTID=%s;{' % (resEpgroupid[0], UPHOSTID) + ename + '}\n'
                    S1IDList = dfS1.loc[(dfS1['站名'] == ename), 'S1对象标识'].to_list()
                    if len(S1IDList)>0:
                        S1ID = getDistNum(S1IDList, 31,1000,1,1)
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST S1ID']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD S1:S1ID=%s,CNOPERATORID=1,EPGROUPCFGFLAG=CP_UP_CFG,CPEPGROUPID=%s,UPEPGROUPID=%s;{' % \
                                  (S1ID[0],resEpgroupid[0],resEpgroupid[0]) + ename + '}\n'
                    texScripts += 'ADD EPGROUP:EPGROUPID=%s,USERLABEL="CBN",IPPMSWITCH=DISABLE,APPTYPE=NULL;{' % \
                                  resEpgroupid[1] + ename + '}\n'

                    SCTPHOSTIDList = dfSCTPHOST.loc[
                        (dfSCTPHOST['站名'] == ename) & (dfSCTPHOST['本端SCTP端口号'] != '36412'), 'SCTP本端标识'].to_list()
                    if len(SCTPHOSTIDList)>0:
                        SCTPHOSTID = SCTPHOSTIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST SCTPHOST2EPGRP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD SCTPHOST2EPGRP:EPGROUPID=%s,SCTPHOSTID=%s;{' % (resEpgroupid[1],SCTPHOSTID) + ename + '}\n'
                    texScripts += 'ADD UPHOST2EPGRP:EPGROUPID=%s,UPHOSTID=%s;{' % (resEpgroupid[1], UPHOSTID) + ename + '}\n'
                    X2IDList = dfX2.loc[(dfX2['站名'] == ename), 'X2对象标识'].to_list()
                    if len(X2IDList)>0:
                        X2ID = getDistNum(X2IDList, 1, 100, 1, 1)
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST X2']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD X2:X2ID=%s,CNOPERATORID=1,EPGROUPCFGFLAG=CP_UP_CFG,CPEPGROUPID=%s,UPEPGROUPID=%s;{' % \
                                  (X2ID[0], resEpgroupid[1], resEpgroupid[1]) + ename + '}\n'
                    for k, row in df.iterrows():
                        texScripts += 'ADD CELLOP:LOCALCELLID=%s,TRACKINGAREAID=%s;{' % (
                                                           row['本地小区标识'], TRACKINGAREAID) + ename + '}\n'
                        backScripts += 'RMV CELLOP:LOCALCELLID=%s,TRACKINGAREAID=%s;{' % (
                                                           row['本地小区标识'], TRACKINGAREAID) + ename + '}\n'
                    # texScripts += 'RST APP:AID=%s;{' %APPID + ename + '}\n'
                    backScripts += 'RMV X2:X2ID=%s;{' % X2ID[0] + ename + '}\n'
                    backScripts += 'RMV EPGROUP:EPGROUPID=%s;{' % resEpgroupid[1] + ename + '}\n'
                    backScripts += 'RMV S1:S1ID=%s;{' % S1ID[0] + ename + '}\n'
                    backScripts += 'RMV EPGROUP:EPGROUPID=%s;{' % resEpgroupid[0] + ename + '}\n'
                    for i in range(len(resSctpList)):
                        backScripts += 'RMV SCTPPEER:SCTPPEERID=%s;{' % resSctpList[i] + ename + '}\n'
                    backScripts += 'RMV CNOPERATORTA:TRACKINGAREAID=%s;{' % TRACKINGAREAID + ename + '}\n'
                    backScripts += 'RMV CNOPERATOR:CNOPERATORID=1;{' + ename + '}\n'
                    backScripts += 'MOD ENODEBSHARINGMODE:ENODEBSHARINGMODE=INDEPENDENT;{' + ename + '}\n'

                    # 邻区脚本
                    for k, row in dflteNcell[dflteNcell['站名'] == ename].iterrows():
                        sid = row['基站标识']; cid = row['小区标识']
                        neiborScripts += 'ADD EUTRANEXTERNALCELLPLMN:MCC="460",MNC="00",ENODEBID=%s,CELLID=%s,SHAREMCC="460",' \
                                         'SHAREMNC="15";{' %(str(sid),str(cid))  + ename + '}\n'
                        neiborBackScripts += 'RMV EUTRANEXTERNALCELLPLMN:MCC="460",MNC="00",' \
                                             'ENODEBID=%s,CELLID=%s,SHAREMCC="460",' \
                                             'SHAREMNC="15";{' %(str(sid),str(cid))  + ename + '}\n'
                    for k, row in dfnrNcell[dfnrNcell['站名'] == ename].iterrows():
                        sid = row['基站标识']; cid = row['小区标识']
                        neiborScripts += 'ADD NREXTERNALCELLPLMN:MCC="460",MNC="00",GNODEBID=%s,CELLID=%s,' \
                                         'SHAREDMCC="460",SHAREDMNC="15",NRNETWORKINGOPTION=SA;{' % (
                                         str(sid), str(cid)) + ename + '}\n'
                        neiborBackScripts += 'RMV NREXTERNALCELLPLMN:MCC="460",MNC="00",GNODEBID=%s,CELLID=%s,' \
                                             'SHAREDMCC="460",SHAREDMNC="15";{' % (str(sid), str(cid)) + ename + '}\n'

                    texScriptsRes += texScripts
                    backScriptsRes += backScripts
                    neiborScriptsRes += neiborScripts
                    neiborBackScriptsRes += neiborBackScripts
                    # 复位脚本
                    APPIDList = dfAPP.loc[(dfAPP['站名'] == ename), '应用ID'].to_list()
                    if len(APPIDList) > 0:
                        APPID = APPIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST APP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        continue
                    rebootScripts += 'RST APP:AID=%s;{' % APPID + ename + '}\n'
                    rebootScriptsRes += rebootScripts
                else:
                    print(tm(), f"{ename}网元断链，参数缺失！")

            if len(texScriptsRes)>0:
                ScriptsDict[fname_1] = texScriptsRes
            if len(backScriptsRes) > 0:
                ScriptsDict[fname_2] = backScriptsRes
            if len(neiborScriptsRes)>0:
                ScriptsDict[fname_3] = neiborScriptsRes
            if len(neiborBackScriptsRes)>0:
                ScriptsDict[fname_4] = neiborBackScriptsRes
            if len(rebootScriptsRes)>0:
                ScriptsDict[fname_5] = rebootScriptsRes
            icnt += 1
    dfNULL = pd.concat([dferror, dfna], axis=0)
    if len(dfNULL)>0:
        ScriptsDict[fname_6] = dfNULL
    return ScriptsDict


def makeHwScripesNr(dfParam,configPath,splitNum,sDay):
    ScriptsDict = {} ; dferror = pd.DataFrame()
    dfGNBOPERATOR, dferr = mml_jx(configPath, r'LST GNBOPERATOR:;', ['站名','运营商标识'])
    dferr = DfError(dferr, 'LST GNBOPERATOR')
    dferror = dferror.append(dferr)
    dfGNBCUNG, dferr = mml_jx(configPath, r'LST GNBCUNG:;', ['站名','gNodeB CU NG对象标识'])
    dferr = DfError(dferr, 'LST GNBCUNG')
    dferror = dferror.append(dferr)
    dfEPGROUP, dferr = mml_jx(configPath, r'LST EPGROUP:;', ['站名','端节点对象归属组标识'])
    dferr = DfError(dferr, 'LST EPGROUP')
    dferror = dferror.append(dferr)
    dfSCTPPEER, dferr = mml_jx(configPath, r'LST SCTPPEER:;', ['站名','SCTP对端标识'])
    dferr = DfError(dferr, 'LST SCTPPEER')
    dferror = dferror.append(dferr)
    dfSCTPHOST, dferr = mml_jx(configPath, r'LST SCTPHOST:;', ['站名','SCTP本端标识','本端SCTP端口号'])
    dferr = DfError(dferr, 'LST SCTPHOST')
    dferror = dferror.append(dferr)
    dfUSERPLANEHOST, dferr = mml_jx(configPath, r'LST USERPLANEHOST:;', ['站名','用户面本端标识','用户标签'])
    dferr = DfError(dferr, 'LST USERPLANEHOST')
    dferror = dferror.append(dferr)
    dfNREXTERNALNCELL, dferr = mml_jx(configPath, r'LST NREXTERNALNCELL:;', ['站名','gNodeB标识','小区标识','跟踪区域码'])
    dferr = DfError(dferr, 'LST NREXTERNALNCELL')
    dferror = dferror.append(dferr)
    dfGNBEUTRAEXTERNALCELL, dferr = mml_jx(configPath, r'LST GNBEUTRAEXTERNALCELL:;', ['站名','基站标识','小区标识'])
    dferr = DfError(dferr, 'LST GNBEUTRAEXTERNALCELL')
    dferror = dferror.append(dferr)
    dfAPP, dferr = mml_jx(configPath, r'LST APP:;', ['站名', '应用ID'])
    dferr = DfError(dferr, 'LST APP')
    dferror = dferror.append(dferr)
    dfGNBCUXN, dferr = mml_jx(configPath, r'LST GNBCUXN:;', ['站名', 'gNodeB CU Xn对象标识'])
    dferr = DfError(dferr, 'LST GNBCUXN')
    dferror = dferror.append(dferr)
    error_enbs = []
    if len(dferror)>0:
        error_enbs = list(dferror['站名'].unique())
    dfna = pd.DataFrame()
    for idxDot,dfDot in dfParam.groupby(['地市', 'OMC归属']):
        eomc = str(idxDot[1]); ecity = str(idxDot[0])
        dfSiteDups = dfDot.drop_duplicates('基站名称',keep='first')
        dfy = df_yield(dfSiteDups, splitNum)
        icnt = 1
        for dft in dfy:
            enbs = dft['基站名称'].to_list()
            dfs = dfDot[dfDot['基站名称'].isin(enbs)]
            texScriptsRes = ''
            backScriptsRes = ''
            neiborScriptsRes = ''
            rebootScriptsRes = ''
            neiborBackScriptsRes = ''
            # texScripts = ''
            # backScripts = ''
            # neiborScripts = ''
            # rebootScripts = ''
            # neiborBackScripts = ''
            enbNum = len(list(dfs['基站名称'].unique()))
            fname_1 = f"{idxDot[0]}_华为_NR_{idxDot[1]}_{enbNum}_{sDay}_改造脚本无复位-{icnt}.txt"
            fname_2 = f"{idxDot[0]}_华为_NR_{idxDot[1]}_{enbNum}_{sDay}_改造回退脚本-{icnt}.txt"
            fname_3 = f"{idxDot[0]}_华为_NR_{idxDot[1]}_{enbNum}_{sDay}_邻区脚本-{icnt}.txt"
            fname_4 = f"{idxDot[0]}_华为_NR_{idxDot[1]}_{enbNum}_{sDay}_邻区回退脚本-{icnt}.txt"
            fname_5 = f"{idxDot[0]}_华为_NR_{idxDot[1]}_{enbNum}_{sDay}_复位脚本-{icnt}.txt"
            fname_6 = f"华为LTE未输出脚本异常明细_{sDay}.csv"
            for ename, df in dfs.groupby('基站名称'):
                if ename not in error_enbs:
                    texScripts = ''
                    backScripts = ''
                    neiborScripts = ''
                    rebootScripts = ''
                    neiborBackScripts = ''
                    print(tm(), f"正在配置共享共建数据：{ename}")
                    for k,row in df.iterrows():
                        texScripts += 'ADD NRDUCELLOP:NRDUCELLID=%s,OPERATORID=0;{' %row['本地小区标识'] + ename + '}\n'
                        backScripts += 'RMV NRDUCELLOP:NRDUCELLID=%s,OPERATORID =1;{' %row['本地小区标识'] + ename + '}\n'
                    CUNGList = dfGNBCUNG.loc[dfGNBCUNG['站名'] == ename, 'gNodeB CU NG对象标识'].to_list()
                    # print(ename, "CUNGList", CUNGList)
                    if len(CUNGList) > 0:
                        for CUNGID in CUNGList:
                            texScripts += 'ADD GNBCUNGOP:GNBCUNGID=%s,OPERATORID=0;{' % CUNGID + ename + '}\n'
                            backScripts += 'RMV GNBCUNGOP:GNBCUNGID=%s,OPERATORID=0;{' % CUNGID + ename + '}\n'
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST GNBCUNGOP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue

                    for CUNGID in CUNGList:
                        backScripts += 'RMV GNBCUXNOP:GNBCUXNID=%s,OPERATORID=0;{' % CUNGID + ename + '}\n'
                        backScripts += 'RMV GNBCUXNOP:GNBCUXNID=%s,OPERATORID=1;{' % CUNGID + ename + '}\n'
                        break

                    texScripts += 'MOD GNBSHARINGMODE:GNBMULTIOPSHARINGMODE=SHARED_FREQ;{' + ename +'}\n'
                    texScripts += 'ADD GNBOPERATOR:OPERATORID=1,OPERATORNAME="CBN",MCC="460",MNC="15",' \
                                  'OPERATORTYPE=SECONDARY_OPERATOR,NRNETWORKINGOPTION=SA;{' + ename + '}\n'

                    EPGROUPIDList = dfEPGROUP.loc[(dfEPGROUP['站名'] == ename), '端节点对象归属组标识'].to_list()
                    if len(CUNGList) > 0:
                        resEpgroupid = getDistNum(EPGROUPIDList, 111, 1000, 1, 1)
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST EPGROUP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD EPGROUP:EPGROUPID=%s,USERLABEL="CBN",IPPMSWITCH=DISABLE,' \
                                  'APPTYPE=NULL;{' % resEpgroupid[0] + ename + '}\n'
                    backScripts += 'RMV EPGROUP:EPGROUPID=%s;{' % resEpgroupid[0] + ename + '}\n'
                    ipGroups = []; ipg = []
                    for colIdx, col in enumerate(list(df.columns)):
                        if colIdx > 3:
                            ipg.append(df[col].iloc[0])
                            if len(ipg) == 2:
                                ipGroups.append(ipg)
                                ipg = []
                    SCTPPEERIDList = dfSCTPPEER.loc[dfSCTPPEER['站名'] == ename, 'SCTP对端标识'].to_list()
                    if len(SCTPPEERIDList) > 0:
                        resSctpList = getDistNum(SCTPPEERIDList, 10, 1000, 1, len(ipGroups))
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST SCTPPEER']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    for ipIdx, ip in enumerate(ipGroups):
                        SCTPPEERID = resSctpList[ipIdx]
                        texScripts += 'ADD SCTPPEER:SCTPPEERID=%s,IPVERSION=IPv4,SIGIP1V4="%s",' \
                                      'SIGIP1SECSWITCH=DISABLE,SIGIP2V4="%s",' \
                                      'SIGIP2SECSWITCH=DISABLE,PN=38412,SIMPLEMODESWITCH=SIMPLE_MODE_OFF,' \
                                      'USERLABEL="CBN-AMF";{' %(SCTPPEERID,ip[0],ip[1])  + ename + '}\n'
                    SCTPHOSTIDList = dfSCTPHOST.loc[
                        (dfSCTPHOST['站名'] == ename) & (dfSCTPHOST['本端SCTP端口号'] == '38412'), 'SCTP本端标识'].to_list()
                    if len(SCTPHOSTIDList) > 0:
                        SCTPHOSTID = SCTPHOSTIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST SCTPHOST2EPGRP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD SCTPHOST2EPGRP:EPGROUPID=%s,SCTPHOSTID=%s;{' % (
                                                resEpgroupid[0], SCTPHOSTID) + ename + '}\n'
                    for i in range(len(resSctpList)):
                        texScripts += 'ADD SCTPPEER2EPGRP:EPGROUPID=%s,SCTPPEERID=%s;{' % (
                                                    resEpgroupid[0], resSctpList[i]) + ename + '}\n'
                    UPHOSTIDList = dfUSERPLANEHOST.loc[(dfUSERPLANEHOST['站名'] == ename) & (dfUSERPLANEHOST['用户标签'] != '2B-U'), '用户面本端标识'].to_list()
                    UPHOSTIDList = [int(i) for i in UPHOSTIDList]
                    UPHOSTIDList.sort(reverse=False)
                    if len(UPHOSTIDList) > 0:
                        UPHOSTID = UPHOSTIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST UPHOST2EPGRP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD UPHOST2EPGRP:EPGROUPID=%s,UPHOSTID=%s;{' % (
                                                        resEpgroupid[0], str(UPHOSTID)) + ename + '}\n'
                    resGNBCUNGID = getDistNum(CUNGList,5,100,1,1)
                    texScripts += 'ADD GNBCUNG:GNBCUNGID=%s,CPEPGROUPID=%s,UPEPGROUPID=%s;{' % (
                                                    resGNBCUNGID[0], resEpgroupid[0], resEpgroupid[0]) + ename + '}\n'
                    backScripts += 'RMV GNBCUNG: GNBCUNGID=%s;{' %resGNBCUNGID[0]  + ename + '}\n'
                    texScripts += 'ADD GNBCUNGOP:GNBCUNGID=%s,OPERATORID=1;{' % resGNBCUNGID[0]  + ename + '}\n'
                    backScripts += 'RMV GNBCUNGOP:GNBCUNGID=%s,OPERATORID=1;{' % resGNBCUNGID[0] + ename + '}\n'
                    GNBCUXNList = dfGNBCUXN.loc[dfGNBCUXN['站名'] == ename, 'gNodeB CU Xn对象标识'].to_list()
                    if len(GNBCUXNList)>0:
                        GNBCUXNList = [int(i) for i in GNBCUXNList]
                        GNBCUXNList.sort(reverse=False)
                        GNBCUXNLID = str(GNBCUXNList[0])
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST GNBCUXNOP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        error_enbs.append(ename)
                        error_enbs = list(set(error_enbs))
                        continue
                    texScripts += 'ADD GNBCUXNOP:GNBCUXNID=%s,OPERATORID=0;{' % GNBCUXNLID + ename + '}\n'
                    texScripts += 'ADD GNBCUXNOP:GNBCUXNID=%s,OPERATORID=1;{' % GNBCUXNLID + ename + '}\n'
                    for k, row in df.iterrows():
                        texScripts += 'ADD NRDUCELLOP:NRDUCELLID=%s,OPERATORID=1;{' % row['本地小区标识'] + ename + '}\n'
                        backScripts += 'RMV NRDUCELLOP:NRDUCELLID=%s,OPERATORID = 0;{' % row['本地小区标识'] + ename + '}\n'
                    backScripts += 'RMV GNBOPERATOR:OPERATORID=1;{' + ename + '}\n'
                    backScripts += 'MOD GNBSHARINGMODE:GNBMULTIOPSHARINGMODE=INDEPENDENT;{' + ename + '}\n'

                    # 邻区脚本
                    for k, row in dfGNBEUTRAEXTERNALCELL[dfGNBEUTRAEXTERNALCELL['站名'] == ename].iterrows():
                        sid = row['基站标识']; cid = row['小区标识']
                        neiborScripts += 'ADD GNBEUTRAEXTCELLPLMN:MCC="460",MNC="00",ENODEBID=%s,' \
                                         'CELLID= %s,SHAREDMCC="460", SHAREDMNC = "15";{' % (str(sid), str(cid)) + ename + '}\n'
                        neiborBackScripts += 'RMV GNBEUTRAEXTCELLPLMN:MCC="460",MNC="00",' \
                                             'ENODEBID=%s,CELLID= %s,SHAREDMCC="460", ' \
                                             'SHAREDMNC = "15";{' % (str(sid), str(cid)) + ename + '}\n'
                    for k, row in dfNREXTERNALNCELL[dfNREXTERNALNCELL['站名'] == ename].iterrows():
                        sid = row['gNodeB标识']; cid = row['小区标识']; tac = row['跟踪区域码']
                        neiborBackScripts += 'RMV NREXTERNALNCELLPLMN: MCC = "460", MNC = "00", ' \
                                         'GNBID = %s, CELLID = %s, SHAREDMCC = "460", ' \
                                         'SHAREDMNC = "15";{' % (
                                             str(sid), str(cid)) + ename + '}\n'
                        neiborScripts += 'ADD NREXTERNALNCELLPLMN: MCC = "460", MNC = "00",' \
                                         ' GNBID = %s, CELLID = %s, SHAREDMCC = "460",' \
                                         ' SHAREDMNC = "15", TAC = %s,' \
                                         ' NRNETWORKINGOPTION = SA;{' % (str(sid), str(cid), str(tac)) + ename + '}\n'

                    texScriptsRes += texScripts
                    backScriptsRes += backScripts
                    neiborScriptsRes += neiborScripts
                    neiborBackScriptsRes += neiborBackScripts

                    # 复位脚本
                    APPIDList = dfAPP.loc[(dfAPP['站名'] == ename), '应用ID'].to_list()
                    if len(APPIDList) > 0:
                        APPID = APPIDList[0]
                    else:
                        dfn = pd.DataFrame([[ename, '参数缺失', 'LST APP']], columns=['站名', '异常类型', '参数命令'])
                        dfna = dfna.append(dfn)
                        continue
                    rebootScripts += 'RST APP:AID=%s;{' % APPID + ename + '}\n'
                    rebootScriptsRes += rebootScripts
                else:
                    print(tm(), f"{ename}网元断链，参数缺失！")


            # if len(texScripts) > 0:
            #     ScriptsDict[fname_1] = texScripts
            # if len(backScripts) > 0:
            #     ScriptsDict[fname_2] = backScripts
            # if len(neiborScripts) > 0:
            #     ScriptsDict[fname_3] = neiborScripts
            # if len(neiborBackScripts) > 0:
            #     ScriptsDict[fname_4] = neiborBackScripts
            # if len(rebootScripts) > 0:
            #     ScriptsDict[fname_5] = rebootScripts

            if len(texScriptsRes) > 0:
                ScriptsDict[fname_1] = texScriptsRes
            if len(backScriptsRes) > 0:
                ScriptsDict[fname_2] = backScriptsRes
            if len(neiborScriptsRes) > 0:
                ScriptsDict[fname_3] = neiborScriptsRes
            if len(neiborBackScriptsRes) > 0:
                ScriptsDict[fname_4] = neiborBackScriptsRes
            if len(rebootScriptsRes) > 0:
                ScriptsDict[fname_5] = rebootScriptsRes
            icnt += 1
    dfNULL = pd.concat([dferror, dfna], axis=0)
    if len(dfNULL) > 0:
        ScriptsDict[fname_6] = dfNULL
    return ScriptsDict


