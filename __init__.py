import bpy
import numpy
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import EnumProperty, StringProperty, FloatProperty, BoolProperty

bl_info = {
    "name" : "Node Formatting",
    "author" : "Rivin",
    "description" : "Allows you to format you Nodes easily",
    "blender" : (2, 80, 9),
    "version" : (0, 0, 2),
    "location" : "Node > UI",
    "category" : "Node"
}

classes = []

def getSelected(nodes, exclude = None):
    l = []
    for node in nodes:
        if node.select and node.name != exclude:
            l.append(node)
    return l

def sortByLocation(nodes, index, reverse):
    return sorted(nodes, key=lambda x: (x.location[index], x.name), reverse= reverse)

def getLow(nodes, index):
    low = nodes[0].location[index] - index * nodes[0].dimensions[index]
    for node in nodes[1:]:
        checkLow = node.location[index] - index * node.dimensions[index]
        if checkLow < low:
            low = checkLow
    return low

def getHeigh(nodes, index):
    high = nodes[0].location[index] + (1 - index) * nodes[0].dimensions[index]
    for node in nodes[1:]:
        checkHigh = node.location[index] + (1 - index) * node.dimensions[index]
        if checkHigh > high:
            high = checkHigh
    return high 

def checkFit(nodes, index, distance):
    for node in nodes:
        distance -= node.dimensions[index]
    return (distance >= 0, distance) 

def distribute(selected, index):
    selected = sortByLocation(selected, index, True)
    heigh = getHeigh(selected, index)
    low = getLow(selected, index)
    check, space = checkFit(selected, index, heigh - low)
    if check:
        singleSpace = space/(len(selected) - 1)
        loc = selected[0].location[index]
        for node in selected:
            node.location[index] = loc
            loc -= node.dimensions[index] + singleSpace
    else:
        loc = selected[0].location[index] + space * -0.5
        for node in selected:
            node.location[index] = loc
            loc -= node.dimensions[index]
        

class NF_PT_AligmentAndDistribut(Panel):
    bl_idname = "NF_PT_Aligment_and_Distribut"
    bl_label = "Aligment & Distribut"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node Formating"

    def draw(self, context):
        layout = self.layout
        nodes = bpy.context.object.active_material.node_tree.nodes
        NF = context.preferences.addons[__name__].preferences
        row = layout.row()
        col = row.column()
        col.alignment = 'CENTER'
        col.scale_y = 1.5
        col.label(text= 'Active: ')
        box = row.box()
        box.scale_x = 1.6
        if nodes.active != None:
            box.label(text= nodes.active.name if nodes.active.label == '' else nodes.active.label)
        row = layout.row()
        box = layout.box()
        row = box.row()
        row.label(text= "Algin")
        row = box.row()
        row.label(text= "X-Axis:")
        row2 = row.row(align= True)
        row2.scale_x = 4
        row2.scale_y = 1.1
        ops = row2.operator(NF_OT_ALign.bl_idname, text= '', icon= 'ANCHOR_LEFT')
        ops.Axis = 'X'
        ops.Aligment = 'Left'
        ops = row2.operator(NF_OT_ALign.bl_idname, text= '', icon= 'ANCHOR_CENTER')
        ops.Axis = 'X'
        ops.Aligment = 'Center'
        ops = row2.operator(NF_OT_ALign.bl_idname, text= '', icon= 'ANCHOR_RIGHT')
        ops.Axis = 'X'
        ops.Aligment = 'Right'
        row = box.row()
        row.label(text= "Y-Axis:")
        row2 = row.row(align= True)
        row2.scale_x = 4
        row2.scale_y = 1.1
        ops = row2.operator(NF_OT_ALign.bl_idname, text= '', icon= 'ANCHOR_TOP')
        ops.Axis = 'Y'
        ops.Aligment = 'Top'
        ops = row2.operator(NF_OT_ALign.bl_idname, text= '', icon= 'ANCHOR_CENTER')
        ops.Axis = 'Y'
        ops.Aligment = 'Center'
        ops = row2.operator(NF_OT_ALign.bl_idname, text= '', icon= 'ANCHOR_BOTTOM')
        ops.Axis = 'Y'
        ops.Aligment = 'Bottom'

        box = layout.box()
        row = box.row()
        row.separator(factor= 0.5)
        row = box.row()
        row.label(text= "Distribut")
        col = row.column()
        col.scale_x = 1.3
        col.prop(NF, 'DistributOffset')
        row = box.row()
        col = row.column()
        col.label(text= "Space")
        col.operator(NF_OT_Distribute.bl_idname, text= "", icon= 'SNAP_EDGE').Pivot = 'Vertical'
        col.operator(NF_OT_Distribute.bl_idname, text= "", icon= 'PAUSE').Pivot = 'Horizontal'
        flow = row.grid_flow(row_major= True, columns= 3, even_columns= True, even_rows= True)
        flow.label(text= "")
        flow.operator(NF_OT_Distribute.bl_idname, text= "", icon= 'ANCHOR_TOP').Pivot = 'Top'
        flow.label(text= "")
        flow.operator(NF_OT_Distribute.bl_idname, text= "", icon='ANCHOR_LEFT').Pivot = 'Left'
        flow.label(text= "")
        flow.operator(NF_OT_Distribute.bl_idname, text= "", icon= 'ANCHOR_RIGHT').Pivot = 'Right'
        flow.label(text= "")
        flow.operator(NF_OT_Distribute.bl_idname, text= "", icon= 'ANCHOR_BOTTOM').Pivot = 'Bottom'
        flow.label(text= "")

classes.append(NF_PT_AligmentAndDistribut)

class NF_OT_ALign(Operator):
    bl_idname = "nf.align"
    bl_label = "Align Node"
    bl_description = "Align the selected Nodes relative to the active Node"
    bl_options = {"REGISTER"}

    Axis : EnumProperty(items= [("X", "X", ''), ("Y", "Y", "")], name= "Axis")
    aligmentsItems = [  ("Top", "Top", ""),
                        ("Bottom", "Bottom", ""),
                        ("Center", "Center", ""),
                        ("Right", "Right", ""),
                        ("Left", "Left", "")]
    Aligment : EnumProperty(items= aligmentsItems, name="Aligment")

    @classmethod
    def poll(cls, context):
        return context.object.active_material.node_tree.nodes.active != None

    def execute(self, context):
        nodes = bpy.context.object.active_material.node_tree.nodes
        active = nodes.active
        selected = getSelected(nodes, active.name)
        aligment = 0 if self.Axis == 'X' else 1
        loc = active.location[aligment]
        length = active.dimensions[aligment]
        #Pivot of Node is Top-Left
        if self.Aligment == 'Top' or self.Aligment == "Left":
            for node in selected:
                node.location[aligment] = loc
        elif self.Aligment == 'Center':
            for node in selected:
                node.location[aligment] = loc - (2 * aligment - 1) * (length - node.dimensions[aligment]) * 0.5
        else:
            for node in selected:
                node.location[aligment] = loc - ( 2 * aligment - 1) * (length - node.dimensions[aligment])
        return {"FINISHED"}
classes.append(NF_OT_ALign)

class NF_OT_Distribute(Operator):
    bl_idname = "nf.distribute"
    bl_label = "Distribute"
    bl_description = "Distribute the selected Nodes relativ to the active Node"
    bl_options = {"REGISTER"}

    pivotItems = [  ("Left", "Left", ""),
                    ("Right", "Right", ""),
                    ("Top", "Top", ""),
                    ("Bottom", "Bottom", ""),
                    ("Vertical", "Vertical", ""),
                    ("Horizontal", "Horizontal", "")]
    Pivot : EnumProperty(items= pivotItems, name= "pivot")

    @classmethod
    def poll(cls, context):
        return context.object.active_material.node_tree.nodes.active != None

    def execute(self, context):
        NF = context.preferences.addons[__name__].preferences
        nodes = bpy.context.object.active_material.node_tree.nodes
        if not (self.Pivot == "Vertical" or self.Pivot == "Horizontal"):
            offset = NF.DistributOffset
            active = nodes.active
            selected = getSelected(nodes, active.name)
            if self.Pivot == 'Left':
                selected = sortByLocation(selected, 0, True)
                loc = active.location[0]
                for node in selected:
                    node.location[0] = loc - offset - node.dimensions[0]
                    loc = node.location[0]
            elif self.Pivot == 'Right':
                selected = sortByLocation(selected, 0, False)
                loc = active.location[0] + active.dimensions[0]
                for node in selected:
                    node.location[0] = loc + offset
                    loc = node.location[0] + node.dimensions[0]
            elif self.Pivot == 'Top':
                selected = sortByLocation(selected, 1, False)
                loc = active.location[1]
                for node in selected:
                    node.location[1] = loc + offset + node.dimensions[1]
                    loc = node.location[1]
            else:
                selected = sortByLocation(selected, 1, True)
                loc = active.location[1] - active.dimensions[1]
                for node in selected:
                    node.location[1] = loc - offset
                    loc = node.location[1] - node.dimensions[1]
        else:
            selected = getSelected(nodes)
            if self.Pivot == 'Vertical':
                distribute(selected, 1)
            else:
                distribute(selected, 0)
        return {"FINISHED"}
classes.append(NF_OT_Distribute)

#--------------------------------------------

def checkExist(Name, NF):
    if bpy.context.object.active_material.node_tree.nodes.find(Name) != -1:
        return True
    else:
        NF.MainNode = ""
        NF.MainLabel = ""
        return False

def getDistances(nodes, index):
    l = [0]
    for i in range(len(nodes) - 1):
        l.append(nodes[i].location[index] - nodes[i].dimensions[index] - nodes[i + 1].location[index])
    return l

def sortNodeLocation(nodes):
    if len(nodes) <= 0:
        return
    nodes = list(dict.fromkeys(nodes))
    nodesLoc = sortByLocation(nodes, 1, True)
    nodesDistances = getDistances(nodesLoc, 1)
    loc = nodesLoc[0].location[1]
    nodes[0].location[1] = loc
    for i in range(1, len(nodesLoc)):
        loc -= nodes[i - 1].dimensions[1] + nodesDistances[i]
        nodes[i].location[1] = loc

def getGroupPorts(nodes, port):
    groupType = "GROUP_" + port
    for node in nodes:
        if node.type == groupType:
            return node

class NF_PT_Formating(Panel):
    bl_idname = "NF_PT_Formating"
    bl_label = "Formating"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node Formating"

    def draw(self, context):
        layout = self.layout
        NF = context.preferences.addons[__name__].preferences
        box = layout.box()
        col = box.column(align= True)
        row = col.row(align= True)
        col2 = row.column()
        col2.scale_y = 1.5
        col2.alignment = 'CENTER'
        col2.label(text= 'Main: ')
        box2 = row.box()
        box2.scale_x = 1.6
        box2.label(text= NF.MainLable)
        col.operator(NF_OT_SetMain.bl_idname, text= "Set Main")
        box.separator(factor= 0.5) #------------------
        row = box.row(align= True)
        col = row.column(align= True)
        col.scale_x = 1.5
        ops = col.operator(NF_OT_RenameFromSocket.bl_idname, text= "Rename from Socket")
        row.prop(NF, 'SelectionTypeRename', text="")
        row = box.row(align= True)
        col = row.column(align= True)
        col.scale_x = 1.5
        ops = col.operator(NF_OT_SortBySocket.bl_idname, text= "Sort by Socket")
        row.prop(NF, 'SelectionTypeSort', text="")
        layout.separator(factor= 0.5) #------------------
        box = layout.box()
        box.operator(NF_OT_SimplifyGroup.bl_idname, text= "Simplify Group")
classes.append(NF_PT_Formating)

class NF_OT_SetMain(Operator):
    bl_idname = "nf.set_main"
    bl_label = "Set Main"
    bl_description = "Set the active Node as the Main Node"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object.active_material.node_tree.nodes.active != None

    def execute(self, context):
        NF = context.preferences.addons[__name__].preferences
        active = context.object.active_material.node_tree.nodes.active
        NF.MainNode = active.name
        NF.MainLable = active.name if active.label == '' else active.label
        return {"FINISHED"}
classes.append(NF_OT_SetMain)

class NF_OT_RenameFromSocket(Operator):
    bl_idname = "nf.rename_from_socket"
    bl_label = "Rename From Socket"
    bl_description = "Rename the selected Nodes from the linked Sockets of the Main Input\n(only the first Socket is taken, others are ignored)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        NF = context.preferences.addons[__name__].preferences
        return NF.MainNode != ""

    def execute(self, context):
        NF = context.preferences.addons[__name__].preferences
        if checkExist(NF.MainNode, NF):
            node = context.object.active_material.node_tree.nodes[NF.MainNode]
            if NF.SelectionTypeRename != 'O':
                nodes = []
                for nIn in node.inputs:
                    for link in nIn.links:
                        nodeCurr = link.from_node
                        if NF.SelectionTypeRename == 'S' and not nodeCurr.select:
                            continue
                        if not (nodeCurr in nodes):
                            nodeCurr.label = nIn.name
                            nodes.append(nodeCurr)
            if NF.SelectionTypeRename != 'I':
                nodes = []
                for nOut in node.outputs:
                    for link in nOut.links:
                        nodeCurr = link.to_node
                        if NF.SelectionTypeRename == 'S' and not nodeCurr.select:
                            continue
                        if not (nodeCurr in nodes):
                            nodeCurr.label = nOut.name
                            nodes.append(nodeCurr)
            return {"FINISHED"}
        else:
            return {"CANCELLED"}
classes.append(NF_OT_RenameFromSocket)

class NF_OT_SortBySocket(Operator):
    bl_idname = "nf.sort_by_socket"
    bl_label = "Sort by Socket"
    bl_description = "Sort the attached Nodes by the Socket"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        NF = context.preferences.addons[__name__].preferences
        return NF.MainNode != ""

    def execute(self, context):
        NF = context.preferences.addons[__name__].preferences
        if checkExist(NF.MainNode, NF):
            node = context.object.active_material.node_tree.nodes[NF.MainNode]
            if NF.SelectionTypeSort != 'O':
                nodes = []
                for nIn in node.inputs:
                    for link in nIn.links:
                        nodeCurr = link.from_node
                        if NF.SelectionTypeSort == 'S' and not nodeCurr.select:
                            continue
                        nodes.append(nodeCurr)
                sortNodeLocation(nodes)
            if NF.SelectionTypeSort != 'I':
                nodes = []
                for nOut in node.outputs:
                    for link in nOut.links:
                        nodeCurr = link.to_node
                        if NF.SelectionTypeSort == 'S' and not nodeCurr.select:
                            continue
                        nodes.append(nodeCurr)
                sortNodeLocation(nodes)
            return {"FINISHED"}
        else:
            return {"CANCELLED"}
classes.append(NF_OT_SortBySocket)

class NF_OT_SimplifyGroup(bpy.types.Operator):
    bl_idname = "nf.simplify_group"
    bl_label = "Simplify Group"
    bl_description = "Simplify the group I/O by deleting socket that has the same input/output-socket or are unused"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        active = context.object.active_material.node_tree.nodes.active
        return active != None and active.type == 'GROUP'

    def execute(self, context):
        active = context.object.active_material.node_tree.nodes.active
        sockets = []
        offset = 0
        for i in range(len(active.inputs)):
            i -= offset
            nIn = active.inputs[i]
            group = active.node_tree
            inputNode = getGroupPorts(group.nodes, "INPUT")
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
            outputNode = getGroupPorts(group.nodes, "OUTPUT")
            nOutGroup = outputNode.inputs[i]
            if nOutGroup.is_linked:
                for grouplink in nOutGroup.links:
                    socket = grouplink.from_socket
                    if socket in sockets:
                        index = sockets.index(socket)
                        for link in nOut.links:
                            context.object.active_material.node_tree.links.new(link.to_socket, active.outputs[index])
                        group.outputs.remove(group.outputs[i])
                        offset += 1
                    else:
                        sockets.append(socket)
            else:
                if not outputNode.inputs[i].is_linked:
                    group.outputs.remove(group.outputs[i])
                    offset += 1
        return {"FINISHED"}
classes.append(NF_OT_SimplifyGroup)

class NF_OT_ReplaceWithActive(bpy.types.Operator):
    bl_idname = "nf.replace_with_active"
    bl_label = "Replace with Active"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object.active_material.node_tree.nodes.active != None

    def execute(self, context):
        
        return {"FINISHED"}


class NF_Prop(AddonPreferences):
    bl_idname = __name__

    MainNode : StringProperty(name= "Main Node", default= "")
    MainLable : StringProperty(name= "Main Lable", default= "")
    selectionItems = [("I", "Inputs", ""), ("O", "Output", ""), ("A", "All", ""), ("S", "Selection", "")]
    SelectionTypeRename : EnumProperty(items= selectionItems)
    SelectionTypeSort : EnumProperty(items= selectionItems)
    DistributOffset : FloatProperty(name= "Offset", default= 1)
classes.append(NF_Prop)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("-------- Registered Node Formating --------")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("-------- Unregistered Node Formating --------")
