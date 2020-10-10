import mix
import maya.mel as mm

import mix.ui.mainWindow
reload(mix.ui.mainWindow)

import mix.ui.centralWidget
reload(mix.ui.centralWidget)

import mix.ui.layerGraphTreeView
reload(mix.ui.layerGraphTreeView)

import mix.ui.layerGraphModel
reload(mix.ui.layerGraphModel)

import mix.pGraph as pGraph
reload(pGraph)

import mix.pNode as pNode
reload(pNode)

import mix.ui.uGraph as uGraph
reload(uGraph)

import showtools.maya.core.psd as rig_psd
reload(rig_psd)

import showtools.maya.core.common as common
reload(common)

import showtools.maya.core.blendShape as rig_blendShape
reload(rig_blendShape)

from functools import partial

import mix.ui.inputDialog
reload(mix.ui.inputDialog)

import maya.cmds as mc
import math

# Pointer to secondary update function
update_secondary = None
# Pointer to qDialog
g_dialog = mix.ui.inputDialog.InputDialog()

def target_clicked(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()

def target_double_clicked(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    if sel_nodes:
        node = sel_nodes[0]
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        rig_psd.goToPose(interp, pose)
    update_secondary()

def apply_pose(interp_graph, pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    geo = mc.ls(sl=1)
    if not geo:
        return
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        bs = rig_psd.getDeformer(interp)
        rig_psd.goToPose(interp, pose)
        if len(geo) == 1:
            rig_psd.applyPose(interp, pose, bs, geo[0])
        else:
            geo_name = get_pose_geo_path(bs, interp, pose)
            if mc.objExists(geo_name):
                rig_psd.applyPose(interp, pose, bs, geo_name)

def get_pose_geo_path(bs, interp, pose):
    interp_name = rig_psd.getInterpNiceName(interp) + '_interp'
    group_name = bs.replace('psd', 'grp')
    full_path = '{}|{}|{}'.format(group_name, interp_name, pose)
    return(full_path)

def delete_pose(interp_graph, pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        rig_psd.deletePose(interp, pose)

    update_secondary()

def delete_deltas(interp_graph, pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        bs = rig_psd.getDeformer(interp)
        if mc.objExists(bs+'.'+pose):
            rig_blendShape.clearTargetDeltas(bs, pose)

def add_pose(interp_graph, pose_graph):
    sel_nodes = interp_graph.getSelectedNodes()
    if not sel_nodes:
        return

    # Get a pose default name to enter in the text
    interp = sel_nodes[0].getAttributeByName('full_name').getValue()
    pose_name_list = rig_psd.getPoseNames(interp) or []
    pose_name = ''
    for pose in pose_name_list:
        if not 'neutral' in pose:
            pose_name = pose
            break

    text, ok = g_dialog.get_text('Add Pose', 'Pose name:', pose_name)
    if not ok:
        return
    text = common.getValidName(text)
    if not text:
        return

    for node in sel_nodes:
        interp = node.getAttributeByName('full_name').getValue()
        bs = rig_psd.getDeformer(interp)
        pose_name_list = rig_psd.getPoseNames(interp) or []
        if text in pose_name_list:
            mc.warning('[ {} ] Interp pose with name  [ {} ] already exists'.format(interp, text))
            continue

        if 'neutral' in pose_name:
            print('[ {} ] Adding neutral pose  [ {} ]'.format(interp, text))
            pose_name = rig_psd.addPose(interp, text)
            continue

        target_name_list = rig_blendShape.getTargetNames(bs) or []
        if text in target_name_list:
            mc.warning('blendShape target with name  [ {}.{} ] already exists'.format(bs, text))
            continue

        print('[ {} ] Adding pose [ {} ]'.format(interp, text))
        pose_name = rig_psd.addPose(interp, text)
        rig_psd.addShape(interp, text, bs=bs)

    update_secondary()

def rename_pose(interp_graph, pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    if not sel_nodes:
        return

    # Get a pose default name to enter in the text
    pose_name = sel_nodes[0].getAttributeByName('full_name').getValue()


    text, ok = g_dialog.get_text('Rename Pose', 'Pose name:', pose_name)
    if not ok:
        return
    text = common.getValidName(text)
    if not text:
        return

    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()

        pose_name_list = rig_psd.getPoseNames(interp)
        if text in pose_name_list:
            mc.warning('Target with name {} already exists'.format(text))
            continue
        print('Renaming pose [ {} ] [ {} ] --> [ {} ] '.format(interp, pose, text))
        rig_psd.renamePose(interp, pose, text)

    update_secondary()

def update_pose(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        rig_psd.updatePose(interp, pose)
        # Update pose control data
        #
        pose_control_data = rig_psd.getPoseControlData(interp, pose)
        if not pose_control_data:
            continue
        for data in pose_control_data:
            name, type, value = data
            value = mc.getAttr(name)

            # Rotate
            if type == 8:
                # Convert degrees to radians
                value = [math.radians(value[0][0]), math.radians(value[0][1]), math.radians(value[0][2])]
                rig_psd.setPoseControlData(interp, pose, name, type, value)
    update_secondary()

def sync_pose(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        rig_psd.goToPose(interp, pose)
        rig_psd.updatePose(interp, pose)
    update_secondary()

def mirror_delta(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        # Get out of sculpt tool if we are in it
        ctx = mc.currentCtx()
        restore_sculpt = None
        if ctx == 'sculptMeshCacheContext':
            mc.setToolTo('Move')
            restore_sculpt = True
        ctx = mc.currentCtx()
        rig_psd.mirrorDelta(interp, pose)
        if restore_sculpt:
            mc.setToolTo('sculptMeshCacheContext')

def activate_pose(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    if sel_nodes:
        node = sel_nodes[0]
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        rig_psd.poseLiveOn(interp, pose)
        pose_graph.setLiveNode(node)

def enable_toggle(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    if sel_nodes:
        state = sel_nodes[0].isActive()
        for node in sel_nodes:
            interp = node.getAttributeByName('interp').getValue()
            pose = node.getAttributeByName('full_name').getValue()
            if state:
                node.disable()
                rig_psd.disablePose(interp, pose)
            else:
                node.enable()
                rig_psd.enablePose(interp, pose)


def duplicate_shape(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    dupes = []
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        dup = rig_psd.duplicatePoseShape(interp, pose)
        dupes.append(dup)
        node.editOn()
    if dupes:
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        for dup in dupes:
            for a in attrs:
                mc.setAttr(dup+'.'+a, l=0)

        mc.select(dupes)

def isolate_shape(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    geos = []
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        bs = rig_psd.getDeformer(interp)
        geo = get_pose_geo_path(bs, interp, pose)

        if mc.objExists(geo):
            geos.append(geo)

    currentPanel = getModelPanel()

    geos = mc.ls(geos)
    if geos:
        # Find the isolate set
        obj_set = mc.isolateSelect(currentPanel, viewObjects=1, q=1)

        # Remove objects in set
        objs_in_set = []
        if obj_set:
            objs_in_set = mc.sets(obj_set, q=1) or []
            mc.sets(clear=obj_set)
            if objs_in_set:
                mc.hide(objs_in_set)

        # Clear isolate state
        mc.isolateSelect(currentPanel, state=0)

        # If the first geo is not in obj set, then isolate them
        if geos[0] not in objs_in_set:
            mc.isolateSelect(currentPanel, state=1)
            obj_set = mc.isolateSelect(currentPanel, viewObjects=1, q=1)
            if obj_set:
                mc.sets(clear=obj_set)

            mc.select(geos)
            mc.isolateSelect(currentPanel, addSelected=1)
            mc.showHidden(geos)

    mc.isolateSelect(currentPanel, update=True)
    mm.eval('updateModelPanelBar {}'.format(currentPanel))

def getModelPanel():
    '''Return the active or first visible model panel.'''

    panel = mc.getPanel(withFocus=True)

    if mc.getPanel(typeOf=panel) != 'modelPanel':
        # just get the first visible model panel we find, hopefully the correct one.
        panels = getModelPanels()
        if panels:
            panel = panels[0]
            mc.setFocus(panel)

    return panel

def getModelPanels():
    '''Return all the model panels visible so you can operate on them.'''
    panels = []
    for p in mc.getPanel(visiblePanels=True):
        if mc.getPanel(typeOf=p) == 'modelPanel':
            panels.append(p)
    return panels

def build_interp_graph(interp_graph):
    interp_graph.clearNodes()

    # Group loop
    psd_group_list = rig_psd.getAllGroups()
    for psd_group in psd_group_list:
        # Add group node
        group_node = interp_graph.addNode(psd_group)

        # Get all interps
        interp_list = rig_psd.getGroupChildren(psd_group)

        # Interp loop
        for interp in interp_list:
            interp_name = rig_psd.getInterpNiceName(interp)

            interp_node = interp_graph.addNode(interp_name, group_node)
            interp_node.addAttribute('full_name', interp)
            bs = rig_psd.getDeformer(interp)
            interp_node.addAttribute('blendshape', bs)

    return (interp_graph)

def refresh_pose_graph(interp_graph, pose_graph, keep_selection=False):
    '''

    :param interp_graph:
    :param pose_graph:
    :return:
    '''
    # Clear graph
    pose_graph.clearNodes()

    # Qeury what poses are live
    live_poses = rig_psd.getLivePoses()

    # Query what poses are duplicated for editing
    # duped_poses = rig_psd.getDupedPoses()

    # Interp node loop
    node_list = interp_graph.getSelectedNodes()
    neutrals = []
    pose_data_list = []

    # Get pose data
    for i in range(len(node_list)):
        node = node_list[i]
        if node.getAttributeByName('blendshape'):
            bs = node.getAttributeByName('blendshape').getValue()
        if node.getAttributeByName('full_name'):
            interp = node.getAttributeByName('full_name').getValue()
            # (PINGS MAYA)
            poses = rig_psd.getPoseNames(interp)
            if not poses:
                continue
            for n in range(len(poses)):
                pose = poses[n]
                pose_weight = rig_psd.getPoseWeight(interp, pose)
                pose_weight = '{:.2f}'.format(round(pose_weight, 2))


                if pose_weight == '-0.00':
                    pose_weight = '0.00'

                pose_weight = '{0:>{1}}'.format(pose_weight, 5)
                pose_data_list.append([pose_weight, pose, interp, bs])

    if not pose_data_list:
        return(pose_graph)

    # Sort by name
    pose_data_list.sort(key=lambda p: p[1])

    # Put left and right sides poses next to each other
    pose_data_list_pair = []
    mirrors_found = []
    for i in range(len(pose_data_list)):
        pose_name, interp = pose_data_list[i][1:3]
        side = common.getSideToken(interp)

        if not side:
            pose_data_list_pair.append(pose_data_list[i])
            continue

        mirror_pose_data = None
        mirror_interp_name = common.getMirrorName(interp)
        mirror_pose_name = common.getMirrorName(pose_name) or pose_name

        if (interp, pose_name) in mirrors_found:
            continue

        right_left_found = False

        if side == 'l':
            # add the left side pose
            pose_data_list_pair.append(pose_data_list[i])

            # check for a right side pose
            for n in range(len(pose_data_list)):
                interp_name_compare = pose_data_list[n][2]
                pose_name_compare = pose_data_list[n][1]

                # Check if this is the mirror interp
                if interp_name_compare == mirror_interp_name:
                    if pose_name_compare == mirror_pose_name:
                        mirror_pose_data = pose_data_list[n]
                        mirrors_found.append((mirror_interp_name, mirror_pose_name))
                        right_left_found = True
                        break

            if mirror_pose_data:
                pose_data_list_pair.append(mirror_pose_data)
        else:
            if not right_left_found:
                pose_data_list_pair.append(pose_data_list[i])


    # justify for row column display
    pose_data_list_justified = common.justify_list_items(pose_data_list_pair)

    # Create graph nodes
    #
    for i in range(len(pose_data_list_pair)):
        pose_weight, pose, interp, bs = pose_data_list_pair[i]

        display_name = '  '.join(pose_data_list_justified[i])
        if 'neutral' in pose:
            neutrals.append([display_name, pose, interp])
            continue

        pose_node = pose_graph.addNode(display_name)
        pose_node.addAttribute('interp', interp)
        pose_node.addAttribute('full_name', pose)

        # Live
        if (bs, pose) in live_poses:
            pose_graph.setLiveNode(pose_node)

        # Duplicated (PING)
        if rig_psd.getPoseShapes(interp, pose):
            pose_node.editOn()
        else:
            pose_node.editOff()

        # Disabled (PING)
        #
        if rig_psd.isEnabled(interp=interp, pose=pose):
            pose_node.enable()
        else:
            pose_node.disable()

    for pose in neutrals:
        pose_node = pose_graph.addNode(pose[0])
        pose_node.addAttribute('interp', pose[2])
        pose_node.addAttribute('full_name', pose[1])

    return (pose_graph)

def build_pose_graph(interp_graph, pose_graph):
    '''

    :param interp_graph:
    :param pose_graph:
    :return:
    '''

    # Connect Click functions
    pose_graph.setClicked(partial(target_clicked, pose_graph))
    pose_graph.setDoubleClicked(partial(target_double_clicked, pose_graph))

    # Radial menu Setup
    pose_graph.setRadialMenuList([

        {'position': 'E', 'text': 'Duplicate Shape', 'func': partial(duplicate_shape, pose_graph)},
        {'position': 'N', 'text': 'Live Edit', 'func': partial(activate_pose, pose_graph)},
        {'position': 'W', 'text': 'Enable Toggle', 'func': partial(enable_toggle, pose_graph)},
        {'position': 'S', 'text': 'Apply', 'func': partial(apply_pose, interp_graph, pose_graph)},
        {'position': 'NE', 'text': 'Mirror Deltas', 'func': partial(mirror_delta, pose_graph)},
        {'position': 'SE', 'text': 'Isolate Toggle', 'func': partial(isolate_shape, pose_graph)},
        {'position': '', 'text': 'Delete Deltas', 'func': partial(delete_deltas, interp_graph, pose_graph)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Add Pose', 'func': partial(add_pose, interp_graph, pose_graph)},
        {'position': '', 'text': 'Rename Pose', 'func': partial(rename_pose, interp_graph, pose_graph)},
        {'position': '', 'text': 'Delete Pose', 'func': partial(delete_pose, interp_graph, pose_graph)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Sync Pose', 'func': partial(sync_pose, pose_graph)},
        {'position': '', 'text': 'Update Pose', 'func': partial(update_pose, pose_graph)},
        {'position': '', 'text': '-------------', 'func': None},

    ])


    # Live status

    return (pose_graph)

def secondary_tree_selection_change(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    shape_list = []
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        shape = rig_psd.getPoseShapes(interp, pose)
        if shape:
            shape_list.append(shape)

    if shape_list:
        mc.select(shape_list)

def launch():
    global update_secondary
    # Build graphs that all specific deformer functions will talk to
    pose_graph = uGraph.UGraph('Poses')
    interp_graph = uGraph.UGraph('Interps')

    # Launch window
    build_interp_graph(interp_graph)
    build_pose_graph(interp_graph, pose_graph)

    mix_win = mix.ui.mainWindow.launch(primary_graph=interp_graph, secondary_graph=pose_graph)

    # Connect graph update functions
    mix_win.centralWidget.update_primary_graph = partial(build_interp_graph, interp_graph)
    mix_win.centralWidget.update_secondary_graph = partial(refresh_pose_graph, interp_graph, pose_graph)
    mix_win.centralWidget.refresh_secondary_graph = partial(secondary_tree_selection_change, pose_graph)

    update_secondary = mix_win.centralWidget.update_secondary


'''
Data flow

Selecting a interp 

LayerGraphTreeView.pSelectionChanged
    centralWidget._setupTreeView.pSelectionChanged
        centralWidget._primary_tree_selection_change
            centralWidget.update_secondary_graph()
                psdModel.refresh_pose_graph
            centralWidget.update_secondary_graph()
    
    psdModel.refresh_pose_graph
        centralWidget.update_secondary_graph
'''

