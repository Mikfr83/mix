'''
Abstract model for default implementation
'''
from mix.ui.weights_model import *
from functools import partial
import showtools.maya.common as common
import showtools.maya.deformer as rig_deformer

DSET_SUFFIX = '_dset'

def update_primary_graph(primary_graph):
    '''
    This will update the primary graph.
    '''
    sel = mc.listRelatives(mc.ls(sl=True, type='mesh', dag=True, ni=True), p=True)
    if sel:
        primary_graph.clearNodes()
        deformer_set_dict = rig_deformer.getDeformerSets(sel[0], DSET_SUFFIX)
        history = rig_deformer.getDeformerStack(sel[0])
        mix_deformer_stack = rig_deformer.getDeformerSetHistory(sel[0], DSET_SUFFIX)
        mix_deformer_stack.reverse()
        for name in mix_deformer_stack:
            node = primary_graph.addNode(name)
            if name.endswith(DSET_SUFFIX):
                node.addAttribute(DSET_SUFFIX, '')
            if deformer_set_dict.has_key(name):
                for child_name in deformer_set_dict[name]:
                    child_node = primary_graph.addNode(child_name, node)
                    enabled_value = mc.getAttr('{}.envelope'.format(child_name))
                    if enabled_value:
                        child_node.enable()
                    else:
                        child_node.disable()
            if name in history:
                enabled_value = mc.getAttr('{}.envelope'.format(name))
                if enabled_value:
                    node.enable()
                else:
                    node.disable()

def init_primary_graph(primary_graph):
    '''
    This will initialize the graph
    '''
    update_primary_graph(primary_graph)

    # Radial menu Setup
    primary_graph.setRadialMenuList([
        {'position': 'W', 'text': 'Toggle Envelope', 'func': partial(toggle_deformer, primary_graph)},
        {'position': 'S', 'text': 'Select Deformer', 'func': partial(select_deformer, primary_graph)}])
'''
    {'position': 'W', 'text': 'Enable Toggle', 'func': partial(enable_interpolator_toggle, interp_graph)},
    {'position': 'E', 'text': 'All Neutral Pose', 'func': partial(set_all_neutral, interp_graph)},
    {'position': 'NW', 'text': 'Add Pose Control', 'func': partial(add_pose_control, interp_graph)},
    {'position': 'S', 'text': 'Select Interpolator', 'func': partial(select_interpolator, interp_graph)},
    {'position': 'SW', 'text': 'Select Drivers', 'func': partial(select_drivers, interp_graph)},
    {'position': 'SE', 'text': 'Delete Interpolator', 'func': partial(delete_interpolator, interp_graph)},
    {'position': '', 'text': 'View Drivers', 'func': partial(view_drivers, interp_graph, True)},
    {'position': '', 'text': 'View Pose Controls', 'func': partial(view_pose_controls, interp_graph, True)},
'''


def toggle_deformer(primary_graph):
    '''
    :param primary_graph:
    :return:
    '''
    node_list = primary_graph.getSelectedNodes()
    for node in node_list:
        if node.getAttributeByName(DSET_SUFFIX):
            continue
        node_name = node.getName()
        enabled_value = mc.getAttr('{}.envelope'.format(node_name))
        if enabled_value:
            node.disable()
            mc.setAttr('{}.envelope'.format(node_name), 0)
            mc.setAttr('{}.nodeState'.format(node_name), 1)
            mc.setAttr('{}.frozen'.format(node_name), 1)
        else:
            node.enable()
            mc.setAttr('{}.envelope'.format(node_name), 1)
            mc.setAttr('{}.nodeState'.format(node_name), 0)
            mc.setAttr('{}.frozen'.format(node_name), 0)

def select_deformer(primary_graph):
    '''
    :param primary_graph:
    :return:
    '''
    node_list = primary_graph.getSelectedNodes()
    current_selection = mc.ls(sl=True)
    for node in node_list:
        if node.getAttributeByName(DSET_SUFFIX):
            continue
        node_name = node.getName()
        if mc.objExists(node_name):
            if current_selection:
                mc.select(clear=True)
                current_selection = None
            mc.select(node_name, add=True)