# General topology rules

from util.taxonomy.expressions import FormatType

# - Topology validation rules

# -- AssertNetHasConsistentPortNetType: all ports connected by a Net should have a consistent NetType

def assertNetsHaveConsistentPortNetTypes(obj):
    net_list=obj.getTopology().getNetList()

    for net in net_list:
        # For all nets in component topology, ensure consistent port net type
        net_type=None
        for port_id in net.getPortIdList():
            # For all ports connected by net
            port=obj.getPortById(port_id)
            if net_type is None:
                net_type=port.getNetType().getValue()
            else:
                if port.getNetType().getValue() != net_type:
                    # Assertion should fail if nets types don't match
                    return False
    return True


def predicateIsComponentHasNets(obj):
    return type(obj).__name__ == 'Component' and len(obj.getTopology().getNetList())>0
    
#  -- AssertNetHasConsistentPortFormatType: all ports connected by a Net should have a consistent FormatType
#  --- Reuse predicateIsComponentHasNets() from NetHasConsistentPortNetType

def assertNetsHaveConsistentPortFormatTypes(obj):
    net_list=obj.getTopology().getNetList()

    for net in net_list:
        # For all nets in component topology, ensure consistent port net type
        format_type=None
        for port_id in net.getPortIdList():
            # For all ports connected by net
            port=obj.getPortById(port_id)
            if format_type is None:
                format_type=port.getFormatType().getValue()
                print(format_type)
            else:
                if not  FormatType.compareFormatTypes(port.getFormatType(),format_type):                
                    # Assertion should fail if format types don't match                
                    return False

    return True