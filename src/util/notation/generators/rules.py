'''Helper functions for processing rules'''
from util.notation import predicates as p_, microarchitecture as m_
from util.notation.generators import boolean_operators as b_
from util.taxonomy.expressions import FormatType, NetType
from util.taxonomy.designelement import Net

def attrCompareTo(obj_attr,inst_attr,attr_info=(None,"string"),wildcard="/",unknown="?"):
    if attr_info[1]=='format':
        return FormatType.compareFormatTypes(obj_attr,inst_attr)
    
    return obj_attr==inst_attr

def allObjAttributesMatchInstanceAttributes(obj_attributes,instance_attributes,attribute_types,wildcard="/",unknown="?"):
    '''
    True if an object's attributes match a particular supported instance.\n

    If not None, instance attributes matching wildcard are not subject to validation.
    If not None, object attributes matching unknown are not subject to validation.\n

    The result of matching reflects those pairs of object/instance attributes remaining
    after the above two filters are applied.\n\n

    Arguments:\n
    - obj_attributes -- list of object attributes. \n
    - instance_attributes -- list of instance attributes.\n
    - wildcard -- instance attribute value not subject to validation; automatic match unless None
    - unknown -- object attribute value representing unknown value; automatic match unless None

    Returns:\n
    - True if all applicable non-unknown object attributes match corresponding applicable non-wildcard instance attributes
    '''
    return all([attrCompareTo(obj_attr,inst_attr,attr_info,wildcard=wildcard,unknown=unknown) \
                    for obj_attr,inst_attr,attr_info in \
                        zip(obj_attributes,instance_attributes,attribute_types) \
                            if ((wildcard is None) or inst_attr!=wildcard) and \
                                ((unknown is None) or (obj_attr!=unknown))])

def findInstanceMatchingObjectAttributes(obj_attributes,supported_instances,attributes):
    '''
    True if an object's attributes match a one from a list of supported instances.\n\n

    Arguments:\n
    - obj_attributes -- list of object attributes. \n
    - supported_instances -- dict of named supported-instance attribute lists.\n\n

    Returns:\n
    - (True,<supp. inst. name>,<supp. inst. attr.>) if all object attributes match 
      corresponding non-wildcard instance attributes, for some supported instance;
      (False,None,None) otherwise.
    '''
    for inst_name in supported_instances:
        # For a given instance,
        inst_attr=supported_instances[inst_name]
        if allObjAttributesMatchInstanceAttributes(obj_attributes,inst_attr,attributes):
            # do object attributes match?
            return (True,inst_name,inst_attr)
    # otherwise...
    return (False,None,None)

def anyInstanceMatchesObjectAttributes(obj_attributes,supported_instances,attributes):
    return findInstanceMatchingObjectAttributes(obj_attributes,supported_instances,attributes)[0]

def isValidComponentOrPrimitiveMatchingCategoryRule(supported_instances,category_template):
    return lambda obj: \
                b_.AND( \
                    lambda x: p_.isComponentOrPrimitiveIsCategory(x,category_template.name_), \
                    b_.NOT(p_.isArchitecture) \
                )(obj), \
           lambda obj: \
                anyInstanceMatchesObjectAttributes(obj.getAttributes(),supported_instances,category_template.attributes_)

def expandComponentsSpec(components_spec, obj, generator_type, generator_arg, component_template):
    if generator_type==None:
        # No generator; no expansion
        return components_spec
    elif generator_type=="fibertree":
        # Repeat components_spec for each fiber rank, substituting
        # rank index for $x and rank format for $v.
        attribute_names=[attr_[0] for attr_ in component_template.attributes_]
        fibertree=obj.getAttributes()[attribute_names.index(generator_arg)]
        rank_list=[fb.getValue() for fb in fibertree]
        expanded_components_spec=[]
        for idx,rank_str in enumerate(rank_list):
            for s in components_spec:
                build_fxn=s[0]
                id=s[1].replace("$x",str(idx)).replace("$v",rank_str)
                build_args=s[2]
                subst_build_args=[]
                for s_arg in build_args:
                    if isinstance(s_arg,str):
                        subst_build_args.append(s_arg.replace("$x",str(idx)).replace("$v",rank_str))
                    else:
                        subst_build_args.append(s_arg)
                subst_build_args=tuple(subst_build_args)
                expanded_components_spec.append((build_fxn,id,subst_build_args))
        return expanded_components_spec

def expandNetlistSpec(netlist_spec, obj, generator_type, generator_arg, category_template):
    if generator_type==None:
        # No generator; no expansion
        return netlist_spec
    elif generator_type=="fibertree":
        # Repeat netlist_spec for each fiber rank, substituting
        # rank index for $x and rank format for $v.
        attribute_names=[attr_[0] for attr_ in category_template.attributes_]
        fibertree=obj.getAttributes()[attribute_names.index(generator_arg)]
        rank_list=[fb.getValue() for fb in fibertree]
        expanded_netlist_spec=[]
        for idx,rank_str in enumerate(rank_list):
            for s in netlist_spec:
                net_type_str=s[0]
                port_list=[port_id.replace("$x",str(idx)).replace("$v",rank_str) for port_id in s[1:]]
                expanded_netlist_spec.append(tuple([net_type_str,*port_list]))
        return expanded_netlist_spec

def transformFillComponentTopologicalHoleWithTopologySpec(obj,instance_topology_spec,category_template,pred):
    if not pred(obj):
        return None

    components_spec=instance_topology_spec[0]
    netlist_spec=instance_topology_spec[1]
    generator_type=instance_topology_spec[2]
    generator_arg_attr=instance_topology_spec[3]

    expanded_components_spec=expandComponentsSpec(components_spec,obj,generator_type, generator_arg_attr,category_template)
    expanded_netlist_spec=expandNetlistSpec(netlist_spec,obj,generator_type,generator_arg_attr,category_template)

    # Component spec: (build fxn,id,build fxn arg tuple)
    components_list=[(s[1],s[0](*(s[2]))) for s in expanded_components_spec]

    # Net spec: (net type, *(port list))
    net_list_=[]
    for sdx in range(len(expanded_netlist_spec)):
        s=expanded_netlist_spec[sdx]
        net_type=NetType.fromIdValue("TestNetType",s[0])
        format_type=FormatType.fromIdValue('TestFormatType','?')        
        net_list_.append((net_type,format_type,*s[1:]))

    obj.setTopology( \
        m_.TopologyWrapper().components(components_list).nets(net_list_).build()
    )

    return obj

def transformFillTopologyOfValidComponentOrPrimitiveMatchingCategoryRule(supported_instances,instance_topologies,category_template):
    pred=lambda obj: b_.AND( \
             lambda x: p_.isComponentOrPrimitiveIsCategory(x,category_template.name_), \
             b_.NOT(p_.isArchitecture), \
             p_.hasTopologicalHole)(obj)
    return pred, \
           lambda obj: \
                transformFillComponentTopologicalHoleWithTopologySpec( \
                    obj, \
                    instance_topologies[ \
                        findInstanceMatchingObjectAttributes(obj.getAttributes(), \
                                                            supported_instances, \
                                                            category_template.attributes_)[1]
                    ], \
                    category_template, \
                    pred
                )