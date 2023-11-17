'''SAFsearch IO library - CLI argparse and YAML dump routines'''
from collections import deque
import util.sparseloop_config_processor as sl_config, yaml, argparse
from util.helper import info,warn,error
import util.helper as helper
import util.notation.predicates as p_
import solver.model.build_support.abstraction as ab
import util.safinfer_io as safinfer_io, \
       util.safmodel_io as safmodel_io

'''Config - condition the format of YAML file dumps'''
yaml.Dumper.ignore_aliases = lambda *args : True

def log_control(setting):
    helper.enable_log=setting

def enable_stdout():
    helper.enable_stdout=True

def enable_stderr():
    helper.enable_stderr=True

def disable_stdout():
    helper.enable_stdout=False

def disable_stderr():
    helper.enable_stderr=False

def disable_logs(disable_file_log=False):
    stream_state = {
        'stdout':helper.enable_stdout,
        'stderr':helper.enable_stderr,
        'log':helper.enable_log,
    }
    disable_stdout()
    disable_stderr()
    if disable_file_log:
        log_control(False)
    return stream_state

def revert_logs(stream_state):
    if stream_state['stdout']:
        enable_stdout()
    else:
        disable_stdout()
    if stream_state['stderr']:
        enable_stderr()
    else:
        disable_stderr()
    log_control(stream_state['log'])

def process_args(args):
    arch, \
    mapping, \
    prob, \
    sparseopts, \
    reconfigurable_arch, \
    bind_out_path, \
    topo_out_path, \
    saflib_path, \
    do_logging,\
    log_fn, \
    taxo_script_lib, \
    safinfer_user_attributes = safinfer_io.process_args(args)

    # TODO: fix
    safinfer_user_attributes=sl_config.load_config_yaml(args.safinfer_settings)

    _, \
    taxo_uarch, \
    _, \
    comp_in, \
    arch_out_path, \
    comp_out_path, \
    safmodel_user_attributes, \
    _,\
    _, \
    characterization_path_list, \
    model_script_lib_list, \
    _ = safmodel_io.process_args(args)

    return arch, \
           mapping, \
           prob, \
           sparseopts, \
           reconfigurable_arch, \
           bind_out_path, \
           topo_out_path, \
           saflib_path, \
           do_logging,\
           log_fn, \
           taxo_script_lib, \
           taxo_uarch, \
           comp_in, \
           arch_out_path, \
           comp_out_path, \
           safinfer_user_attributes, \
           safmodel_user_attributes, \
           characterization_path_list, \
           model_script_lib_list

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a','--arch',default='ref_input/arch.yaml', \
                        help='Sparseloop architecture file.')
    parser.add_argument('-A','--arch-out',default='ref_output/arch_w_SAF.yaml', \
                        help='Output filename for Sparseloop arch augmented with SAF microarchitecture models.')
    parser.add_argument('-b','--binding-out',default='ref_output/bindings.yaml')
    parser.add_argument('-c', '--comp-in', action='append', default=['ref_input/compound_components.yaml'], \
                        help='One or more Accelergy component library YAML filenames.')
    parser.add_argument('-C','--char',action='append',default=['accelergy/data/primitives_table.csv'], \
                        help='CSV EAT characterization table.')
    parser.add_argument('-d','--dir-in',default='', \
                        help='Input files\' directory. If not specified, '+ \
                             'arch (--arch) and components (--comp-in) files must be explicit.')
    parser.add_argument('-D','--dir-out',default='', \
                        help='Output files directory.')
    parser.add_argument('-e','--no-accelergy', action='store_true', \
                        help='Do not output accelergy models as a final step.')
    parser.add_argument('-f','--log-file',default='./safsearch.log', \
                        help='Log filepath (requires -L/--log to enable logging).')
    parser.add_argument('-g','--hcl',action='append',default=['hw/chisel/src'], \
                        help='Path to high-level hardware construction language (HCL) code which generates the verilog.')
    parser.add_argument('-j','--dump-best', action='store_true', \
                        help='Dump best configuration to local directory.')
    parser.add_argument('-k','--comp-out',default='ref_output/', \
                        help='Components output filename (TODO: not currently used).')
    parser.add_argument('-l','--saftaxolib',default='saflib/rulesets/taxo/')
    parser.add_argument('-L','--log', action='store_true', \
                        help='Enable logging.')
    parser.add_argument('-M','--map',default='ref_input/map.yaml')
    parser.add_argument('-m','--model-script-lib',action='append',default=['saflib/microarchitecture/modelscript/*.yaml'])
    parser.add_argument('-n','--netlist',default='ref_output/new_arch.yaml', \
                        help='Taxonomic netlist description of architecture with'+ \
                             ' sparse microarchitecture (generated by safinfer.)')
    parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    parser.add_argument('-q','--safinfer-settings',default='ref_input/safinfer_settings.yaml', \
                        help='safinfer configuration file.')
    parser.add_argument('-r','--rtl',action='append',default=['hw/rtl_out/'], \
                        help='Path to underlying RTL files associated with CSV EAT characterization table (-b/--char)')
    parser.add_argument('-R', '--reconfigurable-arch', action='store_true')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml', \
                        help='Sparseloop SAF specification file.')
    parser.add_argument('-S','--settings',default='ref_input/safmodel_settings.yaml', \
                        help='safmodel configuration file.')
    parser.add_argument('-t','--taxo-script-lib',action='append',default=['saflib/microarchitecture/taxoscript/*.yaml'])
    parser.add_argument('-T','--topology-out',default='ref_output/new_arch.yaml')
    parser.add_argument('-u','--sim',action='append',default=['hw/sim_data'], \
                        help='safmodel configuration file.')
    args = parser.parse_args()

    processed_args = process_args(args)
    return processed_args