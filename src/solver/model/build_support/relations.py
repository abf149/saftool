'''
Compute boundary conditions for scale inference by synthesizing relations (eqns/ineqs)
for scale parameters at architecture buffer interfaces
'''
import solver.model.build_support.abstraction as ab, \
       solver.model.build_support.scale as sc

def make_port_uri_attribute(arch_name,buffer_name,port_prefix,direction,idx,attribute):
    return ab.make_port_uri(arch_name,buffer_name,port_prefix,direction,idx)+"_"+attribute

def reln(lhs,reln,rhs):
    return lhs+" "+reln+" "+rhs

def make_read_width_relations(arch_name,buffer_name,idx,oper,rw):
    relation_list=[
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"rw"),oper,str(rw)),
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"rw"),oper,str(rw)),
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"rw"),oper,str(rw))     
    ]

    return relation_list

def make_pos_rate_relations(arch_name,buffer_name,idx,oper,pr):
    relation_list=[
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"pr"),oper,str(pr)),
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"pr"),oper,str(pr)),
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"pr"),oper,str(pr))        
    ]

    return relation_list

def make_wordwidth_relations(arch_name,buffer_name,idx,oper,mod_out_ww,pos_in_ww,at_bound_in_ww):
    relation_list=[
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"ww"),oper,str(mod_out_ww)),
        reln(make_port_uri_attribute(arch_name,buffer_name,"pos","in",idx,"ww"),oper,str(pos_in_ww)),
        reln(make_port_uri_attribute(arch_name,buffer_name,"at_bound","in",idx,"ww"),oper,str(at_bound_in_ww))        
    ]

    return relation_list

def make_payloadwidth_relations(arch_name,buffer_name,idx,oper,mod_out_pw):
    relation_list=[
        reln(make_port_uri_attribute(arch_name,buffer_name,"md","out",idx,"pw"),oper,str(mod_out_pw))
    ]

    return relation_list

def get_scale_boundary_conditions(gpthrpt,port_attr_dict,fmt_iface_bindings,flat_arch,buff_dags,dtype_list):
    relation_list=[]

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

                        relation_list.extend(make_wordwidth_relations("TestArchitecture",buffer,rdx,"==",mdwidth, \
                                                                                                         poswidth, \
                                                                                                         flagwidth))    
                        relation_list.extend(make_payloadwidth_relations("TestArchitecture",buffer,rdx,"==",payloadwidth))                        
                        if rdx < last_rank:
                            relation_list.extend(make_read_width_relations("TestArchitecture",buffer,rdx,"<=",md_storage_width))
                            relation_list.extend(make_read_width_relations("TestArchitecture",buffer,rdx,">",0.0))
                            relation_list.extend(make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",gpthrpt))
                        else: # last rank
                            relation_list.extend(make_read_width_relations("TestArchitecture",buffer,rdx,"==",md_storage_width))
                            relation_list.extend(make_pos_rate_relations("TestArchitecture",buffer,rdx,">=",gpthrpt))
                else:
                    # Not last-level buffer
                    last_rank=len(fmt_iface_bindings[buffer][dtype])-1
                    for rdx,rank in enumerate(fmt_iface_bindings[buffer][dtype]):
                        mdwidth=rank.get('mdwidth',md_storage_width)
                        poswidth=mdwidth
                        flagwidth=1
                        payloadwidth=rank.get('payloadwidth',md_storage_width)
                        
                        relation_list.extend(make_wordwidth_relations("TestArchitecture",buffer,rdx,"==",mdwidth, \
                                                                                                         poswidth, \
                                                                                                         flagwidth))    
                        relation_list.extend(make_payloadwidth_relations("TestArchitecture",buffer,rdx,"==",payloadwidth))                   
                        if rdx < last_rank:
                            relation_list.extend(make_read_width_relations("TestArchitecture",buffer,rdx,"<=",md_storage_width))
                            relation_list.extend(make_pos_rate_relations("TestArchitecture",buffer,rdx,">",0.0))
                        else: # last rank
                            relation_list.extend(make_read_width_relations("TestArchitecture",buffer,rdx,"==",md_storage_width))
                            relation_list.extend(make_pos_rate_relations("TestArchitecture",buffer,rdx,">",0.0))
        else:
            pass

    return relation_list