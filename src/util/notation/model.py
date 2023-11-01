from util.taxonomy.designelement import Primitive, Component, Architecture, Net, FormatType, \
                                        Topology, NetType, Port, SAF
import solver.model.build_support.abstraction as ab_
import util.model.CasCompat as cc_
from util.helper import info,warn,error
import copy,re

characterization_subs_char="#"

'''Buffer action names which are aliases for the same concept'''
std_buffer_action_aliases= {
    "write":["write"],
    "read":["read"],
    "metadata_read":["metadata_read"],
    "metadata_write":["metadata_write"]
}

'''Attribute construction'''
def makeAttribute(expr,foralls=[]):
    if len(foralls)==0:
        return {"expression":expr}
    else:
        attr_={"expression":expr,"foralls":foralls}
        return attr_

'''Constraint construction'''
def makeConstraint(expr,foralls=[]):
    if len(foralls)==0:
        return {"expression":expr}
    else:
        cnst={"expression":expr,"foralls":foralls}
        return cnst

def makePassthroughConstraint(port_a,port_b,foralls=[]):
    return makeConstraint(port_a+" == "+port_b,foralls=foralls)

def makeValuesConstraint(expr,foralls=[],ranges=[]):
    if len(foralls)==0:
        return {"expression":expr,"ranges":ranges}
    else:
        cnst={"expression":expr,"foralls":foralls,"ranges":ranges}
        return cnst

def makeCombosConstraint(attr_list,combos_list):
    return {"attr_list":attr_list,"combos_list":combos_list}

'''Expression evaluation'''
def injectUriPrefix(str_,uri_prefix):
    if len(uri_prefix)>0:
        return str_.replace("@",uri_prefix+".")
    else:
        return str_.replace("@","")

def injectCharacterizationExpressions(str_,characterization_expressions_dict):
    if (characterization_subs_char in str_) and \
        len(characterization_expressions_dict)>0:

        # Define a regex pattern to match #(expression) in the input string
        pattern = r'#\(([^)]+)\)'

        # Function to replace matched pattern with its value from the dictionary
        def replacer(match):
            key = match.group(1)
            return characterization_expressions_dict.get(key, match.group(0))

        # Use re.sub to replace all instances of the pattern in the string
        return re.sub(pattern, replacer, str_)
    elif (characterization_subs_char in str_):
        error('Cannot inject characterization expressions if there are none.')
        info('Terminating.')
        assert(False)

    # Nothing to replace
    return str_

def extractForAllParams(foralls):
    var_=foralls[0][0]
    expr_type=foralls[0][1]
    type_arg=foralls[0][2]
    return var_,expr_type,type_arg

def evalAttributeExpression(attr_,uri_prefix="",args={}):
    base_expr=injectUriPrefix(attr_["expression"],uri_prefix)
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
    base_expr=injectUriPrefix(cnst["expression"],uri_prefix)
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

def listToArgsString(lst):
    res=""
    for idx,elt in enumerate(lst):
        res+=str(elt)
        if idx<len(lst)-1:
            res+=","
    return res

def evalAttributeRangeExpression(expr_,uri_prefix="",args={}):
    base_expr="Contains("+expr_["expression"] + ",FiniteSet($!))"
    base_expr=injectUriPrefix(base_expr,uri_prefix)
    res=[base_expr]
    if "foralls" in expr_:
        res=[]
        var_,expr_type,type_arg=extractForAllParams(expr_["foralls"])
        if expr_type=="attrs":
            for idx,attr_ in enumerate(type_arg):
                range_expr=expr_["ranges"][idx]
                res.append(base_expr.replace("$"+var_,attr_).replace("$!",listToArgsString(range_expr)))
        elif expr_type=="port_thrpt_attrs":
            for idx,attr_ in enumerate(args["port_thrpt_attrs"][type_arg]):
                range_expr=expr_["ranges"][idx]
                res.append(base_expr.replace("$"+var_,attr_).replace("$!",listToArgsString(range_expr)))
    else:
        res=[base_expr.replace("$!",listToArgsString(expr_["ranges"]))]

    return res

def evalAttributeComboExpression(expr_, uri_prefix=""):
    attr_list = [injectUriPrefix(attr_, uri_prefix) for attr_ in expr_["attr_list"]]
    combos_list = expr_["combos_list"]

    and_clauses = []
    for combo_ in combos_list:
        conditions = ' & '.join(["Eq({}, {})".format(attr_, val) for attr_, val in zip(attr_list, combo_)])
        and_clauses.append("And({})".format(conditions))

    or_expr = "Or({})".format(', '.join(and_clauses))

    return [or_expr]

'''
def evalAttributeComboExpression(expr_,uri_prefix=""):
    # {"attr_list":attr_list,"combos_list":combos_list}
    attr_list=[injectUriPrefix(attr_,uri_prefix) for attr_ in expr_["attr_list"]]
    combos_list=expr_["combos_list"]
    res="Piecewise("
    for combo_ in combos_list:
        conds=listToArgsString([attr_ + " == " + str(val) for attr_,val in zip(attr_list,combo_)])
        res += "(True, And("+ conds +")),"
    res+="(False,True))"

    return [res]
'''

def evalObjectiveExpression(expr_,uri_prefix="",metrics_model_expressions_dict={}):
    return injectUriPrefix(injectCharacterizationExpressions(expr_, \
                                                             metrics_model_expressions_dict), \
                           uri_prefix)

'''
class PrimitiveModel:

    def __init__(self):
        self.design_element_type="Primitive"
        self.name_="PrimitiveModel"
        self.attribute_map={}

    def build(self,id):
        pass
'''