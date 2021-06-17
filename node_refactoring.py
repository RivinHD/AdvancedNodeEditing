import json
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
        row = col.row()
        row.label(text= "Fallback Node")
        row.prop(ANE, 'fallback_node', text= "")
classes.append(ANE_PT_NodeRefactoring)

class ANE_OT_Add_FallbackNodeItem(Operator):
    bl_idname = "ane.add_fallbacknodeitem"
    bl_label = "Add Fallback Node Item"
    bl_description = "Add a Fallback Node Item from the selected Node"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        ANE = context.preferences.addons[__package__].preferences
        for area in context.window_manager.windows[0].screen.areas:
            if area.type == 'NODE_EDITOR':
                space_data = area.spaces[0]
                break
        else:
            return False
        return context.object != None and context.object.active_material != None and hasattr(space_data, 'edit_tree') and space_data.edit_tree != None and space_data.edit_tree.nodes.active != None

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        for area in context.window_manager.windows[0].screen.areas:
            if area.type == 'NODE_EDITOR':
                active = area.spaces[0].edit_tree.nodes.active
                break
        ANE.fallback_node_items = 'a{"name": "' + active.bl_rna.name + '", "node": "' + active.bl_idname + '"}'
        ANE['fallback_node'] = len(json.loads(ANE.fallback_node_items)) - 1
        return {"FINISHED"}
classes.append(ANE_OT_Add_FallbackNodeItem)

class ANE_OT_Delete_FallbackNodeItem(Operator):
    bl_idname = "ane.delete_fallbacknodeitem"
    bl_label = "Delete Fallback Node Item"
    bl_description = "Deletes the Fallback Node Item"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        ANE = context.preferences.addons[__package__].preferences
        return len(ANE.fallback_node) - 1 and fc.get_init_enum(ANE, 'fallback_node') != 0

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        ANE.fallback_node_items = "d%s" % fc.get_init_enum(ANE, 'fallback_node')
        ANE['fallback_node'] = 0
        return {"FINISHED"}
classes.append(ANE_OT_Delete_FallbackNodeItem)

class ANE_OT_ExtractNodeValues(Operator):
    bl_idname = "ane.extract_node_values"
    bl_region_type = 'UI'
    bl_category = 'Item' 
    bl_label = "Extract Node Values"

    inputNodes = []
    outputNodes = []
    skip = False

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree != None and context.space_data.edit_tree.nodes.active != None

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        nodes = context.space_data.edit_tree.nodes
        active = nodes.active
        offset = ANE.DistributOffset
        for node in fc.getSelected(nodes):
            node.select = False
        inputNodes = fc.getNodebyNameList(self.inputNodes, nodes)
        if len(inputNodes):
            for node in inputNodes:
                node.select = True
            nodes.active = inputNodes[0]
            ANE.DistributOffset = 0
            bpy.ops.ane.distribute(context.copy(),'INVOKE_DEFAULT', False, Pivot="Bottom")
            for node in inputNodes:
                node.select = False
        outputNodes = fc.getNodebyNameList(self.outputNodes, nodes)
        if len(outputNodes):
            for node in outputNodes:
                node.select = True
            nodes.active = outputNodes[0]
            ANE.DistributOffset = 0
            bpy.ops.ane.distribute(context.copy(),'INVOKE_DEFAULT', False, Pivot="Bottom")
            for node in outputNodes:
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
                if ANE.Fallback == 'None':
                    return None
                return nodes.new(ANE.Fallback)
            return nodes.new(input_node_types[node_type])

        output_node_types = {
            "RGBA": "ShaderNodeEmission",
            "SHADER": "ShaderNodeEmission"
        }

        def create_output_node(node_type):
            ANE = bpy.context.preferences.addons[__package__].preferences
            if node_type not in output_node_types:
                if ANE.Fallback == 'None':
                    return None
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
        self.inputNodes = []
        for i in range(len(active_node.inputs)):
            input = active_node.inputs[i]
            if input.bl_idname == 'NodeSocketVirtual':
                continue
            view_node = create_input_node(input.type)
            if view_node is None:
                continue
            if hasattr(input, "default_value"):
                set_default_output(view_node, input.default_value)
            _x = x - (view_node.width + offset_x)
            view_node.location = (_x, y)
            y -= view_node.height
            output = view_node.outputs[0]
            connect(input, output)
            self.inputNodes.append(view_node.name)

        x, y = active_node.location
        x += active_node.width + offset_x

        # process outputs
        self.outputNodes = []
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
            self.outputNodes.append(view_node.name)
            # connect(input, output)
        last = ANE.SelectionTypeRename
        ANE.SelectionTypeRename = 'A'
        bpy.ops.ane.rename_from_socket()
        ANE.SelectionTypeRename = last
        context.space_data.edit_tree.nodes.active = active_node
        
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
        if context.object == None or context.object.active_material == None or not hasattr(context.space_data, 'edit_tree') or context.space_data.edit_tree is None or context.space_data.edit_tree.nodes.active is None:
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
