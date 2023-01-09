'''
Primitive constitutive resources
'''

component_class_path='ref_input/compound_components.yaml'

# Constitutive properties
primitive_lib_path="./accelergy/compound_components_template.yaml"
compound_template_path="./accelergy/compound_components_template.yaml"
primitive_constitutive_properties={
                                   "format_uarch":{
                                                   "relative_ports":[""], \
                                                   "action_map":{"?metadata?read!gate!write":"parse_metadata", "idle":"idle"}, \
                                                   "template_path":compound_template_path, \
                                                   "inherit_attributes":["technology","metadatawidth"], \
                                                   "thrpt_io_xform":(lambda bw: bw)
                                                  },    
                                   "md_parser":{
                                                "relative_ports":["md_in"], \
                                                "action_map":{"parse_metadata":"parse_metadata", "idle":"idle"}, \
                                                "template_path":primitive_lib_path, \
                                                "inherit_attributes":["technology","metadatawidth"], \
                                                "thrpt_io_xform":(lambda bw: bw)                                                  
                                               },
                                   "skipping_uarch":{
                                                     "relative_ports":[""], \
                                                     "action_map":{"?metadata?read!gate!write":"skip", "idle":"idle"}, \
                                                     "template_path":compound_template_path, \
                                                     "inherit_attributes":["technology","metadatawidth","addresswidth"], \
                                                     "thrpt_io_xform":(lambda bw: bw)                                                       
                                                    },                                                   
                                   "intersect":{
                                                "relative_ports":["md_in0","md_in1"], \
                                                "action_map":{"skip":"intersect","idle":"idle"}, \
                                                "template_path":primitive_lib_path, \
                                                "inherit_attributes":["technology","metadatawidth"], \
                                                "thrpt_io_xform":(lambda bw: bw)                                                     
                                               },
                                   "pgen":{
                                           "relative_ports":["md_in"], \
                                           "action_map":{"intersect":"generate_position","idle":"idle"}, \
                                           "template_path":primitive_lib_path, \
                                           "inherit_attributes":["technology","metadatawidth","addresswidth"], \
                                           "thrpt_io_xform":(lambda bw: bw)                                                
                                          },
                                   "discard":{
                                           "relative_ports":["md_in"], \
                                           "action_map":{"intersect":"discard","idle":"idle"}, \
                                           "template_path":primitive_lib_path, \
                                           "inherit_attributes":["technology"], \
                                           "thrpt_io_xform":(lambda bw: bw)                                               
                                          }
                                  }

arch={
        'architecture': {
                         'version': 0.3, \
                         'subtree': [{
                                     'name': 'test_design', \
                                     'attributes': {'technology': '45nm'}, \
                                     'local': [
                                                {
                                                 'name':'iact_spad', \
                                                 'class':'storage', \
                                                 'subclass':'SRAM_MD', \
                                                 'attributes': {
                                                                'data_storage_depth': 192,      
                                                                'data_storage_width': 8,
                                                                'metadata_storage_depth': 128, 
                                                                'metadata_storage_width': 8,
                                                                'datawidth': 8,
                                                                'block_size': 1                                                    
                                                               }
                                                },
                                                {
                                                 'name':'weight_spad', \
                                                 'class':'DRAM', \
                                                 'subclass':'DummyStorage', \
                                                 'attributes': {
                                                                'width': 64,
                                                                'block_size': 8,
                                                                'datawidth': 8,
                                                                'metadata_storage_width': 8
                                                               }
                                                }
                                              ]
                                    }]
                        }
     }

# Example processed design
# - Useful graph constants
# - A generic edge is a "real" connection between the interfaces of two components
# - A "primitive edge" is a fictive edge between a primitives input and output
NO_EDGE=0
GENERIC_EDGE=1
PRIMITIVE_EDGE=2
# - Design

port_to_buffer={
                  'iact_spad.md_out0':'iact_spad', \
                  'iact_spad.flag_in0':'iact_spad', \
                  'iact_spad.md_out1':'iact_spad', \
                  'iact_spad.flag_in1':'iact_spad', \
                  'iact_spad.pos_in1':'iact_spad', \

                  'weight_spad.md_out0':'weight_spad', \
                  'weight_spad.flag_in0':'weight_spad', \
                  'weight_spad.md_out1':'weight_spad', \
                  'weight_spad.flag_in1':'weight_spad', \
                  'weight_spad.pos_in1':'weight_spad'                    
                 }

buffer_to_port={
                  'iact_spad':[
                                'iact_spad.md_out0', \
                                'iact_spad.flag_in0', \
                                'iact_spad.md_out1', \
                                'iact_spad.flag_in1', \
                                'iact_spad.pos_in1'
                              ],
                  'weight_spad':[
                                'weight_spad.md_out0', \
                                'weight_spad.flag_in0', \
                                'weight_spad.md_out1', \
                                'weight_spad.flag_in1', \
                                'weight_spad.pos_in1'     
                                ]               
                 }

component_instances={
                     "ia_fmt":           {
                                          "class":"format_uarch"
                                         },
                     "ia_skp":           {
                                          "class":"skipping_uarch"
                                         },
                     "w_fmt":            {
                                          "class":"format_uarch"
                                         }                                                                                                                                                                                                      
                    }

primitive_instances={
                     "ia_fmt.md_parser0":{
                                          "class":"md_parser", \
                                          "input_full_ports":["ia_fmt.md_parser0.md_in"],
                                          "taxonomic_attributes":{
                                                                    'metadataformat': 'UOP' ,
                                                                    'nnzmetadatatype': 'sentinel',
                                                                    'nnzmetadatalocation': 'data',
                                                                    'nummetadatatype': 'none',
                                                                    'nummetadatalocation': 'none'
                                                                 }
                                         },
                     "ia_fmt.md_parser1":{
                                          "class":"md_parser", \
                                          "input_full_ports":["ia_fmt.md_parser1.md_in"],
                                          "taxonomic_attributes":{
                                                                    'metadataformat': 'C' ,
                                                                    'nnzmetadatatype': 'sentinel',
                                                                    'nnzmetadatalocation': 'data',
                                                                    'nummetadatatype': 'none',
                                                                    'nummetadatalocation': 'none'
                                                                 }
                                         },
                     "ia_skp.isect":     {
                                          "class":"intersect", \
                                          "input_full_ports":["ia_skp.isect.md_in0","ia_skp.isect.md_in1"],
                                          "taxonomic_attributes":{
                                                                    'direction': 'leader_follower',
                                                                    'metadataformat': 'UOP',
                                                                    'heuristic': 'none'
                                                                 }
                                         },
                     "ia_skp.pgen0":     {
                                          "class":"pgen", \
                                          "input_full_ports":["ia_skp.pgen0.md_in"],
                                          "taxonomic_attributes":{
                                                                    'metadataformat': 'C',
                                                                    'positionformat': 'address'
                                                                 }
                                         },
                     "ia_skp.pgen1":     {
                                          "class":"pgen", \
                                          "input_full_ports":["ia_skp.pgen1.md_in"],
                                          "taxonomic_attributes":{
                                                                    'metadataformat': 'C',
                                                                    'positionformat': 'address'
                                                                 }
                                         },
                     "w_fmt.md_parser0":{
                                          "class":"md_parser", \
                                          "input_full_ports":["w_fmt.md_parser0.md_in"],
                                          "taxonomic_attributes":{
                                                                    'metadataformat': 'UOP' ,
                                                                    'nnzmetadatatype': 'sentinel',
                                                                    'nnzmetadatalocation': 'data',
                                                                    'nummetadatatype': 'none',
                                                                    'nummetadatalocation': 'none'
                                                                 }
                                         },
                     "w_fmt.md_parser1":{
                                          "class":"md_parser", \
                                          "input_full_ports":["w_fmt.md_parser1.md_in"],
                                          "taxonomic_attributes":{
                                                                    'metadataformat': 'C' ,
                                                                    'nnzmetadatatype': 'sentinel',
                                                                    'nnzmetadatalocation': 'data',
                                                                    'nummetadatatype': 'none',
                                                                    'nummetadatalocation': 'none'
                                                                 }
                                         }                                                                                                                                                                                                             
                    }

annotated_reduced_graph={
                         #iact_pad md_parser0 loop
                         "iact_spad.md_out0":{
                                              "thrpt":1, \
                                              "component_name":"iact_spad", \
                                              "edges_out":[
                                                           ('ia_fmt.md_in0',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_fmt.md_in0':    {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt", \
                                              "edges_out":[
                                                           ('ia_fmt.md_parser0.md_in',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_fmt.md_parser0.md_in':    {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt.md_parser0", \
                                              "edges_out":[
                                                           ('ia_fmt.md_parser0.flag_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'ia_fmt.md_parser0.flag_out':    {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt.md_parser0", \
                                              "edges_out":[
                                                           ('ia_fmt.flag_out0',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_fmt.flag_out0': {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt", \
                                              "edges_out":[
                                                           ('iact_spad.flag_in0',GENERIC_EDGE)
                                                          ]
                                             },
                         'iact_spad.flag_in0': {
                                              "thrpt":1, \
                                              "component_name":"iact_spad", \
                                              "edges_out":[]
                                             },

                         #iact_pad md_parser1 & skip/pgens loop                                             
                         "iact_spad.md_out1":{
                                              "thrpt":1, \
                                              "component_name":"iact_spad", \
                                              "edges_out":[
                                                           ('ia_fmt.md_in1',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_fmt.md_in1':    {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt", \
                                              "edges_out":[
                                                           ('ia_fmt.md_parser1.md_in',GENERIC_EDGE), \
                                                           ('ia_skp.isect.md_in0',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_fmt.md_parser1.md_in':    {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt.md_parser1", \
                                              "edges_out":[
                                                           ('ia_fmt.md_parser1.flag_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'ia_fmt.md_parser1.flag_out':    {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt.md_parser1", \
                                              "edges_out":[
                                                           ('ia_fmt.flag_out1',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_fmt.flag_out1':  {
                                              "thrpt":1, \
                                              "component_name":"ia_fmt", \
                                              "edges_out":[
                                                           ('iact_spad.flag_in1',GENERIC_EDGE)
                                                          ]
                                             },
                         'iact_spad.flag_in1':  {
                                              "thrpt":1, \
                                              "component_name":"iact_spad", \
                                              "edges_out":[]
                                             },
                         'ia_skp.md_in0':    {
                                              "thrpt":1, \
                                              "component_name":"ia_skp", \
                                              "edges_out":[
                                                           ('ia_skp.isect.md_in0',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_skp.isect.md_in0':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp.isect', \
                                              "edges_out":[
                                                           ('ia_skp.isect.md_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'ia_skp.isect.md_out':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp.isect', \
                                              "edges_out":[
                                                           ('ia_skp.pgen1.md_in',GENERIC_EDGE),
                                                           ('ia_skp.pgen0.md_in',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_skp.pgen1.md_in':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp.pgen1', \
                                              "edges_out":[
                                                           ('ia_skp.pgen1.pos_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'ia_skp.pgen1.pos_out':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp.pgen1', \
                                              "edges_out":[
                                                           ('ia_skp.pos_out1',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_skp.pos_out1':  {
                                              "thrpt":1, \
                                              "component_name":'ia_skp', \
                                              "edges_out":[
                                                           ('weight_spad.pos_in0',GENERIC_EDGE)
                                                          ]
                                             },
                         'weight_spad.pos_in0':  {
                                              "thrpt":1, \
                                              "component_name":'weight_spad', \
                                              "edges_out":[]
                                             },
                         'ia_skp.pgen0.md_in':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp.pgen0', \
                                              "edges_out":[
                                                           ('ia_skp.pgen0.pos_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'ia_skp.pgen0.md_out':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp.pgen0', \
                                              "edges_out":[
                                                           ('ia_skp.pos_out0',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_skp.pos_out0':  {
                                              "thrpt":1, \
                                              "component_name":'ia_skp', \
                                              "edges_out":[
                                                           ('iact_spad.pos_in1',GENERIC_EDGE)
                                                          ]
                                             },
                         'iact_spad.pos_in1':  {
                                              "thrpt":1, \
                                              "component_name":'iact_spad', \
                                              "edges_out":[]
                                             },

                         # weight_spad md_parser0 loop 
                         'weight_spad.md_out0':  {
                                              "thrpt":1, \
                                              "component_name":'weight_spad', \
                                              "edges_out":[
                                                           ('w_fmt.md_in0',GENERIC_EDGE),
                                                           ('ia_skp.md_in1',GENERIC_EDGE)
                                                          ]
                                             },
                         'ia_skp.md_in1':    {
                                              "thrpt":1, \
                                              "component_name":'ia_skp', \
                                              "edges_out":[]
                                             },
                         'w_fmt.md_in0':     {
                                              "thrpt":1, \
                                              "component_name":'w_fmt', \
                                              "edges_out":[
                                                           ('w_fmt.md_parser0.md_in',GENERIC_EDGE)
                                                          ]
                                             },
                         'w_fmt.md_parser0.md_in':     {
                                              "thrpt":1, \
                                              "component_name":'w_fmt.md_parser0', \
                                              "edges_out":[
                                                           ('w_fmt.md_parser0.flag_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'w_fmt.md_parser0.flag_out':     {
                                              "thrpt":1, \
                                              "component_name":'w_fmt.md_parser0', \
                                              "edges_out":[
                                                           ('w_fmt.pos_out0',GENERIC_EDGE)
                                                          ]
                                             },
                         'w_fmt.pos_out0':    {
                                              "thrpt":1, \
                                              "component_name":'w_fmt', \
                                              "edges_out":[
                                                           ('weight_spad.flag_in0',GENERIC_EDGE)
                                                          ]
                                             },
                         'weight_spad.flag_in0':     {
                                              "thrpt":1, \
                                              "component_name":'weight_spad', \
                                              "edges_out":[]
                                             },
                         'weight_spad.md_out1':     {
                                              "thrpt":1, \
                                              "component_name":'weight_spad', \
                                              "edges_out":[
                                                           ('w_fmt.md_in1',GENERIC_EDGE)
                                                          ]
                                             },
                         'w_fmt.md_in1':     {
                                              "thrpt":1, \
                                              "component_name":'w_fmt', \
                                              "edges_out":[
                                                           ('w_fmt.md_parser1.md_in',GENERIC_EDGE)
                                                          ]
                                             },
                         'w_fmt.md_parser1.md_in':     {
                                              "thrpt":1, \
                                              "component_name":'w_fmt.md_parser1', \
                                              "edges_out":[
                                                           ('w_fmt.md_parser1.pos_out',PRIMITIVE_EDGE)
                                                          ]
                                             },
                         'w_fmt.md_parser1.pos_out':     {
                                              "thrpt":1, \
                                              "component_name":'w_fmt.md_parser1', \
                                              "edges_out":[
                                                           ('w_fmt.flag_out1',GENERIC_EDGE)
                                                          ]
                                             },
                         'w_fmt.flag_out1':  {
                                              "thrpt":1, \
                                              "component_name":'w_fmt', \
                                              "edges_out":[
                                                           ('weight_spad.flag_in1',GENERIC_EDGE)
                                                          ]
                                             },
                         'weight_spad.flag_in1':  {
                                              "thrpt":1, \
                                              "component_name":'weight_spad', \
                                              "edges_out":[]
                                             }
                        }

def get_test_data():
    return primitive_constitutive_properties, arch, primitive_instances, annotated_reduced_graph, component_class_path, port_to_buffer, buffer_to_port, component_instances