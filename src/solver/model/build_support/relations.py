'''
Compute boundary conditions for scale inference by synthesizing relations (eqns/ineqs)
for scale parameters at architecture buffer interfaces
'''
import solver.model.build_support.abstraction as ab, \
       solver.model.build_support.scale as sc

def make_port_uri_attribute(arch_name,buffer_name,port_prefix,direction,idx,attribute):
    return ab.make_port_uri(arch_name,buffer_name,port_prefix,direction,idx)+"_"+attribute

def reln(lhs,reln,rhs,censor_lhs=True):
    if censor_lhs:
        return lhs.split("_")[-1]+" "+reln+" "+str(rhs)
    else:
        return lhs+" "+reln+" "+str(rhs)

def make_read_width_relations(arch_name,buffer_name,idx,oper,rw,relation_dict):

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"md","out",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"rw"),oper,str(rw)) \
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"pos","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"rw"),oper,str(rw)) \
    )

    relation_dict[ab.make_port_uri(arch_name,buffer_name,"at_bound","in",idx)].append( \
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"rw"),oper,str(rw)) \
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
    #('TestArchitecture.weight_spad',0,'nc','<=',4)
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

        for port_type in port_types:
            relation_dict[ab.uri(uri_prefix,port_type+str(fmt_iface))].append( \
                reln(ab.uri(uri_prefix,port_type+str(fmt_iface))+"_"+sym_suffix, \
                     comparison,val) \
            )

def get_scale_boundary_conditions(gpthrpt,port_attr_dict,fmt_iface_bindings,flat_arch, \
                                  buff_dags,dtype_list,constraints=[]):
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
        if md_storage_width>0:
            for dtype in dtype_list:
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
                            make_read_width_relations("TestArchitecture",buffer,rdx,"<=",md_storage_width,relation_dict)
                            make_read_width_relations("TestArchitecture",buffer,rdx,">",0.0,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",gpthrpt,relation_dict)
                        else: # last rank
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
                            make_read_width_relations("TestArchitecture",buffer,rdx,"<=",md_storage_width,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">",0.0,relation_dict)
                        else: # last rank
                            make_read_width_relations("TestArchitecture",buffer,rdx,"==",md_storage_width,relation_dict)
                            make_pos_rate_relations("TestArchitecture",buffer,rdx,">",0.0,relation_dict)
        else:
            pass

    # Include relations provided as user-specified constraints
    make_constraint_relations(constraints,relation_dict)

    return relation_dict