#CLOCK_PERIODS="1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0 0.95 0.90 0.85 0.80 0.75 0.70 0.65 0.60 0.55 0.50 0.45 0.40 0.35 0.30 0.25 0.20 0.15 0.10 0.05 1.95 1.90 1.85 1.80 1.75 1.70 1.65 1.60 1.55 1.50 1.45 1.40 1.35 1.30 1.25 1.20 1.15 1.10 1.05 2.05 2.10 2.15 2.20 2.25 2.30 2.35 2.40 2.45 2.50 2.55 2.60 2.65 2.70 2.75 2.80 2.85 2.90 2.95 3.05 3.10 3.15 3.20 3.25 3.30 3.35 3.40 3.45 3.50 3.55 3.60 3.65 3.70 3.75 3.80 3.85 3.90 3.95 4.05 4.10 4.15 4.20 4.25 4.30 4.35 4.40 4.45 4.50 4.55 4.60 4.65 4.70 4.75 4.80 4.85 4.90 4.95 5.05 5.10 5.15 5.20 5.25 5.30 5.35 5.40 5.45 5.50 5.55 5.60 5.65 5.70 5.75 5.80 5.85 5.90 5.95 6.05 6.10 6.15 6.20 6.25 6.30 6.35 6.40 6.45 6.50 6.55 6.60 6.65 6.70 6.75 6.80 6.85 6.90 6.95 7.05 7.10 7.15 7.20 7.25 7.30 7.35 7.40 7.45 7.50 7.55 7.60 7.65 7.70 7.75 7.80 7.85 7.90 7.95 8.05 8.10 8.15 8.20 8.25 8.30 8.35 8.40 8.45 8.50 8.55 8.60 8.65 8.70 8.75 8.80 8.85 8.90 8.95 9.05 9.10 9.15 9.20 9.25 9.30 9.35 9.40 9.45 9.50 9.55 9.60 9.65 9.70 9.75 9.80 9.85 9.90 9.95" #ns



EXCLUDE_FILES=(
    "VectorSkipAheadIntersectionUnitRegistered_vectorLength4_numTags16_tagBitWidth5"
    "VectorSkipAheadIntersectionUnitRegistered_vectorLength4_numTags8_tagBitWidth3"
)

CLOCK_PERIODS="1.0 2.0 5.0 10.0" #ns
#SRC_DIR="hw/chisel/test_run_dir"
#DEST_DIR="hw/sim_data"
VERILOG_SRC_DIR="hw/chisel/src/verilog"
VERILOG_DEST_DIR="hw/rtl_out"
SIM_DATA_DIR="hw/sim_data"

#echo Copying over verilog...
#echo $VERILOG_SRC_DIR/*.v
#echo $VERILOG_DEST_DIR/*.v
#cp $VERILOG_SRC_DIR/*.v $VERILOG_DEST_DIR/*.v

#verilog_file_template="$VERILOG_DEST_DIR"/*.v
echo Target verilog files:
#verilog_file_template="${VERILOG_DEST_DIR}/VectorSkipAheadIntersectionUnitRegistered*.v ${VERILOG_DEST_DIR}/VectorTwoFingerMergeIntersectionRegistered*.v"
verilog_file_template="${VERILOG_DEST_DIR}/VectorTwoFingerMergeIntersectionRegistered*.v"
echo $verilog_file_template

make clean_log clean_summary clean_rtl
rm -f $SIM_DATA_DIR/*.csv
rm -f hw/sim_data/primitives_table_global.csv # probably redundant
touch hw/sim_data/primitives_table_global.csv
echo header | python3 parse_summary.py >> hw/sim_data/primitives_table_global.csv

for CLOCK_PERIOD in $CLOCK_PERIODS; do \
    echo $CLOCK_PERIOD ?

    #rm -f $VERILOG_DEST_DIR/*.v
    rm -f $VERILOG_DEST_DIR/*.log
    rm -f $SIM_DATA_DIR/*.log
    rm -f $SIM_DATA_DIR/*.power
    rm -f $SIM_DATA_DIR/*.area
    rm -f $SIM_DATA_DIR/*.latency
    rm -f $SIM_DATA_DIR/*.summary

    if [ ! -d "hw/sim_data/$CLOCK_PERIOD" ]
    then
        echo ...yes...
        # Characterize @ target clock period if data is
        # not already available
        mkdir -p hw/sim_data/$CLOCK_PERIOD
        export CLOCK_PERIOD=$CLOCK_PERIOD

        echo copying...
        find "$VERILOG_SRC_DIR" -name "*.v" -type f -print0 | xargs -0 -I {} cp {} "$VERILOG_DEST_DIR/"
        echo enumerating verilog files
        v_files=($verilog_file_template)
        total_files=${#v_files[@]}

        echo "Total_files: $total_files"

        # Initialize variables for timing and average calculation
        cumulative_time=0
        current_file=0

        # Loop through all .v files
        for v_file in "${v_files[@]}"; do
            if [[ -f "$v_file" ]]; then

                # Extract the base name without extension
                base_name=$(basename "$v_file" .v)

                # Check if this file is in the exclude list
                if [[ " ${EXCLUDE_FILES[@]} " =~ " $base_name " ]]; then
                    echo "Skipping excluded file: $v_file"
                    continue
                fi

                # Start time for this iteration
                start_time=$(date +%s)

                # Increment the current file counter
                ((current_file++))

                # Change the extension from .v to .log
                log_file="${v_file%.v}.log"
                power_file="${v_file%.v}.power"
                area_file="${v_file%.v}.area"
                latency_file="${v_file%.v}.latency"
                summary_file="${v_file%.v}.summary"

                # Call make with the log file
                make -f Makefile_log "$log_file"
                make -f Makefile_power "$power_file"
                make -f Makefile_area "$area_file"
                make -f Makefile_latency "$latency_file"
                make -f Makefile_summary "$summary_file"

                # End time for this iteration and calculate duration
                end_time=$(date +%s)
                duration=$((end_time - start_time))

                # Update cumulative time and calculate average
                cumulative_time=$((cumulative_time + duration))
                average_time=$((cumulative_time / current_file))

                # Calculate estimated time remaining (in seconds)
                remaining_files=$((total_files - current_file))
                eta=$((remaining_files * average_time))

                # Convert ETA from seconds to a more readable format, e.g., HH:MM:SS
                eta_formatted=$(printf '%02d:%02d:%02d\n' $((eta/3600)) $((eta%3600/60)) $((eta%60)))

                # Display progress and estimated time of arrival (ETA)
                echo "Processing Verilog file $current_file/$total_files - ETA: $eta_formatted"
            fi
        done

        # Finished processing
        echo "Finished processing all Verilog files."

        echo "Augmenting primitive characterization table"
        make -f Makefile_table_rows all

        cp hw/sim_data/*.log hw/sim_data/$CLOCK_PERIOD/ # Full log
        cp hw/sim_data/*.area hw/sim_data/$CLOCK_PERIOD/ # Area excerpt
        cp hw/sim_data/*.power hw/sim_data/$CLOCK_PERIOD/ # Power excerpt
        cp hw/sim_data/*.latency hw/sim_data/$CLOCK_PERIOD/ # Latency excerpt
        cp hw/sim_data/*.summary hw/sim_data/$CLOCK_PERIOD/ # Primitive data table row
        #cp hw/sim_data/primitives_data.csv hw/sim_data/$CLOCK_PERIOD/primitives_data.csv
        make clean_log clean_summary clean_rtl
        echo ...characterization done.
    fi

    #if [ ! -f "hw/sim_data/$CLOCK_PERIOD/primitives_table.csv" ]
    #then
    #    echo "- Rebuilding primitive data table for $CLOCK_PERIOD..."
    #    make -f Makefile.k characterize
    #    cp hw/sim_data/*.summary hw/sim_data/$CLOCK_PERIOD/
    #    cp hw/sim_data/primitives_table.csv hw/sim_data/$CLOCK_PERIOD/
    #    rm -f hw/sim_data/*.summary hw/sim_data/primitives_table.csv
    #    echo "- Primitive data table for $CLOCK_PERIOD generated."
    #fi

    #echo "- Appending to global primitives table..."
	#cat hw/sim_data/$CLOCK_PERIOD/primitives_table.csv >> hw/sim_data/primitives_table_global.csv   
done

echo "Installing accelergy primitives table csv"

cp hw/sim_data/primitives_table_global.csv accelergy/data/primitives_table.csv

echo "done."