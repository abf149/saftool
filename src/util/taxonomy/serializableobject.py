import yaml
import sys

class SerializableObject:
    '''
    YAML-serializable object
    '''

    def __init__(self):
        pass

    @classmethod
    def fromId(cls, idParam):
        '''Init from id and class name'''   
        return cls.fromIdAndClass(idParam, cls.__name__) 

    @classmethod
    def fromIdAndClass(cls, idParam, classParam):
        '''Init from id and class name'''
        obj=cls()
        obj.dict2obj({'id':idParam, 'class':classParam})     
        return obj   

    @classmethod
    def fromYamlFilename(cls, fname):
        '''Init from YAML file'''
        return cls.fromDict(cls.yaml2dict(fname))

    @classmethod
    def fromDict(cls, obj_dict):
        '''Init from dict'''
        obj=SerializableObject()
        obj.dict2obj(obj_dict)
        return obj

    @classmethod
    def yaml2dict(self,fname):
        '''Load dict from YAML file.'''
        with open(fname, 'r') as file:
            obj = yaml.safe_load(file)
        return obj

    def dict2obj(self, attr_dict):
        '''Configure object from dict'''
        for key in attr_dict:
            setattr(self, key, attr_dict[key])

    def dump(self,fname):
        '''Dump object to YAML file.'''
        with open(fname, 'w') as file:
            yaml.dump(self.toDict(), file)

    def toDict(self):
        '''Wrapper for __dict__, returns a copy'''
        return self.__dict__.copy()

    def setAttrAsDict(self, attr_name, attr_obj):
        '''Consume SerializableObject argument, convert to YAML and add as attribute'''
        setattr(self, attr_name, attr_obj.toDict())

    def __str__(self):
        '''Print as dict'''
        return str(self.__dict__)