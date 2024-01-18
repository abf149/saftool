CHISEL_PATH := hw/chisel/
STARTDIR:=$(shell pwd)

sbt:
	cd $(CHISEL_PATH);sbt test;cd $(STARTDIR)

clean_sbt:
	rm -f hw/chisel/src/verilog/*.v

clean_rtl:
	rm -f hw/rtl_out/*.v
	rm -f hw/rtl_out/*.log

clean_log:
	rm -f hw/rtl_out/*.log
	rm -f hw/sim_data/*.log

clean_summary:
	rm -f hw/sim_data/*.summary

.PHONY: sbt clean_rtl clean_log clean_summary