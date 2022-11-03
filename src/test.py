import os
from util.taxonomy.serializableobject import SerializableObject
from util.taxonomy.expressions import *

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

print("- FunctionReference")
print("-- From Id+Value('TestPredicate'), Dump, From YAML file")
x = FunctionReference.fromIdValue('FunctionReferenceTest','TestPredicate')
x.dump('function_reference_test.yaml')
print("-- Load from YAML file; print")
x = FunctionReference.fromYamlFilename('function_reference_test.yaml')
print(x)

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
x = FormatType.fromIdValue('FormatTypeTest','data')
x.dump('format_type_test.yaml')
print("-- Load from YAML file; print")
x = FormatType.fromYamlFilename('format_type_test.yaml')
print(x)