import poise.pObject as pObject
import poise.pNode as pNode

class PGraph(pObject.PObject):
    def __init__(self, name):
        '''
        This constructor for the class sets up the base graph attributes.
        
        :param name: Name of the graph
        :type name: str
        '''
        super(PGraph,self).__init__(name)
        
        self._rootNodes = list()
        self._nodes = list()

    def rootNodes(self):
        return self._rootNodes

    def setToRoot(self,node):
        '''
        set the node to the root of the graph

        :param node: Node you wish to put to the root.
        :type node: PNode
        '''
        if node.getParent():
            node.getParent().removeChild(node)
        if node in self._rootNodes:
            return

        self._rootNodes.append(node)
        
    def addNode(self, node, parent = None, index = None):
        #if name passed in instead of node
        if isinstance(node, basestring):
            node = pNode.PNode(node, parent)
        elif parent:
            if node in self._rootNodes:
                self.removeNode(node)
            node.setParent(parent)
        
        if parent and index != None:
            parent.moveChild(node, index)
        elif not parent and index != None:
            self._rootNodes.insert(index,node)
        elif not parent and index == None:
            self._rootNodes.append(node)
        elif parent and index == None:
            parent.addChild(node)
        
        node.setNiceName(node.getName())
        
        return node

    def clearNodes(self):
        self._nodes = list()
        self._rootNodes = list()

    def removeNode(self, node):
        if node in self._rootNodes:
            self._rootNodes.pop(node.index())
        
        if node.getParent():
            node.getParent().removeChild(node)
        
    def nodeCount(self):
        count = len(self._rootNodes)
        
        for node in self._rootNodes:
            count += node.descendantCount()
            
        return count
    
    def getNodes(self):
        nodes = list()
        for node in self._rootNodes:
            nodes.append(node)
            nodes.extend(node.descendants())
            
        return nodes
    
    def log(self, tabLevel = -1):
        '''
        Logs the whole graph. Returns the whole graph in a string
        
        :param tabLevel: This shows how many tabs in we start
        :type tabLevel: int
        '''
        output = "\n"
        tabLevel += 1 #add to the tabLevel
        
        #tab in based on the tabLevel
        for i in range(tabLevel):
            output += "\t"
        
        for node in self._rootNodes:
            output += node.log(tabLevel)
        
        tabLevel -= 1
        output += '\n'
        return output

    def nodeNames(self):
        nodeNames = list()
        for node in self._rootNodes:
            nodeNames.append(node.getName())
            for child in node.descendants():
                nodeNames.append(child.getName())
            
        return nodeNames
    
    def getNodeByName(self, name):
        for node in self.getNodes():
            if name == node.getName():
                return node
        return None

    def getNodeByPath(self, path):
        '''
        This will get the node by passing a path to the method.

        .. example:: 
            getNodeByPath("|animRig|build|body|l_leg|l_foot")

        :param path: Path you want to use to retrieve the node you're looking for.
        :type path: str

        :return: Returns the node at that given path
        :rtype: PNode | None
        '''
        if not isinstance(path, basestring):
            raise TypeError('{} must be a string that represents a path to a node.'.format(path))
        elif "|" not in path:
            raise RuntimeError('path must be passed in like the following example: "|anim|load|joints"')
        try:
            splitPath = path.split("|")
            if not splitPath[0]:
                splitPath.pop(0)
            node = self.getNodeByName(splitPath.pop(0))
            for name in splitPath:
                node = node.getChild(name)
        except:
            node = None
            print "path doesn't seem to exists in this graph. Please double check your input."

        return node
