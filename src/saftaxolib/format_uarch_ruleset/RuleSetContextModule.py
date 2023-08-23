# Format uarch RuleSet

from util.taxonomy.expressions import *
from util.taxonomy.designelement import *
import util.notation.predicates as p_
import util.notation.generators.boolean_operators as b_
import util.notation.generators.quantifiers as q_
import util.notation.generators.comparison as c_
import util.notation.attributes as a_
import util.notation.microarchitecture as m_
from saftaxolib.primitive_md_parser_ruleset.RuleSetContextModule import MetadataParser
from functools import reduce

def net_zip(port_name_expressions,port_net_type_strs,component_names,gen_type='rank_list',gen_attr=[]):
    net_list=[]

    idx=0
    for fiber in gen_attr:
        # Repeat the same pattern of ports for each fiber format
        # $v = fiber format
        # $x = fiber index
        for pn_exps,net_type_str in zip(port_name_expressions,port_net_type_strs):
            full_port_ids=[component_name+'.'+pn_exp.replace("$x",str(idx)).replace("$v",fiber.getValue()) \
                            for component_name,pn_exp in zip(component_names,pn_exps)]

            net_type=NetType.fromIdValue("TestNetType",net_type_str)
            format_type=FormatType.fromIdValue('TestFormatType','?')
            net_name=full_port_ids[0]
            for kdx in range(1,len(full_port_ids)):
                net_name += '_' + full_port_ids[kdx]
            net_list.append(Net.fromIdAttributes(net_name, net_type, format_type, full_port_ids))

        idx+=1   

    return net_list 

def transformTopology(obj,new_component_list,new_net_list,append=True):

    arch_topology=obj.getTopology()
    if append:
        arch_topology.setComponentList(arch_topology.getComponentList()+list(new_component_list))
        arch_topology.setNetList(arch_topology.getNetList()+list(new_net_list))
    else:
        arch_topology.setComponentList(list(new_component_list))
        arch_topology.setNetList(list(new_net_list))

    obj.setTopology(arch_topology)    
    return obj

def transformSAFs(obj,new_saf_list,append=True):
    if append:
        obj.setSAFList(obj.getSAFList()+list(new_saf_list))
    else:
        obj.setSAFList(list(new_saf_list))
    return obj


# - Format microarchitecture

FormatUarch = m_.ComponentCategory().name("FormatUarch") \
                                    .port_in("md_in$x","md","$v") \
                                    .port_out("at_bound_out$x","pos","addr") \
                                    .attribute("fibertree",["fibertree"],[None]) \
                                    .generator("fibertree")

# - Format SAF rewrite rules

# -- ConcretizeArchitectureFormatSAFsToFormatUarches
# --- concretization rule

newFMTUarchFromFMTSAF= \
    lambda fs: FormatUarch.copy().set_attribute("fibertree",fs.getAttributes()[0],"rank_list") \
                                 .generate_ports("fibertree", "fibertree").build(fs.getTarget()+"_datatype_format_uarch")
newFMTUarchBufferStubNetlistFromFMTSAF= \
    lambda fs: net_zip([['md_out$x','md_in$x'],['at_bound_in$x','at_bound_out$x']], ['md','pos'], \
                       [fs.getTarget(),fs.getTarget()+"_datatype_format_uarch"], \
                       gen_type='rank_list',gen_attr=fs.getAttributes()[0])
isFMTSAF=lambda fs: fs.getCategory()=='format'
SAFfilter=lambda pred:(lambda obj: [fs for fs in obj.getSAFList() if pred(fs)])
concretizeArchitectureFormatSAFsToFormatUarches = \
    lambda obj: transformSAFs(
                    transformTopology(obj, \
                                      map(newFMTUarchFromFMTSAF, SAFfilter(isFMTSAF)(obj)), \
                                      reduce(lambda x,y: x+y, map( \
                                              newFMTUarchBufferStubNetlistFromFMTSAF, \
                                              SAFfilter(isFMTSAF)(obj)),[]), \
                                      append=True), \
                    SAFfilter(b_.NOT(isFMTSAF))(obj), append=False \
                )

'''
def concretizeArchitectureFormatSAFsToFormatUarches(obj):
    #Object is an architecture with at least one format SAF; concretize format SAF(s) to format uarch(es) and critically, DELETE THE FORMAT SAFS
    
    arch_saf_list=obj.getSAFList()

    arch_format_saf_list=[format_saf for format_saf in arch_saf_list if format_saf.getCategory() == 'format']
    arch_non_format_saf_list=[format_saf for format_saf in arch_saf_list if format_saf.getCategory() != 'format']
    arch_format_saf_target_list=[format_saf.getTarget() for format_saf in arch_format_saf_list]
    #arch_target_buffer_interface_list=[obj.getSubcomponentById(target_id).getInterface() for target_id in arch_format_saf_target_list]
    arch_format_saf_ranks_list=[format_saf.getAttributes()[0] for format_saf in arch_format_saf_list]

    arch_topology=obj.getTopology()
    arch_topology_component_list=arch_topology.getComponentList()
    arch_topology_net_list=arch_topology.getNetList()

    for idx in range(len(arch_format_saf_list)):
        # Concretize format SAF to format uarch
        buffer_id=arch_format_saf_target_list[idx]     

        format_uarch_name = buffer_id+"_datatype_format_uarch"
        format_uarch=FormatUarch.copy() \
                            .set_attribute("fibertree",arch_format_saf_ranks_list[idx],"rank_list") \
                            .generate_ports("fibertree","fibertree") \
                            .build(format_uarch_name)

        # Add format uarch to architecture
        arch_topology_component_list.append(format_uarch)

        arch_topology_net_list.extend(net_zip([['md_out$x','md_in$x'],['at_bound_in$x','at_bound_out$x']],['md','pos'],[buffer_id,format_uarch_name],gen_type='rank_list',gen_attr=arch_format_saf_ranks_list[idx]))

    arch_topology.setComponentList(arch_topology_component_list)
    arch_topology.setNetList(arch_topology_net_list)
    obj.setTopology(arch_topology)

    # Delete format SAFs
    obj.setSAFList(arch_non_format_saf_list)

    return obj
'''



''' --- predicate '''
'''Object is an architecture with at least one format SAF'''
predicateIsArchitectureHasFormatSAF=b_.AND(p_.isArchitecture, \
                                           q_.anyForObjSAFs( \
                                                c_.equals( \
                                                    m_.SAFFormat.name_, \
                                                    a_.getCategory \
                                                )
                                            )
                                    )

# - Format uarch rewrite rules

# -- TransformTopologicalHoleToPerRankMdParserTopology: For a format uarch with a topological hole, fill the hole with a topology comprising one MetadataParser primitive per traversed tensor rank at this buffer level

def generateFormatUarchTopology(rank_format_strs):
   # Topology ID
    topology_id='TestTopology'

    # Component list setup
    component_list=[]
    for idx in range(len(rank_format_strs)):
        fmt_str=rank_format_strs[idx]
        component_list.append(MetadataParser.copy().set_attribute('format', \
                                               FormatType.fromIdValue('format',fmt_str)
                                              ).build('TestMetadataParser'+str(idx)))

    # Net list setup

    # - Nets connecting metadata (md) ports to primitives, position (pos) ports to primitives
    net_list=[]
    for idx in range(len(rank_format_strs)): 
        fmt_str=rank_format_strs[idx]        
        # Metadata net
        net_type=NetType.fromIdValue('TestNetType','md')
        format_type=FormatType.fromIdValue('TestFormatType',fmt_str)
        port_id_list=['md_in'+str(idx),'TestMetadataParser'+str(idx)+'.md_in']
        net_md=Net.fromIdAttributes('TestMDNet'+str(idx), net_type, format_type, port_id_list)
        # Position net
        net_type=NetType.fromIdValue('TestNetType','pos')
        format_type=FormatType.fromIdValue('TestFormatType','addr')
        port_id_list=['at_bound_out'+str(idx),'TestMetadataParser'+str(idx)+'.at_bound_out']
        net_at_bound=Net.fromIdAttributes('TestPosNet'+str(idx), net_type, format_type, port_id_list)
        net_list.append(net_md)
        net_list.append(net_at_bound)

    # build topology
    return Topology.fromIdNetlistComponentList(topology_id,net_list,component_list)

def transformTopologicalHoleToPerRankMdParserTopology(obj):
    '''Fill the topological hole with a topology comprising one MetadataParser primitive per traversed tensor rank at this buffer level'''
    rank_format_strs = [fmt_type['value'] for fmt_type in obj.attributes[0]]
    obj.setTopology(generateFormatUarchTopology(rank_format_strs))
    return obj

def predicateIsComponent(obj):
    return type(obj).__name__ == 'Component'

def predicateIsFormatUarch(obj):
    return obj.getCategory() == 'FormatUarch'

def predicateHasTopologicalHole(obj):
    return obj.getTopology().isHole()

def predicateIsComponentIsFormatUarchHasTopologicalHole(obj):
    return predicateIsComponent(obj) and predicateIsFormatUarch(obj) and predicateHasTopologicalHole(obj)

