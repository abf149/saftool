'''Miscellaneous combinators'''
import util.notation.predicates as p_

def isCategoryLambda(category):
    return lambda obj: p_.isCategory(obj,category)