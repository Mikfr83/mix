'''
Abstract model for default implementation
'''
from mix.ui.weights_model import *

def update_primary_graph(primary_graph):
    '''
    This will update the primary graph.
    '''
    sel = mc.ls(sl=True)
    if sel:
        primary_graph.clearNodes()
        for name in mc.ls(mc.listHistory(sel[0], pdo=1, il=1), type="geometryFilter"):
            if 'tweak' in name:
                continue
            primary_graph.addNode(name)

def init_primary_graph(primary_graph):
    '''
    This will initialize the graph
    '''
    update_primary_graph(primary_graph)