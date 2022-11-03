from pyclbr import Function
from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *
import importlib
import os, sys

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

class RuleSet(SerializableObject):
    '''Rule engine rule set, comprising one or more different sub-RuleSets (i.e. ValidationRuleSet)'''

    def __init__(self):
        pass

    @classmethod
    def fromIdSubRuleSets(cls, id, validation_rule_set=None):
        '''Init from individual sub-RuleSets'''
        obj=cls.fromId(id)
        if not (validation_rule_set is None):
            obj.setValidationRuleSet(validation_rule_set)
        return obj

    @classmethod
    def importRuleSet(cls, rule_set_path):
        '''Detect a rule set in the provided directory, load the rule set & predicate/conditional code'''
        rule_set_filename=os.path.join(rule_set_path,"rule_set.yaml")

        print('\n- Detecting rule set at',rule_set_path,'\n')
        print('\n-- Importing rule set from',rule_set_filename,'\n')
        rule_set_obj=RuleSet.fromYamlFilename(rule_set_filename)

        print('\n-- Importing rule set context module',os.path.join(rule_set_path,"RuleSetContextModule.py"),'\n')
        old_sys_path=sys.path.copy()
        sys.path.append(rule_set_path)
        rule_set_context_module=importlib.import_module("RuleSetContextModule", package=None)
        sys.path=old_sys_path

        print('\n-- Done importing.\n')

        return rule_set_obj, rule_set_context_module

    def setValidationRuleSet(self, validation_rule_set):
        self.setAttrAsDict('validation_rule_set', validation_rule_set)

    def hasValidationRuleSet(self):
        '''True if RuleSet includes a ValidationRuleSet'''
        return "validation_rule_set" in self.__dict__

    def getValidationRuleSet(self):
        '''Return the ValidationRuleSet in this RuleSet, or None if none exists'''
        if self.hasValidationRuleSet():
            return ValidationRuleSet.fromDict(self.validation_rule_set)
        return None

    def evaluateInModuleContext(self, component, context_module, validate=True):
        '''Evaluate this RuleSet against provided component with imported module as context.'''

        print("\n- Stepping into rule set: ",self.id,"\n")  
        if validate and self.hasValidationRuleSet():
            print("\n-- Test validation rule set. \n")
            validation_rule_set=self.getValidationRuleSet()
            validation_rule_set.evaluateAssertionsInModuleContext(component,context_module)

        print("\n- Exiting rule set: ",self.id,"\n") 


class ValidationRuleSet(RuleSet):
    '''Rule engine ValidationRule set, comprising a list of ValidationRule's '''

    def __init__(self):
        pass

    @classmethod
    def fromIdValidationRules(cls, id, validation_rule_obj_list):
        '''Init from id and a list of ValidationRule's '''
        obj=cls.fromId(id)
        obj.setValidationRules(validation_rule_obj_list)
        return obj

    def setValidationRules(self, validation_rule_obj_list):
        '''Consumes a list of ValidationRule objects, converts to a list of dicts and sets the validation_rules attribute'''
        self.setAttrAsDictList('validation_rules', validation_rule_obj_list)

    def getValidationRules(self):
        '''Converts the validation_rules attribute from a list of dicts to a list of ValidationRule objects, and returns the result'''
        return [ValidationRule.fromDict(validation_rule_dict) for validation_rule_dict in self.validation_rules]

    def evaluateAssertionsInModuleContext(self, component, context_module):
        '''Return the results of evaluating the ValidationRule's in this ValidationRuleSet'''
        
        print("\n-- Stepping into validation rule set: ",self.id,"\n")        
        validation_rule_obj_list=self.getValidationRules()

        for validation_rule in validation_rule_obj_list:
            # Evaluate predicate for each rule & conditionally make an assertion

            result_predicate, result_assertion = validation_rule.evaluateInModuleContext(component, context_module)
            print("--- Validation rule:", self.id, "Predicate:",validation_rule.getPredicate().getValue(),"==",result_predicate)
            if result_predicate:
                # Predicate True; assert
                print("---- Asserting:",validation_rule.getAssertion().getValue())
                assert(result_assertion)
                print("---- => ok.")

        print("\n-- Exiting validation rule set: ",self.id,"\n")

class RulesEngine:
    '''Methods for evaluating microarchitectural validation & transformation rules'''

    def __init__(self, rule_set_dir_path_list):
        '''Rule engine is intialized with a list of paths to rule set directory paths'''
        self.rule_set_dir_path_list=rule_set_dir_path_list

    def preloadRules(self):
        '''From the rule set dir paths provided at initialization, load the rule sets'''
        print('Pre-loading rule sets...')
        self.rule_sets={}
        for rule_set_dir_path in self.rule_set_dir_path_list:
            rule_set_obj, context_module = RuleSet.importRuleSet(rule_set_dir_path)
            self.rule_sets[rule_set_obj.id]={'rule_set_obj':rule_set_obj, 'context_module':context_module}

    def testValidationRules(self, component):
        '''Iterate pre-loaded rule sets and run only the validation rules in each rule set'''
        print('- Running validation tests...')
        for rule_set_name in self.rule_sets:
            # Evaluate RuleSet in context
            self.rule_sets[rule_set_name]['rule_set_obj'].evaluateInModuleContext(component, self.rule_sets[rule_set_name]['context_module'])

    def run(self, component):
        self.testValidationRules(component)
