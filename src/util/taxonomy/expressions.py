from util.taxonomy.serializableobject import SerializableObject

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

class SolvableConstant(Expression):
    '''Expressions which support holes'''

    def __init__(self):
        pass

class NetType(SolvableConstant):
    '''Net types capture the wire-types (data, metadata, position) in the Efficient Processing taxonomy'''

    def __init__(self):
        pass

class FormatType(SolvableConstant):
    '''Format types capture the representation formats utilized in sparse accelerators'''

    def __init__(self):
        pass