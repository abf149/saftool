'''Build a SAFModel throughput inference problem'''
from util.helper import info, warn, error
from .build_support.build1 import build1_graph_representation
from .build_support.build2 import build2_system_of_relations
from .build_support.build3 import build3_simplify_system

def error_taxo_to_model(*args,setting):
    error(*args,also_stdout=True)
    info("Setting:",setting)
    info("Terminating.")
    assert(False)

def assert_field(setting_name,field_name,setting):
    if field_name not in setting:
        error_taxo_to_model(setting_name,"settings must have", \
                            field_name,"field.",setting=setting)

def get_format_interfaces_settings(setting_list):
    dataspace_fmt_iface_to_anchor_overrides_dict={}
    for fmt_iface_settings in setting_list:
        assert_field("Format interface",'dataspace',fmt_iface_settings)
        assert_field("Format interface",'index',fmt_iface_settings)    
        assert_field("Format interface",'settings',fmt_iface_settings)
        fmt_iface_settings_dataspace=fmt_iface_settings['dataspace']
        fmt_iface_settings_index=fmt_iface_settings['index']
        fmt_iface_settings_settings=fmt_iface_settings['settings']
        for fmt_iface_setting in fmt_iface_settings_settings:
            assert_field("Format interface",'name',fmt_iface_setting)
            assert_field("Format interface",'value',fmt_iface_setting)    
            fmt_iface_setting_name=fmt_iface_setting['name']
            fmt_iface_setting_value=fmt_iface_setting['value']
            if fmt_iface_setting_name=='anchor':
                # Assume a given format interface only has one anchor setting
                # However, multiple format interface settings may target the same
                # dataspace.
                dataspace_fmt_iface_to_anchor_overrides_dict \
                    .setdefault(fmt_iface_settings_dataspace,{}) \
                        [fmt_iface_settings_index]=fmt_iface_setting_value
            else:
                error_taxo_to_model( \
                    "Invalid setting name",fmt_iface_setting_name, \
                    setting=fmt_iface_setting)
    return dataspace_fmt_iface_to_anchor_overrides_dict    
            

def get_buffers_settings(settings_list):
    buffer_dataspace_fmt_iface_to_anchor_overrides_dict={}
    for buffer_settings in settings_list:
        assert_field("Buffer",'name',buffer_settings)
        assert_field("Buffer",'settings',buffer_settings)
        buffer_settings_name=buffer_settings['name']
        buffer_settings_settings=buffer_settings['settings']
        for buffer_setting in buffer_settings_settings:
            assert_field("Buffer",'type',buffer_setting)
            assert_field("Buffer",'settings',buffer_setting)
            buffer_setting_type=buffer_setting['type']
            buffer_setting_settings=buffer_setting['settings']
            if buffer_setting_type=='format_interfaces':
                # Assume a given buffer only has one 'format_interfaces" settings
                buffer_dataspace_fmt_iface_to_anchor_overrides_dict \
                    [buffer_settings_name] = \
                        get_format_interfaces_settings(buffer_setting_settings)
            else:
                error_taxo_to_model( \
                    "Invalid setting type",buffer_setting_type, \
                    setting=buffer_setting)
    return buffer_dataspace_fmt_iface_to_anchor_overrides_dict


def get_user_overrides(user_attributes):
    buffer_dataspace_fmt_iface_to_anchor_overrides_dict={}
    if 'custom_taxo_to_model_settings' in user_attributes:
        custom_taxo_to_model_settings=user_attributes['custom_taxo_to_model_settings']
        for setting in custom_taxo_to_model_settings:
            assert_field("Custom taxonomic-to-model",'type',setting)
            assert_field("Custom taxonomic-to-model",'settings',setting)
            setting_type=setting['type']
            setting_settings=setting['settings']
            if setting_type == 'buffer':
                buffer_dataspace_fmt_iface_to_anchor_overrides_dict = \
                    get_buffers_settings(setting_settings)
            else:
                error_taxo_to_model( \
                    "Invalid setting type",setting_type, \
                    setting=setting)
    else:
        return {}
    
    info("- Anchor overrides dict:",buffer_dataspace_fmt_iface_to_anchor_overrides_dict)
    return buffer_dataspace_fmt_iface_to_anchor_overrides_dict

def build_scale_inference_problem(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                  buffer_kept_dataspace_by_buffer,buff_dags,user_attributes=None):

    warn("Building scale inference problem...",also_stdout=True)

    if (user_attributes is None) or ('clock_period' not in user_attributes) or \
        ('constraints' not in user_attributes):
        error('User attributes must at least have a \'clock_period\' key and a constraints key with an empty list as value', \
              also_stdout=True)
        info('Terminating.')
        assert(False)

    # Get user-specified constraints (if any)
    constraints=user_attributes['constraints']

    # Get user-specified format interface anchor overrides (if any)
    anchor_overrides_dict = \
        get_user_overrides(user_attributes)

    problem_as_graph=build1_graph_representation(taxo_uarch,arch,fmt_iface_bindings,dtype_list, \
                                                 buffer_kept_dataspace_by_buffer,buff_dags, \
                                                 anchor_overrides_dict,constraints)

    problem_as_system=build2_system_of_relations(problem_as_graph,user_attributes,fmt_iface_bindings,dtype_list)

    simplified_system=build3_simplify_system(problem_as_system)

    simplified_system['user_attributes']=user_attributes

    warn("=> Done, build.",also_stdout=True)

    return simplified_system