import bpy
from bpy.types import Operator, Panel
from bpy.props import EnumProperty, BoolProperty, IntProperty
from . import functions as fc
from . import update
import json

classes = []


class ANE_PT_AligmentAndDistribut(Panel):
    bl_idname = "ANE_PT_Aligment_and_Distribut"
    bl_label = "Aligment & Distribut"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Advanced Node Editing"

    def draw(self, context):
        layout = self.layout
        ANE = context.preferences.addons[__package__].preferences
        if ANE.AutoUpdate and ANE.Update:
            box = layout.box()
            box.label(text="A new Version is available (" + ANE.Version + ")")
            box.operator(update.ANE_OT_Update.bl_idname, text="Update")
        row = layout.row(align=True)
        col = row.column()
        col.alignment = 'CENTER'
        col.scale_y = 1.5
        col.label(text='Active: ')
        box = row.box()
        box.scale_x = 1.6
        if hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree is not None and context.space_data.edit_tree.nodes.active is not None:
            active = context.space_data.edit_tree.nodes.active
            box.label(text=active.name if active.label == '' else active.label)
        else:
            box.label(text="")
        row = layout.row()
        box = layout.box()
        row = box.row()
        row.label(text="Algin")
        row = box.row()
        row.label(text="X-Axis:")
        row2 = row.row(align=True)
        row2.scale_x = 4
        row2.scale_y = 1.1
        ops = row2.operator(ANE_OT_ALign.bl_idname,
                            text='', icon='ANCHOR_LEFT')
        ops.Axis = 'X'
        ops.Aligment = 'Left'
        ops = row2.operator(ANE_OT_ALign.bl_idname,
                            text='', icon='ANCHOR_CENTER')
        ops.Axis = 'X'
        ops.Aligment = 'Center'
        ops = row2.operator(ANE_OT_ALign.bl_idname,
                            text='', icon='ANCHOR_RIGHT')
        ops.Axis = 'X'
        ops.Aligment = 'Right'
        row = box.row()
        row.label(text="Y-Axis:")
        row2 = row.row(align=True)
        row2.scale_x = 4
        row2.scale_y = 1.1
        ops = row2.operator(ANE_OT_ALign.bl_idname, text='', icon='ANCHOR_TOP')
        ops.Axis = 'Y'
        ops.Aligment = 'Top'
        ops = row2.operator(ANE_OT_ALign.bl_idname,
                            text='', icon='ANCHOR_CENTER')
        ops.Axis = 'Y'
        ops.Aligment = 'Center'
        ops = row2.operator(ANE_OT_ALign.bl_idname,
                            text='', icon='ANCHOR_BOTTOM')
        ops.Axis = 'Y'
        ops.Aligment = 'Bottom'

        box = layout.box()
        row = box.row()
        row.separator(factor=0.5)
        row = box.row()
        row.label(text="Distribut Offset")
        row.prop(ANE, 'distribute_offset', text="")
        row = box.row()
        col = row.column()
        col.label(text="Space")
        col.operator(ANE_OT_Distribute.bl_idname, text="",
                     icon='SNAP_EDGE').Pivot = 'Vertical'
        col.operator(ANE_OT_Distribute.bl_idname, text="",
                     icon='PAUSE').Pivot = 'Horizontal'
        flow = row.grid_flow(row_major=True, columns=3,
                             even_columns=True, even_rows=True)
        flow.label(text="")
        flow.operator(ANE_OT_Distribute.bl_idname, text="",
                      icon='ANCHOR_TOP').Pivot = 'Top'
        flow.label(text="")
        flow.operator(ANE_OT_Distribute.bl_idname, text="",
                      icon='ANCHOR_LEFT').Pivot = 'Left'
        flow.label(text="")
        flow.operator(ANE_OT_Distribute.bl_idname, text="",
                      icon='ANCHOR_RIGHT').Pivot = 'Right'
        flow.label(text="")
        flow.operator(ANE_OT_Distribute.bl_idname, text="",
                      icon='ANCHOR_BOTTOM').Pivot = 'Bottom'
        flow.label(text="")


classes.append(ANE_PT_AligmentAndDistribut)


class ANE_OT_Add_DistributOffsetItem(Operator):
    bl_idname = "ane.add_distributoffsetitem"
    bl_label = "Add Offset"
    bl_description = "Adds a new offset Item"
    bl_options = {"REGISTER"}

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        ANE.distribute_offset_items = "a0"
        ANE['distribute_offset'] = len(
            json.loads(ANE.distribute_offset_items)) - 1
        return {"FINISHED"}


classes.append(ANE_OT_Add_DistributOffsetItem)


class ANE_OT_Delete_DistributOffsetItem(Operator):
    bl_idname = "ane.delete_distributoffsetitem"
    bl_label = "Delete Offset"
    bl_description = "Deletes the selected offset Item"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        ANE = context.preferences.addons[__package__].preferences
        return len(ANE.distribute_offset) - 1

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        ANE.distribute_offset_items = "d%s" % fc.get_init_enum(
            ANE, 'distribute_offset')
        ANE['distribute_offset'] = 0
        return {"FINISHED"}


classes.append(ANE_OT_Delete_DistributOffsetItem)


class ANE_OT_ALign(Operator):
    bl_idname = "ane.align"
    bl_label = "Align Node"
    bl_description = "Align the selected Nodes relative to the active Node"
    bl_options = {"REGISTER"}

    Axis: EnumProperty(items=[("X", "X", ''), ("Y", "Y", "")], name="Axis")
    aligmentsItems = [("Top", "Top", ""),
                      ("Bottom", "Bottom", ""),
                      ("Center", "Center", ""),
                      ("Right", "Right", ""),
                      ("Left", "Left", "")]
    Aligment: EnumProperty(items=aligmentsItems, name="Aligment")

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.active_material is not None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree is not None and context.space_data.edit_tree.nodes.active is not None

    def execute(self, context):
        nodes = context.space_data.edit_tree.nodes
        active = nodes.active
        selected = fc.getSelected(nodes, active.name)
        aligment = 0 if self.Axis == 'X' else 1
        loc = active.location[aligment]
        length = active.dimensions[aligment]
        # Pivot of Node is Top-Left
        if self.Aligment == 'Top' or self.Aligment == "Left":
            for node in selected:
                node.location[aligment] = loc
        elif self.Aligment == 'Center':
            for node in selected:
                node.location[aligment] = loc - \
                    (2 * aligment - 1) * (length -
                                          node.dimensions[aligment]) * 0.5
        else:
            for node in selected:
                node.location[aligment] = loc - \
                    (2 * aligment - 1) * (length - node.dimensions[aligment])
        return {"FINISHED"}


classes.append(ANE_OT_ALign)


class ANE_OT_Distribute(Operator):
    bl_idname = "ane.distribute"
    bl_label = "Distribute"
    bl_description = """Distribute the selected Nodes relativ to the active Node

Shift: use the offset for spacing the nodes (only works with Vertical, Horizontal)"""
    bl_options = {"REGISTER"}

    pivotItems = [("Left", "Left", ""),
                  ("Right", "Right", ""),
                  ("Top", "Top", ""),
                  ("Bottom", "Bottom", ""),
                  ("Vertical", "Vertical", ""),
                  ("Horizontal", "Horizontal", "")]
    Pivot: EnumProperty(items=pivotItems, name="pivot")
    use_offset: BoolProperty(
        default=False,
        name="use offset",
        description="Uses the offset instead of the given area to distribute the nodes"
    )
    override_offset: BoolProperty(
        default=False,
        name="override offset",
        description="Uses the operator based offset instead of the preference set offset"
    )
    offset: IntProperty(name="offset", default=0)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.active_material is not None and hasattr(context.space_data, 'edit_tree') and context.space_data.edit_tree is not None and context.space_data.edit_tree.nodes.active is not None

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.use_offset = event.shift
        return self.execute(context)

    def execute(self, context):
        ANE = context.preferences.addons[__package__].preferences
        nodes = context.space_data.edit_tree.nodes
        offset = int(ANE.distribute_offset.split('-')[1])
        if self.override_offset:
            offset = self.offset
        active = nodes.active
        selected = fc.getSelected(nodes, active.name)
        if not (self.Pivot == "Vertical" or self.Pivot == "Horizontal"):
            if self.Pivot == 'Left':
                selected = fc.sortByLocation(selected, 0, True)
                loc = active.location[0]
                for node in selected:
                    node.location[0] = loc - offset - node.dimensions[0]
                    # loc = node.location[0]
            elif self.Pivot == 'Right':
                selected = fc.sortByLocation(selected, 0, False)
                loc = active.location[0] + active.dimensions[0]
                for node in selected:
                    node.location[0] = loc + offset
                    # loc = node.location[0] + node.dimensions[0]
            elif self.Pivot == 'Top':
                selected = fc.sortByLocation(selected, 1, False)
                loc = active.location[1]
                for node in selected:
                    node.location[1] = loc + offset + node.dimensions[1]
                    # loc = node.location[1]
            else:
                selected = fc.sortByLocation(selected, 1, True)
                loc = active.location[1] - active.dimensions[1]
                for node in selected:
                    node.location[1] = loc - offset
                    # loc = node.location[1] - node.dimensions[1]
        else:
            if self.Pivot == 'Vertical':
                fc.distribute(selected, 1, offset * self.use_offset)
            else:
                fc.distribute(selected, 0, offset * self.use_offset)
        return {"FINISHED"}


classes.append(ANE_OT_Distribute)
