# -*- coding: utf-8 -*-

from os.path import splitext,join
from os import walk,chdir,remove,listdir
from pandas import DataFrame
import pandas as pd
import time

def tm():
    return time.strftime("%Y-%m-%d %H:%M:%S") + ':'

#解析mml文件
def mml_jx(configPath, order, cols, encode='gbk'):
    files = [i for i in listdir(configPath) if splitext(i)[1] == '.txt']
    data_list=[]; col_list=[]; single_columns= []; single_data= []; lst_dl=[];
    feas = ['本地小区标识', '用户面本端标识', '端节点对象归属组标识', '运营商标识', '用户面本端标识', 'gNodeB CU Xn对象标识', '本地跟踪区域标识', 'X2对象标识', '应用ID']
    feas2 = ['运营商索引值']
    for file in files:
        print(tm(), "正在解析华为MML报表文件：%s" % file)
        print(tm(), "当前解析参数命令为：%s" % order)
        a = 0; b = 0; c = 0; d = 0;
        m = 0; n = 0; k = 0; l = 0
        with open(join(configPath, file), encoding=encode) as f:
            while True:
                lines = f.readline().replace('   ', '  ')
                if not lines:
                    break
                item = [i for i in lines.rstrip().split('  ') if len(i) > 0]
                if len(item) > 0:
                    if '====失败命令===' in lines:
                        k = 1
                    elif k == 1 and '网元 : ' in lines:
                        dl_enb = lines.rstrip().split(' ')[2]
                        dic_dl = {}
                        dic_dl['站名'] = dl_enb
                        dic_dl['异常类型'] = '网元断链'
                        lst_dl.append(dic_dl)
                    elif '成功命令' in item[0]:
                        k = 0
                if k == 0 and len(item) > 0:
                    if ('命令-----' + order) in lines:
                        a = 1
                    elif a == 1 and item[0] == '报文 : +++':
                        lst_enb = item[1].rstrip().lstrip()
                        b = 1
                    elif a == 1 and b == 1:
                        if '执行成功' in lines:
                            c = 1
                        elif c == 1 and len(item) > 3 and item[0] in ['本地小区标识', 'SCTP对端标识', 'SCTP本端标识', 'S1对象标识','X2对象标识',
                                                                              'gNodeB CU NG对象标识', '用户面本端标识', '移动国家码','运营商索引值',
                                                                              '本地跟踪区域标识', '运营商标识','应用ID']:
                            columns = [i.rstrip().lstrip() for i in item if len(i) > 0]
                            columns.insert(0, '站名')
                            col_list = columns
                        elif c == 1 and len(item) > 3 and order not in lines and lines[0].isdigit():
                            data = [i.rstrip().lstrip() for i in item if len(i) > 0]
                            data.insert(0, lst_enb)
                            data_dict = dict(zip(columns, data))
                            data_list.append(data_dict)
                        elif c == 1 and len(item) == 3 and item[0].strip() in feas:
                            single_columns = ['站名']
                            single_data = [lst_enb]
                            single_columns.append(item[0].rstrip().lstrip())
                            single_data.append(item[2].rstrip().lstrip())
                            m = 1
                        elif c == 1 and len(item) == 3 and item[0].strip() in feas2 and order == 'LST CNOPERATOR:;':
                            single_columns = ['站名']
                            single_data = [lst_enb]
                            single_columns.append(item[0].rstrip().lstrip())
                            single_data.append(item[2].rstrip().lstrip())
                            m = 1
                        elif len(item) == 3 and '=' in lines and m == 1:
                            if len(item) == 3:
                                single_columns.append(item[0].rstrip().lstrip())
                                single_data.append(item[2].rstrip().lstrip())
                            elif len(item) == 2:
                                single_data[-1] = str(single_data[-1]) + '&' + str(item[1]).rstrip().lstrip()
                        elif a == 1 and b == 1 and 'END' in lines:
                            data_dict = dict(zip(single_columns, single_data))
                            data_list.append(data_dict)
                if a == 1 and b == 1 and c == 1 and '仍有后续报告输出' in lines:
                    l = 1
                elif a == 1 and b == 1 and c == 1 and l == 0 and 'END' in lines:
                    a = 0; b = 0; c = 0
                elif a == 1 and b == 1 and c == 1 and l == 1 and '共有' in lines:
                    data_dict = dict(zip(single_columns, single_data))
                    data_list.append(data_dict)
                    a = 0; b = 0; l = 0; c = 0
    if len(col_list) > 0:
        df = pd.DataFrame(data_list, columns=col_list)
    else:
        df = pd.DataFrame(data_list, columns=cols)
    if len(lst_dl) > 0:
        dferror = pd.DataFrame(lst_dl,columns=['站名','异常类型'])
    else:
        dferror = pd.DataFrame(columns=['站名','异常类型'])
    df.dropna(inplace=True)
    df = df[cols]
    df.drop_duplicates(list(df.columns),keep='first',inplace=True)
    dferror.drop_duplicates('站名', keep='first', inplace=True)
    return df, dferror