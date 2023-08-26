'''Format microarchitecture'''
from util.notation import microarchitecture as m_, transform as t_

'''Microarchitecture primitive imports'''
from .MetadataParser import buildMetadataParser

'''Component definition'''
FormatUarch = m_.ComponentCategory().name("FormatUarch") \
                                    .port_in("md_in$x","md","$v") \
                                    .port_out("at_bound_out$x","pos","addr") \
                                    .attribute("fibertree",["fibertree"],[None]) \
                                    .generator("fibertree")

'''Constructor'''
buildFormatUarch = \
    lambda id,fibertree:FormatUarch.copy().set_attribute("fibertree",fibertree,"rank_list") \
                                   .generate_ports("fibertree", "fibertree").build(id)

'''Supported instances'''
fmt_uarch_instances={ \
    "all":["/"]    
}

'''Supported instance topologies'''
fmt_uarch_topologies=( \
    { \

        "all": (\
            [(buildMetadataParser,'TestMetadataParser$x',('?',))],
            [('md','md_in$x','TestMetadataParser$x.md_in'),('pos','at_bound_out$x','TestMetadataParser$x.at_bound_out')],
            "fibertree", # Generator type
            "fibertree" # Generator argument from this component attribute
        )

    }
)

'''Concretize SAF to microarchitecture'''
'''- Helper functions/constants for wiring to BufferStub'''
getFMTSAFRankList=lambda fs:fs.getAttributes()[0]
FMTSAFUarchBuffer=lambda fs:[fs.getTarget(),fs.getTarget()+"_datatype_format_uarch"]
FMTUarchBufferWiringEndpts = [['md_out$x','md_in$x'],['at_bound_in$x','at_bound_out$x']]
FMTUarchBufferWiringNetTypes = ['md','pos']
'''- Wire to BufferStub'''
newFMTUarchBufferStubNetlistFromFMTSAF= \
    lambda fs: t_.net_zip(FMTUarchBufferWiringEndpts, FMTUarchBufferWiringNetTypes, \
                          FMTSAFUarchBuffer(fs), \
                          gen_type='rank_list',gen_attr=getFMTSAFRankList(fs))
'''- Concretize'''
FMTSAFtoUarch = \
    lambda fs:buildFormatUarch(fs.getTarget()+"_datatype_format_uarch",fs.getAttributes()[0])