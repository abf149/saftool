CLOCK_PERIODS="1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0 0.95 0.90 0.85 0.80 0.75 0.70 0.65 0.60 0.55 0.50 0.45 0.40 0.35 0.30 0.25 0.20 0.15 0.10 0.05 1.95 1.90 1.85 1.80 1.75 1.70 1.65 1.60 1.55 1.50 1.45 1.40 1.35 1.30 1.25 1.20 1.15 1.10 1.05 2.05 2.10 2.15 2.20 2.25 2.30 2.35 2.40 2.45 2.50 2.55 2.60 2.65 2.70 2.75 2.80 2.85 2.90 2.95 3.05 3.10 3.15 3.20 3.25 3.30 3.35 3.40 3.45 3.50 3.55 3.60 3.65 3.70 3.75 3.80 3.85 3.90 3.95 4.05 4.10 4.15 4.20 4.25 4.30 4.35 4.40 4.45 4.50 4.55 4.60 4.65 4.70 4.75 4.80 4.85 4.90 4.95 5.05 5.10 5.15 5.20 5.25 5.30 5.35 5.40 5.45 5.50 5.55 5.60 5.65 5.70 5.75 5.80 5.85 5.90 5.95 6.05 6.10 6.15 6.20 6.25 6.30 6.35 6.40 6.45 6.50 6.55 6.60 6.65 6.70 6.75 6.80 6.85 6.90 6.95 7.05 7.10 7.15 7.20 7.25 7.30 7.35 7.40 7.45 7.50 7.55 7.60 7.65 7.70 7.75 7.80 7.85 7.90 7.95 8.05 8.10 8.15 8.20 8.25 8.30 8.35 8.40 8.45 8.50 8.55 8.60 8.65 8.70 8.75 8.80 8.85 8.90 8.95 9.05 9.10 9.15 9.20 9.25 9.30 9.35 9.40 9.45 9.50 9.55 9.60 9.65 9.70 9.75 9.80 9.85 9.90 9.95" #ns

make clean_log clean_summary
rm -f hw/sim_data/primitives_table_global.csv # probably redundant
touch hw/sim_data/primitives_table_global.csv
echo header | python3 parse_summary.py >> hw/sim_data/primitives_table_global.csv

for CLOCK_PERIOD in $CLOCK_PERIODS; do \
    echo $CLOCK_PERIOD ?
    if [ ! -d "hw/sim_data/$CLOCK_PERIOD" ]
    then
        echo ...yes...
        # Characterize @ target clock period if data is
        # not already available
        mkdir -p hw/sim_data/$CLOCK_PERIOD
        export CLOCK_PERIOD=$CLOCK_PERIOD
        make -f Makefile.k logmetricbreakouts
        cp hw/sim_data/*.log hw/sim_data/$CLOCK_PERIOD/ # Full log
        cp hw/sim_data/*.area hw/sim_data/$CLOCK_PERIOD/ # Area excerpt
        cp hw/sim_data/*.power hw/sim_data/$CLOCK_PERIOD/ # Power excerpt
        cp hw/sim_data/*.latency hw/sim_data/$CLOCK_PERIOD/ # Latency excerpt
        cp hw/sim_data/*.summary hw/sim_data/$CLOCK_PERIOD/ # Primitive data table row
        cp hw/sim_data/primitives_data.csv hw/sim_data/$CLOCK_PERIOD/primitives_data.csv
        make clean_log clean_summary
        echo ...characterization done.
    fi

    if [ ! -f "hw/sim_data/$CLOCK_PERIOD/primitives_table.csv" ]
    then
        echo "- Rebuilding primitive data table for $CLOCK_PERIOD..."
        make -f Makefile.k characterize
        cp hw/sim_data/*.summary hw/sim_data/$CLOCK_PERIOD/
        cp hw/sim_data/primitives_table.csv hw/sim_data/$CLOCK_PERIOD/
        rm -f hw/sim_data/*.summary hw/sim_data/primitives_table.csv
        echo "- Primitive data table for $CLOCK_PERIOD generated."
    fi

    echo "- Appending to global primitives table..."
	cat hw/sim_data/$CLOCK_PERIOD/primitives_table.csv >> hw/sim_data/primitives_table_global.csv   
done

echo "done."