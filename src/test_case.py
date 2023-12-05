import os
from core import sparseloop_config_processor as sl_config
import test_data as td
from test_data import NO_EDGE, GENERIC_EDGE, PRIMITIVE_EDGE
import copy

'''
Input files
'''

primitive_constitutive_properties, \
arch, \
primitive_instances, \
annotated_reduced_graph, \
component_class_path, \
port_to_buffer, \
buffer_to_port=td.get_test_data()

#arch_path='ref_input/arch.yaml'
#arch=sl_config.load_config_yaml(arch_path)


# Load components/
arch_component_classes={}
if not os.path.isdir(component_class_path):
    # Load lumped compound_components file
    arch_component_classes=sl_config.load_config_yaml(component_class_path)
    assert('compound_components' in arch_component_classes)
    arch_component_classes={clss['name']:clss for clss in arch_component_classes['compound_components']['classes']}
#print("\n",arch_component_classes,"\n")

# Load architecture; flatten; augment with class actions
# Assumes MAC is excluded

design_attributes=arch['architecture']['subtree'][0]['attributes']

flat_arch=sl_config.flatten_arch_wrapper(arch)
for buffer in flat_arch:
    buff_class=""
    if 'subclass' in flat_arch[buffer]:
        buff_class=flat_arch[buffer]['subclass']
        flat_arch[buffer]['class_found']='subclass'
    else:
        buff_class=flat_arch[buffer]['class']
        flat_arch[buffer]['class_found']='class'
    if buff_class in arch_component_classes:
        flat_arch[buffer]['actions']=arch_component_classes[buff_class]['actions']
    else:
        # Some classes like DummyBuffer can't be found. For now we will simply avoid assigning SAF uarch to this buffer
        flat_arch[buffer]['class_found']=False


# print({buffer:flat_arch[buffer]['class_found'] for buffer in flat_arch})

'''
Generate new components with SAF
'''
arch_w_SAF=copy.deepcopy(arch)
component_classes_w_SAF=copy.deepcopy(arch_component_classes)
buffer_to_component_class_w_SAF={}

def build_component_actions_recursive(full_port,aggregate_attributes):
    global arch_w_SAF
    global component_classes_w_SAF
    global buffer_to_component_class_w_SAF

    actions_expored=[]   

def build_component_classes_recursive(name_prefix,component_class,full_port,aggregate_attributes):
    global arch_w_SAF
    global component_classes_w_SAF
    global buffer_to_component_class_w_SAF

    parent_name_suffix='_saf'
    
    full_port_info=annotated_reduced_graph[full_port]
    port_component_name=full_port_info['component_name']

    if port_component_name in primitive_instances:
        pass

    component_class_name=''
    component_name=''

    edges_out=annotated_reduced_graph[full_port]['edges_out']

    next_ports=[]
    for full_port in full_ports:
        pass

    return parent_name_suffix, component_class_name, component_name, next_ports


def build_component_classes_wrapper(buffer_name,class_name,class_lvl,aggregate_attributes):
    global arch_w_SAF
    global component_classes_w_SAF
    global buffer_to_component_class_w_SAF
    assert(class_lvl=='subclass')
    #print("\n\n",aggregate_attributes,"\n\n")

    new_class_name=buffer_name + "_" + class_name
    buffer_full_out_ports=[full_port for full_port in buffer_to_port[buffer_name] if 'out' in full_port]
    
    for full_out_port in buffer_full_out_ports:
        full_port_info=annotated_reduced_graph[full_port]
        class_name_suffix=build_component_classes_recursive(full_out_port,aggregate_attributes)
        new_class_name += '_' + class_name_suffix
        

def arch_add_SAF_recursive(hierarchical_arch, prefix_, aggregate_attributes_):
    '''Recursive relabeling of buffer subclasses to point to models w/ SAF'''

    global arch_w_SAF
    global component_classes_w_SAF
    global buffer_to_component_class_w_SAF

    prefix=copy.deepcopy(prefix_)

    for idx in range(len(hierarchical_arch)):
        parent=hierarchical_arch[idx]

        if 'local' in parent:
            # Append buffer-level names at this hierarchical level
            for jdx in range(len(parent['local'])):
                lvl=parent['local'][jdx]
                if lvl['name'] != 'MAC':
                    class_lvl=flat_arch[lvl['name']]['class_found']
                    if class_lvl == False:
                        # If class was not identifiable, do not model SAFs
                        print('Buffer',lvl['name'],'subclass',lvl['subclass'],'could not be found and will not integrate SAF models. Details:')
                        print('- Buffer path in arch:',prefix)
                        print('  - idx',idx,'->local->',jdx,'->{',lvl['name'],'}:',class_lvl)
                    else:
                        #print('prefix:',prefix)
                        #print('arrived at idx',idx,'->local->',jdx,'->{',lvl['name'],'}:',class_lvl)
                        aggregate_attributes=copy.deepcopy(aggregate_attributes_)
                        for attrib in lvl['attributes']:
                            # Update attribute space with attributes defined for this component
                            aggregate_attributes[attrib]=lvl['attributes'][attrib]

                        if class_lvl=='subclass':
                            new_buffer_class_name=build_component_classes_wrapper(lvl['name'],lvl[class_lvl],class_lvl,aggregate_attributes)
                            lvl['subclass']=new_buffer_class_name
                        else:
                            print("Found non-subclass")
                            assert(False)

                    #res[lvl['name']]={attrib:lvl[attrib] for attrib in lvl if attrib != 'name'}
        if 'subtree' in parent:
            # Recurse to list of buffer subtrees below this node
            prefix.extend([idx,'subtree'])
            arch_add_SAF_recursive(parent['subtree'],prefix)

def arch_add_SAF_wrapper():
    '''Wrapper for recursive relabeling of buffer subclasses to point to models w/ SAF'''

    global arch_w_SAF

    aggregate_attributes=copy.deepcopy(design_attributes)

    return arch_add_SAF_recursive(arch_w_SAF['architecture']['subtree'], ['architecture','subtree'], aggregate_attributes)

arch_add_SAF_wrapper()
print(arch_w_SAF)