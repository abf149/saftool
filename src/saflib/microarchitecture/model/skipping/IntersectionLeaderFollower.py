from ...taxo.skipping.IntersectionLeaderFollower import IntersectionLeaderFollower
import util.notation.model as mo_

isect_attr_list=['rw','pr','cr','ww','nc']

IntersectionLeaderFollowerModel=IntersectionLeaderFollower \
    .copy() \
    .scale_parameter("clock","real") \
    .require_port_throughput_attributes("md_in_leader",isect_attr_list) \
    .require_port_throughput_attributes("md_out",isect_attr_list) \
    .taxonomic_instance_alias(["cp_lf_none"],"C") \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
        attributes=[ \
            *mo_.makeAttribute("md_out_$a_thresh",foralls=[("a","attrs",isect_attr_list)]), \
            *mo_.makeAttribute("md_in_leader_$a_thresh",foralls=[("a","attrs",isect_attr_list)])
        ], \
        constraints=[mo_.makeConstraint("@md_out_$a == @md_in_leader_$a",foralls=[("a","attrs",isect_attr_list)])], \
        energy_objective="2*(@md_out_rw + @md_out_pr + @md_out_ww)", \
        area_objective=""
    )