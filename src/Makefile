REMOTE_PATH := tmp/
CLOCK_PERIOD := 5.000 # ns
SYNTH_LIB := /homes/abf149/pdk/ncsu-FreePDK45-1.4/FreePDK45/osu_soc/lib/files/gscl45nm.db
CHISEL_PATH := hw/chisel/
HW_PATH := hw/
ACCELERGY_DATA_PATH := accelergy/data/
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
CHAR_LOG_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(CHAR_LOG_FILENAMES))
CHAR_POWER_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.power)
CHAR_POWER_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(CHAR_POWER_FILENAMES))
CHAR_AREA_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.area)
CHAR_AREA_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(CHAR_AREA_FILENAMES))
CHAR_LATENCY_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.latency)
CHAR_LATENCY_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(CHAR_LATENCY_FILENAMES))
CHAR_SUMMARY_FILENAMES:=$(STRIPPED_SCALA_FILENAMES:.scala=.summary)
CHAR_SUMMARY_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(CHAR_SUMMARY_FILENAMES))
TARGET_VERILOG_FILES:=$(addprefix $(VERILOG_DEST_PATH),$(VERILOG_FILENAMES))
DEST_SIM_FILES:=$(addprefix $(SIM_DATA_DEST_PATH),$(SIM_FILENAMES))
PRIMITIVES_TABLE_FILE=$(SIM_DATA_DEST_PATH)primitives_table.csv

$(TARGET_VERILOG_FILES):
	cd $(CHISEL_PATH);sbt test;cd $(STARTDIR)
	cp -r $(VERILOG_OUTPUT_PATH)* $(VERILOG_DEST_PATH)

$(DEST_SIM_FILES): $(TARGET_VERILOG_FILES)
	cp $(shell find $(SIM_DATA_OUTPUT_PATH) -type f -name '$(notdir $@)') $(SIM_DATA_DEST_PATH)

$(CHAR_LOG_FILES): $(DEST_SIM_FILES)
	echo $@
	rm -f $@
	touch $@
	echo "time CLOCK_PERIOD=$(CLOCK_PERIOD) DESIGN_RTL=mod.v DESIGN_TOPLEVEL=$(basename $(notdir $@)) SYNTH_LIB=$(SYNTH_LIB) dc_shell -f build_dc_nsa.tcl" | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_shell_remote.sh"
	cat scripts/build_dc_nsa.tcl | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_dc_nsa.tcl"	
	scp hw/rtl_out/$(basename $(notdir $@)).v abf149@effie.mit.edu:$(REMOTE_PATH)mod.v
	scp $(basename $@).vcd abf149@effie.mit.edu:$(REMOTE_PATH)sim.vcd
	ssh abf149@effie.mit.edu "vcd2saif -input $(REMOTE_PATH)sim.vcd -o  $(REMOTE_PATH)sim.saif; cd $(REMOTE_PATH); chmod +x build_shell_remote.sh; ./build_shell_remote.sh" | tee -a $@

$(CHAR_POWER_FILES): $(CHAR_LOG_FILES)
	rm -f $@
	sed -n -e "/Report : power/,/Execution successful/ p" $(basename $@).log | sed -e '1d;$d' > $@

$(CHAR_AREA_FILES): $(CHAR_LOG_FILES)
	rm -f $@
	sed -n -e "/Hierarchical area distribution/,/Execution successful/ p" $(basename $@).log | sed -e '1d;$d' > $@

$(CHAR_LATENCY_FILES): $(CHAR_LOG_FILES)
	rm -f $@
	sed -n -e "/Report : qor/,/  Cell Count/ p" $(basename $@).log | sed -e '1d;$d' > $@

logmetricbreakouts: $(CHAR_POWER_FILES) $(CHAR_AREA_FILES) $(CHAR_LATENCY_FILES)

$(CHAR_SUMMARY_FILES): $(CHAR_POWER_FILES) $(CHAR_AREA_FILES) $(CHAR_LATENCY_FILES)
	echo $@
	echo $(basename $@) | python3 parse_summary.py > $@

$(PRIMITIVES_TABLE_FILE): $(CHAR_SUMMARY_FILES)
	rm -f $@
	touch $@
	echo header | python3 parse_summary.py >> $@
	cat $(wildcard $(SIM_DATA_DEST_PATH)*.summary) >> $@

characterize: $(PRIMITIVES_TABLE_FILE)

$(ACCELERGY_DATA_PATH)$(notdir $(PRIMITIVES_TABLE_FILE)): $(PRIMITIVES_TABLE_FILE)
	cp $(PRIMITIVES_TABLE_FILE) $(ACCELERGY_DATA_PATH)

actions: $(ACCELERGY_DATA_PATH)$(notdir $(PRIMITIVES_TABLE_FILE))

# Clean

clean_actions:
	rm -rf $(ACCELERGY_DATA_PATH)*

clean_summary:
	rm -rf $(SIM_DATA_DEST_PATH)*.summary
	rm -rf $(SIM_DATA_DEST_PATH)*.csv

clean_log:
	rm -rf $(SIM_DATA_DEST_PATH)*.log
	rm -rf $(SIM_DATA_DEST_PATH)*.power
	rm -rf $(SIM_DATA_DEST_PATH)*.area
	rm -rf $(SIM_DATA_DEST_PATH)*.latency	

clean_hw:
	rm -rf $(VERILOG_OUTPUT_PATH)*
	rm -rf $(SIM_DATA_OUTPUT_PATH)

clean_hw_all: clean_hw clean_log clean_summary clean_actions
	rm -rf $(VERILOG_DEST_PATH)*.v
	rm -rf $(VERILOG_DEST_PATH)*/	
	rm -rf $(SIM_DATA_DEST_PATH)*.vcd $(SIM_DATA_DEST_PATH)*.log
	rm -rf $(SIM_DATA_DEST_PATH)*/


clean_remote:
	ssh abf149@effie.mit.edu "cd $(REMOTE_PATH); rm -f *.v *.tcl *.sh *.log *.svf *.saif *.vcd; rm -rf alib-52; rm -rf analyzed"

.PHONY: clean_hw clean_hw_all clean_remote clean_log characterize