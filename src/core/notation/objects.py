'''Wrapper for traversing SAFInfer taxonomic objects'''

class ObjectWrapper:
    '''
    Wrapper for traversing SAFInfer taxonomic objects
    '''
    def __init__(self,obj):
        '''
        Wrap SAFInfer taxonomic object.\n\n

        Arguments:\n
        - obj -- SAFInfer taxonomic object
        '''
        self.obj=obj