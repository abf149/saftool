from ...taxo.format.MetadataParser import MetadataParser, md_parser_instances
import core.notation.model as mo_
#import saflib.microarchitecture.model.model_registry as mr_

md_parser_require_attrs=['pr','cr','nc','rw','ww']
scale_determinative_attr_list=['rw','pr','ww']
passthru_list=['cr','nc']

MetadataParserModel=MetadataParser \
    .copy() \
    .scale_parameter("clock","real",yield_=True,inherit_=True) \
    .scale_parameter("technology","string",yield_=True,inherit_=True) \
    .require_port_throughput_attributes("md_in",md_parser_require_attrs) \
    .require_port_throughput_attributes("at_bound_out",md_parser_require_attrs) \
    .yield_taxonomic_attributes() \
    .yield_port_throughput_thresholds(port_attr_dict={"md_in":scale_determinative_attr_list, \
                                                      "at_bound_out":scale_determinative_attr_list}) \
    .action("check_bound") \
    .action("gated_check_bound") \
    .taxonomic_instance_alias(["coordinate_payload"],"C") \
    .taxonomic_instance_alias(["uncompressed"],"U") \
    .register_supported_instances(md_parser_instances) \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
        attr_range_specs=[ \
            mo_.makeValuesConstraint("@md_in_$a_thresh", \
                                     foralls=[("a","attrs",scale_determinative_attr_list)], \
                                     ranges=[(1, 8, 64, 256), 
                                              (1, 8, 64, 256), 
                                              (1, 8, 64, 256)]), \
            mo_.makeValuesConstraint("@at_bound_out_$a_thresh", \
                                     foralls=[("a","attrs",scale_determinative_attr_list)], \
                                     ranges=[(1,), 
                                              (1,), 
                                              (1,)]) \
        ],
        constraints=[mo_.makePassthroughConstraint("@md_in_$a","@at_bound_out_$a", \
                        foralls=[("a","attrs",passthru_list)]), \
                     mo_.makeConstraint("@at_bound_out_pr == @md_in_cr/@md_in_nc") \
                     ], \
        energy_objective={"check_bound": \
                            "2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)", \
                          "gated_check_bound": \
                            "0"}, \
        area_objective="2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)"
    ) \
    .add_implementation( \
        name="U", \
        taxonomic_instance="U", \
        attr_range_specs=[ \
            mo_.makeValuesConstraint("@md_in_$a_thresh", \
                                     foralls=[("a","attrs",scale_determinative_attr_list)], \
                                     ranges=[(1, 8, 64, 256), 
                                              (1, 8, 64, 256), 
                                              (1, 8, 64, 256)]), \
            mo_.makeValuesConstraint("@at_bound_out_$a_thresh", \
                                     foralls=[("a","attrs",scale_determinative_attr_list)], \
                                     ranges=[(1,), 
                                              (1,), 
                                              (1,)]) \
        ],
        constraints=[mo_.makePassthroughConstraint("@md_in_$a","@at_bound_out_$a", \
                        foralls=[("a","attrs",passthru_list)]), \
                     mo_.makeConstraint("@at_bound_out_pr == @md_in_cr/@md_in_nc") \
                     ], \
        energy_objective={"check_bound": \
                            "2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)", \
                          "gated_check_bound": \
                            "0"}, \
        area_objective="2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)"
    )