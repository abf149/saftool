CHISEL_PATH := hw/chisel/
STARTDIR:=$(shell pwd)

sbt:
	cd $(CHISEL_PATH);sbt test;cd $(STARTDIR)

clean_rtl:
	rm -f hw/rtl_out/*.v
	rm -f hw/rtl_out/*.log

.PHONY: sbt clean_rtl