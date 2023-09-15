from ...taxo.address_primitives.PositionGenerator import PositionGenerator, pgen_instances
import util.notation.model as mo_

pgen_attr_list=["pr","cr","pw","nc"]

PositionGeneratorModel=PositionGenerator \
    .copy() \
    .scale_parameter("clock","real") \
    .require_port_throughput_attributes("md_in") \
    .require_port_throughput_attributes("pos_out") \
    .yield_taxonomic_attributes() \
    .yield_port_throughput_thresholds() \
    .taxonomic_instance_alias(["cp_lf_none"],"C") \
    .register_supported_instances(pgen_instances) \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
        attributes=[], \
        constraints=[*mo_.makePassthroughConstraint("@pos_out_$a","@md_in_$a",foralls=[("a","attrs",pgen_attr_list)])], \
        energy_objective="2*(@pos_out_pr_thresh*@md_in_pr_thresh + " \
                         + "@pos_out_cr_thresh*@md_in_cr_thresh + " \
                         + "@pos_out_pw_thresh*@md_in_pw_thresh + " \
                         + "@pos_out_nc_thresh*@md_in_nc_thresh)", \
        area_objective=""
    )

'''
                     *mo_.makeConstraint("@pos_out_$a_thresh >= @pos_out_$a",foralls=[("a","attrs",pgen_attr_list)]),
                     *mo_.makeConstraint("@md_in_$a_thresh >= @md_in_$a",foralls=[("a","attrs",pgen_attr_list)])],
'''