CHISEL_PATH = hw/chisel/
HW_PATH = hw/
VERILOG_OUTPUT_PATH = $(CHISEL_PATH)src/verilog/
VERILOG_DEST_PATH = $(HW_PATH)rtl_out/
SIM_DATA_OUTPUT_PATH = $(CHISEL_PATH)test_run_dir/
SIM_DATA_DEST_PATH = $(HW_PATH)sim_data/

STARTDIR=$(shell pwd)

# Chisel testbenches
hw:
	cd $(CHISEL_PATH);sbt test;cd $(STARTDIR); cp -r $(VERILOG_OUTPUT_PATH)* $(VERILOG_DEST_PATH);cp -r $(SIM_DATA_OUTPUT_PATH)* $(SIM_DATA_DEST_PATH)

# Clean
clean_hw:
	rm -rf $(VERILOG_OUTPUT_PATH)*
	rm -rf $(SIM_DATA_OUTPUT_PATH)

clean_hw_all: clean_hw
	rm -rf $(VERILOG_DEST_PATH)*.v
	rm -rf $(VERILOG_DEST_PATH)*/	
	rm -rf $(SIM_DATA_DEST_PATH)*.vcd
	rm -rf $(SIM_DATA_DEST_PATH)*/

.PHONY: hw clean_hw clean_hw_all