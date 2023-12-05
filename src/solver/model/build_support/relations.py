'''
Compute boundary conditions for scale inference by synthesizing relations (eqns/ineqs)
for scale parameters at architecture buffer interfaces
'''
import solver.model.build_support.abstraction as ab, \
       solver.model.build_support.scale as sc
from core.helper import info, warn, error

def make_port_uri_attribute(arch_name,buffer_name,port_prefix,direction,idx,attribute):
    return ab.make_port_uri(arch_name,buffer_name,port_prefix,direction,idx)+"_"+attribute

def reln(lhs,reln,rhs,censor_lhs=True):
    if censor_lhs:
        return lhs.split("_")[-1]+" "+reln+" "+str(rhs)
    else:
        return lhs+" "+reln+" "+str(rhs)

def make_read_width_relations(arch_name,buffer_name,idx,oper,rw,relation_dict):
    flag_rw=1

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"md","out",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"rw"),oper,str(rw)) \
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"pos","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"rw"),oper,str(rw)) \
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"at_bound","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"rw"),oper,str(flag_rw)) \
    )

def make_pos_rate_relations(arch_name,buffer_name,idx,oper,pr,relation_dict):

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"md","out",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"pr"),oper,str(pr)) \
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"pos","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"pr"),oper,str(pr)) \
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"at_bound","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"pr"),oper,str(pr)) \
    )

def make_wordwidth_relations(arch_name,buffer_name,idx,oper,mod_out_ww,pos_in_ww,at_bound_in_ww,relation_dict):
    
    relation_dict[ab.make_port_uri(arch_name,buffer_name,"md","out",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"ww"),oper,str(mod_out_ww))
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"pos","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"ww"),oper,str(pos_in_ww))
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"at_bound","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"ww"),oper,str(at_bound_in_ww)) 
    )

def make_payloadwidth_relations(arch_name,buffer_name,idx,oper,mod_out_pw,relation_dict):
    relation_dict[ab.make_port_uri(arch_name,buffer_name,"md","out",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"pw"),oper,str(mod_out_pw))
    )

def make_constraint_relations(constraints,relation_dict):
    info("-- Constructing user-provided relations, if any.")
    for cnst in constraints:
        uri_prefix=cnst[0]
        fmt_iface=cnst[1]
        sym_suffix=cnst[2]
        comparison=cnst[3]
        val=cnst[4]

        port_types=[]
        if sym_suffix in 'nc':
            # Number of coordinates in rank
            port_types=['md_out','pos_in','at_bound_in']

        info("--- Parsing user-provided constraint",cnst)
        info("---- uri_prefix =",uri_prefix)
        info("---- fmt_iface =",fmt_iface)
        info("---- sym_suffix =",sym_suffix)
        info("---- comparison =",comparison)
        info("---- val =",val)
        info("---- Applicable port types:",port_types)
        info("--- Adding individual relations.")
        for port_type in port_types:
            new_reln=reln(ab.uri(uri_prefix,port_type+str(fmt_iface))+"_"+sym_suffix, \
                          comparison,val)
            info("---- New relation:",new_reln)
            relation_dict[ab.uri(uri_prefix,port_type+str(fmt_iface))].append(new_reln)
        warn("--- => Done, adding individual relations.")

        warn("--- => Done, parsing user-provided constraint.")
    warn("-- => Done, constructing user-provided relations.")

def get_scale_boundary_conditions(gpthrpt,port_attr_dict,fmt_iface_bindings,flat_arch, \
                                  buff_dags,dtype_list,anchor_overrides_dict,constraints=[]):

    anchor_dict={}

    relation_dict={}
    for buffer in flat_arch:
        fmt_iface=0
        for dtype in dtype_list:
            for _,_ in enumerate(fmt_iface_bindings[buffer][dtype]):
                for port_prefix,port_dir in zip(["md","pos","at_bound"],["out","in","in"]):
                    relation_dict[ab.make_port_uri("TestArchitecture",buffer,port_prefix,port_dir,fmt_iface)]=[]
                fmt_iface+=1

    for bdx,buffer in enumerate(flat_arch):
        md_storage_width=sc.get_buff_md_storage_width(buffer,flat_arch)
        if md_storage_width>0 or any([len(fmt_iface_bindings[buffer][dtype])>0 for dtype in dtype_list]):
            if md_storage_width==-1:
                md_storage_width=1 # Dummy value for dense buffers
            anchor_dict_buffer=anchor_dict.setdefault(buffer,{})
            for dtype in dtype_list:
                info("-- Initializing anchor values for buffer =",buffer,"dtype =",dtype)
                num_fmt_ifaces=len(fmt_iface_bindings[buffer][dtype])
                info("---",str(num_fmt_ifaces),"format interfaces to False")
                anchor_dict_buffer_dtype = \
                    anchor_dict_buffer \
                        .setdefault(dtype,{rdx:False for rdx in range(num_fmt_ifaces)})
                
                if buff_dags[dtype][bdx][-1]:
                    # If last-level buffer for this datatype
                    last_rank=len(fmt_iface_bindings[buffer][dtype])-1
                    for rdx,rank in enumerate(fmt_iface_bindings[buffer][dtype]):

                        mdwidth=rank.get('mdwidth',md_storage_width)
                        poswidth=mdwidth
                        flagwidth=1
                        payloadwidth=rank.get('payloadwidth',md_storage_width)

                        make_wordwidth_relations("TestArchitecture",buffer,rdx,"==",mdwidth, \
                                                                                    poswidth, \
                                                                                    flagwidth, \
                                                                                    relation_dict)

                        make_payloadwidth_relations("TestArchitecture",buffer,rdx,"==",payloadwidth,relation_dict)
                        if rdx < last_rank:
                            #print("last, not last rank",buffer,dtype,rdx,mdwidth,poswidth,flagwidth,payloadwidth,md_storage_width,gpthrpt)
                            make_read_width_relations("TestArchitecture",buffer,rdx,"<=",md_storage_width,relation_dict)
                            make_read_width_relations("TestArchitecture",buffer,rdx,">=",0.0000000001,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",gpthrpt,relation_dict)
                        else: # last rank
                            #print("last, last rank",buffer,dtype,rdx,mdwidth,poswidth,flagwidth,payloadwidth,md_storage_width,gpthrpt)
                            anchor_dict_buffer_dtype[rdx]=True
                            info("-- Strongly-anchored format interface: buffer =",buffer,"dtype =",dtype,"idx =",rdx)
                            make_read_width_relations("TestArchitecture",buffer,rdx,"==",md_storage_width,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",gpthrpt,relation_dict)
                else:
                    # Not last-level buffer
                    last_rank=len(fmt_iface_bindings[buffer][dtype])-1
                    for rdx,rank in enumerate(fmt_iface_bindings[buffer][dtype]):

                        mdwidth=rank.get('mdwidth',md_storage_width)
                        poswidth=mdwidth
                        flagwidth=1
                        payloadwidth=rank.get('payloadwidth',md_storage_width)
                        
                        make_wordwidth_relations("TestArchitecture",buffer,rdx,"==",mdwidth, \
                                                                                    poswidth, \
                                                                                    flagwidth,\
                                                                                    relation_dict)
                        make_payloadwidth_relations("TestArchitecture",buffer,rdx,"==",payloadwidth,relation_dict)
                        if rdx < last_rank:
                            #print("non-last, not last rank",buffer,dtype,rdx,mdwidth,poswidth,flagwidth,payloadwidth,md_storage_width,gpthrpt)
                            make_read_width_relations("TestArchitecture",buffer,rdx,"<=",md_storage_width,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",0.0000000001,relation_dict)
                        else: # last rank
                            #print("non-last, last rank",buffer,dtype,rdx,mdwidth,poswidth,flagwidth,payloadwidth,md_storage_width,gpthrpt)
                            anchor_dict_buffer_dtype[rdx]=True
                            info("-- Strongly-anchored format interface: buffer =",buffer,"dtype =",dtype,"idx =",rdx)
                            make_read_width_relations("TestArchitecture",buffer,rdx,"==",md_storage_width,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",0.0000000001,relation_dict)
        else:
            pass

    # Apply user-provided anchor overrides
    info("-- Anchor dict before overrides:",anchor_dict)

    for buffer in anchor_overrides_dict:
        for dtype in anchor_overrides_dict[buffer]:
            for rdx in anchor_overrides_dict[buffer][dtype]:
                info("--- Overwriting anchor @ buffer =",buffer,"dtype =",dtype,"idx =", \
                     rdx,"from",anchor_dict[buffer][dtype][rdx],"to", \
                     anchor_overrides_dict[buffer][dtype][rdx])
                anchor_dict[buffer][dtype][rdx] = \
                    anchor_overrides_dict[buffer][dtype][rdx]

    info("-- Final anchor dict:",anchor_dict)

    # Include relations provided as user-specified constraints
    make_constraint_relations(constraints,relation_dict)

    return relation_dict,anchor_dict