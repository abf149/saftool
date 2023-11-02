import saflib.microarchitecture.taxo.TaxoRegistry as tr_
#from ...taxo.address_primitives.PositionGenerator import PositionGenerator, pgen_instances
import util.notation.model as mo_

pgen_attr_list=["pr","cr","pw","nc"]


primitive_dict=tr_.getPrimitive('PositionGenerator')
PositionGenerator=primitive_dict['description']
pgen_instances=primitive_dict['instances']

PositionGeneratorModel=PositionGenerator \
    .copy() \
    .scale_parameter("clock","real",yield_=True,inherit_=True) \
    .scale_parameter("technology","string",yield_=True,inherit_=True) \
    .require_port_throughput_attributes("md_in") \
    .require_port_throughput_attributes("pos_out") \
    .yield_taxonomic_attributes() \
    .yield_port_throughput_thresholds(port_attr_dict={"md_in":pgen_attr_list,"pos_out":pgen_attr_list}) \
    .action("gen") \
    .action("gated_gen") \
    .taxonomic_instance_alias(["coordinate_payload"],"C") \
    .register_supported_instances(pgen_instances) \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
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
        constraints=[mo_.makePassthroughConstraint("@pos_out_$a","@md_in_$a",foralls=[("a","attrs",pgen_attr_list)])], \
        energy_objective={"gen": \
                            "2*(@pos_out_pr_thresh*@md_in_pr_thresh + " \
                          + "@pos_out_cr_thresh*@md_in_cr_thresh + " \
                          + "@pos_out_pw_thresh*@md_in_pw_thresh + " \
                          + "@pos_out_nc_thresh*@md_in_nc_thresh)", \
                          "gated_gen": \
                            "0"}, \
        area_objective="@pos_out_pw_thresh*@md_in_pr_thresh+2"
    )