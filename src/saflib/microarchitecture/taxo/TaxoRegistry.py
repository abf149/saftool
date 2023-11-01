from saflib.microarchitecture.taxo.address_primitives.PositionGenerator import PositionGenerator,buildPositionGenerator,pgen_instances
from saflib.microarchitecture.taxo.format.MetadataParser import MetadataParser,buildMetadataParser,md_parser_instances
from saflib.microarchitecture.taxo.skipping.IntersectionLeaderFollower import IntersectionLeaderFollower,buildIntersectionLeaderFollower,intersection_instances
from saflib.microarchitecture.taxo.format.FormatUarch import FormatUarch,buildFormatUarch,fmt_uarch_instances,fmt_uarch_topologies
from saflib.microarchitecture.taxo.skipping.SkippingUarch import SkippingUarch,buildSkippingUarch,skipping_uarch_instances,skipping_uarch_topologies

primitive_taxo_description_dict={}
primitive_taxo_constructor_dict={}
primitive_taxo_instances_dict={}

component_taxo_description_dict={}
component_taxo_constructor_dict={}
component_taxo_instances_dict={}
component_taxo_topologies_dict={}

def registerPrimitive(name_, \
                      taxo_primitive_description, \
                      primitive_constructor=None, \
                      primitive_instances=None):
    '''
    Add a SAF microarchitecture primitive taxonomic category description to registry.\n\n

    Arguments:\n
    - name_ -- string id of primitive component.\n
    - taxo_primitive_description -- structure representing the Taxonomic description of a
    microarchitecture primitive.\n
    - primitive_constructor -- function which builds an instance of the primitive.\n
    - primitive_instances -- list of supported instance flavors (constructor parameters) of the primitive.
    '''
    global primitive_taxo_description_dict
    global primitive_taxo_constructor_dict
    global primitive_taxo_instances_dict
    assert((primitive_constructor is not None) and \
           (primitive_instances is not None))

    primitive_taxo_description_dict[name_]=taxo_primitive_description
    primitive_taxo_constructor_dict[name_]=primitive_constructor
    primitive_taxo_instances_dict[name_]=primitive_instances

def registerComponent(name_, \
                      taxo_component_description, \
                      component_constructor=None, \
                      component_instances=None, \
                      component_topologies=None):
    '''
    Add a SAF microarchitecture component taxonomic category description to registry.\n\n

    Arguments:\n
    - name_ -- string id of component.\n
    - taxo_component_description -- structure representing the Taxonomic description of a
    microarchitecture component.\n
    - component_constructor -- function which builds an instance of the component.\n
    - component_instances -- list of supported instance flavors (constructor parameters) of the component.\n
    - component_topologies -- mapping from instance ids to implementation topologies
    '''
    global component_taxo_description_dict
    global component_taxo_constructor_dict
    global component_taxo_instances_dict
    global component_taxo_topologies_dict
    assert((component_constructor is not None) and \
           (component_instances is not None) and \
           (component_topologies is not None))

    component_taxo_description_dict[name_]=taxo_component_description
    component_taxo_constructor_dict[name_]=component_constructor
    component_taxo_instances_dict[name_]=component_instances
    component_taxo_topologies_dict[name_]=component_topologies

def getPrimitive(name_):
    '''
    Get a SAF microarchitecture primitive taxonomic category description.\n\n

    Arguments:\n
    - name_ -- string id of primitive component.\n\n

    Returns: dict['description','constructor','instances']
    '''
    global primitive_taxo_description_dict
    global primitive_taxo_constructor_dict
    global primitive_taxo_instances_dict

    return {
        'description':primitive_taxo_description_dict[name_],
        'constructor':primitive_taxo_constructor_dict[name_],
        'instances':primitive_taxo_instances_dict[name_]
    }

def getComponent(name_):
    '''
    Get a SAF microarchitecture component taxonomic category description.\n\n

    Arguments:\n
    - name_ -- string id of component.\n\n

    Returns: dict['description','constructor','instances','topologies']
    '''
    global component_taxo_description_dict
    global component_taxo_constructor_dict
    global component_taxo_instances_dict
    global component_taxo_topologies_dict

    return {
        'description':component_taxo_description_dict[name_],
        'constructor':component_taxo_constructor_dict[name_],
        'instances':component_taxo_instances_dict[name_],
        'topologies':component_taxo_topologies_dict[name_],
    }

registerPrimitive('PositionGenerator', \
                  PositionGenerator, \
                  buildPositionGenerator, \
                  pgen_instances)

registerPrimitive('MetadataParser', \
                  MetadataParser, \
                  buildMetadataParser, \
                  md_parser_instances)

registerPrimitive('IntersectionLeaderFollower', \
                  IntersectionLeaderFollower, \
                  buildIntersectionLeaderFollower, \
                  intersection_instances)

registerComponent('FormatUarch', \
                  FormatUarch, \
                  buildFormatUarch, \
                  fmt_uarch_instances, \
                  fmt_uarch_topologies)

registerComponent('SkippingUarch', \
                  SkippingUarch, \
                  buildSkippingUarch, \
                  skipping_uarch_instances, \
                  skipping_uarch_topologies)