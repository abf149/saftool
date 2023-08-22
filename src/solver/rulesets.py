'''SAFInfer rulesets library - wrappers for collections of categorically similar SAF microarchitecture inference rules'''
from solver.rules import ValidationRule, RewriteRule, CompletionRule
from util.taxonomy.serializableobject import SerializableObject
from util.helper import dirpath_to_import_expression, info, warn, error
import os

'''RuleSets'''
class RuleSet(SerializableObject):
    '''Rule engine rule set, comprising one or more different sub-RuleSets (i.e. ValidationRuleSet, CompletionRuleSet)'''

    def __init__(self):
        pass

    @classmethod
    def fromIdSubRuleSets(cls, id, validation_rule_set=None, rewrite_rule_set=None, completion_rule_set=None):
        '''Init from individual sub-RuleSets'''
        obj=cls.fromId(id)
        if validation_rule_set is not None:
            obj.setValidationRuleSet(validation_rule_set)
        if rewrite_rule_set is not None:
            obj.setRewriteRuleSet(rewrite_rule_set)            
        if completion_rule_set is not None:
            obj.setCompletionRuleSet(completion_rule_set)
        return obj

    @classmethod
    def importRuleSet(cls, rule_set_path):
        '''Detect a rule set in the provided directory, load the rule set & predicate/conditional code'''
        rule_set_filename=os.path.join(rule_set_path,"rule_set.yaml")

        info('- Detecting rule set at',rule_set_path)
        info('-- Importing rule set from',rule_set_filename,'')
        rule_set_obj=RuleSet.fromYamlFilename(rule_set_filename)

        info('-- Importing rule set context module',os.path.join(rule_set_path,"RuleSetContextModule.py"),'')
        exec_import_command=dirpath_to_import_expression(rule_set_path,'RuleSetContextModule','rule_set_context_module')
        info('--- Performing generated import command: ',exec_import_command)
        exec(exec_import_command)
        info('-- Done importing.')
        return rule_set_obj, rule_set_context_module #rule_set_context_module is loaded by exec() above

    def setValidationRuleSet(self, validation_rule_set):
        '''Set the ValidationRuleSet sub-RuleSet associated with this RuleSet'''
        self.setAttrAsDict('validation_rule_set', validation_rule_set)

    def hasValidationRuleSet(self):
        '''True if RuleSet includes a ValidationRuleSet'''
        return "validation_rule_set" in self.__dict__

    def getValidationRuleSet(self):
        '''Return the ValidationRuleSet in this RuleSet, or None if none exists'''
        if self.hasValidationRuleSet():
            return ValidationRuleSet.fromDict(self.validation_rule_set)
        return None

    def setRewriteRuleSet(self, rewrite_rule_set):
        '''Set the RewriteRuleSet sub-RuleSet associated with this RuleSet'''
        self.setAttrAsDict('rewrite_rule_set', rewrite_rule_set)

    def hasRewriteRuleSet(self):
        '''True if RuleSet includes a RewriteRuleSet'''
        return "rewrite_rule_set" in self.__dict__

    def getRewriteRuleSet(self):
        '''Return the RewriteRuleSet in this RuleSet, or None if none exists'''
        if self.hasRewriteRuleSet():
            return RewriteRuleSet.fromDict(self.rewrite_rule_set)
        return None

    def setCompletionRuleSet(self, completion_rule_set):
        '''Set the CompletionRuleSet sub-RuleSet associated with this RuleSet'''
        self.setAttrAsDict('completion_rule_set', completion_rule_set)

    def hasCompletionRuleSet(self):
        '''True if RuleSet includes a CompletionRuleSet'''
        return "completion_rule_set" in self.__dict__

    def getCompletionRuleSet(self):
        '''Return the CompletionRuleSet in this RuleSet, or None if none exists'''
        if self.hasCompletionRuleSet():
            return CompletionRuleSet.fromDict(self.completion_rule_set)
        return None        

    def evaluateInModuleContext(self, component, context_module, validate=False, rewrite=False, check_complete=False):
        '''Evaluate this RuleSet against provided component with imported module as context.'''

        result_validate=True
        result_rewrite_modify=False
        result_rewrite_component=component
        result_check_complete=True

        info("- Stepping into rule set:",self.id,"")  

        # Optionally evaluate validate rules
        if validate:
            if self.hasValidationRuleSet():
                info("-- Test validate rule set. ")
                validate_rule_set=self.getValidationRuleSet()
                validate_rule_set.evaluateAssertionsInModuleContext(component,context_module)
            else:
                info("-- No validate rule set. ")
        else:
            warn("-- Skipping validate rule set, if any.")

        # Optionally evaluate rewrite rules
        # TODO

        if rewrite:
            if self.hasRewriteRuleSet():
                info("-- Evaluate rewrite rule set.")
                rewrite_rule_set=self.getRewriteRuleSet()
                result_rewrite_modify,result_rewrite_component = rewrite_rule_set.evaluateTransformsInModuleContext(component,context_module)             
            else:
                info("-- No rewrite rule set. ")
        else:
            warn("-- Skipping rewrite rule set, if any.")

        # Optionally evaluate check_complete rules
        if check_complete:
            if self.hasCompletionRuleSet():
                info("-- Test completion rule set. ")
                completion_rule_set=self.getCompletionRuleSet()
                result_check_complete=completion_rule_set.evaluateCriteriaInModuleContext(component,context_module)
            else:
                info("-- No check_complete rule set. ")
        else:
            warn("-- Skipping check_complete rule set, if any.")        

        info("- Exiting rule set: ",self.id,"") 
        return {"result_validate":result_validate,"result_rewrite_modify":result_rewrite_modify,"result_rewrite_component":result_rewrite_component,"result_check_complete":result_check_complete}
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
        
        info("-- Stepping into validation rule set: ",self.id,"")        
        validation_rule_obj_list=self.getValidationRules()

        for validation_rule in validation_rule_obj_list:
            # Evaluate predicate for each rule & conditionally make an assertion

            result_predicate, result_assertion = validation_rule.evaluateInModuleContext(component, context_module)
            info("--- Validation rule:", validation_rule.id, "Predicate:",validation_rule.getPredicate().getValue(),"==",result_predicate)
            if result_predicate:
                # Predicate True; assert
                info("---- Asserting:",validation_rule.getAssertion().getValue())
                if result_assertion:
                    info("---- => ok.")                    
                else:
                    error("---- => Validation rule FAILED!:",validation_rule.id,also_stdout=True)
                    error("----- Component:",component.getId(),"category:",component.getCategory(),also_stdout=True)
                    error(str(component),also_stdout=True)
                    error("-- Validation ruleset FAILED!:",self.getId(),"",also_stdout=True)
                    error("-- Exiting completion rule set: ",self.getId(),"",also_stdout=True)
                    error("- Terminating.",also_stdout=True)
                    assert(False)
     

        info("-- Exiting validation rule set: ",self.id,"")
class CompletionRuleSet(RuleSet):
    '''Rule engine CompletionRule set, comprising a list of CompletionRule's '''

    def __init__(self):
        pass

    @classmethod
    def fromIdCompletionRules(cls, id, completion_rule_obj_list):
        '''Init from id and a list of ValidationRule's '''
        obj=cls.fromId(id)
        obj.setCompletionRules(completion_rule_obj_list)
        return obj

    def setCompletionRules(self, completion_rule_obj_list):
        '''Consumes a list of CompletionRule objects, converts to a list of dicts and sets the completion_rules attribute'''
        self.setAttrAsDictList('completion_rules', completion_rule_obj_list)

    def getCompletionRules(self):
        '''Converts the completion_rules attribute from a list of dicts to a list of CompletionRule objects, and returns the result'''
        return [CompletionRule.fromDict(completion_rule_dict) for completion_rule_dict in self.completion_rules]

    def evaluateCriteriaInModuleContext(self, component, context_module):
        '''Return the results of evaluating the CompletionRule's in this CompletionRuleSet'''
        
        info("-- Stepping into completion rule set: ",self.getId(),"")        
        completion_rule_obj_list=self.getCompletionRules()

        for completion_rule in completion_rule_obj_list:
            # Evaluate predicate for each rule & conditionally evaluate completion criterion

            result_predicate, result_criterion = completion_rule.evaluateInModuleContext(component, context_module)
            info("--- Completion rule:", completion_rule.id, "Predicate:",completion_rule.getPredicate().getValue(),"==",result_predicate)
            if result_predicate:
                # Predicate True; check completion criterion
                info("---- Evaluating:",completion_rule.getCriterion().getValue())
                if result_criterion:
                    info("---- => Completion rule PASSED.")
                else:
                    error("---- => Completion rule FAILED!",completion_rule.id)
                    error("----- Component:",component.getId(),"category:",component.getCategory())
                    #error(str(component))
                    error("-- Completion ruleset FAILED:",self.getId(),"")
                    info("-- Exiting completion rule set: ",self.getId(),"")
                    return False
                

        info("-- Completion ruleset PASSED:",self.getId(),"")
        info("-- Exiting completion rule set: ",self.getId(),"")    

        return True
class RewriteRuleSet(RuleSet):
    '''Rule engine RewriteRule set, comprising a list of RewriteRule's '''

    def __init__(self):
        pass

    @classmethod
    def fromIdRewriteRules(cls, id, rewrite_rule_obj_list):
        '''Init from id and a list of RewriteRule's '''
        print("rewrite_rule_obj_list:",rewrite_rule_obj_list)
        obj=cls.fromId(id)
        obj.setRewriteRules(rewrite_rule_obj_list)
        return obj

    def setRewriteRules(self, rewrite_rule_obj_list):
        '''Consumes a list of RewriteRule objects, converts to a list of dicts and sets the rewrite_rules attribute'''
        self.setAttrAsDictList('rewrite_rules', rewrite_rule_obj_list)

    def getRewriteRules(self):
        '''Converts the rewrite_rules attribute from a list of dicts to a list of RewriteRule objects, and returns the result'''
        return [RewriteRule.fromDict(rewrite_rule_dict) for rewrite_rule_dict in self.rewrite_rules]

    def evaluateTransformsInModuleContext(self, component, context_module):
        '''Return the results of evaluating the RewriteRule's in this RewriteRuleSet'''
        
        info("-- Stepping into rewrite rule set: ",self.getId(),"")        
        rewrite_rule_obj_list=self.getRewriteRules()

        rewrite_modify=False
        rewrite_component=component

        for rewrite_rule in rewrite_rule_obj_list:
            # Evaluate predicate for each rule & conditionally evaluate transform

            rewrite_modify, rewrite_component = rewrite_rule.evaluateInModuleContext(component, context_module)
            info("--- Rewrite rule:", rewrite_rule.getId(), "Predicate:",rewrite_rule.getPredicate().getValue(),"==",rewrite_modify)
            if rewrite_modify:
                # Predicate True; evaluate rewrite 

                info("---- Evaluating:",rewrite_rule.getTransform().getValue())

                if rewrite_modify:
                    info("\n\n---- => did REWRITE!\n\n")
                    info("-- Rewrite ruleset evaluated WITH rewrites:",self.getId(),"")
                    info("-- Exiting rewrite rule set: ",self.getId(),"")
                    return True, rewrite_component                    
                else:
                    info("---- => No rewrite.")                    

        info("-- Rewrite ruleset evaluated with NO rewrites:",self.getId(),"")
        info("-- Exiting rewrite rule set: ",self.getId(),"")    

        return False, component