from ...taxo.skipping.SkippingUarch import SkippingUarch, skipping_uarch_instances
import util.notation.model as mo_

SkippingUarchModel=SkippingUarch \
    .copy() \
    .scale_parameter("clock","real",yield_=True) \
    .scale_parameter("technology","string",yield_=True) \
    .yield_taxonomic_attributes() \
    .action("fill_leader") \
    .action("fill_follower") \
    .action("skip") \
    .taxonomic_instance_alias(["cp_lf_none_none"],"CLFNN") \
    .register_supported_instances(skipping_uarch_instances) \
    .add_implementation( \
        name="CLFNN", \
        taxonomic_instance="CLFNN",
        energy_objective={"fill_leader": "0", \
                          "fill_follower": "0", \
                          "skip": "0"}, \
        area_objective="0"
    ) \
    .subaction(impl_="CLFNN", \
               action_name_="fill_leader", \
               sub_component="IntersectionLF", \
               sub_action="fill") \
    .subaction(impl_="CLFNN", \
               action_name_="skip", \
               sub_component="IntersectionLF", \
               sub_action="intersect") \
    .subaction(impl_="CLFNN", \
               action_name_="skip", \
               sub_component="PgenFollower", \
               sub_action="gen") \

#    .require_port_throughput_attributes("md_in_leader",isect_attr_list) \
#    .require_port_throughput_attributes("md_out",isect_attr_list) \