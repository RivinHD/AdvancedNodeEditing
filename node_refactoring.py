import bpy
from bpy.types import Operator, Panel
from . import functions as fc

classes = []

class ANE_PT_NodeRefactoring(Panel):
    bl_idname = "ANE_PT_NodeRefactoring"
    bl_label = "Node Refactoring"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Advanced Node Editing"

    def draw(self, context):
        ANE = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.operator(ANE_OT_TransferGroupInputValue.bl_idname)
        layout.operator(ANE_OT_ExtractNodeValues.bl_idname)
        col = layout.column(align= True)
        col.prop(ANE, 'FallbackName')
        col.operator(ANE_OT_SetFallbackNode.bl_idname)
classes.append(ANE_PT_NodeRefactoring)

class ANE_OT_SetFallbackNode(bpy.types.Operator):
    bl_idname = "ane.set_fallback_node"
    bl_label = "Set Fallback Node"
    bl_description = "Set the fallback Node. The fallnack Node is used, when no I/O Node could be addded"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree.nodes.active != None

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        active = context.space_data.edit_tree.nodes.active
        ANE.Fallback = active.bl_idname
        ANE.FallbackName = active.bl_rna.name
        return {"FINISHED"}
classes.append(ANE_OT_SetFallbackNode)

class ANE_OT_ExtractNodeValues(Operator):
    bl_idname = "ane.extract_node_values"
    bl_region_type = 'UI' #des Nキーのメニュー
    bl_category = 'Item' 
    bl_label = "Extract Node Values"

    inputNodes = []
    outputNodes = []
    skip = False

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree.nodes.active != None

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        nodes = context.space_data.edit_tree.nodes
        active = nodes.active
        offset = ANE.DistributOffset
        for node in fc.getSelected(nodes):
            node.select = False
        if len(self.inputNodes):
            for node in self.inputNodes:
                node.select = True
            nodes.active = self.inputNodes[0]
            ANE.DistributOffset = 0
            bpy.ops.ane.distribute('INVOKE_DEFAULT', Pivot="Bottom")
            for node in self.inputNodes:
                node.select = False
        if len(self.outputNodes):
            for node in self.outputNodes:
                node.select = True
            nodes.active = self.outputNodes[0]
            ANE.DistributOffset = 0
            bpy.ops.ane.distribute('INVOKE_DEFAULT', Pivot="Bottom")
            for node in self.outputNodes:
                node.select = False
        nodes.active = active
        ANE.DistributOffset = offset
        return {'FINISHED'}

    def modal(self, context, event):
        if self.skip:
            self.skip = False
            return {'PASS_THROUGH'}
        else:
            return self.execute(context)

    def invoke(self, context, event):
        ANE = context.preferences.addons[__package__].preferences
        node_tree = context.space_data.edit_tree
        nodes = node_tree.nodes
        active_node = context.space_data.edit_tree.nodes.active
        bpy.ops.ane.set_main()
        input_node_types = {
            "RGBA": "ShaderNodeRGB",
            "VALUE": "ShaderNodeValue",
            "VECTOR": "ShaderNodeTexCoord",
        }

        def create_input_node(node_type):
            ANE = bpy.context.preferences.addons[__package__].preferences
            if node_type not in input_node_types:
                return nodes.new(ANE.Fallback)
            return nodes.new(input_node_types[node_type])

        output_node_types = {
            "RGBA": "ShaderNodeEmission",
            "SHADER": "ShaderNodeEmission"
        }

        def create_output_node(node_type):
            ANE = bpy.context.preferences.addons[__package__].preferences
            if node_type not in output_node_types:
                return nodes.new(ANE.Fallback)
            return nodes.new(output_node_types[node_type])

        def set_default_output(node, value):
            node.outputs[0].default_value = value

        def connect(input, output):
            node_tree.links.new(input, output)

        def auto_connect_to_input(output, node):
            ANE = bpy.context.preferences.addons[__package__].preferences
            for input in node.inputs:
                if input.type == output.type or node.bl_idname == ANE.Fallback:
                    connect(input, output)
                    return

        x, y = active_node.location
        offset_x = 50

        newNodes = []
        # process inputs
        for i in range(len(active_node.inputs)):
            input = active_node.inputs[i]
            if input.bl_idname == 'NodeSocketVirtual':
                continue
            view_node = create_input_node(input.type)
            if hasattr(input, "default_value"):
                set_default_output(view_node, input.default_value)
            _x = x - (view_node.width + offset_x)
            view_node.location = (_x, y)
            y -= view_node.height
            output = view_node.outputs[0]
            connect(input, output)
            self.inputNodes.append(view_node)

        x, y = active_node.location
        x += active_node.width + offset_x

        # process outputs
        for i in range(len(active_node.outputs)):
            output = active_node.outputs[i]
            if output.bl_idname == 'NodeSocketVirtual':
                continue
            view_node = create_output_node(output.type)
            if view_node is None:
                continue
            view_node.location = (x, y)
            y -= view_node.height
            input = view_node.inputs[0]
            auto_connect_to_input(output, view_node)
            self.outputNodes.append(view_node)
            # connect(input, output)
        last = ANE.SelectionTypeRename
        ANE.SelectionTypeRename = 'A'
        bpy.ops.ane.rename_from_socket()
        ANE.SelectionTypeRename = last
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0, window=context.window)
        wm.modal_handler_add(self)
        self.skip = True
        return {'RUNNING_MODAL'}
classes.append(ANE_OT_ExtractNodeValues)

class ANE_OT_TransferGroupInputValue(Operator):
    bl_idname = "ane.transfer_groupinput_value"
    bl_label = "Transfer Group-Input Value"

    @classmethod
    def poll(cls, context):
        if context.object == None or context.object.active_material == None or not hasattr(context.space_data, 'edit_tree'):
            return False
        active = context.space_data.edit_tree.nodes.active
        return active != None and active.type == 'GROUP'

    def execute(self, context):
        node_group_instance = context.space_data.edit_tree.nodes.active
        if node_group_instance.bl_idname != "ShaderNodeGroup":
            self.report({'ERROR'}, "select ShaderNodeGroup")
            return {"CANCELLED"}
        node_group_input = fc.find_node_input(node_group_instance.node_tree.nodes)
        for socket_index, output in enumerate(node_group_input.outputs):
            if hasattr(output, 'default_value'):
                fc.transfer_output_value(output, node_group_instance.inputs[socket_index])
        return {'FINISHED'}
classes.append(ANE_OT_TransferGroupInputValue)
