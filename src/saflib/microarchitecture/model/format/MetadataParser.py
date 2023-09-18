from ...taxo.format.MetadataParser import MetadataParser, md_parser_instances
import util.notation.model as mo_
#import saflib.microarchitecture.model.model_registry as mr_

md_parser_require_attrs=['pr','cr','nc','rw','ww']
scale_determinative_attr_list=['rw','pr','ww']
passthru_list=['cr','nc']

MetadataParserModel=MetadataParser \
    .copy() \
    .scale_parameter("clock","real") \
    .require_port_throughput_attributes("md_in",md_parser_require_attrs) \
    .require_port_throughput_attributes("at_bound_out",md_parser_require_attrs) \
    .yield_taxonomic_attributes() \
    .yield_port_throughput_thresholds(port_attr_dict={"md_in":scale_determinative_attr_list, \
                                                      "at_bound_out":scale_determinative_attr_list}) \
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
                            "2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)"}, \
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
                            "2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)"}, \
        area_objective="2*(@md_in_rw_thresh + @md_in_pr_thresh + @md_in_ww_thresh)"
    )

#mr_.registerModel("MetadataParserModel",MetadataParserModel)

'''
pgen_attr_list=["pr","cr","pw","nc"]

PositionGeneratorModel=PositionGenerator \
    .copy() \
    .scale_parameter("clock","real") \
    .require_port_throughput_attributes("md_in") \
    .require_port_throughput_attributes("pos_out") \
    .yield_taxonomic_attributes() \
    .yield_port_throughput_thresholds(port_attr_dict={"md_in":pgen_attr_list,"pos_out":pgen_attr_list}) \
    .taxonomic_instance_alias(["coordinate_payload"],"C") \
    .register_supported_instances(pgen_instances) \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
        attributes=[], \
        attr_range_specs=[ \
            mo_.makeValuesConstraint("@pos_out_$a_thresh", \
                                     foralls=[("a","attrs",pgen_attr_list)], \
                                     ranges=[(1, 8, 64, 256), 
                                              (1, 8, 64, 256), 
                                              (1, 8, 64, 256),
                                              (1, 8, 64, 256)]), \
            mo_.makeValuesConstraint("@md_in_$a_thresh", \
                                     foralls=[("a","attrs",pgen_attr_list)], \
                                     ranges=[(1, 8, 64, 256), 
                                              (1, 8, 64, 256), 
                                              (1, 8, 64, 256),
                                              (1, 8, 64, 256)]) \
        ],
        attr_combo_specs=[mo_.makeCombosConstraint(["@pos_out_pr_thresh","@pos_out_pw_thresh"], \
                                                   [(1,8), \
                                                    (8,64), \
                                                    (64,256)])], \
        constraints=[mo_.makePassthroughConstraint("@pos_out_$a","@md_in_$a",foralls=[("a","attrs",pgen_attr_list)])], \
        energy_objective={"gen": \
                            "2*(@pos_out_pr_thresh*@md_in_pr_thresh + " \
                          + "@pos_out_cr_thresh*@md_in_cr_thresh + " \
                          + "@pos_out_pw_thresh*@md_in_pw_thresh + " \
                          + "@pos_out_nc_thresh*@md_in_nc_thresh)"}, \
        area_objective="@pos_out_pw_thresh*@md_in_pr_thresh+2"
    )
'''