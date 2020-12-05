import bpy
from bpy.types import Operator, Panel, UIList
from bpy.props import EnumProperty
from . import functions as fc

classes = []

class ANE_PT_AdvancedEdit(Panel):
    bl_idname = "ANE_PT_AdvancedEdit"
    bl_label = "Advanced"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node"

    @classmethod
    def poll(cls, context):
        active = bpy.context.object.active_material.node_tree.nodes.active
        return bpy.ops.node.tree_path_parent.poll() and (active.node_tree.active_output != -1 or active.node_tree.active_input != -1)

    def draw(self, context):
        layout = self.layout
        ANE = context.preferences.addons[__package__].preferences
        activeNode = context.object.active_material.node_tree.nodes.active
        active = activeNode.node_tree
        row = layout.row(align= True)
        col = row.column(align= True)
        col.scale_x = 3
        col.prop(ANE, 'NodeSockets', text= "Socket")
        row.operator(ANE_OT_GetTypeOfSelected.bl_idname, text= '', icon= 'EYEDROPPER')
        layout.operator(ANE_OT_Apply.bl_idname, text= 'Apply')
classes.append(ANE_PT_AdvancedEdit)

class ANE_OT_GetTypeOfSelected(Operator):
    bl_idname = "ane.get_type_of_selected"
    bl_label = "Get Type of Selected"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        active = bpy.context.object.active_material.node_tree.nodes.active
        return bpy.ops.node.tree_path_parent.poll() and (active.node_tree.active_output != -1 or active.node_tree.active_input != -1)

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        active = bpy.context.object.active_material.node_tree.nodes.active.node_tree
        port, socket, index = fc.getPort(active)
        ANE.NodeSockets = fc.getDefaultSocket(active, port, index)
        return {"FINISHED"}
classes.append(ANE_OT_GetTypeOfSelected)

class ANE_OT_Apply(Operator):
    bl_idname = "ane.apply"
    bl_label = "Apply"
    bl_description = "Apply chanes"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        active = bpy.context.object.active_material.node_tree.nodes.active
        return bpy.ops.node.tree_path_parent.poll() and (active.node_tree.active_output != -1 or active.node_tree.active_input != -1)

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        activeNode = context.object.active_material.node_tree.nodes.active
        active = activeNode.node_tree
        port, socket, index = fc.getPort(active)
        socketType = ANE.NodeSockets

        #Copy Data
        new = socket.new(socketType, port.name)
        default = eval("bpy.types." + socketType + ".bl_rna.properties['default_value']")
        try:
            if port.is_output:
                activeNode.outputs[-1].default_value = activeNode.outputs[index].default_value
            else:
                activeNode.inputs[-1].default_value = activeNode.inputs[index].default_value
        except:
            if default.is_array:
                new.default_value = default.default_array
            else:
                new.default_value = default.default
        try:
            new.min_value = port.min_value
            new.max_value = port.max_value
        except:
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