'''Skipping microarchitecture'''
from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
from util.notation import microarchitecture as m_, transform as t_
from util.taxonomy.expressions import FormatType

'''Microarchitecture primitive imports'''
from .IntersectionLeaderFollower import buildIntersectionLeaderFollower
from .IntersectionBidirectional import buildIntersectionBidirectional
from ..address_primitives.PositionGenerator import buildPositionGenerator as buildPgen
from ..gating.FillGate import buildFillGate

'''Component definition'''
SkippingUarch = m_.ComponentCategory().name("SkippingUarch") \
                                      .attribute("format_leader","format",FormatType.fromIdValue("format","?")) \
                                      .attribute("format_follower","format",FormatType.fromIdValue("format","?")) \
                                      .attribute("direction","string","bidirectional") \
                                      .attribute("skip_strategy","string","none") \
                                      .attribute("fillgate_strategy","string","none") \
                                      .port_in("md_in_leader","md","?",attr_reference="format_leader") \
                                      .port_in("md_in_follower","md","?",attr_reference="format_follower") \
                                      .port_out("pos_out_leader","pos","addr") \
                                      .port_out("pos_out_follower","pos","addr") \
                                      .generator(None)

'''Constructor'''
buildSkippingUarch = \
    lambda id, f_str_leader,f_str_follower, \
           direction,skip_strategy, \
           fillgate_strategy: SkippingUarch.copy().set_attribute('format_leader', \
                                                      FormatType.fromIdValue('format_leader',f_str_leader)) \
                                                  .set_attribute('format_follower', \
                                                      FormatType.fromIdValue('format_follower',f_str_follower)) \
                                                  .set_attribute('direction', \
                                                      direction) \
                                                  .set_attribute('skip_strategy', \
                                                      skip_strategy) \
                                                  .set_attribute('fillgate_strategy', \
                                                      fillgate_strategy) \
                                                  .build(id)

'''Supported instances'''
skipping_uarch_instances={ \
    "cp_bd_none_none":["C","C","bidirectional","none","none"], \
    "cp_bd_opskip_none":["C","C","bidirectional","operand_skip","none"], \
    "cp_lf_none_none":["C","U","leader_follower","none","none"], \
    "cp_lf_none_pbubble":["C","U","leader_follower","none","pipeline_bubble"], \
    "cp_lf_none_lut":["C","U","leader_follower","none","lut"], \
    "b_bd_none_none":["B","B","bidirectional","none","none"], \
    "b_lf_none_none":["B","U","leader_follower","none","none"], \
    "b_lf_none_pbubble":["B","U","leader_follower","none","pipeline_bubble"], \
    "b_lf_none_lut":["B","U","leader_follower","none","lut"]
}

'''Supported instance topologies'''
skipping_uarch_topologies=( \
    { \

        "cp_bd_none_none": (\
            [(buildIntersectionBidirectional,'IntersectionBD',('C','C','none')), \
             (buildPgen,'PgenLeader',('C',)), \
             (buildPgen,'PgenFollower',('C',))],\
            [('md','md_in_leader','IntersectionBD.md_in_0'), \
             ('md','md_in_follower','IntersectionBD.md_in_1'), \
             ('md','IntersectionBD.md_out','PgenLeader.md_in'), \
             ('md','IntersectionBD.md_out','PgenFollower.md_in'), \
             ('pos','PgenLeader.pos_out','pos_out_leader'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "cp_bd_opskip_none": (\
            [(buildIntersectionBidirectional,'IntersectionBD',('C','C','opskip')), \
             (buildPgen,'PgenLeader',('C',)), \
             (buildPgen,'PgenFollower',('C',))],\
            [('md','md_in_leader','IntersectionBD.md_in_0'), \
             ('md','md_in_follower','IntersectionBD.md_in_1'), \
             ('md','IntersectionBD.md_out','PgenLeader.md_in'), \
             ('md','IntersectionBD.md_out','PgenFollower.md_in'), \
             ('pos','PgenLeader.pos_out','pos_out_leader'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "cp_lf_none_none": (\
            [(buildIntersectionLeaderFollower,'IntersectionLF',('C','none')), \
             (buildPgen,'PgenFollower',('C',))],\
            [('md','md_in_leader','IntersectionLF.md_in_leader'), \
             ('md','IntersectionLF.md_out','PgenFollower.md_in'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "cp_lf_none_pbubble": (\
            [(buildIntersectionLeaderFollower,'IntersectionLF',('C','none')), \
             (buildPgen,'PgenFollower',('C',)),\
             (buildFillGate,'FillGateLeader',('pipeline_bubble'))],\
            [('md','md_in_leader','IntersectionLF.md_in_leader'), \
             ('md','IntersectionLF.md_out','PgenFollower.md_in'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "cp_lf_none_lut": (\
            [(buildIntersectionLeaderFollower,'IntersectionLF',('C','none')), \
             (buildPgen,'PgenFollower',('C',)),\
             ((buildFillGate),'FillGateLeader',('lut'))],\
            [('md','md_in_leader','IntersectionLF.md_in_leader'), \
             ('md','IntersectionLF.md_out','PgenFollower.md_in'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "b_bd_none_none": (\
            [(buildIntersectionBidirectional,'IntersectionBD',('B','B','none')), \
             (buildPgen,'PgenLeader',('B',)), \
             (buildPgen,'PgenFollower',('B',))],\
            [('md','md_in_leader','IntersectionBD.md_in_0'), \
             ('md','md_in_follower','IntersectionBD.md_in_1'), \
             ('md','IntersectionBD.md_out','PgenLeader.md_in'), \
             ('md','IntersectionBD.md_out','PgenFollower.md_in'), \
             ('pos','PgenLeader.pos_out','pos_out_leader'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "b_lf_none_none": (\
            [(buildIntersectionLeaderFollower,'IntersectionLF',('B','none')), \
             (buildPgen,'PgenFollower',('B',))],\
            [('md','md_in_leader','IntersectionLF.md_in_leader'), \
             ('md','IntersectionLF.md_out','PgenFollower.md_in'), \
             ('pos','PgenFollower.pos_out','pos_out_follower')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "b_lf_none_pbubble": (\
            [(buildIntersectionLeaderFollower,'IntersectionLF',('B','none')), \
             (buildPgen,'PgenFollower',('B',)),\
             (buildFillGate,'FillGateLeader',('pipeline_bubble'))],\
            [('md','md_in_leader','IntersectionLF.md_in_leader'), \
             ('md','IntersectionLF.md_out','PgenFollower.md_in'), \
             ('pos','PgenFollower.pos_out','pos_out_follower'), \
             ('pos','PgenLeader.pos_out','FillGateLeader.pos_in')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

        "b_lf_none_lut": (\
            [(buildIntersectionLeaderFollower,'IntersectionLF',('B','none')), \
             (buildPgen,'PgenFollower',('B',)), \
             (buildFillGate,'FillGateLeader',('lut'))],\
            [('md','md_in_leader','IntersectionLF.md_in_leader'), \
             ('md','IntersectionLF.md_out','PgenFollower.md_in'), \
             ('pos','PgenFollower.pos_out','pos_out_follower'), \
             ('pos','PgenLeader.pos_out','FillGateLeader.pos_in')],
            "none", # Generator type
            "" # Generator argument from this component attribute
        ),

    }
)

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
                                  sks.getAttributes()[1],"none","none")



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