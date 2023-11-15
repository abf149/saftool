'''SAFmodel IO library - CLI argparse and YAML dump routines'''
from util.taxonomy import designelement as de
import os, argparse, test_data as td, copy, re
import util.sparseloop_config_processor as sl_config, yaml, argparse
from util.taxonomy.designelement import Architecture
from util.helper import info,warn,error
import saflib.microarchitecture.ModelRegistry as mr_
import saflib.resources.char.ResourceRegistry as rr_
import export.AnalyticalModelExport as am_exp

'''Config - condition the format of YAML file dumps'''
#yaml.Dumper.ignore_aliases = lambda *args : True

'''Register characterization resources'''
def register_characterization_resources(characterization_path_list):
    info("Loading & registering characterization files (",len(characterization_path_list),")...")
    for pth in characterization_path_list:
        rr_.registerCharacterizationTable(filepath=pth)
    warn("=> Done, loading & registering characterization")

'''Load & parse model libraries'''
def load_parse_model_libs(model_script_lib_list):
    # Parse modelscript
    import glob,yaml
    import parser.model_parser_core as tp_
    lib_filepath_list=[]
    lib_filepath_list.extend(glob.glob(model_script_lib_list[0]))
    info("Parsing modelscript libraries (",len(lib_filepath_list),")...")
    for lib_filepath in lib_filepath_list:
        info("-",lib_filepath)
        lib_struct=None
        with open(lib_filepath, 'r') as file:
            lib_struct= yaml.safe_load(file)
        primitives_dict, components_dict=tp_.parse_modelscript(lib_struct)
        if len(primitives_dict)>0:
            info("-- Registering primitives")
            for primitive_id in primitives_dict:
                info("--- registering primitive",primitive_id)
                primitive=primitives_dict[primitive_id]
                mr_.registerPrimitive(primitive_id,primitive)
            warn("-- => Done, registering primitives")
        else:
            info("-- No primitives to register")
        if len(components_dict)>0:
            info("-- Registering components")
            for component_id in components_dict:
                info("--- registering component",component_id)
                component=components_dict[component_id]
                mr_.registerComponent(component_id,component)
            warn("-- => Done, registering components")
        else:
            info("-- No components to register")
    warn("=> Done,")

def process_args(args):
    # Parse the CLI arguments
    print("SAFmodel.\n")
    do_logging=args.log
    print("Parsing input files:")

    if len(args.dir_out) > 0 or len(args.dir_in)>0:
        # Not yet supported
        assert(False) 
 
    print("- netlist:",args.netlist)
    netlist=de.Architecture.fromYamlFilename(args.netlist)
    print("- arch:",args.arch)
    arch=sl_config.load_config_yaml(args.arch)
    print("- sparseopts:",args.sparseopts)
    sparseopts=sl_config.load_config_yaml(args.sparseopts)
    print("- compound components (input):",args.comp_in)
    comp_in=[sl_config.load_config_yaml(fn_str) for fn_str in args.comp_in]
    print("- arch output path:",args.arch_out)
    arch_out_path=args.arch_out
    print("- compound components path (output):",args.comp_out)
    comp_out_path=args.comp_out
    print("- SAFModel settings path:",args.settings)
    user_attributes=sl_config.load_config_yaml(args.settings)

    return arch, \
           netlist, \
           sparseopts, \
           comp_in, \
           arch_out_path, \
           comp_out_path, \
           user_attributes, \
           do_logging,\
           args.log_file,\
           args.char, \
           args.model_script_lib, \
           args.taxo_script_lib

'''CLI argparse'''
def parse_args():

    parser = argparse.ArgumentParser(description='safmodel: SAF microarchitecture modeling generator.')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml', \
                        help='Sparseloop architecture file.')
    parser.add_argument('-b','--char',action='append',default=['accelergy/data/primitives_table.csv'], \
                        help='CSV EAT characterization table.')
    parser.add_argument('-c', '--comp-in', action='append', default=['ref_input/compound_components.yaml'], \
                        help='One or more Accelergy component library YAML filenames.')
    parser.add_argument('-d','--rtl',action='append',default=['hw/rtl_out/'], \
                        help='Path to underlying RTL files associated with CSV EAT characterization table (-b/--char)')
    parser.add_argument('-f','--log-file',default='./safmodel.log', \
                        help='Log filepath (requires -L/--log to enable logging).')
    parser.add_argument('-i','--dir-in',default='', \
                        help='Input files\' directory. If not specified, '+ \
                             'arch (--arch) and components (--comp-in) files must be explicit.')
    parser.add_argument('-j','--hcl',action='append',default=['hw/chisel/src'], \
                        help='Path to high-level hardware construction language (HCL) code which generates the verilog.')
    parser.add_argument('-k','--comp-out',default='ref_output/', \
                        help='Components output filename (TODO: not currently used).')
    parser.add_argument('-L','--log', action='store_true', \
                        help='Enable logging.')
    parser.add_argument('-m','--model-script-lib',action='append',default=['saflib/microarchitecture/modelscript/*.yaml'])
    parser.add_argument('-n','--netlist',default='ref_output/new_arch.yaml', \
                        help='Taxonomic netlist description of architecture with'+ \
                             ' sparse microarchitecture (generated by safinfer.)')
    parser.add_argument('-o','--dir-out',default='', \
                        help='Output files directory.')
    parser.add_argument('-r','--arch-out',default='ref_output/arch_w_SAF.yaml', \
                        help='Output filename for Sparseloop arch augmented with SAF microarchitecture models.')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml', \
                        help='Sparseloop SAF specification file.')
    parser.add_argument('-t','--taxo-script-lib',action='append',default=['saflib/microarchitecture/taxoscript/*.yaml'])
    parser.add_argument('-T','--settings',default='ref_input/safmodel_settings.yaml', \
                        help='safmodel configuration file.')
    parser.add_argument('-u','--sim',action='append',default=['hw/sim_data'], \
                        help='safmodel configuration file.')
    args = parser.parse_args()

    processed_args=process_args(args)

    return processed_args

def load_taxonomic_microarchitecture(netlist):
    '''Load taxonomic description of SAF microarchitecture'''
    return Architecture.fromDict(sl_config.load_config_yaml(netlist))

def export_analytical_models(arch, \
                             comp_in, \
                             arch_out_path, \
                             comp_out_path, \
                             abstract_analytical_primitive_models_dict,abstract_analytical_component_models, \
                             scale_problem,user_attributes):
    backend_args={
        "accelergy_version":user_attributes["model_export_settings"]["accelergy_version"],
        "arch_out_path":arch_out_path,
        "comp_out_path":comp_out_path,
        "component_single_file":user_attributes["model_export_settings"]["component_single_file"]
    }

    '''Augment scale inference problem structure with arch and flattened_arch'''
    flat_arch=sl_config.flatten_arch_wrapper(arch)
    scale_problem['arch']=arch
    scale_problem['flat_arch']=flat_arch

    '''Export abstract analytical models'''
    backend_obj_rep, backend_prim_lib_rep, backend_comp_lib_rep, backend_buffer_lib_rep= \
        am_exp.export_backend_modeling_suite(comp_in, \
                                             mr_.primitive_model_yields_supersets, \
                                             mr_.primitive_model_actions, \
                                             abstract_analytical_primitive_models_dict, \
                                             mr_.component_model_yields_supersets, \
                                             mr_.component_model_actions, \
                                             abstract_analytical_component_models, \
                                             scale_problem, \
                                             backend_args=backend_args)
    return backend_obj_rep, backend_prim_lib_rep, backend_comp_lib_rep, backend_buffer_lib_rep