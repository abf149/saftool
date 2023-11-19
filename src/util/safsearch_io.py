'''SAFsearch IO library - CLI argparse and YAML dump routines'''
import safinfer, safmodel
from collections import deque
import util.sparseloop_config_processor as sl_config, yaml, argparse
from util.helper import info,warn,error
import util.helper as helper
import util.notation.predicates as p_
import solver.model.build_support.abstraction as ab
import util.safinfer_io as safinfer_io, \
       util.safmodel_io as safmodel_io
import dill as pickle

'''Config - condition the format of YAML file dumps'''
yaml.Dumper.ignore_aliases = lambda *args : True

best_config_dump_file='search_results.dill'

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
    _ = safinfer_io.process_args(args)

    # TODO: fix
    safinfer_user_attributes=sl_config.load_config_yaml(args.safinfer_settings)

    safsearch_user_attributes=sl_config.load_config_yaml(args.safsearch_settings)

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
           safsearch_user_attributes, \
           safinfer_user_attributes, \
           safmodel_user_attributes, \
           characterization_path_list, \
           model_script_lib_list,\
           args.dump_best, \
           args.load_best, \
           int(args.top_N), \
           int(args.model_top_x), \
           args.log_taxo_space_discovery, \
           args.log_search_safinfer, \
           args.log_search_safmodel

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
    parser.add_argument('-J','--load-best', action='store_true', \
                        help='Skip initial phases of SAFsearch, and load best configuration from local directory.')
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
    parser.add_argument('-N','--top-N',default=1, \
                        help='The top-N search results will be saved and returned from the search process.'+ \
                             ' sparse microarchitecture (generated by safinfer.)')
    parser.add_argument('-p','--prob',default='ref_input/prob.yaml')
    parser.add_argument('-q','--safinfer-settings',default='ref_input/safinfer_settings.yaml', \
                        help='safinfer configuration file.')
    parser.add_argument('-Q','--safsearch-settings',default='ref_input/safsearch_settings.yaml', \
                        help='safsearch configuration file.')
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
    parser.add_argument('-w','--log-taxo-space-discovery', action='store_true', \
                        help='Log the process of discovering the taxonomic search-space.')
    parser.add_argument('-x','--model-top-x', default=0, \
                        help='Out of the top N (--top-N) search results, generate models for the single top xth model (0==best).')
    parser.add_argument('-z','--log-search-safinfer', action='store_true', \
                        help='Log the SAFinfer phase of each search-point.')
    parser.add_argument('-Z','--log-search-safmodel', action='store_true', \
                        help='Log the SAFmodel phase of each search-point.')
    args = parser.parse_args()

    processed_args = process_args(args)
    return processed_args

def dump_best_config(best_config):
    info(":: Dumping search results to file")
    info("Filename:", best_config_dump_file)
    info("Logging dictionary with keys", str(list(best_config.keys())))
    with open(best_config_dump_file, 'wb') as fp:
        pickle.dump(best_config, fp)
    warn(":: => Done, dumping search results to file")

def load_best_config():
    warn(":: Load search results from file")
    info("Filename:", best_config_dump_file)
    best_config = None
    with open(best_config_dump_file, 'rb') as fp:
        best_config = pickle.load(fp)

    info("Loaded dictionary with keys",str(list(best_config.keys())))
    warn(":: => Done, dumping search results to file")
    return best_config

def export_artifacts_from_search_result(best_config, \
                                        top_N, \
                                        model_top_x, \
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
                                        taxo_script_lib_list, \
                                        taxo_uarch, \
                                        comp_in, \
                                        arch_out_path, \
                                        comp_out_path, \
                                        safinfer_user_attributes, \
                                        safmodel_user_attributes, \
                                        characterization_path_list, \
                                        model_script_lib_list, \
                                        log_global_search_safinfer, \
                                        log_global_search_safmodel):
    info(":: Searching...",also_stdout=True)
    info("Extracting top",model_top_x,"th search result.")
    top_N_tracker=best_config['search_result']['top_N_tracker']
    ranking=top_N_tracker.get_rank()
    if model_top_x > len(ranking)-1:
        error("Only",len(ranking),"results were found; cannot find result at index",model_top_x,"in ranking.")
        info("Terminating.")
        assert(False)
    search_point_struct=ranking[model_top_x]
    objective=search_point_struct['objective']
    search_point_result=search_point_struct['result']
    search_point_id=search_point_result['best_search_point_id']
    state=search_point_result['best_state']
    global_search_point=search_point_result['best_global_search_point']
    safinfer_results=search_point_result['best_safinfer_results']
    outcome=safinfer_results['outcome']
    #component_iterations=safinfer_results['component_iterations']
    #uri=safinfer_results['uri']
    #failure_comp=safinfer_results['failure_comp']
    safmodel_results=search_point_result['best_safmodel_results']
    abstract_analytical_primitive_models_dict=safmodel_results['abstract_analytical_primitive_models_dict']
    abstract_analytical_component_models_dict=safmodel_results['abstract_analytical_component_models_dict']
    scale_prob=safmodel_results['scale_prob']
    info("- Objective:",objective)
    info("- Best search-point ID:",str(search_point_id))
    if not outcome:
        error("Invalid search result: SAFinfer failed")
        info("Terminating.")
        assert(False)
    #taxo_uarch=component_iterations[-1]
    warn("=> Done, extracting search result.")
    info("Dumping SAFinfer results to",topo_out_path,"...")
    safinfer.handle_outcome(safinfer_results,topo_out_path)
    warn("=> Done, dumping SAFinfer results to file.")
    info("Dumping SAFmodel results")
    safmodel.export_result(arch,comp_in,arch_out_path,comp_out_path,abstract_analytical_primitive_models_dict, \
                           abstract_analytical_component_models_dict,scale_prob,safmodel_user_attributes)
    warn("=> Done, dumping SAFmodel results")
    warn(":: => Exporting search result artifacts")