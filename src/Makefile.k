REMOTE_PATH := tmp/
#CLOCK_PERIOD := 5 # 5ns
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
	cp $(shell find $(SIM_DATA_OUTPUT_PATH)$(shell echo $(notdir $(basename $@)) | sed "s/_\(.*\)//")_should_$(shell echo $(notdir $(basename $@)) | sed "s/\(.*\)_//") -type f -name '$(shell echo $(notdir $(basename $@)) | sed "s/_\(.*\)//").vcd') $@

# scp $(basename $@).vcd abf149@effie.mit.edu:$(REMOTE_PATH)sim.vcd
# ssh abf149@effie.mit.edu "vcd2saif -input $(REMOTE_PATH)sim.vcd -o  $(REMOTE_PATH)sim.saif; cd $(REMOTE_PATH); chmod +x build_shell_remote.sh; ./build_shell_remote.sh" | tee -a $@
$(CHAR_LOG_FILES): $(DEST_SIM_FILES)
	echo $@
	rm -f $@
	touch $@
	echo "time CLOCK_PERIOD=$(CLOCK_PERIOD) DESIGN_RTL=mod.v DESIGN_TOPLEVEL=$(shell echo $(notdir $(basename $@)) | sed "s/_\(.*\)//") SYNTH_LIB=$(SYNTH_LIB) dc_shell -f build_dc_nsa.tcl" | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_shell_remote.sh"
	cat scripts/build_dc_nsa.tcl | ssh abf149@effie.mit.edu "/bin/bash -c cat>$(REMOTE_PATH)build_dc_nsa.tcl"	
	scp hw/rtl_out/$(basename $(notdir $@)).v abf149@effie.mit.edu:$(REMOTE_PATH)mod.v
	ssh abf149@effie.mit.edu "cd $(REMOTE_PATH); chmod +x build_shell_remote.sh; ./build_shell_remote.sh" | tee -a $@

$(CHAR_POWER_FILES): $(CHAR_LOG_FILES)
	rm -f $@
	sed -n -e "/Report : power/,/Execution successful/ p" $(basename $@).log | sed -e '1d;$d' > $@

$(CHAR_AREA_FILES): $(CHAR_LOG_FILES)
	rm -f $@
	sed -n -e '/^  Area/,/Design Area:/p' $(basename $@).log > $@

$(CHAR_LATENCY_FILES): $(CHAR_LOG_FILES)
	rm -f $@
	sed -n -e "/Report : qor/,/  Cell Count/ p" $(basename $@).log | sed -e '1d;$d' > $@

logmetricbreakouts: $(CHAR_POWER_FILES) $(CHAR_AREA_FILES) $(CHAR_LATENCY_FILES)

$(CHAR_SUMMARY_FILES):
	echo $@
	echo $(SIM_DATA_DEST_PATH)$(CLOCK_PERIOD)/$(basename $(shell basename $(@)))
	echo $(SIM_DATA_DEST_PATH)$(CLOCK_PERIOD)/$(basename $(shell basename $(@))) | python3 parse_summary.py > $@

# 	echo header | python3 parse_summary.py >> $@
$(PRIMITIVES_TABLE_FILE): $(CHAR_SUMMARY_FILES)
	rm -f $@
	touch $@
	cat $(wildcard $(SIM_DATA_DEST_PATH)*.summary) >> $@

characterize: $(PRIMITIVES_TABLE_FILE)

$(ACCELERGY_DATA_PATH)$(notdir $(PRIMITIVES_TABLE_FILE)): $(PRIMITIVES_TABLE_FILE)
	mkdir -p $(ACCELERGY_DATA_PATH)
	cp $(PRIMITIVES_TABLE_FILE) $(ACCELERGY_DATA_PATH)

actions: $(ACCELERGY_DATA_PATH)$(notdir $(PRIMITIVES_TABLE_FILE))

sbt:
	cd $(CHISEL_PATH);sbt test;cd $(STARTDIR)

vcd: $(DEST_SIM_FILES)	

test: $(DEST_SIM_FILES)

# accelergy -v 3 -o examples/eyerissv2_bidir_bitmask/output/ ref_output/arch_w_SAF.yaml ref_output/compound_components.yaml ./ref_input/action_counts.yaml -v 1
examples: $(ACCELERGY_DATA_PATH)$(notdir $(PRIMITIVES_TABLE_FILE))
	./prep_accelergy.sh
	python3 safinfer.py --dir-in examples/sparten_like/input/ --dir-out examples/sparten_like/output/
	python3 safmodel.py --netlist examples/sparten_like/output/new_arch.yaml --arch examples/sparten_like/input/arch.yaml --comp-in examples/sparten_like/input/compound_components.yaml --arch-out examples/sparten_like/output/arch_w_SAF.yaml --comp-out examples/sparten_like/output/compound_components.yaml
	timeloop-model -o examples/sparten_like/output/ examples/sparten_like/input/arch.yaml examples/sparten_like/input/compound_components.yaml examples/sparten_like/input/prob.yaml examples/sparten_like/input/map.yaml examples/sparten_like/input/sparseopts.yaml
	timeloop-model -o examples/sparten_like/output_w_SAF/ examples/sparten_like/output/arch_w_SAF.yaml examples/sparten_like/output/compound_components.yaml examples/sparten_like/input/prob.yaml examples/sparten_like/input/map.yaml examples/sparten_like/input/sparseopts.yaml	


#python3 safinfer.py --dir-in examples/eyerissv2_bidir_bitmask/input/ --dir-out examples/eyerissv2_bidir_bitmask/output/
#python3 safmodel.py --netlist examples/eyerissv2_bidir_bitmask/output/new_arch.yaml --arch examples/eyerissv2_bidir_bitmask/input/arch.yaml --comp-in examples/eyerissv2_bidir_bitmask/input/compound_components.yaml --arch-out examples/eyerissv2_bidir_bitmask/output/arch_w_SAF.yaml --comp-out examples/eyerissv2_bidir_bitmask/output/compound_components.yaml
#timeloop-model -o examples/eyerissv2_bidir_bitmask/output/ examples/eyerissv2_bidir_bitmask/input/arch.yaml examples/eyerissv2_bidir_bitmask/input/compound_components.yaml examples/eyerissv2_bidir_bitmask/input/prob.yaml examples/eyerissv2_bidir_bitmask/input/map.yaml examples/eyerissv2_bidir_bitmask/input/sparseopts.yaml
#timeloop-model -o examples/eyerissv2_bidir_bitmask/output_w_SAF/ examples/eyerissv2_bidir_bitmask/output/arch_w_SAF.yaml examples/eyerissv2_bidir_bitmask/output/compound_components.yaml examples/eyerissv2_bidir_bitmask/input/prob.yaml examples/eyerissv2_bidir_bitmask/input/map.yaml examples/eyerissv2_bidir_bitmask/input/sparseopts.yaml
#python3 safinfer.py --dir-in examples/sparten_like/input/ --dir-out examples/sparten_like/output/
#python3 safmodel.py --netlist examples/sparten_like/output/new_arch.yaml --arch examples/sparten_like/input/arch.yaml --comp-in examples/sparten_like/input/compound_components.yaml --arch-out examples/sparten_like/output/arch_w_SAF.yaml --comp-out examples/sparten_like/output/compound_components.yaml
#timeloop-model -o examples/sparten_like/output/ examples/sparten_like/input/arch.yaml examples/sparten_like/input/compound_components.yaml examples/sparten_like/input/prob.yaml examples/sparten_like/input/map.yaml examples/sparten_like/input/sparseopts.yaml
#timeloop-model -o examples/sparten_like/output_w_SAF/ examples/sparten_like/output/arch_w_SAF.yaml examples/sparten_like/output/compound_components.yaml examples/sparten_like/input/prob.yaml examples/sparten_like/input/map.yaml examples/sparten_like/input/sparseopts.yaml	
#python3 safinfer.py --dir-in examples/eyerissv2_bidir_coordpayload/input/ --dir-out examples/eyerissv2_bidir_coordpayload/output/
#python3 safmodel.py --netlist examples/eyerissv2_bidir_coordpayload/output/new_arch.yaml --arch examples/eyerissv2_bidir_coordpayload/input/arch.yaml --comp-in examples/eyerissv2_bidir_coordpayload/input/compound_components.yaml --arch-out examples/eyerissv2_bidir_coordpayload/output/arch_w_SAF.yaml --comp-out examples/eyerissv2_bidir_coordpayload/output/compound_components.yaml
#timeloop-model -o examples/eyerissv2_bidir_coordpayload/output/ examples/eyerissv2_bidir_coordpayload/input/arch.yaml examples/eyerissv2_bidir_coordpayload/input/compound_components.yaml examples/eyerissv2_bidir_coordpayload/input/prob.yaml examples/eyerissv2_bidir_coordpayload/input/map.yaml examples/eyerissv2_bidir_coordpayload/input/sparseopts.yaml
#timeloop-model -o examples/eyerissv2_bidir_coordpayload/output_w_SAF/ examples/eyerissv2_bidir_coordpayload/output/arch_w_SAF.yaml examples/eyerissv2_bidir_coordpayload/output/compound_components.yaml examples/eyerissv2_bidir_coordpayload/input/prob.yaml examples/eyerissv2_bidir_coordpayload/input/map.yaml examples/eyerissv2_bidir_coordpayload/input/sparseopts.yaml	

# Clean

clean_actions:
	rm -rf $(ACCELERGY_DATA_PATH)*.csv

clean_summary:
	rm -rf $(SIM_DATA_DEST_PATH)*.summary
	rm -rf primitives_table.csv

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

clean_examples:
	rm -rf examples/eyerissv2_bidir_bitmask/output/*
	rm -rf examples/eyerissv2_bidir_bitmask/output_w_SAF/*
	rm -rf examples/eyerissv2_bidir_coordpayload/output/*
	rm -rf examples/eyerissv2_bidir_coordpayload/output_w_SAF/*	
	rm -rf examples/sparten_like/output/*
	rm -rf examples/sparten_like/output_w_SAF/*		

.PHONY: clean_hw clean_hw_all clean_remote clean_log characterize sbt vcd test examples