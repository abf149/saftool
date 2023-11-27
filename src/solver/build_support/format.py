from saflib.architecture.taxo.stub_primitives.BufferStub import BufferStub
from saflib.saf.FormatSAF import FormatSAF
import solver.build_support.arch as ar_
from util.helper import info,warn,error

def get_buffer_stubs_and_format_safs(arch, fmt_iface_bindings, buffer_stub_list=[], saf_list=[]):
    buffer_stub_list=[]
    saf_list=[]
    buffer_hierarchy=ar_.get_buffer_hierarchy(arch)    
    for buffer in buffer_hierarchy:
        datatype_fmt_ifaces=fmt_iface_bindings[buffer]

        if sum([len(datatype_fmt_ifaces[dtype]) for dtype in datatype_fmt_ifaces])>0:
            fmt_saf=FormatSAF.copy() \
                             .target(buffer) \
                             .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree")

            buffer_stub=BufferStub.copy() \
                                  .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree") \
                                  .generate_ports("fibertree","fibertree")
            buffer_stub_list.append((buffer,buffer_stub))
            saf_list.append(("format_saf",fmt_saf))    
    return buffer_stub_list, saf_list