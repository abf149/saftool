'''Wrapper for using SAFmodel as a middle-layer for evaluating a search-point'''
import safmodel
import core.safsearch_io as safsearch_io

def safmodel_middle_layer(arch,taxo_uarch,sparseopts,user_attributes,log_safmodel=False):
    '''
    SAFmodel backend wrapper, silences stdout, stderr and logging by default.\n\n

    Returns:\n
    - abstract_analytical_primitive_models_dict
    - abstract_analytical_component_models_dict
    - scale_prob
    '''

    stream_state=safsearch_io.disable_logs(disable_file_log=(not log_safmodel))
    return_args=safmodel.pipeline(arch,taxo_uarch,sparseopts,user_attributes,remarks=True)
    safsearch_io.revert_logs(stream_state)
    return return_args