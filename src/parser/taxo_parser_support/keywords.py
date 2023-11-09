'''Taxoscript keywords'''
taxoscript_version='taxoscript_version'

'''General taxoscript fields'''
object_name='name'
object_attributes='attributes'
object_instances='instances'
object_ports='ports'
object_iterator='iterator'
port_input='input'
port_output='output'
valid_port_dirs=[port_input,port_output]

'''Net types'''
md_net_type='md'
pos_net_type='pos'
flag_net_type='flag'

'''Format types'''
supported_md_formats=["C","R","B","U"]
supported_pos_formats=["addr"]
supported_flag_formats=[] # No flag subtypes

'''Attribute types'''
fibertree_attr_type='fibertree'
format_attr_type='format'
string_attr_type='string'
int_attr_type='int'
valid_attr_types=[fibertree_attr_type, \
                  format_attr_type, \
                  string_attr_type, \
                  int_attr_type]