'''Skipping microarchitecture'''
from core.taxonomy.expressions import *
from core.taxonomy.designelement import *
from core.notation import microarchitecture as m_, transform as t_
from core.taxonomy.expressions import FormatType
import saflib.microarchitecture.TaxoRegistry as tr_
skipping_uarch_dict=tr_.getComponent("SkippingUarch")
buildSkippingUarch=skipping_uarch_dict['constructor']

'''Concretize SAF to microarchitecture'''
'''- Helper functions/constants for wiring to BufferStub'''

get_follower_buffer=lambda saf: saf.getTarget()
get_follower_fmt_iface=lambda saf: saf.getAttributes()[0][1]
get_leader_buffer=lambda saf: saf.getAttributes()[0][2]
get_leader_fmt_iface=lambda saf: saf.getAttributes()[0][3]

SkipSAFtoUarch = \
    lambda sks:buildSkippingUarch("Skipping_" + \
                                    get_leader_buffer(sks) + \
                                    str(get_leader_fmt_iface(sks)) + \
                                    "_"+get_follower_buffer(sks) + \
                                    str(get_follower_fmt_iface(sks)), \
                                  "?", \
                                  "?", \
                                  sks.getAttributes()[1],"?","?")



#SkipUarchBufferWiringEndpts=[[sks.getTarget()+".md"]]

#SkipSAFUarchBuffer=lambda sks:

#newSkipUarchBufferStubNetlistFromSkipSAF= \
#    lambda sks: 

#getFMTSAFRankList=lambda fs:fs.getAttributes()[0]
#FMTSAFUarchBuffer=lambda fs:[fs.getTarget(),fs.getTarget()+"_datatype_format_uarch"]
#FMTUarchBufferWiringEndpts = [['md_out$x','md_in$x'],['at_bound_in$x','at_bound_out$x']]
#FMTUarchBufferWiringNetTypes = ['md','pos']
'''- Wire to BufferStub'''

def newSkipUarchBufferStubNetlistFromSkipSAF(saf):

    follower_buffer=get_follower_buffer(saf)
    follower_fmt_iface=get_follower_fmt_iface(saf)
    leader_buffer=get_leader_buffer(saf)
    leader_fmt_iface=get_leader_fmt_iface(saf)

    new_intersect_name="Skipping_" + \
                       leader_buffer + \
                       str(leader_fmt_iface) + \
                       "_"+follower_buffer + \
                       str(follower_fmt_iface)

    leader_buffer_md_port=leader_buffer+".md_out"+str(leader_fmt_iface)
    leader_intersect_md_port=new_intersect_name+".md_in_leader"
    leader_buffer_pos_port=leader_buffer+".pos_in"+str(leader_fmt_iface)
    leader_intersect_pos_port=new_intersect_name+".pos_out_leader"
    follower_buffer_md_port=follower_buffer+".md_out"+str(follower_fmt_iface)
    follower_intersect_md_port=new_intersect_name+".md_in_follower"
    follower_buffer_pos_port=follower_buffer+".pos_in"+str(follower_fmt_iface)
    follower_intersect_pos_port=new_intersect_name+".pos_out_follower"

    net_list=[]

    # md: leader buffer <=> intersection leader md in
    net_list.append(Net.fromIdAttributes("TestNet_"+leader_buffer_md_port.replace(".","_")+"_"+ \
                                            leader_intersect_md_port.replace(".","_"), \
                                         NetType.fromIdValue("TestNetType","md"), \
                                         FormatType.fromIdValue("TestFormatType","?"), \
                                         [leader_buffer_md_port, \
                                          leader_intersect_md_port]))

    # pos: leader buffer <=> intersection leader pos out
    net_list.append(Net.fromIdAttributes("TestNet_"+leader_buffer_pos_port.replace(".","_")+"_"+ \
                                            leader_intersect_pos_port.replace(".","_"), \
                                         NetType.fromIdValue("TestNetType","pos"), \
                                         FormatType.fromIdValue("TestFormatType","addr"), \
                                         [leader_buffer_pos_port, \
                                          leader_intersect_pos_port]))

    # md: follower buffer <=> intersection follower md in
    net_list.append(Net.fromIdAttributes("TestNet_"+follower_buffer_md_port.replace(".","_")+"_"+ \
                                            follower_intersect_md_port.replace(".","_"), \
                                         NetType.fromIdValue("TestNetType","md"), \
                                         FormatType.fromIdValue("TestFormatType","?"), \
                                         [follower_buffer_md_port, \
                                          follower_intersect_md_port]))

    # pos: follower buffer <=> intersection follower pos out
    net_list.append(Net.fromIdAttributes("TestNet_"+follower_buffer_pos_port.replace(".","_")+"_"+ \
                                            follower_intersect_pos_port.replace(".","_"), \
                                         NetType.fromIdValue("TestNetType","pos"), \
                                         FormatType.fromIdValue("TestFormatType","addr"), \
                                         [follower_buffer_pos_port, \
                                          follower_intersect_pos_port]))

    return net_list

#newFMTUarchBufferStubNetlistFromFMTSAF= \
#    lambda fs: t_.net_zip(FMTUarchBufferWiringEndpts, FMTUarchBufferWiringNetTypes, \
#                          FMTSAFUarchBuffer(fs), \
#                          gen_type='rank_list',gen_attr=getFMTSAFRankList(fs))
'''- Concretize'''
#FMTSAFtoUarch = \
#    lambda fs:buildFormatUarch(fs.getTarget()+"_datatype_format_uarch",fs.getAttributes()[0])