from saflib.architecture.taxo.stub_primitives.BufferStub import BufferStub
from saflib.saf.FormatSAF import FormatSAF
import solver.build_support.arch as ar_
from core.helper import info,warn,error

def get_buffer_stubs_and_format_safs(arch, fmt_iface_bindings, buffer_stub_list=[], saf_list=[]):
    info("-- Generating buffer stubs and Format SAFs")
    buffer_stub_list=[]
    saf_list=[]
    buffer_hierarchy=ar_.get_buffer_hierarchy(arch)    
    for buffer in buffer_hierarchy:
        info("--- Buffer:",buffer)
        datatype_fmt_ifaces=fmt_iface_bindings[buffer]

        if sum([len(datatype_fmt_ifaces[dtype]) for dtype in datatype_fmt_ifaces])>0:
            info("---- Format interface bindings:",datatype_fmt_ifaces)
            if any([(len(datatype_fmt_ifaces[dtype])>0 and (not datatype_fmt_ifaces[dtype][0]['dense'])) \
                    for dtype in datatype_fmt_ifaces]):
                info('---- Generating FormatSAF')
                info("")
                fmt_saf=FormatSAF.copy() \
                                .target(buffer) \
                                .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree")
                info("fmt_saf=FormatSAF.copy()")
                info(".target(",buffer,")")
                info(".set_attribute(\'fibertree\',",datatype_fmt_ifaces,",\'fibertree\')")
                info("")
                warn("---- => Done, generating FormatSAF")
                saf_list.append(("format_saf",fmt_saf))  
            else:
                warn("---- Buffer",buffer,"has only dense format interfaces; not generating FormatSAF")

            info("---- Generating BufferStub")
            info("")
            buffer_stub=BufferStub.copy() \
                                  .set_attribute("fibertree",datatype_fmt_ifaces,"fibertree") \
                                  .generate_ports("fibertree","fibertree")
            info("buffer_stub=BufferStub.copy()")
            info(".set_attribute(\'fibertree\',",datatype_fmt_ifaces,",\'fibertree\')")
            info(".generate_ports(\'fibertree\',\'fibertree\')")
            info("")
            warn("---- => Done, generating BufferStub")
            buffer_stub_list.append((buffer,buffer_stub))
        else:
            warn("---- Buffer",buffer,"has no format interfaces; skipping")
  
    warn("-- => Done, generating buffer stubs and Format SAFs")
    return buffer_stub_list, saf_list