'''Accelergy compatibility layer'''
from util.helper import info,warn,error
import pickle

ERTART_fn="primitives_ERT_ART.pkl"

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

def exportAccelergyERTART(primitives_ERT_ART):
    info("--- saving Accelergy ERT/ART to",ERTART_fn,"...")
    with open(ERTART_fn,'wb') as fp:
        pickle.dump(primitives_ERT_ART,fp)
    warn("--- done, saving ERT/ART")