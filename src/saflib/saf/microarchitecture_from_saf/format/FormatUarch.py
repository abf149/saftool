'''Format microarchitecture'''
from util.notation import microarchitecture as m_, transform as t_
import saflib.microarchitecture.TaxoRegistry as tr_
format_uarch_dict=tr_.getComponent("FormatUarch")
buildFormatUarch=format_uarch_dict['constructor']

'''Concretize SAF to microarchitecture'''
'''- Helper functions/constants for wiring to BufferStub'''
getFMTSAFRankList=lambda fs:fs.getAttributes()[0]
FMTSAFUarchBuffer=lambda fs:[fs.getTarget(),fs.getTarget()+"_datatype_format_uarch"]
FMTUarchBufferWiringEndpts = [['md_out$x','md_in$x'],['at_bound_in$x','at_bound_out$x']]
FMTUarchBufferWiringNetTypes = ['md','flag']
'''- Wire to BufferStub'''
newFMTUarchBufferStubNetlistFromFMTSAF= \
    lambda fs: t_.net_zip(FMTUarchBufferWiringEndpts, FMTUarchBufferWiringNetTypes, \
                          FMTSAFUarchBuffer(fs), \
                          gen_type='rank_list',gen_attr=getFMTSAFRankList(fs))
'''- Concretize'''
FMTSAFtoUarch = \
    lambda fs:buildFormatUarch(fs.getTarget()+"_datatype_format_uarch",fs.getAttributes()[0])