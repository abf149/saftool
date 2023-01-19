VERILOG_OUTPUT_PATH = src/verilog/
VERILOG_DEST_PATH = ../rtl_out/
SIM_DATA_OUTPUT_PATH = test_run_dir/
SIM_DATA_DEST_PATH = ../sim_data/


# Chisel testbenches
test:
	sbt test
	cp -r $(VERILOG_OUTPUT_PATH)* $(VERILOG_DEST_PATH)
	cp -r $(SIM_DATA_OUTPUT_PATH)* $(SIM_DATA_DEST_PATH)

# Clean
clean:
	rm -r $(VERILOG_OUTPUT_PATH)*
	rm -r $(SIM_DATA_OUTPUT_PATH)

clean_all: clean
	rm -r $(VERILOG_DEST_PATH)*
	rm -r $(SIM_DATA_DEST_PATH)*

.PHONY: clean clean_all