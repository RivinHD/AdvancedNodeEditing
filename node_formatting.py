import bpy
from bpy.types import Operator, Panel
from . import functions as fc
from bpy.props import FloatProperty

classes = []

class ANE_PT_Formating(Panel):
    bl_idname = "ANE_PT_Formating"
    bl_label = "Formating"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Advanced Node Editing"

    def draw(self, context):
        layout = self.layout
        ANE = context.preferences.addons[__package__].preferences
        box = layout.box()
        col = box.column(align= True)
        row = col.row(align= True)
        col2 = row.column()
        col2.scale_y = 1.5
        col2.alignment = 'CENTER'
        col2.label(text= 'Main:')
        box2 = row.box()
        box2.scale_x = 2
        box2.label(text= ANE.MainLable)
        col.operator(ANE_OT_SetMain.bl_idname, text= "Set Main")
        box.separator(factor= 0.5) #------------------
        row = box.row(align= True)
        col = row.column(align= True)
        col.scale_x = 1.5
        col.operator(ANE_OT_RenameFromSocket.bl_idname, text= "Rename from Socket")
        row.prop(ANE, 'SelectionTypeRename', text="")
        row = box.row(align= True)
        col = row.column(align= True)
        col.scale_x = 1.5
        col.operator(ANE_OT_SortBySocket.bl_idname, text= "Sort by Socket")
        row.prop(ANE, 'SelectionTypeSort', text="")
        layout.separator(factor= 0.5) #------------------
        layout.operator(ANE_OT_SimplifyGroup.bl_idname, text= "Simplify Group")
        layout.operator(ANE_OT_Ungroup.bl_idname, text= 'Advanced Ungroup')
        layout.operator(ANE_OT_ReplaceWithActive.bl_idname, text= "Replace with Active")   
        obj = context.object  
        if obj != None and obj.active_material != None and hasattr(context.space_data, 'edit_tree'):
            active = context.space_data.edit_tree.nodes.active
            if active != None:
                layout.prop(ANE, 'node_width')
classes.append(ANE_PT_Formating)

class ANE_OT_SetMain(Operator):
    bl_idname = "ane.set_main"
    bl_label = "Set Main"
    bl_description = "Set the active Node as the Main Node"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree.nodes.active != None

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        node_tree = context.space_data.edit_tree
        base = fc.getNodeOfTree(context.object.active_material, node_tree)
        if base.rna_type.name == 'Material':
            active = node_tree.nodes.active
            ANE.MainNode = active.name
            ANE.MainLable = active.name if active.label == '' else active.label
        else:
            active = node_tree.nodes.active
            ANE.MainNode = base.name + "\\/" + active.name
            ANE.MainLable =  (base.name if base.label == '' else base.label) + "/" + (active.name if active.label == '' else active.label)
        return {"FINISHED"}
classes.append(ANE_OT_SetMain)

class ANE_OT_RenameFromSocket(Operator):
    bl_idname = "ane.rename_from_socket"
    bl_label = "Rename From Socket"
    bl_description = "Rename the selected Nodes from the linked Sockets of the Main Input\n(only the first Socket is taken, others are ignored)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        ANE = context.preferences.addons[__package__].preferences
        return ANE.MainNode != "" and context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree')

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        if fc.checkExist(ANE.MainNode, ANE):
            node = fc.getMainNode(ANE.MainNode, context.space_data.edit_tree)
            if ANE.SelectionTypeRename != 'O':
                nodes = []
                for nIn in node.inputs:
                    for link in nIn.links:
                        nodeCurr = link.from_node
                        if ANE.SelectionTypeRename == 'S' and not nodeCurr.select:
                            continue
                        if not (nodeCurr in nodes):
                            nodeCurr.label = nIn.name
                            nodes.append(nodeCurr)
            if ANE.SelectionTypeRename != 'I':
                nodes = []
                for nOut in node.outputs:
                    for link in nOut.links:
                        nodeCurr = link.to_node
                        if ANE.SelectionTypeRename == 'S' and not nodeCurr.select:
                            continue
                        if not (nodeCurr in nodes):
                            nodeCurr.label = nOut.name
                            nodes.append(nodeCurr)
            return {"FINISHED"}
        else:
            context.area.tag_redraw()
            return {"CANCELLED"}
classes.append(ANE_OT_RenameFromSocket)

class ANE_OT_SortBySocket(Operator):
    bl_idname = "ane.sort_by_socket"
    bl_label = "Sort by Socket"
    bl_description = "Sort the attached Nodes by the Socket"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        ANE = context.preferences.addons[__package__].preferences
        return ANE.MainNode != "" and context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree')

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        if fc.checkExist(ANE.MainNode, ANE):
            node = fc.getMainNode(ANE.MainNode, context.space_data.edit_tree)
            if ANE.SelectionTypeSort != 'O':
                nodes = []
                for nIn in node.inputs:
                    for link in nIn.links:
                        nodeCurr = link.from_node
                        if ANE.SelectionTypeSort == 'S' and not nodeCurr.select:
                            continue
                        nodes.append(nodeCurr)
                fc.sortNodeLocation(nodes)
            if ANE.SelectionTypeSort != 'I':
                nodes = []
                for nOut in node.outputs:
                    for link in nOut.links:
                        nodeCurr = link.to_node
                        if ANE.SelectionTypeSort == 'S' and not nodeCurr.select:
                            continue
                        nodes.append(nodeCurr)
                fc.sortNodeLocation(nodes)
            return {"FINISHED"}
        else:
            context.area.tag_redraw()
            return {"CANCELLED"}
classes.append(ANE_OT_SortBySocket)

class ANE_OT_SimplifyGroup(Operator):
    bl_idname = "ane.simplify_group"
    bl_label = "Simplify Group"
    bl_description = "Simplify the group I/O by deleting socket that has the same input/output-socket or are unused"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if context.object == None or context.object.active_material == None or not hasattr(context.space_data, 'edit_tree'):
            return False
        active = context.space_data.edit_tree.nodes.active
        return active != None and active.type == 'GROUP'

    def execute(self, context):
        active = context.space_data.edit_tree.nodes.active
        sockets = []
        offset = 0
        for i in range(len(active.inputs)):
            i -= offset
            nIn = active.inputs[i]
            group = active.node_tree
            inputNode = fc.getGroupPorts(group.nodes, "INPUT")
            if nIn.is_linked:
                for link in nIn.links:
                    socket = link.from_socket
                    if socket in sockets:
                        index = sockets.index(socket)
                        for grouplink in inputNode.outputs[i].links:
                            group.links.new(grouplink.to_socket, inputNode.outputs[index])
                        group.inputs.remove(group.inputs[i])
                        offset += 1 
                    else:
                        sockets.append(socket)
            else:
                if not inputNode.outputs[i].is_linked:
                    group.inputs.remove(group.inputs[i])
                    offset += 1
        sockets = []
        offset = 0
        for i in range(len(active.outputs)):
            i -= offset
            nOut = active.outputs[i]
            group = active.node_tree
            outputNode = fc.getGroupPorts(group.nodes, "OUTPUT")
            nOutGroup = outputNode.inputs[i]
            if nOutGroup.is_linked:
                for grouplink in nOutGroup.links:
                    socket = grouplink.from_socket
                    if socket in sockets:
                        index = sockets.index(socket)
                        for link in nOut.links:
                            context.space_data.edit_tree.links.new(link.to_socket, active.outputs[index])
                        group.outputs.remove(group.outputs[i])
                        offset += 1
                    else:
                        sockets.append(socket)
            else:
                if not outputNode.inputs[i].is_linked:
                    group.outputs.remove(group.outputs[i])
                    offset += 1
        return {"FINISHED"}
classes.append(ANE_OT_SimplifyGroup)

class ANE_OT_ReplaceWithActive(Operator):
    bl_idname = "ane.replace_with_active"
    bl_label = "Replace with Active"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.active_material != None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree.nodes.active != None

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        nodes = node_tree.nodes
        active = nodes.active
        selected = fc.getSelected(nodes, active.name)
        for node in selected:
            new = nodes.new(active.bl_idname)
            fc.copyData(active, new)
            new.location = node.location
            for i in range(len(node.inputs)):
                for link in node.inputs[i].links:
                    if len(new.inputs) > i:
                        node_tree.links.new(new.inputs[i], link.from_socket)
            for i in range(len(node.outputs)):
                for link in node.outputs[i].links:
                    if len(new.outputs) > i:
                        node_tree.links.new(link.to_socket, new.outputs[i])
            nodes.remove(node)
        return {"FINISHED"}
classes.append(ANE_OT_ReplaceWithActive)

class ANE_OT_Ungroup(Operator):
    bl_idname = "ane.ungroup"
    bl_label = "Advanced Ungroup"
    bl_description = "Ungroups the selected group and move I/O-nodes relative to the ungrouped nodes"
    bl_options = {"REGISTER"}

    nodes_input = {}
    nodes_output = {}
    old_loc_x = 0
    skip = False

    @classmethod
    def poll(cls, context):
        if context.object == None or context.object.active_material == None or not hasattr(context.space_data, 'edit_tree'):
            return False
        active = context.space_data.edit_tree.nodes.active
        return active != None and active.type == 'GROUP'

    def execute(self, context):
        # distribute I/O nodes
        nodes = context.space_data.edit_tree.nodes
        left_group_node_loc = fc.sortByLocation(fc.getSelected(nodes), 0, False)[0].location[0]
        input_nodes = fc.getNodebyNameList(self.nodes_input.keys(), nodes)
        i = 0
        for node in input_nodes:
            newloc = left_group_node_loc + self.nodes_input[node.name]
            offset = newloc - node.location[0]
            print(node, left_group_node_loc, self.nodes_input[node.name], newloc)
            node.location[0] = newloc
            for subnode in fc.getSubNodes(node, 'input'):
                subnode.location[0] += offset
                print(subnode, subnode.location[0], offset)
            print(node.location[0])
            i += 1
        right_group_node_loc = fc.sortByLocation(fc.getSelected(nodes), 0, True)[0].location[0]
        output_nodes = fc.getNodebyNameList(self.nodes_output.keys(), nodes)
        i = 0
        for node in output_nodes:
            newloc = right_group_node_loc + self.nodes_output[node.name]
            offset = newloc - node.location[0]
            print(node, right_group_node_loc, self.nodes_output[node.name], newloc)
            node.location[0] = newloc
            for subnode in fc.getSubNodes(node, 'output'):
                subnode.location[0] += offset
                print(subnode, subnode.location[0], offset)
            print(node.location[0])
            i += 1
        return {"FINISHED"}

    def modal(self, context, event):
        if self.skip:
            self.skip = False
            return {'PASS_THROUGH'}
        else:
            return self.execute(context)

    def invoke(self, context, event):
        active = context.space_data.edit_tree.nodes.active
        # save states 
        selected_nodes = fc.getSelected(context.space_data.edit_tree.nodes, active.name)
        for node in selected_nodes:
            node.select = False
        loc = active.location[0]
        self.nodes_offset_input = []
        for inp in active.inputs:
            for link in inp.links:
                node = link.from_node
                self.nodes_input[node.name] = node.location[0] - loc
        self.nodes_offset_output = []
        for out in active.outputs:
            for link in out.links:
                node = link.to_node
                self.nodes_output[node.name] = node.location[0] - loc
        self.old_loc = active.location[0]
        bpy.ops.node.group_ungroup()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0, window=context.window)
        wm.modal_handler_add(self)
        self.skip = True
        return {'RUNNING_MODAL'}
classes.append(ANE_OT_Ungroup)