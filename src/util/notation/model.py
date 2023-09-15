from util.taxonomy.designelement import Primitive, Component, Architecture, Net, FormatType, \
                                        Topology, NetType, Port, SAF
import solver.model.build_support.abstraction as ab_
from util.helper import info,warn,error
import copy

#"clock",("real",(0.05, 10.0))
def makeAttribute(expr,foralls=[]):
    if len(foralls)==0:
        return {"expression":expr}
    else:
        attr_={"expression":expr,"foralls":foralls}
        return attr_

def makeConstraint(expr,foralls=[]):
    if len(foralls)==0:
        return {"expression":expr}
    else:
        cnst={"expression":expr,"foralls":foralls}
        return cnst

def makePassthroughConstraint(port_a,port_b,foralls=[]):
    return makeConstraint(port_a+" == "+port_b,foralls=foralls)

def injectUriPrefix(str_,uri_prefix):
    return str_["expression"].replace("@",uri_prefix+".")

def extractForAllParams(foralls):
    var_=foralls[0][0]
    expr_type=foralls[0][1]
    type_arg=foralls[0][2]
    return var_,expr_type,type_arg

def evalAttributeExpression(attr_,uri_prefix="",args={}):
    base_expr=injectUriPrefix(attr_,uri_prefix)
    res=[base_expr]
    if "foralls" in attr_:
        res=[]
        var_,attr_type,type_arg=extractForAllParams(attr_["foralls"])
        if attr_type=="attrs":
            for attr_suffix in type_arg:
                res.append(base_expr.replace("$"+var_,attr_suffix))
        elif attr_type=="port_thrpt_attrs":
            for attr_suffix in args["port_thrpt_attrs"][type_arg]:
                res.append(base_expr.replace("$"+var_,attr_suffix))

    return res

def evalConstraintExpression(cnst,uri_prefix="",args={}):
    base_expr=injectUriPrefix(cnst,uri_prefix)
    res=[base_expr]
    if "foralls" in cnst:
        res=[]
        var_,cnst_type,type_arg=extractForAllParams(cnst["foralls"])
        if cnst_type=="attrs":
            for attr_ in type_arg:
                res.append(base_expr.replace("$"+var_,attr_))
        elif cnst_type=="port_thrpt_attrs":
            for attr_ in args["port_thrpt_attrs"][type_arg]:
                res.append(base_expr.replace("$"+var_,attr_))
    return res

'''
class PrimitiveModel:

    def __init__(self):
        self.design_element_type="Primitive"
        self.name_="PrimitiveModel"
        self.attribute_map={}

    def build(self,id):
        pass
'''