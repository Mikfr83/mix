'''
This is an abstract graph model.

List of functions that will need to be overridden for reimplementation.
'''
from mix.ui import *
from mix.ui.graph_model import GraphModel
def init_primary_graph(primary_graph):
    '''
    Abstract method for initializing the primary graph.
    '''
    pass

def init_secondary_graph(primary_graph, secondary_graph):
    '''
    Abstract method for initializing the primary graph.
    '''
    pass

def update_primary_graph(primary_graph):
    '''
    Abstract method for updating the primary graph.
    '''
    pass

def update_secondary_graph(secondary_graph):
    '''
    Abstract method for updating the secondary graph.
    '''
    pass

def refresh_secondary_graph(primary_graph, secondary_graph):
    '''
    Abstract method for refreshing the secondary graph.
    '''
    pass