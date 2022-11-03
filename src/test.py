import os
from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *
from util.taxonomy.rulesengine import *

os.system('rm *test.yaml')

print("\n\n")

# SerializableObject test
print("SerializableObject tests:")

print("\n\n")

print("- SerializableObject initialize, dump, load")
print("-- From Id and Class")
x = SerializableObject.fromIdAndClass('SerializableObjectTest', 'SerializableObject')
print("-- Dump")
x.dump('serializable_object_test.yaml')
print("-- From YAML file")
x = SerializableObject.fromYamlFilename('serializable_object_test.yaml')
print(x)
print("-- From Id, Dump, From YAML file")
x = SerializableObject.fromId('SerializableObjectTest')
x.dump('serializable_object_test.yaml')
x = SerializableObject.fromYamlFilename('serializable_object_test.yaml')
print(x)

print("\n\n")

print("- SerializableObject nesting")
print("-- Child from Id and Class; print")
childObj = SerializableObject.fromIdAndClass('childObj', 'SerializableObject')
print(childObj)
print("-- Parent from Id and Class; print")
parentObj = SerializableObject.fromIdAndClass('parentObj', 'SerializableObject')
print(parentObj)
print("-- Child as child attribute of parent; dump; load from YAMl; print")
parentObj.setAttrAsDict('child',childObj)
parentObj.dump('nested_serializable_object_test.yaml')
x = SerializableObject.fromYamlFilename('nested_serializable_object_test.yaml')
print(x)

print("\n\n")

# Expression & subclass (FunctionReference, SolvableConstant, NetType, FormatType) tests
print("Expression & subclass (FunctionReference, SolvableConstant, NetType, FormatType) tests:")

print("\n\n")

print("- Expression")
print("-- From Id, Dump, From YAML file")
x = Expression.fromId('ExpressionTest')
x.dump('expression_test.yaml')
print("-- Load from YAML file; print")
print(x)
x = Expression.fromYamlFilename('expression_test.yaml')
print("-- From Id+Value('1'), Dump, From YAML file")
x = Expression.fromIdValue('ExpressionTest','1')
x.dump('expression_test.yaml')
print("-- Load from YAML file; print")
x = Expression.fromYamlFilename('expression_test.yaml')
print(x)
print("-- Expression().getValue()")
print(x.getValue())
print("-- Expression().setValue('2'); Expression().getValue()")
print(x.setValue('2'))
print(x.getValue())

print("\n\n")

rule_set_path='saftaxolib/ref_ruleset/'
print('- Test setup: importing rule set context module',os.path.join(rule_set_path,"RuleSetContextModule.py"))
old_sys_path=sys.path.copy()
sys.path.append(rule_set_path)
rule_set_context_module=importlib.import_module("RuleSetContextModule", package=None)
sys.path=old_sys_path

print("\n\n")

print("- FunctionReference")
print("-- From Id+Value('alwaysTrue1','alwaysFalse1'), Dump, From YAML file")
x = FunctionReference.fromIdValue('FunctionReferenceTest','alwaysTrue1')
y = FunctionReference.fromIdValue('FunctionReferenceTest','alwaysFalse1')
x.dump('function_reference_test.yaml')
print("-- Load from YAML file; print")
x = FunctionReference.fromYamlFilename('function_reference_test.yaml')
print(x)
print("-- Evaluate alwaysTrue1:", x.evaluateInModuleContext({}, rule_set_context_module))
print("-- Evaluate alwaysFalse1:", y.evaluateInModuleContext({}, rule_set_context_module))


print("\n\n")

print("- SolvableConstant")
print("-- From Id+Value('1'), Dump, From YAML file")
x = SolvableConstant.fromIdValue('SolvableConstantTest','1')
x.dump('solvable_constant_test.yaml')
print("-- Load from YAML file; print")
x = SolvableConstant.fromYamlFilename('solvable_constant_test.yaml')
print(x)

print("\n\n")

print("- NetType")
print("-- From Id+Value('data'), Dump, From YAML file")
x = NetType.fromIdValue('NetTypeTest','data')
x.dump('net_type_test.yaml')
print("-- Load from YAML file; print")
x = NetType.fromYamlFilename('net_type_test.yaml')
print(x)

print("\n\n")

print("- FormatType")
print("-- From Id+Value('C'), Dump, From YAML file")
x = FormatType.fromIdValue('FormatTypeTest','C')
x.dump('format_type_test.yaml')
print("-- Load from YAML file; print")
x = FormatType.fromYamlFilename('format_type_test.yaml')
print(x)

# RulesEngine & subclasses (Rule, ValidationRule, RuleSet, ValidationRuleSet) tests
print("RulesEngine & subclasses (Rule, ValidationRule, RuleSet, ValidationRuleSet) tests:")

print("\n\n")

print("- Rule")
print("-- From Id+Predicate+Conditionally-evaluated-expression; print")
predicateTrue1=FunctionReference.fromIdValue('predicateTrue1','alwaysTrue1')
predicateTrue2=FunctionReference.fromIdValue('predicateTrue2','alwaysTrue2')
predicateFalse1=FunctionReference.fromIdValue('predicateFalse1','alwaysFalse1')
predicateFalse2=FunctionReference.fromIdValue('predicateFalse2','alwaysFalse2')
x = Rule.fromIdPredicateConditionallyEvaluatedExpression('RuleTest', predicateTrue1, predicateTrue2)
y = Rule.fromIdPredicateConditionallyEvaluatedExpression('RuleTest', predicateFalse1, predicateTrue2)
z = Rule.fromIdPredicateConditionallyEvaluatedExpression('RuleTest', predicateTrue1, predicateFalse2)
q = Rule.fromIdPredicateConditionallyEvaluatedExpression('RuleTest', predicateFalse1, predicateFalse2)
print(x)
print('getPredicate() type:', x.getPredicate().__class__.__name__,'getConditionallyEvaluatedExpression() type:', x.getConditionallyEvaluatedExpression().__class__.__name__)
print("-- Dump to YAML and load")
x.dump('rule_test.yaml')
x = Rule.fromYamlFilename('rule_test.yaml')
print(x)
print("-- Evaluate Rule1:")
pred,asst=x.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)
print("-- Evaluate Rule2:")
pred,asst=y.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)
print("-- Evaluate Rule3:")
pred,asst=z.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)
print("-- Evaluate Rule4:")
pred,asst=q.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)

print("\n\n")

print("- ValidationRule")
print("-- From Id+Predicate+Assertion; print")
x = ValidationRule.fromIdPredicateAssertion('ValidationRuleTest_T->T', predicateTrue1, predicateTrue2)
y = ValidationRule.fromIdPredicateAssertion('ValidationRuleTest_F->T', predicateFalse1, predicateTrue2)
z = ValidationRule.fromIdPredicateAssertion('ValidationRuleTest_T->F', predicateTrue1, predicateFalse2)
q = ValidationRule.fromIdPredicateAssertion('ValidationRuleTest_F->F', predicateFalse1, predicateFalse2)
print(x)
print('getPredicate() type:', x.getPredicate().__class__.__name__,'getConditionallyEvaluatedExpression() type:', x.getAssertion().__class__.__name__)
print("-- Dump to YAML and load")
x.dump('validation_rule_test.yaml')
x = ValidationRule.fromYamlFilename('validation_rule_test.yaml')
print(x)
print("-- Evaluate Rule1:")
pred,asst=x.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)
print("-- Evaluate Rule2:")
pred,asst=y.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)
print("-- Evaluate Rule3:")
pred,asst=z.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)
print("-- Evaluate Rule4:")
pred,asst=q.evaluateInModuleContext({}, rule_set_context_module)
print("--- predicate:",pred,"assert:",asst)

print("\n\n")

print("- ValidationRuleSet")
print("-- From Id+ValidationRule-List; print")
valid_rule_list=[x,y,z,q]
valid_rule_set = ValidationRuleSet.fromIdValidationRules('ValidationRuleSetTest',valid_rule_list)
print(valid_rule_set)
print("-- getValidationRules(); print")
print(valid_rule_set.getValidationRules())
print("-- evaluateAssertionsInModuleContext(); print")
try:
    print(valid_rule_set.evaluateAssertionsInModuleContext({},rule_set_context_module))
except:
    print('----- EXCEPTION: this is expected for false assertions')

print("\n\n")

print("- RuleSet")
print("-- From Id+None Sub RuleSet; print")
rule_set = RuleSet.fromIdSubRuleSets('RuleSetTest')
print(rule_set)
print("-- hasValidationRuleSet; print")
print(rule_set.hasValidationRuleSet())
print("-- From Id+ValidationRuleSet; print")
rule_set = RuleSet.fromIdSubRuleSets('RuleSetTest',valid_rule_set)
print(rule_set)
print("-- hasValidationRuleSet; print")
print(rule_set.hasValidationRuleSet())
print("-- getValidationRuleSet(); print")
print(rule_set.getValidationRuleSet())
print("-- evaluateInModuleContext(validate=False); print")
rule_set.evaluateInModuleContext({},rule_set_context_module,validate=False)
print("-- evaluateInModuleContext(validate=True); print")
try:
    rule_set.evaluateInModuleContext({},rule_set_context_module)
except:
    print('----- EXCEPTION: this is expected for false assertions')

print("\n\n")

print("- RulesEngine")
rule_set_yaml_path=os.path.join(rule_set_path,'rule_set.yaml')
print("-- Prepare experiment: dump rule set YAML to",rule_set_yaml_path)
rule_set.dump(os.path.join(rule_set_path,'rule_set.yaml'))
print("-- From list of rule set dir paths")
rules_engine = RulesEngine([rule_set_path])
print("-- Preload rules")
rules_engine.preloadRules()
print("-- run()")
try:
    rules_engine.run({})
except:
    print('----- EXCEPTION: this is expected for false assertions')