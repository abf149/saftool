'''Accelergy compatibility layer'''
from util.helper import info,warn,error
import util.sparseloop_config_processor as sl_config
import yaml
import pickle, shutil, os

def dict_representer(dumper, data):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

yaml.add_representer(dict, dict_representer)

accelergy_root="accelergy/"
ERTART_fn="primitives_ERT_ART.pkl"
lib_fn="saf_primitives.lib.yaml"
obj_install_path=os.path.join(os.path.join(accelergy_root,"data/"),ERTART_fn)
lib_install_path=os.path.join(os.path.join(accelergy_root,"primitive_component_libs/"),lib_fn)

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

def getAccelergyPrimitivesLibrary(analytical_model_classes_dict, \
                                  analytical_model_actions_dict):
    info("--- moving forward with Accelergy modeling backend...")

    primitives_lib={
                    "version": 0.3,
                    "classes":[\
                        {
                            "name":name_,
                            "attributes": { \
                                yield_:analytical_model_classes_dict[name_][yield_] \
                                for yield_ in analytical_model_classes_dict[name_]
                            }, \
                            "actions":[ \
                                action_expression_from_tuple(act_tuple)
                                for act_tuple in analytical_model_actions_dict[name_]
                            ]
                        }
                        for name_ in analytical_model_classes_dict
                    ]}


    warn("--- done, build primitive classes library")
    return primitives_lib

def getAccelergyTables(abstract_analytical_models_dict,primitive_models):
    info("--- moving forward with Accelergy modeling backend...")

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

    return table_dict

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