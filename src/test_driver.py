import os
from util.taxonomy.designelement import Port
from test import basictests, validationtests

os.system('rm -f *test.yaml')

# Basic netlist functionality tests
basictests.do_tests()

# Test validation rules
validationtests.do_tests()