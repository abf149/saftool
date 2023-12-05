'''SAFInfer rules library - defines categories of SAF microarchitecture inference rules'''
from core.taxonomy.serializableobject import SerializableObject
from core.taxonomy.expressions import FunctionReference

'''Rules'''
class Rule(SerializableObject):
    '''Base class for a Rule (conditional expression which is evaluated when a predicate is true)'''

    def __init__(self):
        pass

    @classmethod
    def fromIdPredicateConditionallyEvaluatedExpression(cls, id, predicate, conditionally_evaluated_expression):
        '''Create a Rule specifiying the Rule id, predicate, and conditionally-evaluated expression'''

        obj=cls.fromId(id)
        obj.setPredicate(predicate)
        obj.setConditionallyEvaluatedExpression(conditionally_evaluated_expression)
        return obj

    def setPredicate(self, predicate):
        '''Set the FunctionReference object which is the predicate of this rule'''
        self.setAttrAsDict('predicate',predicate)

    def getPredicate(self):
        '''Get the FunctionReference object which is the predicate of this rule'''
        return FunctionReference.fromDict(self.predicate)

    def setConditionallyEvaluatedExpression(self, conditionally_evaluated_expression):
        '''Set the FunctionReference object which is evaluated when the predicate is True'''
        self.setAttrAsDict('conditionally_evaluated_expression',conditionally_evaluated_expression)

    def getConditionallyEvaluatedExpression(self):
        '''Get the FunctionReference object which is evaluated when the predicate is True'''
        return FunctionReference.fromDict(self.conditionally_evaluated_expression)

    def evaluateInModuleContext(self, component, context_module):
        '''Return the result of evaluating the predicate, and conditionally the result of evaluating the conditional expression'''
        result_conditionally_evaluated_expression=None
        result_predicate=self.getPredicate().evaluateInModuleContext(component, context_module)
        if result_predicate:
            result_conditionally_evaluated_expression=self.getConditionallyEvaluatedExpression().evaluateInModuleContext(component, context_module)
        return result_predicate, result_conditionally_evaluated_expression
class ValidationRule(Rule):
    '''Component validation rule with predicate and assertion'''

    def __init__(self):
        pass

    @classmethod
    def fromIdPredicateAssertion(cls, id, predicate, assertion):
        '''Create a ValidationRule specifiying the Rule id, predicate, and assertion for validity'''

        obj=cls.fromId(id)
        obj.setPredicate(predicate)
        obj.setAssertion(assertion)
        return obj    

    def setAssertion(self, assertion):
        '''Set the FunctionReference object which refers to an assertion'''
        self.setConditionallyEvaluatedExpression(assertion)

    def getAssertion(self):
        '''Get the FunctionReference object which refers to an assertion'''
        return self.getConditionallyEvaluatedExpression()
class CompletionRule(Rule):
    '''SAF microarchitecture inference completion rule with predicate and completion criterion'''

    def __init__(self):
        pass

    @classmethod
    def fromIdPredicateCriterion(cls, id, predicate, criterion):
        '''Create a CompletionRule specifying the Rule id, predicate, and completion criterion'''

        obj=cls.fromId(id)
        obj.setPredicate(predicate)
        obj.setCriterion(criterion)
        return obj

    def setCriterion(self, criterion):
        '''Set the FunctionReference object which refers to a completion criterion'''
        self.setConditionallyEvaluatedExpression(criterion)

    def getCriterion(self):
        '''Get the FunctionReference object which refers to a completion criterion'''
        return self.getConditionallyEvaluatedExpression()        
class RewriteRule(Rule):
    '''SAF component rewrite rule'''

    def __init__(self):
        pass

    @classmethod
    def fromIdPredicateTransform(cls, id, predicate, transform):
        '''Create a RewriteRule specifying the Rule id, predicate, and transform'''

        obj=cls.fromId(id)
        obj.setPredicate(predicate)
        obj.setTransform(transform)
        return obj

    def setTransform(self, transform):
        '''Set the FunctionReference object which refers to a transform'''
        self.setConditionallyEvaluatedExpression(transform)

    def getTransform(self):
        '''Get the FunctionReference object which refers to a transform'''
        return self.getConditionallyEvaluatedExpression() 