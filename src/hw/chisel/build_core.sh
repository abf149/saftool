# Intersection, SparTen-like: fmt=B, md_orch=uncoupled
#dut_name=AUX_Intersect_Format_B_MDOrch_Uncoupled
#src_dir=intersect/intersect_fmt_B_mdorch_uncoupled

# Intersection, ExTensor-like: fmt=C, md_orch=uncoupled
dut_name=AUX_Intersect_Format_C_MDOrch_Uncoupled
src_dir=verilog
data_dir=../sim_data

# Intersection, ExTensor-like: fmt=C, md_orch=coupled
#dut_name=AUX_Intersect_Format_C_MDOrch_Coupled
#src_dir=intersect/intersect_fmt_C_mdorch_coupled

# Pgen, SparTen-like: input fmt=B, output pos=addr, CONVERT subcomponent
#dut_name=AUX_Pgen_Input_Format_B_Output_Pos_Addr_Convert
#src_dir=pgen/pgen_input_fmt_B_output_pos_addr_convert

# Pgen, SparTen-like: input fmt=B, output pos=addr, SKIP subcomponent
#dut_name=AUX_Pgen_Input_Format_B_Output_Pos_Addr_Skip
#src_dir=pgen/pgen_input_fmt_B_output_pos_addr_skip

clk_period=5.000

# FBA PBC unit
#dut_name=fbna_pbc
#src_dir=fbna/pbc

echo Simulating ${dut_name}...

rm src/*
cp output/src/${src_dir}/* output/src/
cd output/src/
iverilog tb.v
vvp a.out
cp sim.vcd ../../
cd ../../
echo - Saving results...
echo -- output/src/${src_dir}/
cp sim.vcd output/src/${src_dir}/

echo "Moving sim and src over to characterization machine (effie.mit.edu)..."
scp sim.vcd  abf149@effie.mit.edu:~/git_clones/intersection-model/
scp -i ./id_rsa output/src/*.v  abf149@effie.mit.edu:~/git_clones/intersection-model/

echo "Creating build script build_shell_remote.sh on characterization machine (effie.mit.edu)..."
echo "- echo time CLOCK_PERIOD=${clk_period} DESIGN_RTL=/homes/abf149/git_clones/intersection-model/${dut_name}.v DESIGN_TOPLEVEL=${dut_name} SYNTH_LIB=/homes/abf149/pdk/ncsu-FreePDK45-1.4/FreePDK45/osu_soc/lib/files/gscl45nm.db dc_shell -f build_dc_nsa.tcl > build_shell_remote.sh"

ssh -i ./id_rsa abf149@effie.mit.edu "echo time CLOCK_PERIOD=${clk_period} DESIGN_RTL=/homes/abf149/git_clones/intersection-model/${dut_name}.v DESIGN_TOPLEVEL=${dut_name} SYNTH_LIB=/homes/abf149/pdk/ncsu-FreePDK45-1.4/FreePDK45/osu_soc/lib/files/gscl45nm.db dc_shell -f build_dc_nsa.tcl > git_clones/intersection-model/build_shell_remote.sh && chmod 777 git_clones/intersection-model/build_shell_remote.sh"

echo "Running characterization on effie.mit.edu..."

ssh abf149@effie.mit.edu "vcd2saif -input ~/git_clones/intersection-model/sim.vcd -o  ~/git_clones/intersection-model/sim.saif; cd git_clones/intersection-model/; ./build_shell_remote.sh" | tee ${data_dir}/build_shell.log
grep -i "Report : power" output/src/${src_dir}/build_shell.log -A 70 > output/src/${src_dir}/power.log
grep -i "Report : area" output/src/${src_dir}/build_shell.log -A 70 > output/src/${src_dir}/area.log