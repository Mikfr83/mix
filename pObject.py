'''
Base weight object.
'''

class PObject(object):
    def __init__(self,name):
        self._name = name
        self._color = (100,100,100)

    def __repr__(self):
        '''
        This is the string representation of the object when query the object.
        '''
        return '< {0} {1} >'.format(self.__class__.__name__, self._name)
    
    #{ GET
    def getName(self):
        '''
        Gets the name of the current object
        '''
        return self._name


    def getColor(self):
        '''
        Returns the color values

        :return: Color in rgb values
        :rtype: tuple
        '''
        return self._color
    
    #{ SET
    def setName(self, value):
        '''
        Sets the name on the current object
        '''
        if self._name == value:
            return

        self._name = value

    def setColor(self,value):
        if not isinstance(value,tuple) and not isinstance(value,list):
            raise TypeError('{0} must be {1} or {2}'.format(value,type(tuple),type(list)))
        
        if len(value) != 3:
            raise ValueError("{0} must be the length of 3 (R,G,B) values".format(value))
        
        self._color = value     
    
    def delete(self):
        '''
        Deletes attribute
        '''
        del(self)