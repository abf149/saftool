from core.taxonomy.serializableobject import SerializableObject
from core.helper import info,warn,error


class Expression(SerializableObject):
    '''Base class for expressions'''

    def __init__(self):
        pass

    @classmethod
    def fromIdValue(cls, id, valueParam):
        '''Factory method for expression from value'''

        obj=cls.fromId(id)
        obj.setValue(valueParam)
        return obj

    def getValue(self):
        return self.value

    def setValue(self, valueParam):
        self.value=valueParam

class FunctionReference(Expression):
    '''References an executable Python function'''

    def __init__(self):
        pass

    def evaluateInModuleContext(self, fxn_arg, context_module):
        '''Dereference and evaluate the function in the context of an imported module; currently only a single argument is supported'''
        fxn = getattr(context_module, self.value)
        return fxn(fxn_arg)

class SolvableConstant(Expression):
    '''Expressions which support unknown values'''

    def __init__(self):
        pass

    def isUnknown(self):
        '''SolvableConstants can be unknown, this method returns True for unknown'''
        return self.getValue()=='?'

class NetType(SolvableConstant):
    '''Net types capture the wire-types (data, metadata, position) in the Efficient Processing taxonomy'''

    def __init__(self):
        pass

class FormatType(SolvableConstant):
    '''Format types capture the representation formats utilized in sparse accelerators'''

    def __init__(self):
        pass

    @classmethod
    def compareFormatTypes(cls, format_type_0, format_type_1, unknowns_wild=True):
        '''Compare two FormatTypes or format type strings for equality; unknowns are wildcards for comparison unless otherwise specified.'''

        # If either format type argument is a string, convert to FormatType
        if type(format_type_0).__name__ == 'str':
            format_type_0=FormatType.fromIdValue('format_type_0',format_type_0)
        if type(format_type_1).__name__ == 'str':
            format_type_1=FormatType.fromIdValue('format_type_1',format_type_1)

        #print(format_type_0)
        #print(format_type_1)

        if format_type_1 is None or format_type_0 is None:
            error("While comparing format values for equality, detected a None-valued format. One possible cause for this error is if a positional (pos) port is declared without a default format, i.e. \"- output: pos_out(pos)\"; one possible fix for this is to assign a default format type, i.e. \"- output: pos_out(pos)=addr\", although this is not necessarily the root cause.",also_stdout=True)
            info("- Additional info:")
            info("- format_type_0:",format_type_0)
            info("- format_type_1:",format_type_1)
            info("- unknowns_wild:",unknowns_wild)
            info("Terminating.")
            assert(False)

        if unknowns_wild and (format_type_0.getValue() == '?' or format_type_1.getValue() == '?'):
            # Implement unknowns wild
            return True
        return format_type_0.getValue() == format_type_1.getValue()
