'''Format microarchitecture'''
from util.notation import microarchitecture as m_, transform as t_
from util.taxonomy.expressions import FormatType

'''Metadata parser microarchitecture primitive definition'''
MetadataParser = m_.PrimitiveCategory().name("MetadataParser") \
                   .port_in("md_in","md","?") \
                   .port_out("at_bound_out","pos","addr") \
                   .attribute("format","format",FormatType.fromIdValue("format","?")) \
                   .generator(None)
buildMetadataParser = \
    lambda fmt_str: MetadataParser.copy().set_attribute('format', \
                                                           FormatType.fromIdValue('format',fmt_str)
                                           )

'''Format microarchitecture component definition'''
FormatUarch = m_.ComponentCategory().name("FormatUarch") \
                                    .port_in("md_in$x","md","$v") \
                                    .port_out("at_bound_out$x","pos","addr") \
                                    .attribute("fibertree",["fibertree"],[None]) \
                                    .generator("fibertree")
buildFormatUarch = \
    lambda id,fibertree:FormatUarch.copy().set_attribute("fibertree",fibertree,"rank_list") \
                                   .generate_ports("fibertree", "fibertree").build(id)

'''Format microarchitecture <> Buffer stub wiring helper functions/constants'''
getFMTSAFRankList=lambda fs:fs.getAttributes()[0]
FMTSAFUarchBuffer=lambda fs:[fs.getTarget(),fs.getTarget()+"_datatype_format_uarch"]
FMTUarchBufferWiringEndpts = [['md_out$x','md_in$x'],['at_bound_in$x','at_bound_out$x']]
FMTUarchBufferWiringNetTypes = ['md','pos']
'''Format microarchitecture <> Buffer stub wiring'''
newFMTUarchBufferStubNetlistFromFMTSAF= \
    lambda fs: t_.net_zip(FMTUarchBufferWiringEndpts, FMTUarchBufferWiringNetTypes, \
                          FMTSAFUarchBuffer(fs), \
                          gen_type='rank_list',gen_attr=getFMTSAFRankList(fs))

'''Format microarchitecture supported instance topology'''
fmt_uarch_topologies=( \
    { \

        "all": (\
            [(buildMetadataParser,'TestMetadataParser$x',('$v',))],
            [('md','md_in$x','TestMetadataParser$x.md_in'),('pos','at_bound_out$x','TestMetadataParser$x.at_bound_out')],
            "fibertree", # Generator type
            "fibertree" # Generator argument from this component attribute
        )

    }
)