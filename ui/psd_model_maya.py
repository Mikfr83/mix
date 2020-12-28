import mix
from mix.ui import *
from mix.ui.psd_model import *
import openrig.maya.psd as rig_psd
import openrig.shared.common as common
import openrig.maya.blendShape as rig_blendShape
from functools import partial
import mix.ui.input_dialog
import openrig.maya.attr as rig_attribute
import openrig.maya.delta_blend as rig_delta_blend
import traceback

# Pointer to secondary update function
update_primary = None
update_secondary = None
# Pointer to qDialog
g_dialog = mix.ui.input_dialog.InputDialog()

# temp widgets
driver_widget = mix.ui.input_dialog.TwistTableDialog()
driver_widget.setWindowTitle('Drivers')
driver_widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
pose_control_widget = QtWidgets.QListWidget()
pose_control_widget.setWindowTitle('Pose Controls')
pose_control_widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
driven_widget = QtWidgets.QListWidget()
driven_widget.setWindowTitle('Drivens')
driven_widget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

def interp_clicked(interp_graph):
    '''
    '''
    view_pose_controls(interp_graph)
    view_drivers(interp_graph)
    view_drivens(interp_graph)

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
    sel_geo = mc.ls(sl=1)
    if not sel_geo:
        return
    sel_geo = sel_geo[0]

    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        blendshape_list = rig_psd.getDrivenNodes(interp, pose)
        for bs in blendshape_list:
            rig_psd.goToPose(interp, pose)
            pose_geo = get_pose_geo_path(bs, interp, pose)
            if len(sel_geo) == 1:
                pose_geo = sel_geo
            if mc.objExists(pose_geo):
                rig_psd.applyPoseSymmetry(interp, pose, bs, pose_geo)

def get_pose_geo_path(bs, interp, pose):
    interp_name = rig_psd.getInterpNiceName(interp) + '_interp'
    group_name = rig_psd.getGroup(interp)+'_grp'
    geo = mc.deformer(bs, q=1, g=1)
    geo = mc.listRelatives(geo, p=1, path=1)[0].split('|')[-1]
    full_path = '{}|{}|{}_{}'.format(group_name, interp_name, geo, pose)
    return(full_path)

def set_all_neutral(interp_graph):
    '''
    Will set all interpolator neutral poses to get to the default state of the character.
    '''
    mc.undoInfo(openChunk=1)
    try:
        node_list = interp_graph.getNodes()

        for node in node_list:
            full_name_attr = node.getAttributeByName('full_name')
            if full_name_attr:
                interp_list = mc.ls(full_name_attr.getValue())
                if interp_list:
                    rig_psd.goToNeutralPose(interp_list)
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def delete_interpolator(interp_graph):
    '''
    This will delete the selected interpolators from the maya session.
    '''

    mc.undoInfo(openChunk=1)
    try:
        selected_node_list = interp_graph.getSelectedNodes()
        if not selected_node_list:
            return
        # loop throught the selected nodes in the list and delete them q
        for node in selected_node_list:
            interp = node.getAttributeByName('full_name').getValue()
            pose_list = rig_psd.getPoseNames(interp)
            rig_psd.deletePose(interp, pose_list)
            mc.delete(mc.listRelatives(interp, p=True)[0])

        update_primary()
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def delete_pose(interp_graph, pose_graph):
    mc.undoInfo(openChunk=1)
    try:
        sel_nodes = pose_graph.getSelectedNodes()
        for node in sel_nodes:
            interp = node.getAttributeByName('interp').getValue()
            pose = node.getAttributeByName('full_name').getValue()
            rig_psd.deletePose(interp, pose)

        update_secondary()
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def delete_deltas(interp_graph, pose_graph):
    mc.undoInfo(openChunk=1)
    try:
        sel_nodes = pose_graph.getSelectedNodes()
        for node in sel_nodes:
            interp = node.getAttributeByName('interp').getValue()
            pose = node.getAttributeByName('full_name').getValue()
            blendshape_list = rig_psd.getDrivenNodes(interp)
            for bs in blendshape_list:
                if mc.objExists(bs+'.'+pose):
                    rig_blendShape.clearTargetDeltas(bs, pose)
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def add_interpolator(interp_graph):
    '''
    Add an interpolator to the the graph.
    :pram interp_graph: The graph where the interpolators live
    :type interp_graph: UGraph
    '''
    mc.undoInfo(openChunk=1)
    try:
        # get the selected nodes.
        selected_node_list = interp_graph.getSelectedNodes()

        # get the current group list to check against.
        current_group_list = [mc.getAttr('{}.directoryName'.format(parent_attr)) for parent_attr in
                              mc.ls('poseInterpolatorManager.poseInterpolatorDirectory[*]')]

        # if there is a group selected we will
        group_name = None
        for node in selected_node_list:
            # store the node name in a variable
            node_name = node.getName()
            if node_name in current_group_list:
                group_name = node_name
                break
            elif mc.nodeType(node.getAttributeByName('full_name').getValue()) == 'poseInterpolator':
                full_name = node.getAttributeByName('full_name').getValue()
                group_name = rig_psd.getGroup(rig_psd.getInterp(full_name))
                break

        # if no groups are selected we will punt and ask a user to select a group.
        if not group_name:
            print('Please select a group that so we can add the interpolator to it.')

        # pull up the dialog box
        text, ok = g_dialog.get_text('interpolator', 'Interpolator name:', "poseInterp")
        if not ok:
            return

        interp_text = common.getValidName(text)
        if not interp_text:
            return
        # Get all interps
        interp_list = rig_psd.getGroupChildren(group_name)
        interp_name = '{}_poseInterpolator'.format(interp_text)
        print('Adding Interpolator [ {} ]'.format(interp_text))
        # create the interpolator and make the connection to the blendshape attribute
        interp = rig_psd.addInterp(interp_name, group=group_name)
        # make sure the attributes exist on the node and then make the connections
        if not mc.objExists('{}.driven_node'.format(interp)):
            mc.addAttr(interp, ln='driven_node', at='message')

        # pull up the dialog box
        group_node = interp_graph.getNodeByName(group_name)
        interp_node = interp_graph.addNode(interp_text, group_node)
        interp_node.addAttribute('full_name', interp)

        update_primary()
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def add_driver(interp_graph):
    '''
    This will add drivers to the selected interpolator in the graph.
    :pram interp_graph: The graph where the interpolators live
    :type interp_graph: UGraph
    '''
    mc.undoInfo(openChunk=1)
    try:
        sel_nodes = interp_graph.getSelectedNodes()
        if not sel_nodes:
            return

        driver_list = mc.ls(sl=True, type=['joint', 'transform'])

        if not driver_list:
            raise RuntimeError('Only joints can be drivers. Please select a joint you want to use as a driver.')

        # Get a pose default name to enter in the text
        interp = sel_nodes[0].getAttributeByName('full_name').getValue()
        rig_psd.addDriver(interp, driver_list)
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def add_driven(interp_graph):
    '''
    This will take what is selected in your scene and add the geometry as a driven. If your geometry currently doesn't
    have a blendShape, we will create one and name it geoName_blendShape then add targets if any poses exist.

    .. note::
        This currently is only handling blendShape nodes. We're not handling numeric drivens in this function
        at the moment.

    :pram interp_graph: The graph where the interpolators live
    :type interp_graph: UGraph
    :return:
    '''
    mc.undoInfo(openChunk=1)
    try:
        sel_nodes = interp_graph.getSelectedNodes()
        # selected nodes in maya session.
        sel_list = mc.ls(sl=True)
        if not sel_nodes or not sel_list:
            return
        # loop through each interp and add drivens to the poses if they don't currently exist.
        for index, interp_name in enumerate(sel_nodes):
            # Get a pose default name to enter in the text
            interp = sel_nodes[index].getAttributeByName('full_name').getValue()
            # get all of the driven nodes. Currently only doing blendShapes.
            # TODO: this is currently only blendshapes. We will need to update this to act differently in the future.
            driven_list = rig_psd.getDrivenNodes(interp) or list()
            geo_list = list()
            for node in driven_list:
                if mc.nodeType(node) == 'blendShape':
                    geo_list = list(set(geo_list + mc.blendShape(node, q=True, g=True)))

            # get the transforms for the shape nodes.
            geo_list = [mc.listRelatives(geo, p=True)[0] for geo in geo_list]
            add_list = [node for node in sel_list if not node in geo_list]

            # if node in add_list has a blendShape with the same name as geometry, we will use that. Otherwise, we will make
            # a blendShape that is front of chain using the name of geometry as a prefix
            new_driven_list = list()
            for geo in add_list:
                # get the blendShapes on the geometry
                geo_blendshape_list = rig_blendShape.getBlendShapes(geo)
                blendshape_name = '{}_blendShape'.format(geo)
                if not blendshape_name in geo_blendshape_list:
                    mc.select(geo, r=True)
                    mc.blendShape(name=blendshape_name, frontOfChain=True)

                new_driven_list.append(blendshape_name)

            rig_psd.addDriven(interp, new_driven_list)
            mc.select(sel_list)
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def add_pose_control(interp_graph):
    '''
    This will add selected attributes as a pose control for the interpolator selected in the graph.
    :pram interp_graph: The graph where the interpolators live
    :type interp_graph: UGraph
    '''
    mc.undoInfo(openChunk=1)
    try:
        sel_nodes = interp_graph.getSelectedNodes()
        for interp_node in sel_nodes:
            selected_controls = mc.ls(sl=True)
            selected_attributes = rig_attribute.get_selected_main_channel_box()
            # get the interp
            interp = interp_node.getAttributeByName('full_name').getValue()
            # loop through the selected controls
            for control in selected_controls:
                control_attr_list = rig_attribute.get_resolved_attributes(control, selected_attributes)
                rig_psd.addPoseControl(interp, control_attr_list)
            pose_names = rig_psd.getPoseNames(interp) or []
            # go through each existing pose and make sure that the pose information is updated.
            for pose in pose_names:
                for control_attr in control_attr_list:
                    # get the value
                    attr_value = mc.getAttr(control_attr)
                    # split the name so we can query the type of attribute, incase it's a double3
                    control_attr_split = control_attr.split('.')
                    attr_name = control_attr_split[-1]
                    node_name = control_attr_split[0]
                    if mc.attributeQuery(attr_name, node=node_name, at=True) == 'double3':
                        attr_value = attr_value[0]
                        attr_value = [mm.eval('deg_to_rad({})'.format(value)) for value in attr_value]
                    elif mc.attributeQuery(attr_name, node=node_name, at=True) in 'doubleAngle':
                        attr_value = mm.eval('deg_to_rad({})'.format(attr_value))
                    rig_psd.setPoseControlData(interp, pose, control_attr, attr_value)
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

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
        blendshape_list = rig_psd.getDrivenNodes(interp)
        pose_name_list = rig_psd.getPoseNames(interp) or []
        if text in pose_name_list:
            mc.warning('[ {} ] Interp pose with name  [ {} ] already exists'.format(interp, text))
            continue
        if 'neutral' in text:
            print('[ {} ] Adding neutral pose  [ {} ]'.format(interp, text))
            pose_name = rig_psd.addPose(interp, text)
            continue

        if blendshape_list:
            for bs in blendshape_list:
                target_name_list = rig_blendShape.getTargetNames(bs) or []
                if text in target_name_list:
                    mc.warning('blendShape target with name  [ {}.{} ] already exists'.format(bs, text))
                    continue

                print('[ {} ] Adding pose [ {} ]'.format(interp, text))
                pose_name_list = rig_psd.getPoseNames(interp)
                if text not in pose_name_list:
                    rig_psd.addPose(interp, text)

                rig_psd.addShape(interp, text, blendShape=blendshape_list)

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

def rename_interpolator(interp_graph):
    '''
    :param interp_graph:
    :return:
    '''
    sel_nodes = interp_graph.getSelectedNodes()
    if not sel_nodes:
        return

    # Get a pose default name to enter in the text
    interp_name = sel_nodes[0].getName()
    text, ok = g_dialog.get_text('Rename Interp', 'Interp name:', interp_name)

    if not ok:
        return

    text = common.getValidName(text)

    if not text:
        return

    print('Renaming pose [ {} ] --> [ {} ] '.format(interp_name, text))
    rig_psd.renameInterpolator(sel_nodes[0].getAttributeByName('full_name').getValue(),
                               '{}_poseInterpolator'.format(text))
    sel_nodes[0].getAttributeByName('full_name').setValue('{}_poseInterpolator'.format(text))
    sel_nodes[0].setName(text)

    update_primary()

def select_interpolator(interp_graph):
    '''
    This will select the interpolators you have selected in the graph
    '''
    selected_node_list = interp_graph.getSelectedNodes()
    if not selected_node_list:
        return
    # select the nodes
    mc.select(mc.ls([node.getAttributeByName('full_name').getValue() for node in selected_node_list]))

def select_drivers(interp_graph):
    '''
    This will select the interpolators you have selected in the graph
    '''
    selected_node_list = interp_graph.getSelectedNodes()
    if not selected_node_list:
        return

    # select the nodes
    driver_list = list()
    for node in selected_node_list:
        driver_list.extend(rig_psd.getDrivers(node.getAttributeByName('full_name').getValue()))

    mc.select(mc.ls(driver_list))

def set_pose_falloff(interp_graph, pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    if not sel_nodes:
        return

    # Get a pose default name to enter in the text
    pose_name = sel_nodes[0].getAttributeByName('full_name').getValue()
    interp = sel_nodes[0].getAttributeByName('interp').getValue()
    value = str(rig_psd.getPoseFalloff(interp, pose_name))

    text, ok = g_dialog.get_text('Pose Falloff', 'Set Pose Fallof:', value)
    if not ok:
        return

    if not text:
        return

    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()

        print('Setting falloff for pose [ {} ] [ {} ] --> [ {} ] '.format(interp, pose, text))
        rig_psd.setPoseFalloff(interp, pose, float(text))

    update_secondary()

def set_pose_type(interp_graph, pose_graph):
    '''
    This will bring up a list widget that the user can use to set the type of pose they want it to be.
    '''
    sel_nodes = pose_graph.getSelectedNodes()
    if not sel_nodes:
        return
    # get the first index info
    pose_name = sel_nodes[0].getAttributeByName('full_name').getValue()
    interp_name = sel_nodes[0].getAttributeByName('interp').getValue()
    pose_type_index = mc.getAttr('{}.pose[{}].poseType'.format(interp_name, rig_psd.getPoseIndex(interp_name, pose_name)))
    default_item_list = ['swing', 'twist', 'swing and twist']
    index_name_list = ['swing and twist', 'swing', 'twist']
    default_index = default_item_list.index(index_name_list[pose_type_index])
    # pull up the dialog box
    item, ok = g_dialog.get_item('Set Pose Type', 'Pose Type:', default_item_list, default_index)

    if not ok or not item:
        return
    pose_type_index = index_name_list.index(item)
    for pose_node in sel_nodes:
        pose_name = pose_node.getAttributeByName('full_name').getValue()
        interp_name = pose_node.getAttributeByName('interp').getValue()
        print 'setting pose {} on interp {} to pose type {}->{}'.format(pose_name, interp_name, item, pose_type_index)
        mc.setAttr('{}.pose[{}].poseType'.format(interp_name, rig_psd.getPoseIndex(interp_name, pose_name)), pose_type_index)

    update_secondary()

def enable_interpolator_toggle(interp_graph):
    '''
    '''
    mc.undoInfo(openChunk=1)
    try:
        sel_nodes = interp_graph.getSelectedNodes()
        if sel_nodes:
            state = sel_nodes[0].isActive()
            for node in sel_nodes:
                interp = node.getAttributeByName('full_name').getValue()
                if state:
                    node.disable()
                    rig_psd.disableInterp(interp)
                else:
                    node.enable()
                    rig_psd.enableInterp(interp)
        update_secondary()
    except:
        traceback.print_exc()
    mc.undoInfo(closeChunk=1)

def update_pose(pose_graph):
    '''
    This will update the selected poses with whatever the controls that are pose controls on the interpolator.
    :param pose_graph: This is the graph where the poses are being set.
    :type pose_graph: UGraph
    '''
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        rig_psd.updatePose(interp, pose)

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
    symmetry_state = mc.symmetricModelling(q=1, symmetry=1)

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

    if not symmetry_state:
        mc.symmetricModelling(e=1, symmetry=0)

def live_toggle(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    if sel_nodes:
        node = sel_nodes[0]
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        state = rig_psd.poseLiveToggle(interp, pose)
        if state:
            pose_graph.setLiveNode(node)
        else:
            pose_graph.clearLiveNode()

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
    update_secondary()

def duplicate_shape(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    dup_list = []
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        dup_list.extend(rig_psd.duplicatePoseShape(interp, pose) or list())
        node.editOn()

    # unlock attributes on the transforms of duplicates.
    if dup_list:
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        for dup in dup_list:
            for a in attrs:
                mc.setAttr(dup+'.'+a, l=False)

        mc.select(dup_list)

def delta_blend(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        blendshape_list = rig_psd.getDrivenNodes(interp)
        for bs in blendshape_list:
            geo = get_pose_geo_path(bs, interp, pose)
            if not mc.objExists(geo):
                continue
            rig_psd.goToPose(interp, pose)
            rig_delta_blend.delta_blend(geo)

def isolate_shape(pose_graph):
    sel_nodes = pose_graph.getSelectedNodes()
    geos = []
    for node in sel_nodes:
        interp = node.getAttributeByName('interp').getValue()
        pose = node.getAttributeByName('full_name').getValue()
        blendshape_list = rig_psd.getDrivenNodes(interp)
        for bs in blendshape_list:
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

# these are temporary functions
"""
def view_drivers(interp_graph, show=False):
    '''
    show the selected drivers using a list view
    '''
    driver_widget.clear()
    selected_nodes = interp_graph.getSelectedNodes()
    if selected_nodes:
        node_attr = selected_nodes[0].getAttributeByName('full_name')
        pose_control_list = []
        if node_attr:
            # driver list for the first selected interpolator.
            driver_list = rig_psd.getDrivers(selected_nodes[0].getAttributeByName('full_name').getValue()) or []
            driver_widget.addItems(driver_list)
        driver_widget.setWindowTitle('{}: Drivers'.format(selected_nodes[0].getName()))
    else:
        pose_control_widget.addItems([])
    if show:
        driver_widget.show()
    else:
        driver_widget.repaint()
"""
def view_drivers(interp_graph, show=False):
    selected_nodes = interp_graph.getSelectedNodes()

    if selected_nodes:
        interp_attr_list = [node.getAttributeByName('full_name') for node in selected_nodes]
        interp_list = [interp_attr.getValue() for interp_attr in interp_attr_list if interp_attr]
        if interp_list:
            # driver list for the first selected interpolator.
            driver_widget.set_twist(interp_list)

    if show:
        driver_widget.show()
    else:
        driver_widget.repaint()

def view_pose_controls(interp_graph, show=False):
    '''
    show the selected drivers using a list view
    '''
    pose_control_widget.clear()
    selected_nodes = interp_graph.getSelectedNodes()

    if selected_nodes:
        # driver list for the first selected interpolator.
        node_attr = selected_nodes[0].getAttributeByName('full_name')
        pose_control_list = []
        if node_attr:
            pose_control_list = rig_psd.getPoseControls(node_attr.getValue()) or []
            pose_control_widget.addItems(pose_control_list)

        pose_control_widget.setWindowTitle('{}: Pose Controls'.format(selected_nodes[0].getName()))
    else:
        pose_control_widget.addItems([])
    if show:
        pose_control_widget.show()
    else:
        pose_control_widget.repaint()

def view_drivens(interp_graph, show=False):
    driven_widget.clear()
    selected_nodes = interp_graph.getSelectedNodes()

    if selected_nodes:
        # driver list for the first selected interpolator.
        node_attr = selected_nodes[0].getAttributeByName('full_name')
        driven_list = []
        if node_attr:
            driven_list = rig_psd.getDrivenNodes(node_attr.getValue()) or []
            driven_widget.addItems(driven_list)

        driven_widget.setWindowTitle('{}: Drivens'.format(selected_nodes[0].getName()))
    else:
        driven_widget.addItems([])
    if show:
        driven_widget.show()
    else:
        driven_widget.repaint()

def build_interp_graph(interp_graph):
    interp_graph.clearNodes()

    # Connect Click functions
    interp_graph.setClicked(partial(interp_clicked, interp_graph))

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
            blendshape_list = rig_psd.getDrivenNodes(interp)
            for bs in blendshape_list:
                if not mc.objExists('{}.enabled'.format(interp)):
                    mc.addAttr(interp, ln='enabled', at='bool', dv=1)
                    interp_node.enable()
                else:
                    enabled_value = mc.getAttr('{}.enabled'.format(interp))
                    if enabled_value:
                        interp_node.enable()
                    else:
                        interp_node.disable()

    # Radial menu Setup
    interp_graph.setRadialMenuList([
        {'position': 'N', 'text': 'Add Interpolator', 'func': partial(add_interpolator, interp_graph)},
        {'position': 'NW', 'text': 'Rename Interpolator', 'func': partial(rename_interpolator, interp_graph)},
        {'position': 'W', 'text': 'Enable Toggle', 'func': partial(enable_interpolator_toggle, interp_graph)},
        {'position': 'E', 'text': 'All Neutral Pose', 'func': partial(set_all_neutral, interp_graph)},
        {'position': 'S', 'text': 'Select Interpolator', 'func': partial(select_interpolator, interp_graph)},
        {'position': '', 'text': 'Delete Interpolator', 'func': partial(delete_interpolator, interp_graph)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Add Driver', 'func': partial(add_driver, interp_graph)},
        {'position': '', 'text': 'Select Drivers', 'func': partial(select_drivers, interp_graph)},
        {'position': '', 'text': 'View Drivers', 'func': partial(view_drivers, interp_graph, True)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Add Driven', 'func': partial(add_driven, interp_graph)},
        {'position': '', 'text': 'View Drivens', 'func': partial(view_drivens, interp_graph, True)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Add Pose Control', 'func': partial(add_pose_control, interp_graph)},
        {'position': '', 'text': 'View Pose Controls', 'func': partial(view_pose_controls, interp_graph, True)},
        {'position': '', 'text': '-------------', 'func': None},

    ])

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
        if node.getAttributeByName('full_name'):
            interp = node.getAttributeByName('full_name').getValue()
            blendshape_list = rig_psd.getDrivenNodes(interp)
            # (PINGS MAYA)
            try:
                poses = rig_psd.getPoseNames(interp)
            except:
                poses = None
            if not poses:
                continue
            for n in range(len(poses)):
                pose = poses[n]
                pose_weight = rig_psd.getPoseWeight(interp, pose)
                pose_weight = '{:.2f}'.format(round(pose_weight, 2))

                if pose_weight == '-0.00':
                    pose_weight = '0.00'

                pose_weight = '{0:>{1}}'.format(pose_weight, 5)

                # Get pose falloff
                falloff = rig_psd.getPoseFalloff(interp, pose)
                falloff = '{:.1f}'.format(round(falloff, 1))
                pose_data_list.append([pose_weight, pose, falloff, interp, blendshape_list])

    if not pose_data_list:
        return (pose_graph)

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
        pose_weight, pose, falloff, interp, blendshape_list = pose_data_list_pair[i]

        display_name = '  '.join(pose_data_list_justified[i])
        if 'neutral' in pose:
            neutrals.append([display_name, pose, interp])
            continue

        pose_node = pose_graph.addNode(display_name)
        pose_node.addAttribute('interp', interp)
        pose_node.addAttribute('full_name', pose)

        # Live
        for bs in blendshape_list:
            if (bs, pose) in live_poses:
                pose_graph.setLiveNode(pose_node)
                break

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
        display_name, pose, interp = pose
        pose_node = pose_graph.addNode(display_name)
        pose_node.addAttribute('interp', interp)
        pose_node.addAttribute('full_name', pose)

        # Live
        for bs in blendshape_list:
            if (bs, pose) in live_poses:
                pose_graph.setLiveNode(pose_node)
                break

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

    view_pose_controls(interp_graph)
    view_drivers(interp_graph)
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
        {'position': 'N', 'text': 'Live Edit', 'func': partial(live_toggle, pose_graph)},
        {'position': 'W', 'text': 'Enable Toggle', 'func': partial(enable_toggle, pose_graph)},
        {'position': 'S', 'text': 'Apply', 'func': partial(apply_pose, interp_graph, pose_graph)},
        {'position': 'NE', 'text': 'Mirror Deltas', 'func': partial(mirror_delta, pose_graph)},
        {'position': 'NW', 'text': 'Delta Blend', 'func': partial(delta_blend, pose_graph)},
        {'position': 'SE', 'text': 'Isolate Toggle', 'func': partial(isolate_shape, pose_graph)},
        {'position': '', 'text': 'Delete Deltas', 'func': partial(delete_deltas, interp_graph, pose_graph)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Add Pose', 'func': partial(add_pose, interp_graph, pose_graph)},
        {'position': '', 'text': 'Rename Pose', 'func': partial(rename_pose, interp_graph, pose_graph)},
        {'position': '', 'text': 'Delete Pose', 'func': partial(delete_pose, interp_graph, pose_graph)},
        {'position': '', 'text': '-------------', 'func': None},
        {'position': '', 'text': 'Set Pose Falloff', 'func': partial(set_pose_falloff, interp_graph, pose_graph)},
        {'position': '', 'text': 'Set Pose Type', 'func': partial(set_pose_type, interp_graph, pose_graph)},
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
            shape_list = list(set(shape_list + shape))

    if shape_list:
        mc.select(shape_list)

def set_driver_twist_value(interp, index, value):
    mc.setAttr('{}.driver[{}].driverTwistAxis'.format(interp, index), value)

def get_current_twist_value(interp, driver_index):
    return mc.getAttr('{}.driver[{}].driverTwistAxis'.format(interp, driver_index))

def get_drivers(system):
    '''
    wrapper for the UI to use the model so we can create multiple models depending on the DCC
    '''
    return rig_psd.getDrivers(system)

def update_primary_graph(primary_graph):
    '''
    Wrapper to call build graph
    '''
    return build_interp_graph(primary_graph)

def update_secondary_graph(primary_graph, secondary_graph):
    '''
    Wrapper to call build_pose_graph
    '''
    return refresh_pose_graph(primary_graph, secondary_graph)

def refresh_secondary_graph(secondary_graph):
    '''
    Wrapper around secondary_tree_selection_change
    '''
    return secondary_tree_selection_change(secondary_graph)

def init_primary_graph(primary_graph):
    return build_interp_graph(primary_graph)

def init_secondary_graph(primary_graph, secondary_graph):
    return build_pose_graph(primary_graph, secondary_graph)


'''
Data flow

Selecting a interp 

GraphTreeView.pSelectionChanged
    graph_widget._setupTreeView.pSelectionChanged
        graph_widget._primary_tree_selection_change
            graph_widget.update_secondary_graph()
                psd_model_maya.refresh_pose_graph
            graph_widget.update_secondary_graph()

    psd_model_maya.refresh_pose_graph
        graph_widget.update_secondary_graph
'''