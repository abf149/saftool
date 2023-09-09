'''Build a SAFModel throughput inference problem'''
import util.notation.predicates as p_

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

def out_port_net_dict_from_net_list(net_list,port_list):
    out_port_net_dict={out_port_uri:[] for out_port_uri in port_list}
    for idx,net in enumerate(net_list):
        out_port_net_dict[net["out_port"]].append(idx)

    return out_port_net_dict

def get_object_port_uris_and_attributes(obj,port_list,port_attr_dict,obj_uri=""):
    '''Get object ports and port attributes'''
    obj_port_objlist=obj.getInterface()    
    for port_obj in obj_port_objlist:
        port_uri=uri(obj_uri,port_obj.getId())
        port_list.append(port_uri)
        port_attr_dict[port_uri]={}

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

def get_port_uris_and_attributes_and_nets(obj,port_list,port_attr_dict,net_list,parent_uri=""):
    '''
    Get port URIs for an object; also get nets and recurse into subcomponent if not a primitive.
    '''
    obj_uri=uri(parent_uri,obj.getId())    
    get_object_port_uris_and_attributes(obj,port_list,port_attr_dict,obj_uri=obj_uri)
    if p_.isComponentOrArchitecture(obj):
        get_object_nets(obj,net_list,obj_uri=obj_uri)
        # Recurse into child objects, only if this is not a primitive
        obj_component_objlist=obj.getTopology().getComponentList()         
        for comp in obj_component_objlist:
            get_port_uris_and_attributes_and_nets(comp,port_list,port_attr_dict,net_list, \
                parent_uri=obj_uri)
        

def get_port_uris_and_attributes_and_nets_wrapper(taxo_uarch):
    port_list=[]
    port_attr_dict={} # includes direction
    net_list=[]

    get_port_uris_and_attributes_and_nets(taxo_uarch,port_list,port_attr_dict,net_list)
    out_port_net_dict=out_port_net_dict_from_net_list(net_list,port_list)

    return port_list,port_attr_dict,net_list,out_port_net_dict

def build_scale_inference_problem(taxo_uarch,arch,sparseopts,constraints=[]):
    pass