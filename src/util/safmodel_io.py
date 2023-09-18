'''SAFmodel IO library - CLI argparse and YAML dump routines'''
from util.taxonomy import designelement as de
import os, argparse, test_data as td, copy, re
import util.sparseloop_config_processor as sl_config, yaml, argparse
from util.taxonomy.designelement import Architecture
from util.helper import info,warn,error

'''Config - condition the format of YAML file dumps'''
#yaml.Dumper.ignore_aliases = lambda *args : True

'''CLI argparse'''
def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--dir-in',default='')
    parser.add_argument('-n','--netlist',default='ref_output/new_arch.yaml')
    parser.add_argument('-a','--arch',default='ref_input/arch.yaml')
    parser.add_argument('-s','--sparseopts',default='ref_input/sparseopts.yaml')
    parser.add_argument('-c','--comp-in',default='ref_input/compound_components.yaml')
    parser.add_argument('-o','--dir-out',default='')
    parser.add_argument('-r','--arch-out',default='ref_output/arch_w_SAF.yaml')
    parser.add_argument('-k','--comp-out',default='ref_output/compound_components.yaml')
    parser.add_argument('-L','--log', action='store_true')
    parser.add_argument('-f','--log-file',default='./safmodel.log')    
    args = parser.parse_args()

    # Parse the CLI arguments
    print("SAFmodel.\n")
    do_logging=args.log
    print("Parsing input files:")

    if len(args.dir_out) > 0 or len(args.dir_in)>0:
        # Not yet supported
        assert(False) 
 
    print("- netlist:",args.netlist)
    netlist=de.Architecture.fromYamlFilename(args.netlist)
    print("- arch:",args.arch)
    arch=sl_config.load_config_yaml(args.arch)
    print("- sparseopts:",args.sparseopts)
    sparseopts=sl_config.load_config_yaml(args.sparseopts)
    print("- compound components (input):",args.comp_in)
    comp_in=sl_config.load_config_yaml(args.comp_in)
    print("- arch output path:",args.arch_out)
    arch_out_path=args.arch_out
    print("- compound components path (output):",args.comp_out)
    comp_out_path=args.comp_out

    return arch, \
           netlist, \
           sparseopts, \
           comp_in, \
           arch_out_path, \
           comp_out_path, \
           do_logging,\
           args.log_file

def load_taxonomic_microarchitecture(netlist):
    '''Load taxonomic description of SAF microarchitecture'''
    return Architecture.fromDict(sl_config.load_config_yaml(netlist))