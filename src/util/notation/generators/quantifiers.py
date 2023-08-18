'''Logical quantifiers and comparators over object and sub-object fields'''
from itertools import groupby

'''For loop lambdas'''

'''
def groupByForGen(iter_func, eval_func, compareTo=lambda x,y:x==y, initial=None, pass_loop_state=False):

    def groupByFor(obj):
    iter_ = iter_func(obj)
    if pass_loop_state:
        return groupby([eval_func(x,loop_state) for x in iter_func(obj)], key=compareTo)
    else:
        return groupby([eval_func(x) for x in iter_func(obj)], key=compareTo)

def nGroupGen(func,n=1):
    return 
'''

'''Comparator over net ports'''
def sameForNetPorts(attr_, comparator=lambda x,y:x==y):
    '''
    Returns a lambda function that checks if an attribute getter has the same value for all ports in a net.\n\n

    Arguments\n
    - attr_ = lambda1(x,x_type) -> value where x is of type described by x_type\n
    - comparator = f(attr_value1,attr_value2) -> bool which tells if the values are equal\n\n

    Returns:\n
    - lambda(x,obj) -> bool, x is net
    '''
    def check_all_ports_for_net(net,loop_state):

        net_type = None
        for port_id in net.getPortIdList():
            port = loop_state['obj'].getPortById(port_id)  # Assuming this method exists in the net object
            if net_type is None:
                net_type = attr_(port, "port")
            else:
                if not comparator(attr_(port, "port"), net_type):
                    return False
        return True

    return check_all_ports_for_net
'''Quantifiers over object nets'''
def anyForObjNets(predicate, passObj=False):
    '''
    Returns a lambda function that checks if a predicate is true for any nets in an object.\n\n

    Arguments\n
    - predicate = lambda1(x) -> bool or lambda1(x,obj) -> bool\n
    - passObj -- if true, predicate = lambda1(x,obj)\n\n

    Returns:\n
    - lambda(x) -> bool
    '''
    def check_all_nets_for_obj(obj):
        net_list = obj.getTopology().getNetList()
        for net in net_list:
            if predicate(net):
                return True
        return False
    def check_all_nets_for_obj_pass_obj(obj):
        net_list = obj.getTopology().getNetList()
        for net in net_list:
            if predicate(net,{'obj':obj,'net':net}):
                return True
        return False
    if passObj:
        return check_all_nets_for_obj_pass_obj
    else:
        return check_all_nets_for_obj
def allForObjNets(predicate, passObj=False):
    '''
    Returns a lambda function that checks if a predicate is true for all nets in an object.\n\n

    Arguments\n
    - predicate = lambda1(x) -> bool or lambda1(x,obj) -> bool\n
    - passObj -- if true, predicate = lambda1(x,obj)\n\n

    Returns:\n
    - lambda(x) -> bool
    '''
    def check_all_nets_for_obj(obj,loop_state={}):
        net_list = obj.getTopology().getNetList()
        return all(predicate(net) for net in net_list)
    def check_all_nets_for_obj_pass_obj(obj,loop_state={}):
        net_list = obj.getTopology().getNetList()
        new_loop_state={**loop_state}
        new_loop_state['obj']=obj       
        return all(predicate(net,{'net':net,**new_loop_state}) for net in net_list)
    if passObj:
        return check_all_nets_for_obj_pass_obj
    else:
        return check_all_nets_for_obj
'''Quantifiers over object ports'''
def anyForObjPorts(predicate, passObj=False):
    '''
    Returns a lambda function that checks if a predicate is true for all ports of an object.\n\n

    Arguments\n
    - predicate = lambda1(x) -> bool, x is an attribute\n\n

    Returns:\n
    - lambda(x) -> bool, x is an object
    '''     
    def any_lmbd(obj,loop_state={}):
        for port in obj.getInterface():
            if predicate(port):
                # Break if predicate==True for any port
                return True
        return False

    def any_lmbd_pass_obj(obj,loop_state={}):
        new_loop_state={**loop_state}

        if 'obj' in new_loop_state:
            for port in loop_state['obj'].getInterface():
                if predicate(port,{'port':port,**new_loop_state}):
                    # Break if predicate==True for any port
                    return True
        else:
            new_loop_state['obj']=obj
            for port in obj.getInterface():
                if predicate(port,{'port':port,**new_loop_state}):
                    # Break if predicate==True for any port
                    return True            

        return False                

    if passObj:
        return any_lmbd_pass_obj
    else:
        return any_lmbd
    #return lambda obj: any(predicate(port) for port in obj.getInterface())
'''Quantifiers over object attributes'''
def anyForObjAttributes(predicate):
    '''
    Returns a lambda function that checks if a predicate is true for all attributes of an object.\n\n

    Arguments\n
    - predicate = lambda1(x) -> bool, x is an attribute\n\n

    Returns:\n
    - lambda(x) -> bool, x is an object
    '''    
    def any_lmbd(obj):
        for att in obj.getAttributes():
            if predicate(att):
                # Break if predicate==True for any port
                return True
        return False

    return any_lmbd

'''Quantifiers over object subcomponents'''
def anyForObjComponents(predicate):
    '''
    '''
    def any_lmbd(obj):
        for comp in obj.getTopology().getComponentList():
            if predicate(comp):
                # Break if predicate==True for any port
                return True
        return False

    return any_lmbd

'''Convenient compound quantifiers'''
def forObjNetsForNetPorts(outer,inner,func,comparator=lambda x,y:x==y):
    '''
    Returns a lambda function that quantifies over object nets and
    net ports, applying the specified conditions to the inner and
    outer predicates to determine the return value.\n\n

    Arguments\n
    - outer -- quantifier over object nets; "all" - true if all(predicate) over object nets\n
    - inner -- quantifier over net ports; "same" - true if func value is the same over net ports\n
    - func = (attribute getter) lambda1(x,x_type) -> value where x is of type described by x_type\n\n

    Returns:\n
    - (if outer quantifier is "all") bool
    '''    
    func_outer=allForObjNets
    func_inner=sameForNetPorts

    if inner=="same":
        # Generate inner-loop predicate
        func_inner=sameForNetPorts(func,comparator)
    else:
        print("Invalid inner loop condition generator",inner,"in forObjNetsForNetPorts()")
        assert(False)

    if outer=="all":
        # Return predicate
        return allForObjNets(func_inner,passObj=True)
    elif outer=="any":
        # Return predicate
        return anyForObjNets(func_inner,passObj=True)        
    else:
        print("Invalid outer loop condition generator",outer,"in forObjNetsForNetPorts()")
        assert(False)

def forObjNetsForObjPorts(outer,inner,func,cond_outer=True,cond_inner=True,comparator=lambda x,y:x==y):
    func_outer=allForObjNets
    func_inner=anyForObjPorts

    if inner=="any":
        # Generate inner-loop predicate
        func_inner=anyForObjPorts(func,passObj=True)
    else:
        print("Invalid inner loop condition generator",inner,"in forObjNetsForObjPorts()")
        assert(False)

    if outer=="any":
        # Return predicate
        return anyForObjNets(func_inner,passObj=True)        
    else:
        print("Invalid outer loop condition generator",outer,"in forObjNetsForObjPorts()")
        assert(False)


        
