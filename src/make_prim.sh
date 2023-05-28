CLOCK_PERIODS="1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0 0.95 0.90 0.85 0.80 0.75 0.70 0.65 0.60 0.55 0.50 0.45 0.40 0.35 0.30 0.25 0.20 0.15 0.10 0.05 1.95 1.90 1.85 1.80 1.75 1.70 1.65 1.60 1.55 1.50 1.45 1.40 1.35 1.30 1.25 1.20 1.15 1.10 1.05" #ns

make clean_log clean_summary

for i in $CLOCK_PERIODS; do \
    echo $i ?
    if [ ! -d "hw/sim_data/$i" ]
    then
        echo ...yes...
        # Characterize @ target clock period if data is
        # not already available
        mkdir -p hw/sim_data/$i
        export CLOCK_PERIOD=$i
        make -f Makefile.k logmetricbreakouts
        cp hw/sim_data/*.log hw/sim_data/$i/ # Full log
        cp hw/sim_data/*.area hw/sim_data/$i/ # Area excerpt
        cp hw/sim_data/*.power hw/sim_data/$i/ # Power excerpt
        cp hw/sim_data/*.latency hw/sim_data/$i/ # Latency excerpt
        cp hw/sim_data/*.summary hw/sim_data/$i/ # Primitive data table row
        make clean_log clean_summary
        echo ...done.
    fi
done