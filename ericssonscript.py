
def MakeEricssonNRScript(file_path, par):
    nr_str_tmp = '''confbd+
lt all
$date = `date +%y%m%d%H%M`
cvms before_MOCN
st bpu
st cell
st term

bl cell

### Activate Shared NR RAN 
set CXC4012479 featureState 1

### Activate RAN Slicing Framework
set CXC4012379 featureState 1

### Create RPM MO for CBN CUCP                              
cr GNBCUCPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN
### Set RPM MO for CBN CUCP (Plmn and sNSSAI 根据CBN分配定义) 
set GNBCUCPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN pLMNIdList mcc=460,mnc=15
set GNBCUCPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN sNSSAIList sd=16777215,sst=1

cr GNBCUCPFunction=1,EndpointResource=CBN
cr GNBCUCPFunction=1,EndpointResource=CBN,LocalSctpEndpoint=CBN_NG
4
Transport=1,SctpEndpoint=2

cr GNBCUCPFunction=1,EndpointResource=CBN,LocalSctpEndpoint=CBN_XN
6
Transport=1,SctpEndpoint=3

set GNBCUCPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN endpointResourceRef GNBCUCPFunction=1,EndpointResource=CBN

//CUUP
### Create RPM MO for CBN CUUP
cr GNBCUUPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN
### set RPM MO for CBN CUUP (Plmn and sNSSAI 根据CBN分配定义) 
set GNBCUUPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN pLMNIdList mcc=460,mnc=15
set GNBCUUPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN sNSSAIList sd=16777215,sst=1

cr GNBCUUPFunction=1,EndpointResource=CBN
cr GNBCUUPFunction=1,EndpointResource=CBN,LocalIpEndpoint=1
Transport=1,Router=Traffic_OAM,InterfaceIPv4=Traffic_OAM,AddressIPv4=Traffic_OAM
4,6

cr GNBCUUPFunction=1,EndpointResource=CBN,LocalIpEndpoint=1
Transport=1,Router=Traffic,InterfaceIPv4=Traffic,AddressIPv4=Traffic
4,6

set GNBCUUPFunction=1,ResourcePartitions=1,ResourcePartition=1,ResourcePartitionMember=CBN endpointResourceRef GNBCUUPFunction=1,EndpointResource=CBN

//add amf01 amf02
cr GNBCUCPFunction=1,TermPointToAmf=CBN_AMF01
set GNBCUCPFunction=1,TermPointToAmf=CBN_AMF01 ipv4Address1 ''' + par[0] + '''
set GNBCUCPFunction=1,TermPointToAmf=CBN_AMF01 ipv4Address2 ''' + par[1] + '''

cr GNBCUCPFunction=1,TermPointToAmf=CBN_AMF02
set GNBCUCPFunction=1,TermPointToAmf=CBN_AMF02 ipv4Address1 ''' + par[2] + '''
set GNBCUCPFunction=1,TermPointToAmf=CBN_AMF02 ipv4Address2 ''' + par[3] + '''

deb CBN_AMF

confbd-


#############################
###ShareRan Parameters Part##
#############################

confb+

# Add Voice 



### Create CBN AdditionalPLMNInfo
mr celldu_g
ma celldu_g NRCellDU=
pr celldu_g
for $cell in celldu_g
$mo = fdn($cell)
get $cell nRTAC > $tac
crn $mo,AdditionalPLMNInfo=1
nRTAC $tac
pLMNIdList mcc=460,mnc=15
end
done
 
 
#license 
set CXC4012479 featurestate 1

#creat ExternalBroadcastPLMNInfo
bl TermPointToGNodeB
wait 5
st TermPointToGNodeB
mr extcell_g
ma extcell_g ExternalNRCellCU
pr extcell_g
for $extcell in extcell_g
$mo1 = fdn($extcell)
get $extcell nRTAC > $nrtac
set $extcell plmnIdList mcc=460,mnc=00;mcc=460,mnc=15
crn $mo1,ExternalBroadcastPLMNInfo=1
nRTAC $nrtac
pLMNIdList mcc=460,mnc=00
end
crn $mo1,ExternalBroadcastPLMNInfo=2
nRTAC $nrtac
pLMNIdList mcc=460,mnc=15
end
done
deb TermPointToGNodeB

get EUtranFreqRelation=38400|38950 ueMCEUtranFreqRelProfileRef

cr GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400

crn GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400,UeMCEUtranFreqRelProfileUeCfg=MOCN
blindRwrAllowed true
connModeAllowedPCell true
ueConfGroupList 101
end

crn GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400,UeMCEUtranFreqRelProfileUeCfg=CBN-5qi1
blindRwrAllowed true
connModeAllowedPCell true
ueConfGroupList 102
end

crn GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400,UeMCEUtranFreqRelProfileUeCfg=CBN-5qi2
blindRwrAllowed true
connModeAllowedPCell true
ueConfGroupList 103
end

set GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400,UeMCEUtranFreqRelProfileUeCfg=Base connModeAllowedPCell true
set GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400,UeMCEUtranFreqRelProfileUeCfg=Base blindRwrAllowed true


cr GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950

crn GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950,UeMCEUtranFreqRelProfileUeCfg=MOCN
blindRwrAllowed true
connModeAllowedPCell true
ueConfGroupList 101
end

crn GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950,UeMCEUtranFreqRelProfileUeCfg=CBN-5qi1
blindRwrAllowed true
connModeAllowedPCell true
ueConfGroupList 102
end

crn GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950,UeMCEUtranFreqRelProfileUeCfg=CBN-5qi2
blindRwrAllowed true
connModeAllowedPCell true
ueConfGroupList 103
end

set GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950,UeMCEUtranFreqRelProfileUeCfg=Base connModeAllowedPCell true
set GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950,UeMCEUtranFreqRelProfileUeCfg=Base blindRwrAllowed true

set NRCellCU=.,EUtranFreqRelation=38400 ueMCEUtranFreqRelProfileRef GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38400
set NRCellCU=.,EUtranFreqRelation=38950 ueMCEUtranFreqRelProfileRef GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=38950
 
get EUtranFreqRelation=38400|38950 mcpcPCellEUtranFreqRelProfileRef

cr GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38400

crn GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38400,McpcPCellEUtranFreqRelProfileUeCfg=MOCN
ueConfGroupList 101
end
crn GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38400,McpcPCellEUtranFreqRelProfileUeCfg=CBN-5qi1
ueConfGroupList 102
end
crn GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38400,McpcPCellEUtranFreqRelProfileUeCfg=CBN-5qi2
ueConfGroupList 103
end

cr GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38950

crn GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38950,McpcPCellEUtranFreqRelProfileUeCfg=MOCN
ueConfGroupList 101
end

crn GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38950,McpcPCellEUtranFreqRelProfileUeCfg=CBN-5qi1
ueConfGroupList 102
end

crn GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38950,McpcPCellEUtranFreqRelProfileUeCfg=CBN-5qi2
ueConfGroupList 103
end

set NRCellCU=.,EUtranFreqRelation=38400 mcpcPCellEUtranFreqRelProfileRef GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38400
set NRCellCU=.,EUtranFreqRelation=38950 mcpcPCellEUtranFreqRelProfileRef GNBCUCPFunction=1,Mcpc=1,McpcPCellEUtranFreqRelProfile=38950


mr UeMCEUtranFreq_gp
ma UeMCEUtranFreq_gp GNBCUCPFunction=1,UeMC=1,UeMCEUtranFreqRelProfile=
pr UeMCEUtranFreq_gp
for $UeMCEUtranFreq in UeMCEUtranFreq_gp
$mo1 = fdn($UeMCEUtranFreq)
get $UeMCEUtranFreq ueMCEUtranFreqRelProfileId > $NonMocn
if $NonMocn !~ 38950 && $NonMocn !~ 38400
crn $mo1,UeMCEUtranFreqRelProfileUeCfg=MOCN
blindRwrAllowed false
connModeAllowedPCell false
ueConfGroupList 101
end
crn $mo1,UeMCEUtranFreqRelProfileUeCfg=CBN-5qi1
blindRwrAllowed false
connModeAllowedPCell false
ueConfGroupList 102
end
crn $mo1,UeMCEUtranFreqRelProfileUeCfg=CBN-5qi2
blindRwrAllowed false
connModeAllowedPCell false
ueConfGroupList 103
end
set UeMC=1,UeMCEUtranFreqRelProfile=$NonMocn,UeMCEUtranFreqRelProfileUeCfg=Base connModeAllowedPCell true
set UeMC=1,UeMCEUtranFreqRelProfile=$NonMocn,UeMCEUtranFreqRelProfileUeCfg=Base blindRwrAllowed true
fi
done

deb cell
cvms aft_add_cbn_mocn_$date

accn bpu-1 restartunit 1 0 0

confb-

'''
    bom_str = b'\xef\xbb\xbf'
    nr_str_tmp = nr_str_tmp.replace('\n', '\r\n')

    f = open(file_path, 'wb+')
    nr_str = bom_str + nr_str_tmp.encode(encoding='utf-8')
    f.write(nr_str)
    f.close()



def MakeEricssonLTEScript(file_path):
    lte_tmp_str = '''////////////////////////////////////
###Create MME Mo if Need Add New MME for CBN
###No Mme Mo add if CBN plmn roaming from CM Core 
////////////////////////////////////

confb+
st cell

#####################
### Set Parameter
####################
# Shared LTE RAN
#set CXC4010960 featureState 1

set ENodeBFunction=1 allowMocnCellLevelCommonTac True
set1 EUtranCell[FT]DD additionalPlmnList mcc=460,mnc=15,mncLength=2;mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2;mcc=1,mnc=1,mncLength=2
set1 EUtranCell[FT]DD additionalPlmnReservedList false,false,false,false,false
set1 EUtranCell[FT]DD primaryPlmnReserved false
set ENodeBFunction=1 allowMocnCellLevelCommonTac TRUE

set EUtranCell[FT]DD	endcAllowedPlmnList mcc=460,mnc=00;
set GUtranFreqRelation	allowedPlmnList mcc=460,mnc=00;
set ExternalGUtranCell	plmnList mcc=460,mnc=00;
set EUtranCellRelation	includeInSystemInformation	FALSE
set EUtranCell[FT]DD MappingInfo$	mappingInfoSIB5=1

confb-'''

    bom_str = b'\xef\xbb\xbf'
    lte_tmp_str = lte_tmp_str.replace('\n', '\r\n')
    f = open(file_path, 'wb+')
    lte_str = bom_str + lte_tmp_str.encode(encoding='utf-8')
    f.write(lte_str)
    f.close()
