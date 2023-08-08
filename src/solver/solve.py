'''SAFinfer solver library - solve SAF microarchitecture inference problem'''
from util.taxonomy.serializableobject import SerializableObject
from solver.rulesets import RuleSet
from util.helper import dirpath_to_import_expression
import os

'''Solver'''
class Solver:
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