from ...taxo.skipping.IntersectionLeaderFollower import IntersectionLeaderFollower, intersection_instances
import util.notation.model as mo_
import util.notation.characterization as ch_
import saflib.resources.char.ResourceRegistry as rr_

ctbl=rr_.getCharacterizationTable('accelergy/data/primitives_table.csv')
cfxn=ch_.CharacterizationMetricModel('test_fxn',ctbl) \
        .parentComponentUri('f.g') \
        .nameExpression('BidirectionalBitmaskIntersectDecoupled_metaDataWidth$(u)',['u']) \
        .symbolMap({'u':'@x','v':'@y'}) \
        .inheritParameters({'clock':'5ns','technology':'45nm'}) \
        .latencyIndependentVariableExpression('critical_path_clock_latency') \
        .latencyRangeExpression('And(latency<=2,latency>=0)')\
        .rowEnergyMetricFromRowPowerMetricExpression('combinational_total_power+register_total_power+clock_network_total_power') \
        .rowAreaMetricExpression('Combinational_Area') \
        .buildSymbolMap() \
        .buildSymList() \
        .buildCharacterizationTableView() \
        .buildSupportedConfigurations() \
        .buildSupportedSymbolValuesConstraints() \
        .buildSupportedSymbolValueCombosConstraints() \
        .buildRowEnergyMetricExpressionIfDerivedFromPower() \
        .buildRowEnergyLambda() \
        .buildRowAreaLambda() \
        .buildEnergyAreaLatencyTable() \
        .buildEnergyAreaMetricModels()

isect_attr_list=['rw','pr','cr','ww','nc']
scale_determinative_attr_list=['rw','pr','ww']

IntersectionLeaderFollowerModel=IntersectionLeaderFollower \
    .copy() \
    .scale_parameter("clock","real",yield_=True,inherit_=True) \
    .scale_parameter("technology","string",yield_=True,inherit_=True) \
    .require_port_throughput_attributes("md_in_leader",isect_attr_list) \
    .require_port_throughput_attributes("md_out",isect_attr_list) \
    .yield_taxonomic_attributes() \
    .yield_port_throughput_thresholds(port_attr_dict={"md_in_leader":scale_determinative_attr_list, \
                                                      "md_out":scale_determinative_attr_list}) \
    .action("fill") \
    .action("intersect") \
    .action("gated_fill") \
    .action("gated_intersect") \
    .taxonomic_instance_alias(["cp_lf_none"],"C") \
    .register_supported_instances(intersection_instances) \
    .add_implementation( \
        name="C", \
        taxonomic_instance="C", \
        attr_range_specs=[ \
            mo_.makeValuesConstraint("@md_in_leader_$a_thresh", \
                                     foralls=[("a","attrs",scale_determinative_attr_list)], \
                                     ranges=[(1, 8, 64, 256), 
                                              (1, 8, 64, 256), 
                                              (1, 8, 64, 256),
                                              (1, 8, 64, 256)]), \
            mo_.makeValuesConstraint("@md_out_$a_thresh", \
                                     foralls=[("a","attrs",scale_determinative_attr_list)], \
                                     ranges=[(1, 8, 64, 256), 
                                              (1, 8, 64, 256), 
                                              (1, 8, 64, 256),
                                              (1, 8, 64, 256)]) \
        ],
        constraints=[mo_.makePassthroughConstraint("@md_out_$a","@md_in_leader_$a",foralls=[("a","attrs",isect_attr_list)])], \
        energy_objective={"fill": \
                            "2*(@md_out_rw_thresh + @md_out_pr_thresh + @md_out_ww_thresh)", \
                          "intersect": \
                            "2*(@md_out_rw_thresh + @md_out_pr_thresh + @md_out_ww_thresh)", \
                          "gated_fill":"0", \
                          "gated_intersect":"0"}, \
        area_objective="2*(@md_out_rw_thresh + @md_out_pr_thresh + @md_out_ww_thresh)"
    )