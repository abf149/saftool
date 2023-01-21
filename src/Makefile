REMOTE_PATH := tmp/
CLOCK_PERIOD := 5.000 # ns
#TOPLEVEL := BidirectionalCoordinatePayloadIntersectDecoupled
#VCDFILE := hw/sim_data/BidirectionalCoordinatePayloadIntersectDecoupled_should_default_workload/BidirectionalCoordinatePayloadIntersectDecoupled.vcd
SYNTH_LIB := /homes/abf149/pdk/ncsu-FreePDK45-1.4/FreePDK45/osu_soc/lib/files/gscl45nm.db
CHISEL_PATH := hw/chisel/
HW_PATH := hw/
VERILOG_OUTPUT_PATH := $(CHISEL_PATH)src/verilog/
VERILOG_DEST_PATH := $(HW_PATH)rtl_out/
SIM_DATA_OUTPUT_PATH := $(CHISEL_PATH)test_run_dir/
SIM_DATA_DEST_PATH := $(HW_PATH)sim_data/

STARTDIR:=$(shell pwd)

INPUT_SCALA_TEST_FILENAMES:=$(notdir $(wildcard hw/chisel/src/test/scala/saftool/*.scala))
STRIPPED_SCALA_FILENAMES:=$(INPUT_SCALA_TEST_FILENAMES:test_%=%)
VERILOG_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.v)
SIM_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.vcd)
CHAR_LOG_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.log)
TARGET_VERILOG_FILES:=$(addprefix $(VERILOG_DEST_PATH),$(VERILOG_FILENAMES))
DEST_SIM_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(SIM_FILENAMES))

$(TARGET_VERILOG_FILES):
	cd $(CHISEL_PATH);sbt test;cd $(STARTDIR)
	cp -r $(VERILOG_OUTPUT_PATH)* $(VERILOG_DEST_PATH)

$(DEST_SIM_FILES): $(TARGET_VERILOG_FILES)
	cp $(shell find $(SIM_DATA_OUTPUT_PATH) -type f -name '$(notdir $@)') $(SIM_DATA_DEST_PATH)

$(CHAR_LOG_FILENAMES): $(DEST_SIM_FILES)
	touch $(SIM_DATA_DEST_PATH)$@
	echo "time CLOCK_PERIOD=$(CLOCK_PERIOD) DESIGN_RTL=mod.v DESIGN_TOPLEVEL=$(basename $@) SYNTH_LIB=$(SYNTH_LIB) dc_shell -f build_dc_nsa.tcl" | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_shell_remote.sh"
	cat scripts/build_dc_nsa.tcl | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_dc_nsa.tcl"	
	scp hw/rtl_out/$(basename $@).v abf149@effie.mit.edu:$(REMOTE_PATH)mod.v
	scp $(addprefix $(SIM_DATA_DEST_PATH),$(basename $@).vcd) abf149@effie.mit.edu:$(REMOTE_PATH)sim.vcd
	ssh abf149@effie.mit.edu "vcd2saif -input $(REMOTE_PATH)sim.vcd -o  $(REMOTE_PATH)sim.saif; cd $(REMOTE_PATH); chmod +x build_shell_remote.sh; ./build_shell_remote.sh" | tee -a $(SIM_DATA_DEST_PATH)$@

actions: $(CHAR_LOG_FILENAMES)

# Clean
clean_hw:
	rm -rf $(VERILOG_OUTPUT_PATH)*
	rm -rf $(SIM_DATA_OUTPUT_PATH)

clean_hw_all: clean_hw
	rm -rf $(VERILOG_DEST_PATH)*.v
	rm -rf $(VERILOG_DEST_PATH)*/	
	rm -rf $(SIM_DATA_DEST_PATH)*.vcd $(SIM_DATA_DEST_PATH)*.log
	rm -rf $(SIM_DATA_DEST_PATH)*/


clean_remote:
	ssh abf149@effie.mit.edu "cd $(REMOTE_PATH); rm -f *.v *.tcl *.sh *.log *.svf *.saif *.vcd; rm -rf alib-52; rm -rf analyzed"

.PHONY: hw clean_hw clean_hw_all clean_remote char sbt actions