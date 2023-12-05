'''SAFmodel - tool to build SAF models from SAF microarchitecture topologies'''
import core.helper as helper
from core.helper import info,warn,error
from core import safmodel_core as safcore, \
                 safmodel_io as safio, \
                 safinfer_io

def opening_remark():
    info(">> SAFmodel",also_stdout=True)  

def log_config(do_logging,log_fn):
    print("logging:",do_logging)
    helper.enable_log=do_logging
    if do_logging:
        helper.log_init(log_fn)

def setup(taxo_script_lib_list,characterization_path_list,model_script_lib_list,require_taxo=True):
    info(":: Setup",also_stdout=True)
    '''Register characterization resources; load and parse model libraries'''
    if require_taxo:
        info("SAFinfer taxonomic libraries required for this worload...")
        safinfer_io.load_parse_taxo_libs(taxo_script_lib_list)
    else:
        info("Skipping SAFinfer taxonomic library load.")
    safio.register_characterization_resources(characterization_path_list)
    safio.load_parse_model_libs(model_script_lib_list)
    warn(":: => Done, setup")

def pipeline(arch,taxo_uarch,sparseopts,user_attributes,remarks=False):
    if remarks:
        opening_remark()
    warn(":: Scale inference",also_stdout=True)
    '''Build scale inference problem'''
    scale_prob=safcore.build_scale_inference_problem(arch, sparseopts, taxo_uarch, user_attributes=user_attributes)

    '''Solve scale inference problem'''
    abstract_analytical_primitive_models_dict,abstract_analytical_component_models_dict= \
        safcore.solve_scale_inference_problem(scale_prob)

    warn(":: => Done, scale inference",also_stdout=True)
    warn("")
    if remarks:
        closing_remark()

    return abstract_analytical_primitive_models_dict, \
           abstract_analytical_component_models_dict, \
           scale_prob

def export_result(arch,comp_in,arch_out_path,comp_out_path,abstract_analytical_primitive_models_dict, \
                  abstract_analytical_component_models_dict,scale_prob,user_attributes):
    warn(":: Export Accelergy models",also_stdout=True)
    safio.export_analytical_models(arch, \
                                    comp_in, \
                                    arch_out_path, \
                                    comp_out_path, \
                                    abstract_analytical_primitive_models_dict, \
                                    abstract_analytical_component_models_dict,scale_prob,user_attributes)
    warn(":: => Done, Accelergy export",also_stdout=True)

def closing_remark():
    warn("<< Done, SAFmodel",also_stdout=True)

def main():
    arch, \
    taxo_uarch, \
    sparseopts, \
    comp_in, \
    arch_out_path, \
    comp_out_path, \
    user_attributes, \
    do_logging,\
    log_fn, \
    characterization_path_list, \
    model_script_lib_list, \
    taxo_script_lib_list = safio.parse_args()

    log_config(do_logging,log_fn)
    opening_remark()
    setup(taxo_script_lib_list,characterization_path_list,model_script_lib_list)
    abstract_analytical_primitive_models_dict, \
    abstract_analytical_component_models_dict,scale_prob = \
        pipeline(arch,taxo_uarch,sparseopts,user_attributes)
    export_result(arch,comp_in,arch_out_path,comp_out_path,abstract_analytical_primitive_models_dict, \
                  abstract_analytical_component_models_dict,scale_prob,user_attributes)
    closing_remark()

if __name__=="__main__":
    main()