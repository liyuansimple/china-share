import pandas as pd
import nokiaScriptFunction as nf
import time


def tm():
    return time.strftime("%Y-%m-%d %H:%M:%S") + ':'


def MakeNokiaLTEScript(file_path, out_folder=None, fun_switch=None):
    # {'配置IP和VLAN':TRUE,
    # '配置广电路由':FALSE,
    # '配置广电用户面控制面IP地址':FALSE,
    # '添加广电LTAC':TRUE,
    # '添加广电LNMME':TRUE,
    # '基站共享开关':TRUE,
    # '移动策略MODPR':TRUE,
    # '切换策略':TRUE,
    # '重选策略4G':TRUE,
    # '重选策略5G':TRUE,
    # '重定向策略':TRUE,
    # '添加广电小区PLMN和移动策略组':TRUE}

    TEMPLATE_VLAN_IPIF = '新增VLAN_IPIF'
    TEMPLATE_ROUTE = '新增路由'
    TEMPLATE_LNMME = '新增LNMME'

    if fun_switch is None:
        fun_switch = {}
    site_data = pd.read_excel(file_path, sheet_name='LTE基站共享数据')
    site_list = list(site_data['LNBTS'].unique())
    site_count = len(site_list)
    print(tm(), '准备制作...')

    # ncell_data = pd.read_excel(file_path, sheet_name='LTE邻区共享数据')
    # 将需要的数据加载到变量
    if fun_switch['配置IP和VLAN']:
        vlan_data = pd.read_excel(file_path, sheet_name='现网VLAN配置')
        ipif_data = pd.read_excel(file_path, sheet_name='现网IP配置')
    if fun_switch['配置广电路由']:
        route_data = pd.read_excel(file_path, sheet_name='现网路由配置')
    if fun_switch['添加广电LNMME']:
        lnmme_data = pd.read_excel(file_path, sheet_name='现网LNMME配置')
    if fun_switch['添加广电小区PLMN和移动策略组']:
        cell_data = pd.read_excel(file_path, sheet_name='LTE小区共享数据')
        moprmap_data = pd.read_excel(file_path, sheet_name='现网moprMappingList配置')

    scxml = nf.NokiaXml()
    scxml.add_root()

    current_site_num = 0
    for site in site_list:
        site_df = site_data[site_data['LNBTS'] == site].reset_index(drop=True)
        enb_ver = str(site_df.at[0, '基站版本'])
        enb_t_mode_tmp = str(site_df.at[0, '基站传输模式'])
        site_s = str(site)


        current_site_num = current_site_num + 1
        print(tm(), r'制作(%d/%d)站点的脚本，LTE站号：%s' % (current_site_num, site_count, site_s))
        # 配置IP和VLAN
        if fun_switch['配置IP和VLAN']:
            element_list = [[vlan_data, 'VLANIF', 'MRBTS', site, 50], [ipif_data, 'IPIF', 'MRBTS', site, 50]]
            element_canbeuse = get_canbeuse(site_df, TEMPLATE_VLAN_IPIF, 10, element_list)
            par_name2 = []
            dist_s_head = r'PLMN-PLMN/MRBTS-' + site_s
            for i in range(len(element_canbeuse[0])):
                ip_address = element_canbeuse[0][i].split('#')
                # 配置VLANIF
                dist_s = dist_s_head + r'/TNLSVC-1/TNL-1/ETHSVC-1/ETHIF-1/VLANIF-' + str(element_canbeuse[1][i])
                script_type = [1]
                par_name = ['vlanId']
                par_val = [ip_address[0]]
                par_data = [script_type, par_name, par_name2, par_val]
                scxml.add_comm_node('VLANIF', enb_ver, dist_s, parameter_data=par_data)

                # 创建IPIF模块
                dist_s = dist_s_head + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-' + str(element_canbeuse[2][i])
                script_type = [1, 1]
                par_name = ['interfaceDN', 'ipMtu']
                ipDN = 'MRBTS-' + site_s + '/TNLSVC-1/TNL-1/ETHSVC-1/ETHIF-1/VLANIF-' + str(element_canbeuse[1][i])
                par_val = [ipDN, '1500']
                par_data = [script_type, par_name, par_name2, par_val]
                scxml.add_comm_node('IPIF', enb_ver, dist_s, parameter_data=par_data)

                # 添加广电IP
                dist_s = dist_s + r'/IPADDRESSV4-1'
                script_type = [1, 1, 1]
                par_name = ['ipAddressAllocationMethod', 'localIpAddr', 'localIpPrefixLength']
                par_val = ['0', ip_address[0], '30']
                par_data = [script_type, par_name, par_name2, par_val]
                scxml.add_comm_node('IPADDRESSV4', enb_ver, dist_s, parameter_data=par_data)

        # 配置广电路由
        if fun_switch['配置广电路由']:
            # 添加广电路由IPRT
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPRT-1'
            script_type = [5]
            par_name = ['staticRoutes']
            par_name_tmp = ['destinationIpPrefixLength', 'destIpAddr', 'gateway', 'preference', 'preSrcIpv4Addr']
            par_name2_list = []
            par_val_list = []
            route_df = route_data[route_data['enb'] == site].reset_index(drop=True)
            routes_count = route_df.shape[0]
            # 拷贝现网路由
            for route_i in range(routes_count):
                par_name2_list.append(par_name_tmp)
                route_destin = str(route_df.at[route_i, 'destinationIpPrefixLength'])
                route_ipaddr = str(route_df.at[route_i, 'destIpAddr'])
                route_gateway = str(route_df.at[route_i, 'gateway'])
                val_tmp = [route_destin, route_ipaddr, route_gateway, '1', '0.0.0.0']
                par_val_list.append(val_tmp)
            # 添加广电路由
            element_canbeuse = get_canbeuse(site_df, TEMPLATE_ROUTE, 10)
            for route_i in element_canbeuse[0]:
                par_name2_list.append(par_name_tmp)
                route_s = route_i.split('#')
                val_tmp = [route_s[1], route_s[0], route_s[2], '1', '0.0.0.0']
                par_val_list.append(val_tmp)
            par_name2 = [par_name2_list]
            par_val = [par_val_list]
            par_data = [script_type, par_name, par_name2, par_val]
            scxml.add_comm_node('IPRT', enb_ver, dist_s, parameter_data=par_data)

        # 配置广电用户面控制面IP地址
        if fun_switch['配置广电用户面控制面IP地址']:
            dist_s = r'MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/TRSNW-1'
            script_type = [4, 4, 1, 1]
            par_name = ['cPlane', 'uPlane', 'transportNwId', 'transportNwInUse']
            par_name2 = [['ipV4AddressDN1'], ['ipV4AddressDN1'], '', '']
            val1 = r'MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-1/IPADDRESSV4-1'
            val2 = r'MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-1/IPADDRESSV4-1'
            par_val = [[val1], [val2], '1', 'true']
            par_data = [script_type, par_name, par_name2, par_val]
            scxml.add_comm_node('TRSNW', enb_ver, dist_s, opera_s='create', parameter_data=par_data)

        # 添加广电LTAC
        if fun_switch['添加广电LTAC']:
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/MNL-1/MNLENT-1/TAC-1/LTAC-2'
            script_type = [1, 1, 1, 1]
            par_name = ['tacLimitGbrEmergency', 'tacLimitGbrHandover', 'tacLimitGbrNormal', 'transportNwId']
            par_name2 = []
            par_val = ['1000000', '1000000', '1000000', '1']
            par_data = [script_type, par_name, par_name2, par_val]
            scxml.add_comm_node('LTAC', enb_ver, dist_s, opera_s='create', parameter_data=par_data)

        # 添加广电LNMME
        if fun_switch['添加广电LNMME']:
            script_type = [1, 1, 1, 1]
            par_name = ['administrativeState', 'ipAddrPrim', 'mmeRatSupport', 'transportNwId']
            par_name2 = []
            par_val = ['1', '0', '1', '0']
            element_list = [[lnmme_data, 'MME_ID', 'ENB_ID', site, 50]]
            element_canbeuse = get_canbeuse(site_df, TEMPLATE_LNMME, 8, element_list)
            for i in range(len(element_canbeuse[0])):
                dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s \
                         + r'/LNMME-' + str(element_canbeuse[1][i])
                par_val[1] = str(element_canbeuse[0][i])
                par_data = [script_type, par_name, par_name2, par_val]
                scxml.add_comm_node('LNMME', enb_ver, dist_s, parameter_data=par_data)

        # 基站共享开关
        if fun_switch['基站共享开关']:
            enb_t_mode = '0'
            if enb_t_mode_tmp == '双IP模式':
                enb_t_mode = '1'
            script_type = [1, 1, 1]
            par_name = ['actTransportSeparationLte', 'actSelMobPrf', 'moProfileSelect']
            par_name2 = []
            par_val = [enb_t_mode, '1', '0']
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s
            par_data = [script_type, par_name, par_name2, par_val]
            scxml.add_comm_node('LNBTS', enb_ver, dist_s, parameter_data=par_data)

        # MODPR移动策略
        if fun_switch['移动策略MODPR']:
            script_type = [1, 1, 1, 1, 1, 1, 1]
            par_name = ['autoAdapt', 'autoAdaptIMLB', 'caBlockingAllowed', 'idleLBPercCaUe', 'idleLBPercUeTM9',
                        'idleLBPercentageOfUes', 'targetSelMethod']
            par_name2 = []
            par_val = ['1', '1', '0', '0', '0', '100', '0']
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/MODPR-0'
            par_data = [script_type, par_name, par_name2, par_val]
            scxml.add_comm_node('MODPR', enb_ver, dist_s, parameter_data=par_data)

        # MOPR切换策略
        if fun_switch['切换策略']:
            element_canbeuse = get_canbeuse(site_df, '切换策略MOPR-4G频点', 8)
            if len(element_canbeuse[0]) > 0:
                script_type = [1, 1, 1, 1, 1, 3]
                par_name = ['idleLBPercCaUe', 'idleLBPercentageOfUes', 'caBlockingAllowed', 'idleLBPercUeTM9',
                            'targetSelMethod', 'freqLayListLte']
                par_name2 = []
                par_val = ['0', '100', '0', '0', '0', element_canbeuse[0]]
                dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/MOPR-2'
                par_data = [script_type, par_name, par_name2, par_val]
                scxml.add_comm_node('MOPR', enb_ver, dist_s, parameter_data=par_data)

        # MOIMP重选参数、5G重选频点
        if fun_switch['重选策略4G'] or fun_switch['重选策略5G']:
            script_type = []
            par_name = []
            par_name2 = []
            par_val = []
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/MOPR-2/MOIMP-1'
            if fun_switch['重选策略4G']:
                element_canbeuse = get_canbeuse(site_df, '重选策略配置MOIMP-4G频点', 8)
                if len(element_canbeuse[0]) > 0:
                    par_tmp = ['dlCarFrqEut', 'idleLBEutCelResPrio', 'idleLBEutCelResWeight']
                    script_type.append(5)
                    par_name.append('dlCarFrqEutL')
                    name_tmp = []
                    val_tmp = []
                    for ele_i in element_canbeuse[0]:
                        ele_tmp = ele_i.split('-')
                        name_tmp.append(par_tmp)
                        val_tmp_tmp = [ele_tmp[0], str(int(float(ele_tmp[1]) * 5)), '100']
                        val_tmp.append(val_tmp_tmp)
                    par_name2.append(name_tmp)
                    par_val.append(val_tmp)

            if fun_switch['重选策略5G']:
                element_canbeuse = get_canbeuse(site_df, '重选策略配置MOIMP-5G频点', 8)
                if len(element_canbeuse[0]) > 0:
                    par_tmp_nr = ['dlCarFrqNr', 'idleLBNrCelResPref', 'idleLBNrCelResPrio', 'idleLBNrCelResWeight']
                    script_type.append(5)
                    par_name.append('nrCarFrqL')
                    name_tmp = []
                    val_tmp = []
                    for ele_i in element_canbeuse[0]:
                        ele_tmp = ele_i.split('-')
                        name_tmp.append(par_tmp_nr)
                        val_tmp_tmp = [ele_tmp[0], '1', str(int(float(ele_tmp[1]) * 5)), '100']
                        val_tmp.append(val_tmp_tmp)
                    par_name2.append(name_tmp)
                    par_val.append(val_tmp)
            par_data = [script_type, par_name, par_name2, par_val]
            scxml.add_comm_node('MOIMP', enb_ver, dist_s, parameter_data=par_data)

        # 5G重定向
        if fun_switch['重定向策略']:
            element_canbeuse = get_canbeuse(site_df, '重定向策略MORED-5G频点', 2)
            p_count = 0
            if len(element_canbeuse[0]) > 0:
                for ele_i in element_canbeuse[0]:
                    script_type = [1, 1, 1, 1, 1, 1, 1]
                    par_name = ['redirNrCarFrqcarrierFreqNrCell', 'redirNrCarFrqssbDuration', 'redirNrCarFrqssbOffset',
                                'redirNrCarFrqssbPeriodicity', 'redirNrCarFrqssbSubcarrierSpacing',
                                'redirRAT', 'redirectPrio']
                    par_name2 = []
                    ele_tmp = ele_i.split('-')
                    par_val = [ele_tmp[0], '4', '0', '2', ele_tmp[1][:-1], '6', ele_tmp[2]]
                    dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/MOPR-2/MORED-' + str(p_count)
                    p_count = p_count + 1
                    par_data = [script_type, par_name, par_name2, par_val]
                    scxml.add_comm_node('MORED', enb_ver, dist_s, parameter_data=par_data)

        # 添加广电小区PLMN和移动策略组
        if fun_switch['添加广电小区PLMN和移动策略组']:
            cell_df = cell_data[cell_data['LNBTS'] == site].sort_values('LNCEL', ascending=True).reset_index(drop=True)
            cells_count = cell_df.shape[0]
            for cell_i in range(cells_count):
                cell_id_temp = cell_df.at[cell_i, 'LNCEL']
                cell_id = str(cell_id_temp)
                moprmap_df = moprmap_data[(moprmap_data['eNodeB_id'] == site) & (moprmap_data['Lncel'] == cell_id_temp)].reset_index(drop=True)
                moprmap_count = moprmap_df.shape[0]
                if moprmap_count == 0:
                    script_type = [4, 4]
                    par_name = ['furtherPlmnIdL', 'moPrMappingList']
                    par_name2 = [['autoRemovalAllowed', 'cellReserve', 'mcc', 'mnc', 'mncLength'],
                                 ['lteNrDualConnectSupport', 'mcc', 'mnc', 'mncLength', 'moPrId']]
                    par_val = [['0', '0', '460', '15', '2'], ['0', '460', '15', '2', '2']]
                else:
                    script_type = [4]
                    par_name = ['furtherPlmnIdL']
                    par_name2 = [['autoRemovalAllowed', 'cellReserve', 'mcc', 'mnc', 'mncLength']]
                    par_val = [['0', '0', '460', '15', '2']]
                    have_cbn = False
                    mcc_mnc_count = 0
                    for moprmap_i in range(moprmap_count):
                        mcc_tmp = str(moprmap_df.at[moprmap_i, 'MCC'])
                        if len(mcc_tmp) <= 1:
                            continue
                        mnc_tmp = str(moprmap_df.at[moprmap_i, 'MNC'])
                        if len(mnc_tmp) == 1:
                            mnc_tmp = '0' + mnc_tmp
                        if (mcc_tmp == '460') and (mnc_tmp == '15'):
                            have_cbn = True
                        mcc_mnc_count = mcc_mnc_count + 1
                    if not have_cbn:
                        mcc_mnc_count = mcc_mnc_count + 1

                    if mcc_mnc_count == 1:
                        script_type.append(4)
                        par_name.append('moPrMappingList')
                        par_name2.append(['lteNrDualConnectSupport', 'mcc', 'mnc', 'mncLength', 'moPrId'])
                        if not have_cbn:
                            par_val.append(['0', '460', '15', '2', '2'])
                        else:
                            for moprmap_i in range(moprmap_count):
                                mcc_tmp = str(moprmap_df.at[moprmap_i, 'MCC'])
                                if len(mcc_tmp) <= 1:
                                    continue
                                mnc_tmp = str(moprmap_df.at[moprmap_i, 'MNC'])
                                if len(mnc_tmp) == 1:
                                    mnc_tmp = '0' + mnc_tmp
                                mod_tmp = str(moprmap_df.at[moprmap_i, 'lteNrDualConnectSupport'])
                                if mod_tmp == 'EN-DC_capable':
                                    lteNrDualCS = '1'
                                elif mod_tmp == 'EN-DC_not_capable':
                                    lteNrDualCS = '2'
                                else:
                                    lteNrDualCS = '0'
                                moprid_tmp = str(moprmap_df.at[moprmap_i, 'moPrId'])
                                par_val.append([lteNrDualCS, mcc_tmp, mnc_tmp, '2', moprid_tmp])
                    else:
                        script_type.append(5)
                        par_name.append('moPrMappingList')
                        par_name2_tmp = []
                        val_tmp = []

                        for moprmap_i in range(moprmap_count):
                            mcc_tmp = str(moprmap_df.at[moprmap_i, 'MCC'])
                            if len(mcc_tmp) <= 1:
                                continue
                            mnc_tmp = str(moprmap_df.at[moprmap_i, 'MNC'])
                            if len(mnc_tmp) == 1:
                                mnc_tmp = '0' + mnc_tmp
                            mod_tmp = str(moprmap_df.at[moprmap_i, 'lteNrDualConnectSupport'])
                            if mod_tmp == 'EN-DC_capable':
                                lteNrDualCS = '1'
                            elif mod_tmp == 'EN-DC_not_capable':
                                lteNrDualCS = '2'
                            else:
                                lteNrDualCS = '0'
                            moprid_tmp = str(moprmap_df.at[moprmap_i, 'moPrId'])

                            par_name2_tmp.append(['lteNrDualConnectSupport', 'mcc', 'mnc', 'mncLength', 'moPrId'])
                            val_tmp.append([lteNrDualCS, mcc_tmp, mnc_tmp, '2', moprid_tmp])
                        if not have_cbn:
                            par_name2_tmp.append(['lteNrDualConnectSupport', 'mcc', 'mnc', 'mncLength', 'moPrId'])
                            val_tmp.append(['0', '460', '15', '2', '2'])
                        par_name2.append(par_name2_tmp)
                        par_val.append(val_tmp)
                dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/LNBTS-' + site_s + r'/LNCEL-' + cell_id
                par_data = [script_type, par_name, par_name2, par_val]
                scxml.add_comm_node('LNCEL', enb_ver, dist_s, parameter_data=par_data)
    context = scxml.save_xml()
    print(tm(), '完成！总共%d个LTE基站脚本。' % site_count)
    return context


def get_canbeuse(find_data, find_range_name, find_range_len, element=None):
    find_set = []
    for i in range(1, find_range_len + 1):
        find_tmp = str(find_data.at[0, find_range_name + str(i)])
        if not (find_tmp.strip() == '' or find_tmp == 'nan'):
            find_set.append(find_tmp)
    get_set = [find_set]
    if element is not None:
        for ele in element:
            element_data = ele[0]
            index_element = ele[1]
            index_find = ele[2]
            find_id = ele[3]
            element_range_len = ele[4]
            element_df = element_data[element_data[index_find] == find_id]
            element_list = list(element_df[index_element].unique())
            ele_canbeused = [i for i in range(1, element_range_len) if i not in element_list]
            get_set.append(ele_canbeused)
    return get_set


def MakeNokiaNRScript(file_path, out_folder=None, fun_switch1=None):
    # {'添加广电AMF':True,
    # '添加广电PLMN':True,
    # '添加IP和VLAN':False,
    # '添加广电路由':True,
    # '更新切片中广电的PLMN':True,
    # '添加NGUplane地址并关联PLMN':False,
    # '添加NGCplan地址':False,
    # '更新XNCplan地址':False,
    # '更新XNUplan地址':False,
    # '更新NR邻区':True
    # '打开RanShraing开关':True,
    # '打开传输RanShraing开关':True,
    # '添加小区下面新的PLMN':True,
    # '关联跟踪区':True
    # '添加重定向参数':True
    #  }

    fun_switch = {'添加广电AMF': True,
                  '添加广电PLMN': True,
                  '添加IP和VLAN': False,
                  '添加广电路由': False,
                  '更新切片中广电的PLMN': True,
                  '添加NGUplane地址并关联PLMN': False,
                  '添加NGCplan地址': False,
                  '更新XNCplan地址': False,
                  '更新XNUplan地址': False,
                  '更新NR邻区': True,
                  '打开RanShraing开关': True,
                  '打开传输RanShraing开关': True,
                  '添加小区下面新的PLMN': True,
                  '关联跟踪区': False,
                  '添加重定向参数': True}

    TEMPLATE_AMF = '新增AMF'
    TEMPLATE_VLAN_IPIF = '新增VLAN_IPIF'
    TEMPLATE_TA = '关联跟踪区'

    site_data = pd.read_excel(file_path, sheet_name='NR基站共享数据')
    site_list = list(site_data['NRBTS'].unique())
    site_count = len(site_list)
    print(tm(), '准备制作...')

    # 将需要的数据加载到变量
    if fun_switch['添加IP和VLAN']:
        vlan_data = pd.read_excel(file_path, sheet_name='现网VLAN配置')
        ipif_data = pd.read_excel(file_path, sheet_name='现网IP配置')
    # if fun_switch['配置广电路由']:
    # route_data = pd.read_excel(file_path, sheet_name='现网路由配置')
    if fun_switch['添加广电AMF']:
        amf_data = pd.read_excel(file_path, sheet_name='现网SERVEDAMF配置')
    if fun_switch['添加小区下面新的PLMN']:
        cell_data = pd.read_excel(file_path, sheet_name='NR小区共享数据')
    if fun_switch['更新NR邻区']:
        nradjcell_data = pd.read_excel(file_path, sheet_name='现网NRADJNRCELL')
    if fun_switch['添加重定向参数']:
        nrred_data = pd.read_excel(file_path, sheet_name='现网NRREDRT')

    nrscxml_step1 = nf.NokiaXml()
    nrscxml_step1.add_root()
    nrscxml_step2 = nf.NokiaXml()
    nrscxml_step2.add_root()

    current_site_num = 0
    for site in site_list:
        site_df = site_data[site_data['NRBTS'] == site].reset_index(drop=True)
        gnb_ver = str(site_df.at[0, '基站版本'])
        site_s = str(site)

        current_site_num = current_site_num + 1
        print(tm(), r'制作(%d/%d)站点的脚本，NR站号：%s' % (current_site_num, site_count, site_s))

        # 添加广电AMF
        if fun_switch['添加广电AMF']:
            element_list = [[amf_data, 'SERVEDAMF', 'NRBTS', site, 50]]
            element_canbeuse = get_canbeuse(site_df, TEMPLATE_AMF, 8, element_list)
            par_name2 = []
            dist_s_head = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/SERVEDAMF-'
            for i in range(len(element_canbeuse[0])):
                script_type = [1, 1, 1]
                par_name = ['administrativeState', 'amfIPAddress', 'defaultAMF']
                par_val = ['2', str(element_canbeuse[0][i]), '1']
                par_data = [script_type, par_name, par_name2, par_val]
                dist_s = dist_s_head + str(element_canbeuse[1][i])
                nrscxml_step1.add_comm_node('SERVEDAMF', gnb_ver, dist_s, parameter_data=par_data)

        # 添加广电PLMN
        if fun_switch['添加广电PLMN']:
            script_type = [1, 1, 1]
            par_name = ['mcc', 'mnc', 'mncLength']
            par_name2 = []
            par_val = ['460', '15', '2']
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-2'
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step1.add_comm_node('NRPLMN', gnb_ver, dist_s, opera_s='create', parameter_data=par_data)

        # 添加IP和VLAN
        if fun_switch['添加IP和VLAN']:
            element_list = [[vlan_data, 'VLANIF', 'MRBTS', site, 50], [ipif_data, 'IPIF', 'MRBTS', site, 50]]
            element_canbeuse = get_canbeuse(site_df, TEMPLATE_VLAN_IPIF, 8, element_list)
            par_name2 = []
            dist_s_head = r'PLMN-PLMN/MRBTS-' + site_s
            for i in range(len(element_canbeuse[0])):
                ip_address = element_canbeuse[0][i].split('#')
                # 配置VLANIF
                dist_s = dist_s_head + r'/TNLSVC-1/TNL-1/ETHSVC-1/ETHIF-1/VLANIF-' + str(element_canbeuse[1][i])
                script_type = [1]
                par_name = ['vlanId']
                par_val = [ip_address[0]]
                par_data = [script_type, par_name, par_name2, par_val]
                nrscxml_step1.add_comm_node('VLANIF', gnb_ver, dist_s, parameter_data=par_data)

                # 创建IPIF模块
                dist_s = dist_s_head + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-' + str(element_canbeuse[2][i])
                script_type = [1, 1]
                par_name = ['interfaceDN', 'ipMtu']
                ipDN = 'MRBTS-' + site_s + '/TNLSVC-1/TNL-1/ETHSVC-1/ETHIF-1/VLANIF-' + str(element_canbeuse[1][i])
                par_val = [ipDN, '1500']
                par_data = [script_type, par_name, par_name2, par_val]
                nrscxml_step1.add_comm_node('IPIF', gnb_ver, dist_s, parameter_data=par_data)

                # 添加广电IP
                dist_s = dist_s + r'/IPADDRESSV4-1'
                script_type = [1, 1, 1]
                par_name = ['ipAddressAllocationMethod', 'localIpAddr', 'localIpPrefixLength']
                par_val = ['0', ip_address[0], '30']
                par_data = [script_type, par_name, par_name2, par_val]
                nrscxml_step1.add_comm_node('IPADDRESSV4', gnb_ver, dist_s, parameter_data=par_data)

        # 添加广电路由
        if fun_switch['添加广电路由']:
            # 添加广电默认路由
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPRT-2'
            script_type = [4]
            par_name = ['staticRoutes']
            par_name2 = [['destinationIpPrefixLength', 'destIpAddr', 'gateway', 'preference', 'preSrcIpv4Addr']]
            par_val = [['0', '0.0.0.0', str(site_df.at[0, r'路由更新(IPRT):新增默认路由']), '1', '0.0.0.0']]
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step1.add_comm_node('IPRT', gnb_ver, dist_s, parameter_data=par_data)

            # 路由策略更新
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/RTPOL-1'
            script_type = [5]
            par_name = ['routingPolicies']
            par_name2_tmp = ['orderNumber', 'routingTableDN', 'srcIpAddress', 'srcIpPrefixLength']
            par_name2 = [[par_name2_tmp, par_name2_tmp]]
            par_val_tmp = []
            for i in range(1, 3):
                col_val = str(site_df.at[0, '路由策略(RTPOL)' + str(i) + ':srcIpAddress'])
                rout_DN = r'PLMN-PLMN/MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPRT-' + str(i)
                par_val_tmp.append([str(i), rout_DN, col_val, '30'])
            par_val = [par_val_tmp]
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step1.add_comm_node('RTPOL', gnb_ver, dist_s, parameter_data=par_data)

        # 更新切片中广电的PLMN
        if fun_switch['更新切片中广电的PLMN']:
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/SNSSAI-1'
            script_type = [1]
            par_name = ['administrativeState']
            par_name2 = ['']
            par_val = ['0']
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step1.add_comm_node('SNSSAI', gnb_ver, dist_s, parameter_data=par_data)

            script_type = [1, 1, 3]
            par_name = ['administrativeState', 'sst', 'nrPlmnDNList']
            par_name2 = ['', '', ['', '']]
            val1 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-1'
            val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-2'
            par_val = ['2', '1', [val1, val2]]
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step2.add_comm_node('SNSSAI', gnb_ver, dist_s, parameter_data=par_data)

        if fun_switch['添加NGUplane地址并关联PLMN'] or fun_switch['添加NGCplan地址'] or \
                fun_switch['更新XNCplan地址'] or fun_switch['更新XNUplan地址']:
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s
            script_type = []
            par_name = []
            par_name2 = []
            par_val = []

            # 添加NGUplane地址并关联PLMN
            if fun_switch['添加NGUplane地址并关联PLMN']:
                script_type.append(5)
                par_name.append('ngUplane')
                par_name2.append([['ipV4AddressDN1', 'nrPlmnDN'], ['ipV4AddressDN1', 'nrPlmnDN']])
                val1 = r'MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-1/IPADDRESSV4-1'
                val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-'
                val3 = val2 + '1'
                val4 = val2 + '2'
                par_val.append([[val1, val3], [val1, val4]])

            # 添加NGCplan地址
            if fun_switch['添加NGCplan地址']:
                script_type.append(5)
                par_name.append('ngCplane')
                par_name2.append([['ipV4AddressDN1', 'ngTnlId'], ['ipV4AddressDN1', 'ngTnlId']])
                val1 = r'MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-1/IPADDRESSV4-1'
                par_val.append([[val1, '1'], [val1, '2']])

            # 更新XNCplan地址
            if fun_switch['更新XNCplan地址']:
                script_type.append(5)
                par_name.append('xnCplane')
                par_name2.append([['ipV4AddressDN1', 'xnTnlId'], ['ipV4AddressDN1', 'xnTnlId']])
                val1 = r'MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-1/IPADDRESSV4-1'
                par_val.append([[val1, '1'], [val1, '2']])

            # 更新XNUplan地址
            if fun_switch['更新XNUplan地址']:
                script_type.append(5)
                par_name.append('xnUplane')
                par_name2.append([['ipV4AddressDN1', 'nrPlmnDN'], ['ipV4AddressDN1', 'nrPlmnDN']])
                val1 = r'MRBTS-' + site_s + r'/TNLSVC-1/TNL-1/IPNO-1/IPIF-1/IPADDRESSV4-1'
                val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-'
                val3 = val2 + '1'
                val4 = val2 + '2'
                par_val.append([[val1, val3], [val1, val4]])
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step1.add_comm_node('NRBTS', gnb_ver, dist_s, parameter_data=par_data)

        if fun_switch['更新NR邻区']:
            nradjcell_df = nradjcell_data[nradjcell_data['nrBtsId'] == site].reset_index(drop=True)
            nradjcell_count = nradjcell_df.shape[0]
            dist_s_tmp = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRADJNRCELL-'
            for nradjcell_i in range(nradjcell_count):
                ncell_id = str(nradjcell_df.at[nradjcell_i, 'NRADJNRCELLID'])
                ncell_tac = str(nradjcell_df.at[nradjcell_i, 'fiveGsTac'])
                ncell_dtype = str(nradjcell_df.at[nradjcell_i, 'cellDepType'])
                dist_s = dist_s_tmp + ncell_id
                script_type = [1]
                par_name = ['fiveGsTac']
                par_name2 = []
                par_val = ['']
                par_data = [script_type, par_name, par_name2, par_val]
                nrscxml_step2.add_comm_node('NRADJNRCELL', gnb_ver, dist_s, parameter_data=par_data)
                dist_s = dist_s_tmp + ncell_id + r'/ADJ_NRPLMNSET_SA-1'
                script_type = [1, 3]
                par_name = ['fiveGsTac', 'nrPlmnDNList']
                par_name2 = ['', ['', '']]
                val1 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-1'
                val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-2'
                par_val = [ncell_tac, [val1, val2]]
                par_data = [script_type, par_name, par_name2, par_val]
                nrscxml_step2.add_comm_node('ADJ_NRPLMNSET_SA', gnb_ver, dist_s, parameter_data=par_data)
                if ncell_dtype == '10':
                    dist_s = dist_s_tmp + ncell_id + r'/ADJ_NRPLMNSET_NSA-1'
                    script_type = [3]
                    par_name = ['nrPlmnDNList']
                    par_name2 = [['', '']]
                    val1 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-1'
                    val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-2'
                    par_val = [[val1, val2]]
                    par_data = [script_type, par_name, par_name2, par_val]
                    nrscxml_step2.add_comm_node('ADJ_NRPLMNSET_NSA', gnb_ver, dist_s, parameter_data=par_data)

        if fun_switch['打开RanShraing开关'] or fun_switch['打开传输RanShraing开关']:
            dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s
            script_type = []
            par_name = []
            par_name2 = []
            par_val = []
            # 打开RanShraing开关
            if fun_switch['打开RanShraing开关']:
                script_type.append(1)
                par_name.append('actRanSharing')
                par_name2.append('')
                par_val.append('1')

            # 打开传输RanShraing开关
            if fun_switch['打开传输RanShraing开关']:
                script_type.append(1)
                par_name.append('actTrsSepaSARanSharing')
                par_name2.append('')
                if fun_switch['添加IP和VLAN']:
                    par_val.append('1')
                else:
                    par_val.append('0')
            par_data = [script_type, par_name, par_name2, par_val]
            nrscxml_step2.add_comm_node('NRBTS', gnb_ver, dist_s, parameter_data=par_data)

        # 添加小区下面新的PLMN
        if fun_switch['添加小区下面新的PLMN']:
            cell_df = cell_data[cell_data['NRBTS'] == site].sort_values('NRCEL', ascending=True).reset_index(drop=True)
            cells_count = cell_df.shape[0]
            for cell_i in range(cells_count):
                cell_id_tmp = cell_df.at[cell_i, 'NRCEL']
                cell_id = str(cell_id_tmp)
                script_type = [3]
                par_name = ['nrPlmnDNList']
                par_name2 = [['', '']]
                val1 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-1'
                val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-2'
                par_val = [[val1, val2]]
                dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s \
                         + r'/NRCELL-' + cell_id + r'/NRPLMNSET_SA-1'
                if fun_switch['关联跟踪区']:
                    element_canbeuse = get_canbeuse(site_df, TEMPLATE_TA, 8)
                    for ta_i in element_canbeuse[0]:
                        script_type.append(1)
                        par_name.append('trackingAreaDN')
                        par_name2.append('')
                        val3 = r'MRBTS-' + site_s + '/NRBTS-' + site_s + r'/TRACKINGAREA-' + str(ta_i)
                        par_val.append(val3)
                par_data = [script_type, par_name, par_name2, par_val]
                nrscxml_step2.add_comm_node('NRPLMNSET_SA', gnb_ver, dist_s, parameter_data=par_data)

                # 添加小区重定向参数
                if fun_switch['添加重定向参数']:
                    nrred_df = nrred_data[
                        (nrred_data['nrBtsId'] == site) & (nrred_data['NRCELL'] == cell_id_tmp)].reset_index(drop=True)
                    nrred_count = nrred_df.shape[0]
                    for nrred_i in range(nrred_count):
                        dist_s = r'PLMN-PLMN/MRBTS-' + site_s + r'/NRBTS-' + site_s \
                                 + r'/NRCELL-' + cell_id + r'/NRREDRT-' + str(nrred_df.at[nrred_i, 'nrredrtId'])
                        script_type = [3]
                        par_name = ['nrPlmnDNList']
                        par_name2 = [['', '']]
                        val1 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-1'
                        val2 = r'MRBTS-' + site_s + r'/NRBTS-' + site_s + r'/NRPLMN-2'
                        par_val = [[val1, val2]]
                        par_data = [script_type, par_name, par_name2, par_val]
                        nrscxml_step2.add_comm_node('NRREDRT', gnb_ver, dist_s, parameter_data=par_data)

    context = [nrscxml_step1.save_xml(), nrscxml_step2.save_xml()]
    print(tm(), '完成！总共%d个NR基站脚本。' % site_count)
    return context
