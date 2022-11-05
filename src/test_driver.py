'''Regression testbench'''

import os
from util.taxonomy.designelement import Port
from test import basictests, validationtests, formatuarchtests, incompleteuarchtests

os.system('rm -f *test.yaml')

# Basic netlist functionality tests
basictests.do_tests()

# Test validation rules
validationtests.do_tests()

# Format uarch rule set
formatuarchtests.do_tests()

# Incomplete microarchitecture rule set
incompleteuarchtests.do_tests()