# accelergyTables may need to be run once
accelergyTables

# Clear prior outputs
rm ref_outputs/*

accelergy -o ref_outputs/ ref_inputs/arch/*.yaml ref_inputs/components/*.yaml ./ref_inputs/*.yaml -v 1