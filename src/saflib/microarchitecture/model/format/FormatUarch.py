from ...taxo.format.FormatUarch import FormatUarch, fmt_uarch_instances
import util.notation.model as mo_

FormatUarchModel=FormatUarch \
    .copy() \
    .scale_parameter("clock","real",yield_=True,inherit_=True) \
    .scale_parameter("technology","string",yield_=True,inherit_=True) \
    .scale_parameter("high_impact_mdparser_indices","list",yield_=False,inherit_=False,param_default=[]) \
    .yield_taxonomic_attributes() \
    .action("check_bounds") \
    .taxonomic_instance_alias(["all"],"all") \
    .register_supported_instances(fmt_uarch_instances) \
    .add_implementation( \
        name="all", \
        taxonomic_instance="all",
        energy_objective={"check_bounds": "0"}, \
        area_objective="0"
    ) \
    .subaction(impl_="all", \
               action_name_="check_bounds", \
               sub_component="TestMetadataParser$x", \
               sub_action="check_bound", \
               foralls=[("x","param","high_impact_mdparser_indices",None)]) \
    .subaction(impl_="all", \
               action_name_="check_bounds", \
               sub_component="TestMetadataParser$x", \
               sub_action="gated_check_bound", \
               foralls=[("x,v","taxo_fibertree","fibertree",("not in","param","high_impact_mdparser_indices"))])