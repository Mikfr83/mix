import mix.pGraph as pGraph

class UGraph(pGraph.PGraph):
    def __init__(self, name):
        '''
        This constructor for the class sets up the graph UI attributes.

        :param name: Name of the graph
        :type name: str
        '''
        super(UGraph,self).__init__(name)

        # UI
        self._selected_nodes = list()
        self._clicked = None
        self._double_clicked = None
        self._live_node = None
        self._widget = None

        # Radial
        self._radial_menu_list = [
            {'position': 'N', 'text': 'North', 'func': '', 'checkbox': False},
            {'position': 'S', 'text': 'South', 'func': '', 'checkbox': False},
            {'position': 'E', 'text': 'East', 'func': '', 'checkbox': False},
            {'position': 'W', 'text': 'West', 'func': '', 'checkbox': False},
            {'position': 'NW', 'text': 'NorthWest', 'func': '', 'checkbox': False},
            {'position': 'NE', 'text': 'NorthEast', 'func': '', 'checkbox': False},
            {'position': 'SW', 'text': 'SouthWest', 'func': '', 'checkbox': False},
            {'position': 'SE', 'text': 'SouthEast', 'func': '', 'checkbox': False},

            # Column Items
            {'position': None, 'text': 'Row 1', 'func': '', 'checkbox': False},
            {'position': None, 'text': 'Row 2', 'func': '', 'checkbox': False}
        ]

    def setSelectedNodes(self, nodes):
        self._selected_nodes = nodes

    def getSelectedNodes(self):
        return(self._selected_nodes)

    def clearSelectedNodes(self):
        self._selected_nodes = []

    def getClicked(self):
        return(self._clicked)

    def setClicked(self, function):
        self._clicked = function

    def getDoubleClicked(self):
        return(self._double_clicked)

    def setDoubleClicked(self, function):
        self._double_clicked = function

    def setRadialMenuList(self, item_dict_list):
        self._radial_menu_list = item_dict_list

    def getRadialMenuList(self):
        return(self._radial_menu_list)

    def setLiveNode(self, node):
        self.clearLiveNode()
        self._live_node = node
        node.liveOn()

    def getLiveNoe(self):
        return(self._live_node)

    def clearLiveNode(self):
        if self._live_node:
            try:
                self._live_node.liveOff()
            except:
                pass
        self._live_node = None
