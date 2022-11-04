import os
from util.taxonomy.designelement import Port
from test import basictests

os.system('rm -f *test.yaml')

# Basic netlist functionality tests
basictests.do_tests()