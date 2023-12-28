CLOCK_PERIODS="1.0 2.0 5.0 10.0" #ns
#SRC_DIR="hw/chisel/test_run_dir"
#DEST_DIR="hw/sim_data"
VERILOG_SRC_DIR="hw/chisel/src/verilog"
VERILOG_DEST_DIR="hw/rtl_out"

CLOCK_PERIOD="1.0"

export CLOCK_PERIOD=$CLOCK_PERIOD

v_files=("$VERILOG_DEST_DIR"/VectorSkipAheadIntersectionUnitRegistered_vectorLength4_numTags16_tagBitWidth5.v)

log_file="$VERILOG_DEST_DIR"/VectorSkipAheadIntersectionUnitRegistered_vectorLength4_numTags16_tagBitWidth5.log

echo make "$log_file"
make -f Makefile_log "$log_file"