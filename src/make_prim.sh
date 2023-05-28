CLOCK_PERIODS="1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0" #ns

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