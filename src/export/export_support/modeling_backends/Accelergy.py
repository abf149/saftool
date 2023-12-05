'''Accelergy compatibility layer'''
from core.helper import info,warn,error
import core.sparseloop_config_processor as sl_config
import core.model.CasCompat as cc_
import yaml
import pickle, shutil, os, copy
import solver.model.build_support.abstraction as ab_
import core.general_io as genio

def dict_representer(dumper, data):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

yaml.add_representer(dict, dict_representer)

accelergy_root="src/accelergy/"
ERTART_fn="primitives_ERT_ART.pkl"
lib_fn="saf_primitives.lib.yaml"
repo_obj_install_path=os.path.join(os.path.join(accelergy_root,"data/"),ERTART_fn)
repo_lib_install_path=os.path.join(os.path.join(accelergy_root,"primitive_component_libs/"),lib_fn)
obj_install_path=genio.get_abs_path_relative_to_cwd(repo_obj_install_path)
lib_install_path=genio.get_abs_path_relative_to_cwd(repo_lib_install_path)

def getDefaultInstallPath():
    global obj_install_path
    return obj_install_path

def action_expression_from_tuple(action_tuple):
    action_dict={"name":action_tuple[0]}
    args_=action_tuple[1]
    if len(args_) > 0:
        action_dict["arguments"]={}
        for arg_ in args_:
            arg_name=arg_[0]
            arg_default=0
            if len(arg_) > 2:
                arg_default=arg_[2]
            action_dict["arguments"][arg_name]=arg_default
    

    return action_dict

def getAccelergyPrimitivesLibrary(analytical_primitive_model_classes_dict, \
                                  analytical_primitive_model_actions_dict, \
                                  backend_args={}):

    info("--- moving forward with Accelergy modeling backend...")
    accelergy_version=backend_args['accelergy_version']
    # analytical_model_classes_dict[name_][yield_]
    primitives_lib={
                    "version": accelergy_version,
                    "classes":[\
                        {
                            "name":name_,
                            "attributes": { \
                                yield_: "must_specify" \
                                for yield_ in analytical_primitive_model_classes_dict[name_]
                            }, \
                            "actions":[ \
                                action_expression_from_tuple(act_tuple)
                                for act_tuple in analytical_primitive_model_actions_dict[name_]
                            ]
                        }
                        for name_ in analytical_primitive_model_classes_dict
                    ]}


    warn("--- done, build primitive classes library")
    return primitives_lib

def buildSubcomponentsStructure(comp_uri, \
                                analytical_component_model_classes_dict, \
                                analytical_primitive_model_classes_dict, \
                                abstract_analytical_component_models_dict, \
                                abstract_analytical_primitive_models_dict, \
                                analytical_component_model_actions_dict, \
                                component_energy_action_tree):

    subcomp_name_list=abstract_analytical_component_models_dict[comp_uri]['subcomponent_list']
    subcomp_uri_list=[ab_.uri(comp_uri,subcomp_name)\
                        for subcomp_name in subcomp_name_list]

    #TODO: support true subcomponents
    return \
        [
            {
                "name":subcomp_name,
                "class":abstract_analytical_primitive_models_dict[subcomp_uri]['category'],
                "attributes": {
                    attr_:abstract_analytical_primitive_models_dict[subcomp_uri]['attributes'][attr_]
                        for attr_ in abstract_analytical_primitive_models_dict[subcomp_uri]['attributes']
                }
            }
            for subcomp_name,subcomp_uri in zip(subcomp_name_list,subcomp_uri_list)
        ]

def buildComponentSubActionStructure(comp_uri, \
                                     analytical_component_model_classes_dict, \
                                     analytical_primitive_model_classes_dict, \
                                     abstract_analytical_component_models_dict, \
                                     abstract_analytical_primitive_models_dict, \
                                     analytical_component_model_actions_dict, \
                                     component_energy_action_tree):
    
    comp_action_dict=component_energy_action_tree[comp_uri]

    return \
        [
            {
                "name":action_,
                "subcomponents": [ \
                    { \
                        "name":ab_.split_uri(subcomp_uri)[1], \
                        "actions": [ \
                            {"name":sub_action}
                            for sub_action in comp_action_dict[action_][subcomp_uri]
                        ]
                    } \
                    for subcomp_uri in comp_action_dict[action_] \
                ]
            }
            for action_ in comp_action_dict
        ]    

def getAccelergySingleComponentStructure(comp_uri, \
                                         analytical_component_model_classes_dict, \
                                         analytical_primitive_model_classes_dict, \
                                         abstract_analytical_component_models_dict, \
                                         abstract_analytical_primitive_models_dict, \
                                         analytical_component_model_actions_dict, \
                                         component_energy_action_tree, \
                                         backend_args={}):

    yield_list=list(analytical_component_model_classes_dict[ \
        abstract_analytical_component_models_dict[comp_uri]['category']+'Model'
    ])
    component_struct={
                        "name":cc_.create_safe_symbol(comp_uri),
                        "attributes": { \
                            yield_: "must_specify" \
                            for yield_ in yield_list \
                                if type(yield_).__name__ != "list"
                        }, \
                        "subcomponents": \
                            buildSubcomponentsStructure(comp_uri, \
                                                        analytical_component_model_classes_dict, \
                                                        analytical_primitive_model_classes_dict, \
                                                        abstract_analytical_component_models_dict, \
                                                        abstract_analytical_primitive_models_dict, \
                                                        analytical_component_model_actions_dict, \
                                                        component_energy_action_tree),
                        "actions": \
                            buildComponentSubActionStructure(comp_uri, \
                                                             analytical_component_model_classes_dict, \
                                                             analytical_primitive_model_classes_dict, \
                                                             abstract_analytical_component_models_dict, \
                                                             abstract_analytical_primitive_models_dict, \
                                                             analytical_component_model_actions_dict, \
                                                             component_energy_action_tree)
                     }

    return component_struct

def getAccelergyComponentsLibrary(analytical_component_model_classes_dict, \
                                  analytical_primitive_model_classes_dict, \
                                  analytical_component_model_actions_dict, \
                                  abstract_analytical_primitive_models_dict, \
                                  abstract_analytical_component_models_dict, \
                                  component_energy_action_tree, \
                                  backend_args={}):
    info("--- moving forward with Accelergy modeling backend...")

    component_struct_list=[]

    for comp_uri in abstract_analytical_component_models_dict:
        component_struct=getAccelergySingleComponentStructure(comp_uri, \
                                                              analytical_component_model_classes_dict, \
                                                              analytical_primitive_model_classes_dict, \
                                                              abstract_analytical_component_models_dict, \
                                                              abstract_analytical_primitive_models_dict, \
                                                              analytical_component_model_actions_dict, \
                                                              component_energy_action_tree, \
                                                              backend_args=backend_args)
        
        component_struct_list.append(component_struct)

    warn("--- done, build component classes library")
    return {"component_struct_list":component_struct_list, \
            "accelergy_version":backend_args['accelergy_version']}

def search_for_primitive(arch_buff_subclass_name,backend_args):
    library_search_paths=backend_args["library_search_paths"]
    info("------- Architecture buffer subclass name:",arch_buff_subclass_name)
    info("------- Library search paths:",library_search_paths)

    for search_path in library_search_paths:
        info("------- Searching",search_path)
        try:
            comp_lib=sl_config.load_config_yaml(search_path)
            info("-------- Successfully loaded file...")
            # Determine whether we are working with primitives or components
            # and handle accordingly
            classes=None
            if 'compound_components' in comp_lib:
                info("-------- (Accelergy components file)")
                classes=comp_lib['compound_components']['classes']
            else:
                info("-------- (Accelergy primitives file)")
                classes=comp_lib['classes']
            assert(classes is not None)
            info("-------- Scanning",len(classes),"classes...")
            for cls_ in classes:
                if cls_["name"] == arch_buff_subclass_name:
                    warn("-------- => Found class",cls_["name"])
                    info("--------",cls_)
                    warn("------ => Done, searching more broadly for primitive/component")
                    return cls_
        except:
            warn("-------- Could not open",search_path,"; skipping.")

        error("Finished searching more broadly for component",arch_buff_subclass_name, \
              "but could not find it.",also_stdout=True)
        info("Terminating.")
        assert(False)
def getArchInstanceAndClass(buffer_id,flat_arch,flat_comp_dict,backend_args={}):
    info("----- Getting architectural component instance and class")
    info("------ buffer_id =",buffer_id)
    info("------ len(flat_comp_dict) =",str(len(flat_comp_dict)))
    arch_buff=flat_arch[buffer_id]
    assert(arch_buff['class']=='storage')
    arch_buff_subclass_name=arch_buff['subclass']
    arch_buff_attributes=arch_buff['attributes']
    buff_class_def=None
    if arch_buff_subclass_name not in flat_comp_dict:
        # If architectural buffer subclass name is not immediately found in user-provided components,
        # search in additional locations
        if len(backend_args)>0 and "library_search_paths" in backend_args:
            info("------ Could not find subclass",arch_buff_subclass_name,"in user-provided component files; search more broadly.")
            buff_class_def=search_for_primitive(arch_buff_subclass_name,backend_args=backend_args)
            warn("------ => Done, searching more broadly.")
        else:
            error("Could not find architectural buffer subclass",arch_buff_subclass_name, \
                  "in user-specified components, and no other search locations were specified.",also_stdout=True)
            info("- buffer_id:",buffer_id)
            info("- flat_arch:",flat_arch)
            info("- len(flat_comp_dict):",flat_comp_dict)
            info("- backend_args:",backend_args)
            info("Terminating.")
            assert(False)
    else:
        buff_class_def=flat_comp_dict[arch_buff_subclass_name]
    buff_class_attributes=buff_class_def['attributes']
    actions_dict=buff_class_def['actions']
    warn("----- => Done, getting architectural component instance and class")
    return arch_buff_subclass_name,arch_buff,arch_buff_attributes, \
           buff_class_def,buff_class_attributes,actions_dict

def getBufferWrapperId(arch_buff_subclass_id,buffer_uri):
    return arch_buff_subclass_id+"_"+cc_.create_safe_symbol(buffer_uri)

def getUarchModelInstanceId(uarch_uri):
    return "inst_"+cc_.create_safe_symbol(uarch_uri)

def getAccelergySingleBufferStructure(flat_arch, \
                                      flat_comp_dict, \
                                      backend_comp_lib_rep, \
                                      buffer_uri, \
                                      analytical_component_model_classes_dict, \
                                      analytical_primitive_model_classes_dict, \
                                      abstract_analytical_component_models_dict, \
                                      abstract_analytical_primitive_models_dict, \
                                      analytical_component_model_actions_dict, \
                                      buffer_action_tree, \
                                      backend_args={}):

    info("----",buffer_uri)

    prefix_split,buffer_id=ab_.split_uri(buffer_uri)
    spec_action_tree=buffer_action_tree[buffer_uri]
    arch_buff_subclass_id,arch_buff,arch_buff_attributes, \
        buff_class_def,buff_class_attributes,buff_class_actions_list= \
            getArchInstanceAndClass(buffer_id,flat_arch,flat_comp_dict,backend_args=backend_args)
    buffer_wrapper_id=getBufferWrapperId(arch_buff_subclass_id,buffer_uri)
    wrapped_buffer_id=buffer_id+"_wrapped"
    # Augmented buffer with sparse microarchitecture
    buffer_subcomponent=copy.copy(arch_buff)
    buffer_subcomponent['name']=wrapped_buffer_id
    buffer_wrapper={
        'name':buffer_wrapper_id,
        'attributes':copy.copy(buff_class_attributes),
        'subcomponents':[],
        'actions':[]
    }
    # - Set attributes & attribute inheritance for wrapped buffer
    for attr_ in buff_class_attributes:
        buffer_wrapper['attributes'][attr_] = buff_class_def['attributes'][attr_]
        buffer_subcomponent['attributes'][attr_] = attr_
    # - Set subcomponents & action tree
    uarch_subcomp_uri_list={}
    buffer_wrapper['subcomponents'].append(buffer_subcomponent) # wrapped buffer
    for action_spec in buff_class_actions_list:
        action_id=action_spec['name']
        action_struct={
            'name':action_id,
            'subcomponents':[
                {
                    'name':wrapped_buffer_id,
                    'actions':[
                        {
                            'name':action_id
                        }
                    ]
                }
            ]
        }

        if 'arguments' in action_spec:
            # Arguments dict: arg -> range
            class_args_dict=action_spec['arguments']
            action_struct['subcomponents'][0]['actions'][0]['arguments'] = \
                wrapper_args_dict={arg_:arg_ for arg_ in class_args_dict}
        
        if action_id in spec_action_tree:
            subcomp_dict=spec_action_tree[action_id]
            if len(list(subcomp_dict.keys()))>0:
                info("----- Buffer action",action_id,":")
                for subcomp_uri in subcomp_dict:
                    uarchModelInstanceId=getUarchModelInstanceId(subcomp_uri)
                    if uarchModelInstanceId not in uarch_subcomp_uri_list:
                        uarch_subcomp_uri_list[uarchModelInstanceId]=subcomp_uri
                    info("------",uarchModelInstanceId)
                    _,subcomp_class_id=ab_.split_uri(subcomp_uri)
                    info("------",subcomp_class_id)
                    subaction_list=subcomp_dict[subcomp_uri]
                    action_struct['subcomponents'].append({
                        'name':uarchModelInstanceId,
                        'actions':[{'name':uarch_action_id} \
                                   for uarch_action_id in subaction_list]
                    })
            else:
                warn("----- Buffer action",action_id,"references no microarchitecture actions")
        else:
            warn("----- Buffer action",action_id,"not required for uarch modeling")

        buffer_wrapper['actions'].append(action_struct)

    for subcomp_inst_id in uarch_subcomp_uri_list:
        subcomp_uri=uarch_subcomp_uri_list[subcomp_inst_id]
        class_id=cc_.create_safe_symbol(subcomp_uri)
        yield_list=list(analytical_component_model_classes_dict[ \
            abstract_analytical_component_models_dict[subcomp_uri]['category']+'Model'
        ])
        subcomp_attr_dict=abstract_analytical_component_models_dict[subcomp_uri]['attributes']
        
        buffer_wrapper['subcomponents'].append({
            "name":subcomp_inst_id,
            "class":class_id,
            "attributes": { \
                yield_: subcomp_attr_dict[yield_] \
                for yield_ in subcomp_attr_dict \
                    if type(subcomp_attr_dict[yield_]).__name__ != "list"
            }
        })

    return buffer_wrapper

def getAccelergyBufferLibrary(flat_arch, \
                              flat_comp_dict, \
                              backend_comp_lib_rep, \
                              analytical_component_model_classes_dict, \
                              analytical_primitive_model_classes_dict, \
                              analytical_component_model_actions_dict, \
                              abstract_analytical_primitive_models_dict, \
                              abstract_analytical_component_models_dict, \
                              buffer_action_tree, \
                              backend_args={}):
    info("--- Building Accelergy buffer model component library")
    info("---- moving forward with Accelergy modeling backend...")

    buffer_struct_list=[]
    buffer_model_map={}
    for buffer_uri in buffer_action_tree:
        buffer_struct=getAccelergySingleBufferStructure(flat_arch, \
                                                        flat_comp_dict, \
                                                        backend_comp_lib_rep, \
                                                        buffer_uri, \
                                                        analytical_component_model_classes_dict, \
                                                        analytical_primitive_model_classes_dict, \
                                                        abstract_analytical_component_models_dict, \
                                                        abstract_analytical_primitive_models_dict, \
                                                        analytical_component_model_actions_dict, \
                                                        buffer_action_tree, \
                                                        backend_args=backend_args)
        _,buffer_id=ab_.split_uri(buffer_uri)
        buffer_model_map[buffer_id]=buffer_struct['name']
        buffer_struct_list.append(buffer_struct)

    warn("--- => done, build buffer library")
    return {"buffer_struct_list":buffer_struct_list, \
            "buffer_model_map":buffer_model_map, \
            "accelergy_version":backend_args['accelergy_version']}

def transformArchTier(sub_arch,buffer_model_map):
    info("---- Recursively (DFS) transforming arch to use augmented buffer models...")

    if 'local' in sub_arch:
        local_buffers=sub_arch['local']
        info("----- Found",len(local_buffers),"local buffers.")
        for idx,buffer_spec in enumerate(local_buffers):
            buffer_name=buffer_spec['name']
            info("-------",buffer_name,"(",str(idx),")")
            if buffer_name in buffer_model_map:
                buffer_class=buffer_model_map[buffer_name]
                if 'subclass' in buffer_spec:
                    warn("-------- => Integrating",buffer_class, \
                        "in place of\"",buffer_spec['subclass'],"\"for buffer SUBclass")
                    buffer_spec['subclass']=buffer_class #Should update in-place
                else:
                    warn("-------- => Integrating",buffer_class, \
                        "in place of\"",buffer_spec['class'],"\"for buffer class")
                    buffer_spec['class']=buffer_class #Should update in-place
            else:
                info("-------- (No applicable augmented buffer model)")

    if 'subtree' in sub_arch:
        info("----- Found subtree list:")
        for tree_ in sub_arch['subtree']:
            info("------ Recursing into subtree",tree_['name'])
            transformArchTier(tree_,buffer_model_map)
            info("------ Leaving subtree",tree_['name'])
        return 
    else:
        info("----- No subtree found; returning")
        return

def getAccelergyBackendArchTransformation(arch,backend_buffer_lib_rep, \
                                          backend="accelergy",backend_args={}):
    info("--- Building Accelergy arch spec updated with SAF microarchitecture-augmented buffer model ids")
    info("---- moving forward with Accelergy modeling backend...")
    
    buffer_model_map=backend_buffer_lib_rep['buffer_model_map']

    arch_w_saf=copy.copy(arch)
    transformArchTier(arch_w_saf['architecture'],buffer_model_map)

    warn("--- => done, transform arch spec")
    return arch_w_saf

def getAccelergyTables(abstract_analytical_models_dict,primitive_models,backend_args={}):
    info("--- moving forward with Accelergy modeling backend...")
    accelergy_version=backend_args['accelergy_version']
    table_dict={}
    for primitive_name in abstract_analytical_models_dict:
        attr_names=abstract_analytical_models_dict[primitive_name]["attribute_names"]
        attr_vals=abstract_analytical_models_dict[primitive_name]["attribute_values"]
        prim_model=primitive_models[primitive_name]
        prim_model.build_ERT()
        prim_model.build_ART()
        cat=prim_model.get_category()
        table_entry={"ERT":prim_model.get_ERT(), \
                     "ART":prim_model.get_ART(), \
                     "attr_names":attr_names}
        if cat not in table_dict:
            table_dict[cat]={tuple(attr_vals):table_entry}
        else:
            table_dict[cat][tuple(attr_vals)] = table_entry

    warn("--- done, built primitive ERTs and ARTs")
    warn("OVERVIEW ACCELERGY TABLES:")
    info("  Accelergy ART")
    for cat in table_dict:
        info("   ",cat,":")
        table_attrs_to_EART_dict=table_dict[cat]
        for attr_vals in table_attrs_to_EART_dict:
            EART_dict=table_attrs_to_EART_dict[attr_vals]

            ART=EART_dict['ART']
            attr_names=EART_dict['attr_names']
            info("\n\n",''.join("%s = %s\n" % nm_val for nm_val in zip(attr_names,attr_vals)),'=',ART,'um^2\n')

    info("  Accelergy ERT")
    for cat in table_dict:
        info("   ",cat,":")
        table_attrs_to_EART_dict=table_dict[cat]
        for attr_vals in table_attrs_to_EART_dict:
            EART_dict=table_attrs_to_EART_dict[attr_vals]

            ERT=EART_dict['ERT']
            attr_names=EART_dict['attr_names']
            info("\n",''.join("\n%s = %s" % nm_val for nm_val in zip(attr_names,attr_vals)),':\n', \
                 ''.join("- %s: %s pJ\n" % (action,ERT[action]) for action in ERT),'\n')

    return {"table_dict":table_dict,"accelergy_version":accelergy_version}

def exportAccelergyERTART(primitives_ERT_ART,ERTART_fn_=ERTART_fn):
    info("--- saving Accelergy ERT/ART to",ERTART_fn_,"...")
    with open(ERTART_fn_,'wb') as fp:
        pickle.dump(primitives_ERT_ART,fp)
    warn("--- done, saving ERT/ART")

    return ERTART_fn_

def exportAccelergyPrimitivesLib(backend_lib_rep,lib_fn_=lib_fn):
    info("--- saving Accelergy primitive library to",lib_fn_,"...")
    with open(lib_fn_,'w') as fp:
        yaml.dump(backend_lib_rep,fp, default_flow_style=False)
    warn("--- done, saving primitive library")

    return lib_fn_

def exportAccelergyComponentsLib(backend_lib_rep, \
                                 backend_buffer_lib_rep, \
                                 lib_fn_=lib_fn, single_file=True):

    if lib_fn_ is None:
        lib_fn_=lib_fn

    backend_lib_rep_lib=backend_lib_rep['component_struct_list']
    backend_lib_rep_version=backend_lib_rep['accelergy_version']
    backend_buffer_lib_rep_lib=backend_buffer_lib_rep['buffer_struct_list']
    backend_buffer_lib_rep_version=backend_buffer_lib_rep['accelergy_version']
    combined_backend_lib=backend_lib_rep_lib+backend_buffer_lib_rep_lib

    res={}
    if single_file:
        full_fn=os.path.join(lib_fn_,'compound_components.yaml')
        info("--- saving Accelergy component library as single file; filename:",full_fn,"...")
        if backend_lib_rep_version == backend_buffer_lib_rep_version:
            # To be in the same YAML file all components must use the same Accelergy version
            res={
                'compound_components': {
                    'version':backend_lib_rep_version,
                    'classes':combined_backend_lib
                }
            }
            sl_config.save_yaml(res,full_fn)
        else:
            error("Accelergy version mismatch between microarchitecture and buffer models.",also_stdout=True)
            info("Terminating.")
            assert(False)
    else:
        info("--- Saving Accelergy microarchitecture component library; directory:",lib_fn_,"...")
        for component in backend_lib_rep_lib:
            comp_name=component['name']
            lib_dir=os.path.join(lib_fn_,comp_name)
            lib_file=os.path.join(lib_dir,comp_name+"_acc_model.yaml")
            if not os.path.exists(lib_dir):
                os.makedirs(lib_dir)
                warn("---- creating directory")
            res={
                # Single-component library
                'compound_components': {
                    'version':backend_lib_rep_version,
                    'classes':[component]
                }
            }
            info("----",comp_name,"=>",lib_file)
            sl_config.save_yaml(res,lib_file)
        # Now, save wrapped buffer component library
        lib_file=os.path.join(lib_fn_,'buffer_components.yaml')
        info("--- Saving Accelergy wrapped buffer component library; file:",lib_file)
        res={
            # Multi-component buffer model library
            'compound_components': {
                'version':backend_buffer_lib_rep_version,
                'classes':backend_buffer_lib_rep_lib
            }
        }
        sl_config.save_yaml(res,lib_file)

    warn("--- done, saving component library")

    return lib_fn_

def exportAccelergyArchSpec(backend_arch_rep, \
                            arch_install_filename):

    info("--- saving Accelergy arch representation as single file; filename:",arch_install_filename,"...")
    sl_config.save_yaml(backend_arch_rep,arch_install_filename)
    warn("--- done, saving arch library")
    return arch_install_filename

def installERTART(ERTART_fn_,install_path_=obj_install_path):
    info("--- installing: copying Accelergy ERT/ART from",ERTART_fn_,"to",install_path_,"...")
    dest = shutil.copyfile(ERTART_fn_, install_path_)
    warn("--- done, installing ERT/ART to backend")
    return dest

def installPrimitivesLib(lib_fn_,install_path_=lib_install_path):
    info("--- installing: copying Accelergy primitives lib from",lib_fn_,"to",install_path_,"...")
    dest = shutil.copyfile(lib_fn_, install_path_)
    warn("--- done, installing primitives lib to backend")
    return dest