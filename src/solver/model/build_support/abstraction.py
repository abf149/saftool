'''
Consistent abstractions for representing microarchitecture as a graph of ports
'''
import core.notation.predicates as p_
import solver.model.build_support.scale as sc

def uri(prfx,sffx):
    '''Extend a uri with a suffix; semantics are similar to os.path'''
    prfx_strp=prfx
    sffx_strp=sffx
    if len(prfx)>0 and prfx[-1]==".":
        prfx_strp=prfx[0:-1]

    assert(len(sffx)>0)
    if sffx[0]==".":
        sffx_strp=sffx[1:]
    
    if len(prfx_strp)>0:
        return prfx_strp + "." + sffx_strp
    else:
        return sffx_strp

def split_uri(uri):
    uri_split=uri.split('.')
    base_id=uri_split[-1]
    prefix_split=uri_split[0:-1]
    return prefix_split,base_id

def make_port_uri(arch_name,buffer_name,port_prefix,direction,idx):
    return uri(uri(arch_name,buffer_name),port_prefix+"_"+direction+str(idx))

def out_port_net_dict_from_net_list(net_list):
    return {net["out_port"]:idx for idx,net in enumerate(net_list)}

def in_port_net_dict_from_net_list(net_list):
    return {in_port:idx for idx,net in enumerate(net_list) for in_port in net["in_ports"]}

def get_object_port_uris_and_attributes(obj,port_list,port_attr_dict,flat_arch,buffer,obj_uri=""):
    '''Get object ports and port attributes'''
    obj_port_objlist=obj.getInterface() 
    if p_.isCategory(obj,"BufferStub"):
        # Architectural buffer stub
        if 'metadata_storage_width' in flat_arch[buffer]['attributes']:
            # Buffer stub has at least some sparse ranks
            md_storage_width=flat_arch[buffer]['attributes']['metadata_storage_width']
            for port_obj in obj_port_objlist:
                port_uri=uri(obj_uri,port_obj.getId())
                port_list.append(port_uri)
                port_attr_dict[port_uri]={"obj":obj_uri,"ww":md_storage_width,"pw":md_storage_width, \
                                          "microarchitecture":False,"primitive":True}
        elif len(obj_port_objlist)>0:
            # Entirely dense buffer stub with user-specified dense ranks
            # Dummy value for md_storage_width
            md_storage_width=1
            for port_obj in obj_port_objlist:
                port_uri=uri(obj_uri,port_obj.getId())
                port_list.append(port_uri)
                port_attr_dict[port_uri]={"obj":obj_uri,"ww":md_storage_width,"pw":md_storage_width, \
                                          "microarchitecture":False,"primitive":True}
    else:
        # Microarchitectural component or primitive
        for port_obj in obj_port_objlist:
            port_uri=uri(obj_uri,port_obj.getId())
            port_list.append(port_uri)
            port_attr_dict[port_uri]={"obj":obj_uri,"microarchitecture":True,"primitive":p_.isPrimitive(obj)}

def port_is_out_in_context(port_relative_uri,obj):
    '''
    In-context, a port functions as an out-port if
    (1) it is a subcomponent out-port or
    (2) it is an in-port of the component currently under consideration
    '''
    port_obj=obj.getPortById(port_relative_uri)
    return (port_obj.getDirection()=="out" and ("." in port_relative_uri)) or \
           (port_obj.getDirection()=="in" and ("." not in port_relative_uri))

def get_object_nets(obj,net_list,obj_uri=""):
    '''Get object nets'''
    obj_topology=obj.getTopology()
    obj_net_objlist=obj_topology.getNetList()    
    for net_obj in obj_net_objlist:
        out_port=""
        in_ports=[]
        net_name=net_obj.getId()
        net_uri=uri(obj_uri,net_name)
        for port_relative_uri in net_obj.getPortIdList():
            # Identify net's out port and in port(s)
            port_uri=uri(obj_uri,port_relative_uri)
            port_is_out=port_is_out_in_context(port_relative_uri,obj)
            if port_is_out and out_port=="":
                out_port=port_uri
            elif not port_is_out:
                in_ports.append(port_uri)
            elif port_is_out:
                print("Error attempted to modify net out_port from",out_port, \
                    "to",port_relative_uri,"on net",net_uri)
                assert(False)
        net_list.append({"net_uri":net_uri,"out_port":out_port,"in_ports":in_ports})

def get_port_uris_and_attributes_and_nets(obj,port_list,port_attr_dict,net_list,flat_arch,parent_uri="",buffer=None):
    '''
    Get port URIs for an object; also get nets and recurse into subcomponent if not a primitive.
    '''
    obj_uri=uri(parent_uri,obj.getId())    
    get_object_port_uris_and_attributes(obj,port_list,port_attr_dict,flat_arch,buffer,obj_uri=obj_uri)
    if p_.isComponentOrArchitecture(obj):
        get_object_nets(obj,net_list,obj_uri=obj_uri)
        # Recurse into child objects, only if this is not a primitive
        obj_component_objlist=obj.getTopology().getComponentList()
        new_buffer=buffer
        for comp in obj_component_objlist:
            if buffer is None:
                new_buffer=comp.getId()
            get_port_uris_and_attributes_and_nets(comp,port_list,port_attr_dict,net_list, flat_arch, \
                parent_uri=obj_uri,buffer=new_buffer)

def get_port_uris_and_attributes_and_nets_wrapper(taxo_uarch,flat_arch):
    port_list=[]
    port_attr_dict={} # includes direction
    net_list=[]

    get_port_uris_and_attributes_and_nets(taxo_uarch,port_list,port_attr_dict,net_list,flat_arch)
    out_port_net_dict=out_port_net_dict_from_net_list(net_list)
    in_port_net_dict=in_port_net_dict_from_net_list(net_list)

    # Generate mathematical symbols for solving scale inference problem
    # - rw - read width
    # - pr - position rate
    # - cr - coordinate rate
    # - ww - word width
    # - pw - position width
    # - nc - num coordinates in rank
    symbol_list=[port_uri+"_"+sym for port_uri in port_list for sym in sc.sym_suffixes]

    uarch_symbol_list=[port_uri+"_"+sym \
        for sym in sc.sym_suffixes for port_uri in port_list if port_attr_dict[port_uri]['microarchitecture']]

    # Generate mapping from objects to ports
    obj_to_ports={}
    for port_uri in port_list:
        if port_attr_dict[port_uri]['obj'] in obj_to_ports:
            obj_to_ports[port_attr_dict[port_uri]['obj']].append(port_uri)
        else:
            obj_to_ports[port_attr_dict[port_uri]['obj']]=[port_uri]

    return port_list,port_attr_dict,net_list,out_port_net_dict,in_port_net_dict,symbol_list,uarch_symbol_list,obj_to_ports

def build_component_dict(obj,obj_dict={},uri_prefix=""):
    if not p_.isArchitecture(obj):
        obj_dict[uri(uri_prefix,obj.getId())]={"obj":obj, \
                            "microarchitecture":obj.getCategory()!="BufferStub", \
                            "primitive":(not p_.isComponentOrArchitecture(obj)), \
                            "uri_prefix":uri_prefix}

    #print(obj.getId())
    if p_.isComponentOrArchitecture(obj):
        # Recurse into child objects, only if this is not a primitive
        new_prefix=uri(uri_prefix,obj.getId())
        obj_component_objlist=obj.getTopology().getComponentList()
        for comp in obj_component_objlist:
            build_component_dict(comp,obj_dict,new_prefix)