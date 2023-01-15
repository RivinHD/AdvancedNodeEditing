import bpy
from bpy.types import Operator, Panel
from . import functions as fc

classes = []


class ANE_PT_Input_AdvancedEdit(Panel):
    bl_idname = "ANE_PT_Input_AdvancedEdit"
    bl_label = "Advanced"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node"

    @classmethod
    def poll(cls, context):
        if not bpy.ops.node.tree_path_parent.poll() or not hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree != None:
            return False
        active = fc.getNodeOfTree(
            context.object.active_material, context.space_data.edit_tree)
        return active and active.type == 'GROUP' and bpy.ops.node.tree_path_parent.poll() and (active.node_tree.active_output != -1 or active.node_tree.active_input != -1)

    def draw(self, context):
        layout = self.layout
        ANE = context.preferences.addons[__package__].preferences
        activeNode = fc.getNodeOfTree(
            context.object.active_material, context.space_data.edit_tree)
        row = layout.row(align=True)
        row.prop(ANE, 'NodeType', expand=True)
        row = layout.row(align=True)
        col = row.column(align=True)
        col.scale_x = 3
        col.prop(ANE, 'NodeSockets', text="Socket")
        row.operator(ANE_OT_GetTypeOfSelected.bl_idname,
                     text='', icon='EYEDROPPER')
        layout.operator(ANE_OT_Apply.bl_idname, text='Apply')


classes.append(ANE_PT_Input_AdvancedEdit)


class ANE_OT_GetTypeOfSelected(Operator):
    bl_idname = "ane.get_type_of_selected"
    bl_label = "Get Type of Selected"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if not bpy.ops.node.tree_path_parent.poll() or not hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree != None:
            return False
        active = fc.getNodeOfTree(
            context.object.active_material, context.space_data.edit_tree)
        return active and active.type == 'GROUP' and bpy.ops.node.tree_path_parent.poll() and (active.node_tree.active_output != -1 or active.node_tree.active_input != -1)

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        active = fc.getNodeOfTree(
            context.object.active_material, context.space_data.edit_tree).node_tree
        nodetype = ANE.NodeType
        port, socket, index = fc.getPort(active, nodetype)
        ANE.NodeSockets = fc.getDefaultSocket(active, port, index)
        return {"FINISHED"}


classes.append(ANE_OT_GetTypeOfSelected)


class ANE_OT_Apply(Operator):
    bl_idname = "ane.apply"
    bl_label = "Apply"
    bl_description = "Apply Type"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if not bpy.ops.node.tree_path_parent.poll() or not hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree != None:
            return False
        active = fc.getNodeOfTree(
            context.object.active_material, context.space_data.edit_tree)
        return active and active.type == 'GROUP' and bpy.ops.node.tree_path_parent.poll() and (active.node_tree.active_output != -1 or active.node_tree.active_input != -1)

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        activeNode = fc.getNodeOfTree(
            context.object.active_material, context.space_data.edit_tree)
        active = activeNode.node_tree
        nodetype = ANE.NodeType
        port, socket, index = fc.getPort(active, nodetype)
        socketType = ANE.NodeSockets

        # Copy Data
        new = socket.new(socketType, port.name)
        props = getattr(bpy.types, socketType).bl_rna.properties
        if props.find('default_value') != -1:
            default = props['default_value']
        else:
            default = None
        try:
            if port.is_output:
                activeNode.outputs[-1].default_value = activeNode.outputs[index].default_value
            else:
                activeNode.inputs[-1].default_value = activeNode.inputs[index].default_value
        except TypeError:
            if default != None:
                if hasattr(default, 'is_array') and default.is_array:
                    new.default_value = default.default_array
                else:
                    new.default_value = default.default
        try:
            new.min_value = port.min_value
            new.max_value = port.max_value
        except AttributeError:
            if hasattr(new, 'min_value'):
                new.min_value = default.soft_min
                new.max_value = default.soft_max

        # Copy Links
        portType = 'OUTPUT' if new.is_output else 'INPUT'
        node = fc.findNodeOfSocket(active.nodes, portType)
        if portType == 'OUTPUT':
            nodeSocket = node.inputs
            nodePort = nodeSocket[index]
            for link in nodePort.links:
                active.links.new(nodeSocket[-2], link.from_socket)
        else:
            nodeSocket = node.outputs
            nodePort = nodeSocket[index]
            for link in nodePort.links:
                active.links.new(link.to_socket, nodeSocket[-2])

        # Move Socket
        socket.move(len(socket) - 1, index)
        socket.remove(port)
        if portType == 'OUTPUT':
            active.active_output = index
        else:
            active.active_input = index
        return {"FINISHED"}


classes.append(ANE_OT_Apply)
