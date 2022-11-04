import os
from util.taxonomy.designelement import Port
from test import basictests, validationtests, formatuarchtests

os.system('rm -f *test.yaml')

# Basic netlist functionality tests
basictests.do_tests()

# Test validation rules
validationtests.do_tests()

# Format uarch validation rules
formatuarchtests.do_tests()