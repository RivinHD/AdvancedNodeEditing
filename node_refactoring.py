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
        layout = self.layout
        layout.operator(ANE_OT_TransferGroupInputValue.bl_idname)
        layout.operator(ANE_OT_ExtractNodeValues.bl_idname)
classes.append(ANE_PT_NodeRefactoring)

class ANE_OT_ExtractNodeValues(Operator):
    bl_idname = "ane.extract_node_values"
    bl_region_type = 'UI' #des Nキーのメニュー
    bl_category = 'Item' 
    bl_label = "Extract Node Values"

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.active_material.node_tree.nodes.active != None

    def execute(self, context):
        active_material = bpy.context.object.active_material
        node_tree = active_material.node_tree
        nodes = node_tree.nodes

        active_node = bpy.context.object.active_material.node_tree.nodes.active

        input_node_types = {
            "RGBA": "ShaderNodeRGB",
            "VALUE": "ShaderNodeValue",
            "VECTOR": "ShaderNodeTexCoord",
        }

        def create_input_node(node_type):
            if node_type not in input_node_types:
                return "NodeReroute"
            node = nodes.new(input_node_types[node_type])
            return node

        output_node_types = {
            "RGBA": "ShaderNodeEmission",
            "SHADER": "ShaderNodeEmission",
            "VECTOR": "NodeReroute",
        }

        def create_output_node(node_type):
            if node_type not in output_node_types:
                return "NodeReroute"
            node = nodes.new(output_node_types[node_type])
            return node

        def set_default_output(node, value):
            node.outputs[0].default_value = value

        def connect(input, output):
            node_tree.links.new(input, output)

        def auto_connect_to_input(output, node):
            for input in node.inputs:
                if input.type == output.type or node.type == 'REROUTE':
                    connect(input, output)
                    return

        offset_x = 50
        offset_y = 50

        x, y = active_node.location

        # process inputs
        for i in range(len(active_node.inputs)):
            input = active_node.inputs[i]
            view_node = create_input_node(input.type)
            set_default_output(view_node, input.default_value)
            _x = x - (view_node.width + offset_x)
            _y = y
            y -= view_node.height + offset_y
            view_node.location = (_x, _y)
            output = view_node.outputs[0]
            connect(input, output)

        x, y = active_node.location
        x += active_node.width + offset_x

        # process outputs
        for i in range(len(active_node.outputs)):
            output = active_node.outputs[i]
            view_node = create_output_node(output.type)
            if view_node is None:
                continue
            _x = x
            _y = y
            y -= view_node.height + offset_y
            view_node.location = (_x, _y)
            input = view_node.inputs[0]
            auto_connect_to_input(output, view_node)
            # connect(input, output)
        return {'FINISHED'}
classes.append(ANE_OT_ExtractNodeValues)

class ANE_OT_TransferGroupInputValue(Operator):
    bl_idname = "ane.transfer_groupinput_value"
    bl_label = "Transfer Group-Input Value"

    @classmethod
    def poll(cls, context):
        if context.object == None:
            return False
        active = context.object.active_material.node_tree.nodes.active
        return active != None and active.type == 'GROUP'

    def execute(self, context):
        node_group_instance = bpy.context.object.active_material.node_tree.nodes.active
        if node_group_instance.bl_idname != "ShaderNodeGroup":
            raise ValueError("select ShaderNodeGroup.")
        node_group_input = fc.find_node_input(node_group_instance.node_tree.nodes)
        for socket_index, output in enumerate(node_group_input.outputs):
            if output.bl_idname == "NodeSocketVirtual":
                continue
            fc.transfer_output_value(output, node_group_instance.inputs[socket_index].default_value)
        return {'FINISHED'}
classes.append(ANE_OT_TransferGroupInputValue)
