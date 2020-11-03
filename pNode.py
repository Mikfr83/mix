'''
Node will track and manage all data with-in a node
'''
import mix.pDict as pDict
import mix.pAttribute as pAttribute
import mix.pObject as pObject
class PNode(pObject.PObject):
    '''
    Base node to manage all data for nodes
    '''

    @staticmethod
    def isValid(node):
        '''
        Check to see if the node is a valid type or not.

        :param node: Attribute to check
        :type node: PNode se
        '''
        if not isinstance(node, PNode):
            return False
        
        return True
    
    @staticmethod
    def inValidError(node):
        '''
        Raises an error for the given node.
        '''
        raise TypeError("{0} is not of type pNode.PNode".format(node))

    def __init__(self, name, parent = None):
        '''
        This is the constructor class.

        :param name: Name of the node.
        :type name: str

        :param parent: Parent node of this instance of PNode
        :type parent: PNode
        '''
        super(PNode,self).__init__(name)

        #declare class variable
        self._parent = parent
        self._children = pDict.PDict()
        self._attributes = pDict.PDict()
        self._dirty = True
        self._running = False
        self._enabled = True
        self._niceName = name
        self._live = False
        self._edit = False

        #If there is a parent passed into the constructor
        #we will check if it is a PNode type and if it is
        #we will make this node a child of it.
        if parent:
            if not PNode.isValid(parent):
                PNode.inValidError(parent)
            parent.addChild(self)

    #{ GET
    def getParent(self):
        '''Returns the parent node of this instance.'''
        return self._parent
    
    def getChildren(self):
        '''Returns the children of this node.'''
        return self._children.values()
    
    def getAttributes(self):
        '''
        Returns the attributes that the node contains.
        '''
        return self._attributes.values()
    
    def getAttributeByName(self, name):
        '''
        Get the attribute with the given name
        ''' 
        if name in self._attributes.keys():
            return self._attributes[name]
        
        return None

    def getNiceName(self):
        '''Returns the nice name for this node.'''
        return self._niceName

    def getFullPath(self):
        '''
        Returns the full path of the node.

        .. example:
            >>> a = pNode.PNode('A')
            >>> b = pNode.PNode('B',parent=a)
            >>> c = pNode.PNode('C',parent=b)
            >>> a.getFullPath()
            a|b|build|face|tongue

        :return: Number of descendants.
        :rtype: int
        '''
        parent = self.getParent()
        parentNodes = []
        if parent:
            parentNodes.append(self.getName())
            newNodes = parent.getFullPath().split("|")
            if newNodes:
                if newNodes not in parentNodes:
                    parentNodes = newNodes + parentNodes
            return "|".join(parentNodes)
        else:
            return "|".join(["|{}".format(self.getName())])

    def attributeAtIndex(self, index = None):
        '''
        Returns the attribute at the index given.

        :param index: Index of the attribute you want returned
        :type index: int
        '''
        #check the value passed. It must be a string.
        #if not we will raise an error.
        if not isinstance(int,int):
            raise TypeError("{0} must be a <int>".format(index))

        if index != None and not index > len(self._attributes.keys()):
            return self._attributes.values()[index]

    def running(self):
        '''Returns whether the node is currently running.'''
        return self._running
    
    def getChild(self, name = str(), index = None):
        '''
        Gets child by name
        
        :param name: Name of the child to query
        :type name: str
        
        :return: Child node
        :rtype: pNode.PNode  
        '''
        if self._children.has_key(name):
            return self._children[name]
        
        return None

    def childAtIndex(self, index = None):
        '''
        Gets child by name
        
        :param name: Name of the child to query
        :type name: str
        
        :return: Child node
        :rtype: pNode.PNode  
        '''
        if index != None:
            if self.getChildren():
                return self.getChildren()[index]
        
        return None

    def childCount(self):
        '''
        Returns the length of the children
        '''
        return len(self.getChildren())
    
    def descendantCount(self):
        '''
        returns the count of all descendants.

        .. example:
            >>> a = pNode.PNode('A')
            >>> b = pNode.PNode('B',parent=a)
            >>> c = pNode.PNode('C',parent=b)
            >>> a.descendantCount()
            2

        :return: Number of descendants.
        :rtype: int
        '''
        children = self.getChildren()
        count = 0
        if children:
            for child in children: 
                count += 1
                count += child.descendantCount()
            return count
        else:
            return count
        
    def descendants(self):
        '''
        Returns all descendants.

        .. example:
            >>> a = pNode.PNode('A')
            >>> b = pNode.PNode('B',parent=a)
            >>> c = pNode.PNode('C',parent=b)
            >>> a.descendantCount()
            ('A','B','C')

        :return: Number of descendants.
        :rtype: tuple
        '''
        children = self.getChildren()
        nodes = list()
        if children:
            for child in children:
                nodes.append(child)
                newNodes = child.descendants()
                if newNodes:
                    if newNodes not in nodes:
                        nodes.extend(newNodes)
            return tuple(nodes)
        else:
            return tuple(nodes)

    def index(self):
        '''
        returns what index the current node is at on the parents list of children
        '''
        if self._parent:
            if self._parent.getChildren():
                return self._parent.getChildren().index(self)
        
        return 0



    #{ SET
    def setParent(self, parent):
        '''
        Sets the parent for self. Parent node must be node.Node
        
        :example:
            >>> a = pNode.PNode('A')
            >>> b = pNode.PNode('B') 
            >>> b.setParent(a)
            >>> a.children
            ['B' : b]
        
        :param parent: Node you want to be parent of self
        :type parent: pNode.PNode 
        '''
        #validate
        if not PNode.isValid(parent) and parent != None:
            PNode.inValidError(parent)

        #check if parent
        if self._parent and self._parent != parent:
            self._parent.removeChild(self) #remove child from parent
        elif self._parent == parent:
            return #return if there is a parent

        #add self to parent
        self._parent = parent
        if parent == None:
            return
        parent.addChild(self)
        
    def setRunning(self,value):
        if not isinstance(value,bool):
            raise TypeError("{0} must be a {1}".format(value,type(bool)))
        
        self.__running = True
    
    def setDirty(self,value):
        if not isinstance(value,bool):
            raise TypeError("{0} must be a {1}".format(value,type(bool)))
        
        self._dirty = True

    def setNiceName(self, value): #void
        '''
        Sets the nice name for this node. Must be a string
        
        :param value: Name for the given nodes nice name
        :type value: str
        '''
        if not isinstance(value,basestring):
            return TypeError("{0} must be a {1}".format(value,type(str)))
        
        self._niceName = value
        
    def enable(self):
        '''
        Enables the node. Make sure that the node can
        be exectuded.
        '''
        self._enabled = True
    
    def disable(self):
        '''
        Disables the node. Make sure that the node cannot 
        be exectuded.
        '''
        self._enabled = False

    def liveOn(self):
        '''
        Set node to be live
        '''
        self._live = True

    def liveOff(self):
        '''
        Set node to not be live
        '''
        self._live = False

    def editOn(self):
        '''
        Set node to be live
        '''
        self._edit = True

    def editOff(self):
        '''
        Set node to not be live
        '''
        self._edit = False

    #{ MISC
        
    def isActive(self):
        '''
        Returns whether or not the node is currently
        active.
        '''
        return self._enabled

    def isLive(self):
        '''
        Returns whether or not the node set to live mode
        '''
        return self._live

    def isEdit(self):
        '''
        Returns whether or not the node is in edit mode
        '''
        return self._edit


    def addAttribute(self, attr, value, index = -1, attrType = None):
        '''
        sets the data on the node based on key : value pairs
        
        :example:
            >>> addAttribute(limb.arm(), position = [20,10,10])
            {"Left Arm" : []}
            
        :param attr: Nice name for user interface
        :type attr: str

        :param value: python object to be called when run() is called
        :type value: str
        '''
        if isinstance(attr, basestring):
            attr = pAttribute.PAttribute(attr, value = value, attrType = attrType)
            
        #check to make sure an attribute was passed in
        if not isinstance(attr, pAttribute.PAttribute):
            raise TypeError('{0} must be {1}'.format(pAttribute, pAttribute.PAttribute))
        
        #change index if it's none
        if index == -1:
            index = len(self._attributes.keys())
        
        #add attributes to the attributes dictionary
        self._attributes.add(attr.getName(), attr, index)

        return attr
        
    def addChild(self, child, index = None):
        '''
        Adds an existing node as a child.
        
        .. example:
            >>> a = pNode.PNode('A')
            >>> b = pNode.PNode('B') 
            >>> a.addChild(a)
            >>> a.children
            ['B']
            
        :param child: child node you wish to add 
        :type child: pNode.PNode  
        '''
        #validate child
        if not PNode.isValid(child):
            PNode.inValidError(child)
        
        #check the index, make sure it's never 0
        
        #add self as parent of child node
        child.setParent(self)
        
        #change index if it's none
        if index == None:
            index = len(self._children.keys())

        #add child
        self._children.add(child.getName(), child, index)
        
    def addChildren(self, children, index = None):
        '''
        Adds an existing node as a child.
        
        .. example:
            >>> a = pNode.PNode('A')
            >>> b = pNode.PNode('B') 
            >>> a.addChild(a)
            >>> a.children
            ['B']
            
        :param child: child node you wish to add 
        :type child: pNode.PNode
        '''
        if index == None:
            index = len(self._children.keys())
            
        for child in children:
            self.addChild(child, index)
            index +=1
    
    def hasChild(self, name = str()):
        '''
        Returns True or False depending on whether or not self 
        has child node.
        
        :param name: Name of the child to query
        :type name: str
        
        :return: True if it has child, False if it does not
        :rtype: bool 
        '''
        #check to see if the node has a child
        if self.isChild(name):
            return True
        
        return False

    def removeAttribute(self, attribute):
        if not attribute.Attribute.isValid(attribute):
            attribute.Attribute.inValidError(attribute)
        #remove it from the attributes dictionary
        self._attributes.pop(attribute.getName())
        #delete the attribute
        del(attribute)
    
    def removeChild(self, child):
        '''
        Removes child node from list of children and take is out of self
        
        :example:
            >>> a.children
            ['B', 'C']
            >>> b.parent.getName()
            A
            >>> a.removeChild(b)
            >>> a.children
            ['C']
        
        :param child: Node you want to remove from self
        :type child: pNode.PNode
        '''
        #check if child is valid
        if not PNode.isValid(child):
            PNode.inValidError(child)
        #check key on  __children dict, if it exists, pop it out of dict
        if self._children.has_key(child.getName()):
            self._children.pop(child.getName()) #remove it from __children dict
            child.setParent(None) #remove self from parent
            
    def moveChild(self, child, index):
        '''
        moves child node from one position in dict to another
        
        :example:
            >>> a.children
            ['B', 'C']
            >>> b.parent.getName()
            A
            >>> a.moveChild(b,1)
            >>> a.children
            ['C','B']
        
        :param child: Node you want to move
        :type child: pNode.PNode | str
        '''
        #check if child is a valid node
        if not PNode.isValid(child):
            PNode.inValidError(child)
        #reorder the __children dict
        self._children.move(child.getName(), index)

    def isChild(self, node):
        '''
        Returns wheter the node passed in is a child 
        of this node or not.

        :param node: Node to check whether it's a child or not.
        :type node: PNode
        '''
        #check if node is valid or not.
        if not PNode.isValid(node):
            PNode.inValidError(node)
        
        #If node is a child, return True
        if self._children.has_key(node.getName()):
            return True
        
        return False
    
    def log(self, tabLevel = -1):
        output = "\n"
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
            
        output += '|____%s\n' % self._name
        
        for child in self.getChildren():
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += '\n'
        return output
    
    def execute(self, *args, **kwargs):
        '''
        .. todo: add execution code here
        '''
        return

