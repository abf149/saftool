from ...taxo.address_primitives.PositionGenerator import PositionGenerator
import util.notation.model as mo_

pgen_attr_list=["pr","cr","pw","nc"]

PositionGeneratorModel=PositionGenerator \
    .copy() \
    .scale_parameter("clock","real") \
    .require_port_throughput_attributes("md_in") \
    .require_port_throughput_attributes("pos_out") \
    .taxonomic_instance_alias(["cp_lf_none"],"C") \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
        attributes=[ \
            *mo_.makeAttribute("pos_out_$a_thresh",foralls=[("a","attrs",pgen_attr_list)]), \
            *mo_.makeAttribute("md_in_$a_thresh",foralls=[("a","attrs",pgen_attr_list)])
        ], \
        constraints=[*mo_.makeConstraint("@pos_out_$a == @md_in_$a",foralls=[("a","attrs",pgen_attr_list)]), \
                     *mo_.makeConstraint("@pos_out_$a_thresh >= @pos_out_$a",foralls=[("a","attrs",pgen_attr_list)]), \
                     *mo_.makeConstraint("@md_in_$a_thresh >= @md_in_$a",foralls=[("a","attrs",pgen_attr_list)])], \
        energy_objective="2*(@pos_out_pr_thresh*@md_in_pr_thresh + " \
                         + "@pos_out_cr_thresh*@md_in_cr_thresh + " \
                         + "@pos_out_pw_thresh*@md_in_pw_thresh + " \
                         + "@pos_out_nc_thresh*@md_in_nc_thresh)", \
        area_objective=""
    )