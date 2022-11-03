from util.taxonomy.serializableobject import SerializableObject
import importlib
import os, sys

class Rule(serializableobject):
    '''Base class for component rule which is evaluated when a predicate is true'''

    def __init__(self):
        pass

    def getPredicate(self):
        return self.predicate

class ValidationRule(serializableobject):
    '''Component validation rule with predicate and assertion'''

    def __init__(self):
        pass

class RuleSet(serializableobject):
    '''Rule engine rule set'''

    def __init__(self):
        pass

    @classmethod
    def fromYamlFilename(cls, fname):
        '''Init from YAML file'''
        obj=RuleSet()
        obj.dict2obj(cls.yaml2dict(fname))
        return obj

    def hasValidationRuleSet(self):
        return "validation_ruleset" in self.__dict__

class ValidationEngine:
    '''Methods for validating component correctness'''
    @classmethod
    def validateComponent(component, rule_set_root_path):
        '''Load the ruleset at ruleset_root_path and validate the component against the rules'''

        # Add rule predicate and assert clauses to Python path
        old_sys_path=sys.path.copy()
        sys.path.append(rule_set_root_path)

        # Load validation ruleset
        rule_set_filepath=os.path.join(rule_set_root_path,'ruleset.yaml')
        rule_set=serializableobject.fromYamlFilename(rule_set_filepath)
        validation_ruleset = rule_set.validation_ruleset

        for validation_rule_obj in validation_ruleset.rules:
            # For each validation rule, assert that the validation rule Python module exists, then import it
            assert(importlib.find_loader(validation_rule_obj.mod_name) is not None)
            validation_rule=importlib.import_module(validation_rule_obj.mod_name, package=None)

            

        # Reset Python path
        sys.path=old_sys_path
