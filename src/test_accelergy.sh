# accelergyTables may need to be run once
accelergyTables

# Clear prior outputs
rm ref_outputs/*

accelergy -o ref_output/ ref_output/arch_w_SAF.yaml ref_output/compound_components.yaml ./ref_input/action_counts.yaml -v 1