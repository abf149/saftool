from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *
from util.helper import dirpath_to_import_expression
import os

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

        print('\n- Detecting rule set at',rule_set_path,'\n')
        print('\n-- Importing rule set from',rule_set_filename,'\n')
        rule_set_obj=RuleSet.fromYamlFilename(rule_set_filename)

        print('\n-- Importing rule set context module',os.path.join(rule_set_path,"RuleSetContextModule.py"),'\n')
        exec_import_command=dirpath_to_import_expression(rule_set_path,'RuleSetContextModule','rule_set_context_module')
        print('--- Performing generated import command: ',exec_import_command)
        exec(exec_import_command)
        print('\n-- Done importing.\n')
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

        print("\n- Stepping into rule set:",self.id,"\n")  

        # Optionally evaluate validate rules
        if validate:
            if self.hasValidationRuleSet():
                print("\n-- Test validate rule set. \n")
                validate_rule_set=self.getValidationRuleSet()
                validate_rule_set.evaluateAssertionsInModuleContext(component,context_module)
            else:
                print("\n-- No validate rule set. \n")
        else:
            print("\n-- Skipping validate rule set, if any.\n")

        # Optionally evaluate rewrite rules
        # TODO

        if rewrite:
            if self.hasRewriteRuleSet():
                print("\n-- Evaluate rewrite rule set.\n")
                rewrite_rule_set=self.getRewriteRuleSet()
                result_rewrite_modify,result_rewrite_component = rewrite_rule_set.evaluateTransformsInModuleContext(component,context_module)             
            else:
                print("\n-- No rewrite rule set. \n")
        else:
            print("\n-- Skipping rewrite rule set, if any.\n")

        # Optionally evaluate check_complete rules
        if check_complete:
            if self.hasCompletionRuleSet():
                print("\n-- Test completion rule set. \n")
                completion_rule_set=self.getCompletionRuleSet()
                result_check_complete=completion_rule_set.evaluateCriteriaInModuleContext(component,context_module)
            else:
                print("\n-- No check_complete rule set. \n")
        else:
            print("\n-- Skipping check_complete rule set, if any.\n")        

        print("\n- Exiting rule set: ",self.id,"\n") 
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
        
        print("\n-- Stepping into validation rule set: ",self.id,"\n")        
        validation_rule_obj_list=self.getValidationRules()

        for validation_rule in validation_rule_obj_list:
            # Evaluate predicate for each rule & conditionally make an assertion

            result_predicate, result_assertion = validation_rule.evaluateInModuleContext(component, context_module)
            print("--- Validation rule:", validation_rule.id, "Predicate:",validation_rule.getPredicate().getValue(),"==",result_predicate)
            if result_predicate:
                # Predicate True; assert
                print("---- Asserting:",validation_rule.getAssertion().getValue())
                assert(result_assertion)
                print("---- => ok.")

        print("\n-- Exiting validation rule set: ",self.id,"\n")


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
        
        print("\n-- Stepping into completion rule set: ",self.getId(),"\n")        
        completion_rule_obj_list=self.getCompletionRules()

        for completion_rule in completion_rule_obj_list:
            # Evaluate predicate for each rule & conditionally evaluate completion criterion

            result_predicate, result_criterion = completion_rule.evaluateInModuleContext(component, context_module)
            print("--- Completion rule:", completion_rule.id, "Predicate:",completion_rule.getPredicate().getValue(),"==",result_predicate)
            if result_predicate:
                # Predicate True; check completion criterion
                print("---- Evaluating:",completion_rule.getCriterion().getValue())
                if result_criterion:
                    print("---- => Completion rule PASSED.")
                else:
                    print("---- => Completion rule FAILED!")
                    print("\n-- Completion ruleset FAILED:",self.getId(),"\n")
                    print("\n-- Exiting completion rule set: ",self.getId(),"\n")
                    return False
                

        print("\n-- Completion ruleset PASSED:",self.getId(),"\n")
        print("\n-- Exiting completion rule set: ",self.getId(),"\n")    

        return True

class RewriteRuleSet(RuleSet):
    '''Rule engine RewriteRule set, comprising a list of RewriteRule's '''

    def __init__(self):
        pass

    @classmethod
    def fromIdRewriteRules(cls, id, rewrite_rule_obj_list):
        '''Init from id and a list of RewriteRule's '''
        obj=cls.fromId(id)
        obj.setRewriteRules(rewrite_rule_obj_list)
        return obj

    def setRewriteRules(self, rewrite_rule_obj_list):
        '''Consumes a list of CompletionRule objects, converts to a list of dicts and sets the completion_rules attribute'''
        self.setAttrAsDictList('rewrite_rules', rewrite_rule_obj_list)

    def getRewriteRules(self):
        '''Converts the rewrite_rules attribute from a list of dicts to a list of RewriteRule objects, and returns the result'''
        return [RewriteRule.fromDict(rewrite_rule_dict) for rewrite_rule_dict in self.rewrite_rules]

    def evaluateTransformsInModuleContext(self, component, context_module):
        '''Return the results of evaluating the RewriteRule's in this RewriteRuleSet'''
        
        print("\n-- Stepping into rewrite rule set: ",self.getId(),"\n")        
        rewrite_rule_obj_list=self.getRewriteRules()

        rewrite_modify=False
        rewrite_component=component

        for rewrite_rule in rewrite_rule_obj_list:
            # Evaluate predicate for each rule & conditionally evaluate transform

            rewrite_modify, rewrite_component = rewrite_rule.evaluateInModuleContext(component, context_module)
            print("--- Rewrite rule:", rewrite_rule.getId(), "Predicate:",rewrite_rule.getPredicate().getValue(),"==",rewrite_modify)
            if rewrite_modify:
                # Predicate True; evaluate rewrite 

                print("---- Evaluating:",rewrite_rule.getTransform().getValue())

                if rewrite_modify:
                    print("---- => did REWRITE!")
                    print("\n-- Rewrite ruleset evaluated WITH rewrites:",self.getId(),"\n")
                    print("\n-- Exiting rewrite rule set: ",self.getId(),"\n")
                    return True, rewrite_component                    
                else:
                    print("---- => No rewrite.")                    

        print("\n-- Rewrite ruleset evaluated with NO rewrites:",self.getId(),"\n")
        print("\n-- Exiting rewrite rule set: ",self.getId(),"\n")    

        return False, component

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

    def evaluateRuleSet(self, component, validate=False, rule_type='validate', recurse=True):
        '''Iterate pre-loaded rule sets and run only the validation rules in each rule set, optionally with recursion'''

        validate=False
        rewrite=False
        check_complete=False
        if rule_type=='validate':
            validate=True
        if rule_type=='rewrite':
            rewrite=True
        if rule_type=='check_complete':
            check_complete=True

        result_dict={'result_validate':True,'result_rewrite_modify':False,"result_rewrite_component":component,'result_check_complete':True}

        print('- Evaluating',rule_type,'tests against component',component.getId(),'...')
        for rule_set_name in self.rule_sets:
            # Evaluate RuleSet in context
            rule_set_result_dict=self.rule_sets[rule_set_name]['rule_set_obj'].evaluateInModuleContext(component, self.rule_sets[rule_set_name]['context_module'], validate=validate, rewrite=rewrite, check_complete=check_complete)
            result_dict['result_validate']=result_dict['result_validate'] and rule_set_result_dict['result_validate']
            result_dict['result_check_complete']=result_dict['result_check_complete'] and rule_set_result_dict['result_check_complete']
            if not result_dict['result_check_complete']:
                return result_dict
            if rule_type=='rewrite' and rule_set_result_dict['result_rewrite_modify']:
                result_dict['result_rewrite_modify']=True
                result_dict['result_rewrite_component']=rule_set_result_dict['result_rewrite_component']
                print('result_rewrite_modify',result_dict)
                return result_dict

        if component.getClassType()!='Primitive' and recurse and not(rule_type=='check_complete' and not result_dict['result_check_complete']):
            # Recurse against all subcomponents (unless this component is a primitive!)
            print('\n- STARTING: recurse against subcomponents of',component.getId(),'\n')
            topology=component.getTopology()
            comp_list=topology.getComponentList()
            for idx in range(len(comp_list)):
                subcomponent=comp_list[idx]
                print('\n-- STARTING: recurse against subcomponent',subcomponent.getId(),'\n')
                recursive_result_dict=self.evaluateRuleSet(subcomponent, rule_type=rule_type, recurse=recurse)
                result_dict['result_validate']=result_dict['result_validate'] and recursive_result_dict['result_validate']
                result_dict['result_check_complete']=result_dict['result_check_complete'] and recursive_result_dict['result_check_complete']   
                if not result_dict['result_check_complete']:
                    return result_dict       
                if rule_type=='rewrite' and recursive_result_dict['result_rewrite_modify']:
                    result_dict['result_rewrite_modify']=True
                    comp_list[idx]=recursive_result_dict['result_rewrite_component']
                    topology.setComponentList(comp_list)
                    component.setTopology(topology)
                    result_dict['result_rewrite_component']=component

                    #print('result_rewrite_modify',result_dict['result_rewrite_component'].getTopology().getComponentList()[0].getAttributes())
                    return result_dict                                         
            print('\n- DONE: recurse against subcomponents of',component.getId(),'\n')

#        print('\n- DONE: validation\n')
        return result_dict

    def runSMPass(self, component, recurse=True):
        '''One pass of the microarchitecture inference state machine entails validation, rewrite, and completion criteria check'''

        # Validation step
        self.evaluateRuleSet(component, rule_type='validate', recurse=recurse)

        # Rewrite step
        result_rewrite_modify=False
        result_rewrite_component=component
        result_dict=self.evaluateRuleSet(component, rule_type='rewrite', recurse=recurse)
        print('result_rewrite_modify',result_dict)
        result_rewrite_modify=result_dict['result_rewrite_modify']
        result_rewrite_component=result_dict['result_rewrite_component']     

        # Check-completion step
        result_dict=self.evaluateRuleSet(component, rule_type='check_complete', recurse=recurse)
        result_check_complete=result_dict['result_check_complete']


        if result_check_complete:
            # Completed microarchitecture inference
            return 'complete', result_rewrite_component
        elif (not result_check_complete) and result_rewrite_modify:
            # Validate the partial microarchitecture produced by this pass
            return 'doValidate', result_rewrite_component
        elif not (result_check_complete or result_rewrite_modify):
            # Microarchitecture is valid but cannot be completely inferred; error
            return 'error', result_rewrite_component

    def run(self, component, recurse=True, max_sm_passes=100):
        # Wrapper for multiple passes of (optionally-)recursive rule evaluation against the provided component and its subcomponents

        rule_engine_sm_pass_count=0
        next_sm_state='doValidate'
        component_iterations=[component]
        res=False

        print('\nSTARTING: rule engine  \n')

        while(next_sm_state=='doValidate' and rule_engine_sm_pass_count < max_sm_passes):
            print('\n- STARTING: state-machine pass',rule_engine_sm_pass_count,'\n')
            next_sm_state, component=self.runSMPass(component, recurse=recurse)
            component_iterations.append(component)
            print('\n- DONE: state-machine pass',rule_engine_sm_pass_count,'\n')
            rule_engine_sm_pass_count += 1            

        if next_sm_state=='complete':
            print('\n- COMPLETE: microarchitecture inference\n')
            res=True
        else:
            print('\n- ERROR: could not infer microarchitecture\n')
            res=False

        print('\nDONE: rule engine \n')
        return res, component_iterations