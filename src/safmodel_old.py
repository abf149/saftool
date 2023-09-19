import util.sparseloop_config_processor as sl_config
from util.taxonomy import designelement as de
import os, argparse, test_data as td, copy, yaml, re

def get_primitive_with_name(name,primitive_classes):
    '''Get primitive class declaration from Accelergy primitives structure'''
    search_for_class=[clss for clss in primitive_classes['classes'] if clss['name']==name]
    if len(search_for_class)==0:
        return False
    return search_for_class[0]

def get_component_with_name(name,component_classes):
    '''Get component class declaration from Sparseloop components structure'''
    search_for_class=[clss for clss in component_classes['compound_components']['classes'] if clss['name']==name]
    if len(search_for_class)==0:
        return False
    return search_for_class[0]
    
def set_component(new_component,component_classes):
    '''Add the specified component to the existing Sparseloop components structure'''
    component_classes['compound_components']['classes'].append(new_component)

def build_md_parser_primitive_model(name, topo_md_parser,thrpt):
    pass

def build_format_SAF_model(name, topo_format_uarch,max_thrpt):
    # Get format uarch templates
    saf_primitives=copy.deepcopy(sl_config.load_config_yaml('accelergy/primitive_component_libs/saf_primitives.lib.yaml'))
    saf_model_templates=copy.deepcopy(sl_config.load_config_yaml('accelergy/compound_components_template.yaml'))
    fmt_model_template=get_component_with_name('format_uarch',saf_model_templates)

def add_format_SAF_uarch(buffer,buffer_class,netlist,aggregate_attributes,prim_const,component_classes_w_SAF):
    # Get format uarch templates
    saf_primitives=copy.deepcopy(sl_config.load_config_yaml('accelergy/primitive_component_libs/saf_primitives.lib.yaml'))
    saf_model_templates=copy.deepcopy(sl_config.load_config_yaml('accelergy/compound_components_template.yaml'))
    fmt_model_template_=get_component_with_name('format_uarch',saf_model_templates)

    # Get top-level taxonomic components & netlist
    taxo_netlist=netlist.getTopology().getNetList()    
    taxo_components=netlist.getTopology().getComponentList()
    # Get target buffer instance taxonomic component & its ports
    buffer_name=buffer['name']
    buffer_max_md_thrpt=buffer['attributes']['metadata_storage_width']
    taxo_buffer=[comp for comp in taxo_components if comp.getId()==buffer_name][0]
    taxo_buffer_ports=taxo_buffer.getInterface()
    max_buffer_port_idx=len([md_out_port for md_out_port in taxo_buffer_ports if 'md_out' in md_out_port.getId()])-1
    # Placeholder for new format uarch model
    fmt_uarch_model_name=""

    #
    print('-')    
    print(buffer_name)    
    for net in taxo_netlist:
        net_port_list=net.getPortIdList()        
        buffer_port=[port_id for port_id in net_port_list if buffer_name in port_id and 'md_out' in port_id]        
        if len(buffer_port)>0:
            #print(buffer_port)            
            buffer_port_num=re.findall(r'\d+', buffer_port[0])[-1]
            buffer_port_idx=int(buffer_port_num[0])
            for port_id in net_port_list:
                dest_comp=port_id.split('.')[0]
                if dest_comp != buffer_name:
                    #print('--')
                    for comp in taxo_components:
                        if comp.getId()==dest_comp:
                            print('---')
                            if comp.getCategory()=='FormatUarch':
                                fmt_uarch_model_name=dest_comp
                                print(buffer_port_num) 
                                print(dest_comp)
                                # Build format uarch model
                                # - Attributes
                                fmt_uarch=copy.deepcopy(fmt_model_template_)
                                #fmt_uarch['class']=fmt_uarch['name']
                                fmt_uarch_instance_name=buffer_name+"_fmt_uarch"
                                fmt_uarch['name']=buffer_name+"_format_uarch"
                                aggregate_attributes_fmt=copy.deepcopy(aggregate_attributes)
                                for attrib in fmt_uarch['attributes']:
                                    if attrib in aggregate_attributes:
                                        fmt_uarch[attrib]=aggregate_attributes[attrib]
                                    aggregate_attributes_fmt[attrib]=fmt_uarch['attributes'][attrib]                                        
                                # - Subcomponents
                                # -- md_parser primitive subcomponents
                                fmt_uarch_ports=comp.getInterface()
                                for prt in fmt_uarch_ports:
                                    if 'md_in' in prt.getId():
                                        prt_idx=int(re.findall(r'\d+', prt.getId())[0])
                                        fmt_type_str=prt.getFormatType().getValue()
                                        print("prt_idx",prt_idx,'fmt_type_str',fmt_type_str)
                                        md_parser=copy.deepcopy(get_primitive_with_name('md_parser',saf_primitives))
                                        md_parser['class']=md_parser['name']
                                        md_parser['name']='md_parser'+str(prt_idx)
                                        for attrib in md_parser['attributes']:
                                            if attrib in aggregate_attributes_fmt:
                                                md_parser[attrib]=aggregate_attributes_fmt[attrib]
                                        md_parser['attributes']['metadataformat']=fmt_type_str
                                        # -- Skipping uarch
                                        is_weight=False
                                        if 'weight' in buffer_name and prt_idx>=max_buffer_port_idx:
                                            is_weight=True
                                            print("\n\n","fmt:",fmt_type_str,"\n\n")
                                            intersect=copy.deepcopy(get_primitive_with_name('intersect',saf_primitives))
                                            intersect['class']=intersect['name']
                                            intersect['name']='intersect0'
                                            intersect['attributes']['metadataformat']=fmt_type_str                                            
                                            pgen0=copy.deepcopy(get_primitive_with_name('pgen',saf_primitives))
                                            pgen0['class']=pgen0['name']
                                            pgen0['name']='pgen0'
                                            pgen0['attributes']['metadataformat']=fmt_type_str
                                            pgen1=copy.deepcopy(get_primitive_with_name('pgen',saf_primitives))
                                            pgen1['class']=pgen1['name']
                                            pgen1['name']='pgen1'
                                            pgen1['attributes']['metadataformat']=fmt_type_str                                            
                                        # -- Construct format uarch                                        
                                        if 'subcomponents' not in fmt_uarch:
                                            if is_weight:
                                                fmt_uarch['subcomponents']=[md_parser,intersect,pgen0,pgen1]
                                            else:
                                                fmt_uarch['subcomponents']=[md_parser]
                                        else:
                                            if is_weight:
                                                fmt_uarch['subcomponents'].extend([md_parser,intersect,pgen0,pgen1])
                                            else:
                                                fmt_uarch['subcomponents'].append(md_parser)
                                        for action in fmt_uarch['actions']:
                                            if action['name']=='idle':
                                                if not 'subcomponents' in action:
                                                    if is_weight:                                                    
                                                        action['subcomponents']=[{'name':md_parser['name'],'actions':[{'name':'idle'}]}, \
                                                                                  {'name':intersect['name'],'actions':[{'name':'idle'}]}, \
                                                                                 {'name':pgen0['name'],'actions':[{'name':'idle'}]}, \
                                                                                 {'name':pgen1['name'],'actions':[{'name':'idle'}]}]
                                                    else:
                                                        action['subcomponents']=[{'name':md_parser['name'],'actions':[{'name':'idle'}]}]
                                                else:
                                                    if is_weight:                                                          
                                                        action['subcomponents'].extend([{'name':md_parser['name'],'actions':[{'name':'idle'}]}, \
                                                                                  {'name':intersect['name'],'actions':[{'name':'idle'}]}, \
                                                                                 {'name':pgen0['name'],'actions':[{'name':'idle'}]}, \
                                                                                 {'name':pgen1['name'],'actions':[{'name':'idle'}]}])
                                                    else:
                                                        action['subcomponents'].append({'name':md_parser['name'],'actions':[{'name':'idle'}]})
                                            elif action['name']=='parse_metadata':
                                                if not 'subcomponents' in action:
                                                    if is_weight:                                                       
                                                        action['subcomponents']=[{'name':md_parser['name'],'actions':[{'name':'parse_metadata'}]}, \
                                                                                  {'name':intersect['name'],'actions':[{'name':'parse_metadata'}]}, \
                                                                                 {'name':pgen0['name'],'actions':[{'name':'parse_metadata'}]}, \
                                                                                 {'name':pgen1['name'],'actions':[{'name':'parse_metadata'}]}]
                                                    else:
                                                        action['subcomponents']=[{'name':md_parser['name'],'actions':[{'name':'parse_metadata'}]}]
                                                else:
                                                    if is_weight:                                                        
                                                        action['subcomponents'].extend([{'name':md_parser['name'],'actions':[{'name':'parse_metadata'}]}, \
                                                                                  {'name':intersect['name'],'actions':[{'name':'parse_metadata'}]}, \
                                                                                 {'name':pgen0['name'],'actions':[{'name':'parse_metadata'}]}, \
                                                                                 {'name':pgen1['name'],'actions':[{'name':'parse_metadata'}]}])     
                                                    else:        
                                                        action['subcomponents'].append({'name':md_parser['name'],'actions':[{'name':'parse_metadata'}]})                                            

                                if buffer_port_idx<max_buffer_port_idx:
                                    print('thrpt 0')
                                else:
                                    print('thrpt',buffer_max_md_thrpt)
                                # Inject fmt uarch into components
                                set_component(fmt_uarch,component_classes_w_SAF)
                                # Inject fmt uarch into model
                                fmt_uarch_inst={'name':fmt_uarch_instance_name,'class':fmt_uarch['name'],'attributes':fmt_uarch['attributes']}
                                if 'subcomponents' not in buffer_class:
                                    buffer_class['subcomponents']=[fmt_uarch_inst]
                                else:
                                    print('append')
                                    buffer_class['subcomponents'].append(fmt_uarch_inst)
                                for action in buffer_class['actions']:
                                    if action['name']=='idle':
                                        if not 'subcomponents' in action:
                                            action['subcomponents']=[{'name':fmt_uarch_inst['name'],'actions':[{'name':'idle'}]}]
                                        else:
                                            action['subcomponents'].append({'name':fmt_uarch_inst['name'],'actions':[{'name':'idle'}]})
                                    if 'metadata' in action['name'] and 'read' in action['name'] and not ('gate' in action['name']):
                                        if not 'subcomponents' in action:
                                            action['subcomponents']=[{'name':fmt_uarch_inst['name'],'actions':[{'name':'parse_metadata'}]}]
                                        else:
                                            action['subcomponents'].append({'name':fmt_uarch_inst['name'],'actions':[{'name':'parse_metadata'}]})                                               
                                break
                if len(fmt_uarch_model_name)>0:
                    break
        if len(fmt_uarch_model_name)>0:                
            break

    #print("max_buffer_port_idx:",max_buffer_port_idx)
    #print(taxo_buffer_ports)
    #print(taxo_buffer)

def arch_add_SAF_recursive(hierarchical_arch,flat_arch,component_classes_w_SAF, prefix_, aggregate_attributes_, netlist, prim_const):
    '''Recursive relabeling of buffer subclasses to point to models w/ SAF'''

    prefix=copy.deepcopy(prefix_)

    for idx in range(len(hierarchical_arch)):
        parent=hierarchical_arch[idx]

        if 'local' in parent:
            # Append buffer-level names at this hierarchical level
            for jdx in range(len(parent['local'])):
                lvl=parent['local'][jdx]
                if lvl['name'] != 'MAC':
                    class_lvl=flat_arch[lvl['name']]['class_found']
                    if class_lvl != 'subclass':
                        # If class was not identifiable, do not model SAFs
                        print('Buffer',lvl['name'],'could not be found and will not integrate SAF models. Details:')
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
                            # Name the modified buffer class declaration which supports SAF modeling
                            old_buffer_class_name=lvl[class_lvl]
                            lvl[class_lvl]=lvl[class_lvl]+"_"+lvl['name']+"_SAF"
                            # Copy existing non-SAF buffer class declaration and rename
                            new_class=copy.deepcopy(get_component_with_name(old_buffer_class_name,component_classes_w_SAF))
                            new_class['name']=lvl[class_lvl]
                            # Add format SAFs as-needed
                            add_format_SAF_uarch(lvl,new_class,netlist,aggregate_attributes,prim_const,component_classes_w_SAF)
                            set_component(new_class,component_classes_w_SAF)
                        else:
                            print("Found non-subclass")
                            assert(False)

                    #res[lvl['name']]={attrib:lvl[attrib] for attrib in lvl if attrib != 'name'}
        if 'subtree' in parent:
            # Recurse to list of buffer subtrees below this node
            prefix.extend([idx,'subtree'])
            arch_add_SAF_recursive(parent['subtree'], flat_arch,component_classes_w_SAF, prefix, aggregate_attributes_, netlist, prim_const)

def arch_add_SAF_wrapper(arch_w_SAF, component_classes_w_SAF, netlist, prim_const):
    '''Wrapper for recursive relabeling of buffer subclasses to point to models w/ SAF'''

    flat_arch=sl_config.flatten_arch_wrapper(arch)
    for buffer in flat_arch:
        buff_class=""
        if 'subclass' in flat_arch[buffer]:
            buff_class=flat_arch[buffer]['subclass']
            flat_arch[buffer]['class_found']='subclass'
        else:
            buff_class=flat_arch[buffer]['class']
            flat_arch[buffer]['class_found']='class'
        comp_class=get_component_with_name(buff_class,component_classes_w_SAF)
        if comp_class!=False:
            flat_arch[buffer]['actions']=get_component_with_name(buff_class,component_classes_w_SAF)['actions']
        else:
            # Some classes like DummyBuffer can't be found. For now we will simply avoid assigning SAF uarch to this buffer
            flat_arch[buffer]['class_found']=False

    aggregate_attributes=copy.deepcopy(arch['architecture']['subtree'][0]['attributes'])

    return arch_add_SAF_recursive(arch_w_SAF['architecture']['subtree'], flat_arch, component_classes_w_SAF, ['architecture','subtree'], aggregate_attributes, netlist,prim_const)

def gen_unary_safmodels(netlist, arch, comp_in, prim_const):
    arch_w_SAF=copy.deepcopy(arch)
    comp_out=copy.deepcopy(comp_in)

    arch_add_SAF_wrapper(arch_w_SAF, comp_out, netlist, prim_const)

    return arch_w_SAF, comp_out

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('-l','--saftaxolib',default='saftaxolib/')
    parser.add_argument('-i','--dir-in',default='')
    parser.add_argument('-n','--netlist',default='ref_output/new_arch.yaml')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml')
    parser.add_argument('-c','--comp-in',default='ref_input/compound_components.yaml')
    #parser.add_argument('-m','--map',default='ref_input/map.yaml')
    #parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    #parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml')
    parser.add_argument('-o','--dir-out',default='')
    #parser.add_argument('-b','--binding-out',default='ref_output/bindings.yaml')
    parser.add_argument('-r','--arch-out',default='ref_output/arch_w_SAF.yaml')
    parser.add_argument('-k','--comp-out',default='ref_output/compound_components.yaml')
    args = parser.parse_args()

    print("SAFmodel.\n")

    print("Parsing input files:")

    if len(args.dir_in)>0:
        # Not yet supported
        assert(False)
        """         print("- arch:",args.dir_in+'arch.yaml')
                arch=sl_config.load_config_yaml(args.dir_in+'arch.yaml')
                print("- map:",args.dir_in+'map.yaml')
                mapping=sl_config.load_config_yaml(args.dir_in+'map.yaml')
                print("- prob:",args.dir_in+'prob.yaml')
                prob=sl_config.load_config_yaml(args.dir_in+'prob.yaml')
                print("- sparseopts:",args.dir_in+'sparseopts.yaml')
                sparseopts=sl_config.load_config_yaml(args.dir_in+'sparseopts.yaml')     """    
    else:    
        print("- netlist:",args.netlist)
        #netlist=sl_config.load_config_yaml(args.netlist)
        netlist=de.Architecture.fromYamlFilename(args.netlist)
        print("- arch:",args.arch)
        arch=sl_config.load_config_yaml(args.arch)
        print("- compound components (input):",args.comp_in)
        comp_in=sl_config.load_config_yaml(args.comp_in)
        print("- arch output path:",args.arch_out)
        arch_out_path=args.arch_out
        print("- compound components path (output):",args.comp_out)
        comp_out_path=args.comp_out
        #comp_out=sl_config.load_config_yaml(args.comp_out)
        
        #print("- compound components (output):",args.comp_out)
        #arch=sl_config.load_config_yaml(args.comp_out)

    print("\nLoading primitive component constitutive relations.")
    primitive_constitutive_properties=td.get_test_data()

    arch_w_SAF,comp_out = gen_unary_safmodels(netlist, arch, comp_in, primitive_constitutive_properties)    

    if len(args.dir_out) > 0:
        # Not yet supported
        assert(False)

    print("Saving arch to",arch_out_path,"new components file to",comp_out_path,"...")
    with open(arch_out_path, 'w') as arch_file:
        yaml.dump(arch_w_SAF, arch_file, default_flow_style=False)
    with open(comp_out_path, 'w') as comp_file:
        yaml.dump(comp_out, comp_file, default_flow_style=False)