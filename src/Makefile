REMOTE_PATH = tmp/
CLOCK_PERIOD = 5.000 # ns
TOPLEVEL = BidirectionalCoordinatePayloadIntersectDecoupled
VCDFILE = hw/sim_data/BidirectionalCoordinatePayloadIntersectDecoupled_should_default_workload/BidirectionalCoordinatePayloadIntersectDecoupled.vcd
SYNTH_LIB = /homes/abf149/pdk/ncsu-FreePDK45-1.4/FreePDK45/osu_soc/lib/files/gscl45nm.db
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

# Characterization
char: hw clean_remote
	echo "time CLOCK_PERIOD=$(CLOCK_PERIOD) DESIGN_RTL=mod.v DESIGN_TOPLEVEL=$(TOPLEVEL) SYNTH_LIB=$(SYNTH_LIB) dc_shell -f build_dc_nsa.tcl" | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_shell_remote.sh"
	cat scripts/build_dc_nsa.tcl | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_dc_nsa.tcl"	
	scp hw/rtl_out/$(TOPLEVEL).v abf149@effie.mit.edu:$(REMOTE_PATH)mod.v
	scp $(VCDFILE) abf149@effie.mit.edu:$(REMOTE_PATH)sim.vcd
	ssh abf149@effie.mit.edu "vcd2saif -input $(REMOTE_PATH)sim.vcd -o  $(REMOTE_PATH)sim.saif; cd $(REMOTE_PATH); chmod +x build_shell_remote.sh; ./build_shell_remote.sh"

# Clean
clean_hw:
	rm -rf $(VERILOG_OUTPUT_PATH)*
	rm -rf $(SIM_DATA_OUTPUT_PATH)

clean_hw_all: clean_hw
	rm -rf $(VERILOG_DEST_PATH)*.v
	rm -rf $(VERILOG_DEST_PATH)*/	
	rm -rf $(SIM_DATA_DEST_PATH)*.vcd
	rm -rf $(SIM_DATA_DEST_PATH)*/


clean_remote:
	ssh abf149@effie.mit.edu "cd $(REMOTE_PATH); rm -f *.v *.tcl *.sh *.log *.svf *.saif *.vcd; rm -rf alib-52; rm -rf analyzed"

.PHONY: hw clean_hw clean_hw_all clean_remote char