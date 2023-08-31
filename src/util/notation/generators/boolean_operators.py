'''Boolean operators'''

def AND(*funcs):
    '''
    Arguments\n
    - funcs = lambda1(x) -> bool, lambda2(x) -> bool, ... (varargs)\n\n

    Returns:\n
    - lambda(x) -> bool = lambda1(x) AND lambda2(x) AND ...
    '''
    def lmbda(x):
        x=all(f(x) for f in funcs)
        #print("AND:",x)
        return x
    return lmbda
    #return lambda x: all(f(x) for f in funcs)
def OR(*funcs):
    '''
    Arguments\n
    - funcs = lambda1(x) -> bool, lambda2(x) -> bool, ... (varargs)\n\n

    Returns:\n
    - lambda(x) -> bool = lambda1(x) OR lambda2(x) OR ...
    '''
    def lmbda(x):
        x=any(f(x) for f in funcs)
        #print("OR:",x)
        return x

    return lmbda
    #return lambda x: any(f(x) for f in funcs)
def NOT(func):
    '''
    Arguments\n
    - func = lambda(x) -> bool\n\n

    Returns:\n
    - lambda'(x) -> bool = NOT lambda(x) ...
    '''
    return lambda x: not func(x)
def NOR(*funcs):
    '''
    Arguments\n
    - funcs = lambda1(x) -> bool, lambda2(x) -> bool, ... (varargs)\n\n

    Returns:\n
    - lambda(x) -> bool = NOT(lambda1(x) OR lambda2(x) OR ...)
    '''
    return lambda x: not OR(*funcs)(x)
def NAND(*funcs):
    '''
    Arguments\n
    - funcs = lambda1(x) -> bool, lambda2(x) -> bool, ... (varargs)\n\n

    Returns:\n
    - lambda(x) -> bool = NOT(lambda1(x) AND lambda2(x) AND ...)
    '''
    return lambda x: not AND(*funcs)(x)
