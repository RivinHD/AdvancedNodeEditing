import bpy
import numpy
from bpy.types import CollectionProperty, Panel, Operator, AddonPreferences, PropertyGroup
from bpy.props import EnumProperty, IntProperty, StringProperty, FloatProperty, BoolProperty
from . import node_formatting, node_alignment_and_distribut, node_group_editing, node_refactoring, update
import json
from . import functions as fc

bl_info = {
    "name": "Advanced Node Editing",
    "author": "Rivin",
    "description": "Allows you to format, align, edit your Nodes easily",
    "blender": (3, 3, 0),
    "version": (0, 1, 2),
    "location": "Node > UI",
    "category": "Node"
}

classes = []


class ANE_Prop(AddonPreferences):
    bl_idname = __name__

    MainNode: StringProperty(name="Main Node", default="")
    MainLable: StringProperty(name="Main Lable", default="")
    selectionItems = [("I", "Inputs", ""), ("O", "Output", ""),
                      ("A", "All", ""), ("S", "Selection", "")]
    SelectionTypeRename: EnumProperty(items=selectionItems, default="A")
    SelectionTypeSort: EnumProperty(items=selectionItems, default="A")

    def get_distribute_offset_items(self):
        return self.get("distribute_offset_items", "[0, 20, 40]")

    def set_distribute_offset_items(self, value):
        data = json.loads(self.get("distribute_offset_items", "[0, 20, 40]"))
        if value[0] == 'd':
            data.pop(int(value[1:]))
        elif value[0] == 'a':
            data.append(int(value[1:]))
        else:
            data[fc.get_init_enum(self, 'distribute_offset')] = value
        self["distribute_offset_items"] = json.dumps(data)

    distribute_offset_items: StringProperty(
        name="offset items",
        default="[0, 20, 40]",
        set=set_distribute_offset_items,
        get=get_distribute_offset_items
    )

    def get_distribute_offset_edit(self):
        if self.distribute_offset == "":
            return 0
        return int(self.distribute_offset.split("-")[1])

    def set_distribute_offset_edit(self, value):
        self.distribute_offset_items = str(value)

    distribute_offset_edit: IntProperty(
        name="offset edit",
        get=get_distribute_offset_edit,
        set=set_distribute_offset_edit,
        step=10
    )

    def item_distribute_offset(self, context):
        l = []
        i = 0
        data = json.loads(self.distribute_offset_items)
        for item in data:
            l.append((str(i) + "-" + str(item), str(item), "", "", i))
            i += 1
        return l

    distribute_offset: EnumProperty(
        name='Offset',
        description='changes the width of the active Node. New offsets can be added in the preferences',
        items=item_distribute_offset
    )

    SocketItems = [
        ('', 'Float', '', -1),
        ('NodeSocketFloat', 'Float', 'float in [-inf, inf]'),
        ('NodeSocketFloatAngle', 'Float (Angle)',
         'float in [-inf, inf]'),
        ('NodeSocketFloatFactor',
         'Float (Factor)', 'float in [0, 1]'),
        ('NodeSocketFloatPercentage',
         'Float (Percentage)', 'float in [-inf, inf]'),
        ('NodeSocketFloatTime', 'Float (Time)',
         'float in [-inf, inf]'),
        ('NodeSocketFloatUnsigned',
         'Float (Unsigned)', 'float in [0, inf]'),

        ('', 'Integer', '', -1),
        ('NodeSocketInt', 'Int', 'int in [-inf, inf]'),
        ('NodeSocketIntFactor', 'Int (Factor)', 'int in [0, inf]'),
        ('NodeSocketIntPercentage',
         'Int (Percentage)', 'int in [0, inf]'),
        ('NodeSocketIntUnsigned',
         'Int (Unsigned)', 'int in [0, inf]'),

        ('', 'Vector', '', -1),
        ('NodeSocketVector', 'Vector',
         'float array of 3 items in [-inf, inf]'),
        ('NodeSocketVectorAcceleration', 'Vector (Acceleration)',
         'float array of 3 items in [-inf, inf]'),
        ('NodeSocketVectorDirection', 'Vector (Direction)',
         'float array of 3 items in [-inf, inf]'),
        ('NodeSocketVectorEuler', 'Vector (Euler)',
         'float array of 3 items in [-inf, inf]'),
        ('NodeSocketVectorTranslation', 'Vector (Translation)',
         'float array of 3 items in [-inf, inf]'),
        ('NodeSocketVectorVelocity', 'Vector (Velocity)',
         'float array of 3 items in [-inf, inf]'),
        ('NodeSocketVectorXYZ', 'Vector (XYZ)',
         'float array of 3 items in [-inf, inf]'),

        ('', 'Other', '', -1),
        ('NodeSocketBool', 'Bool', 'boolean'),
        ('NodeSocketString', 'String', 'string'),
        ('NodeSocketColor', 'Color',
         'float array of 4 items in [0, inf]'),
        ('NodeSocketImage', 'Image', 'type Image'),
        ('NodeSocketShader', 'Shader', ''),
        ('NodeSocketObject', 'Object', 'type Object')
    ]
    NodeSockets: EnumProperty(
        items=SocketItems,
        name='Sockets',
        description='All available Sockets for a Node'
    )

    NodeType: EnumProperty(
        items=[("input", "Input", ''), ("output", "Output", '')],
        name="Type"
    )

    def get_fallback_node_items(self):
        return self.get("fallback_node_items", '[{"name": "None", "node": "None"}]')

    def set_fallback_node_items(self, value):
        data = json.loads(self.get("fallback_node_items",
                          '[{"name": "None", "node": "None"}]'))
        if value[0] == 'd':
            data.pop(int(value[1:]))
        elif value[0] == 'a':
            data.append(json.loads(value[1:]))
        else:
            data[fc.get_init_enum(self, 'fallback_node')] = value
        self["fallback_node_items"] = json.dumps(data)
    fallback_node_items: StringProperty(
        name="Fallback Node Items", default='[{"name": "None", "node": "None"}]', set=set_fallback_node_items, get=get_fallback_node_items)

    def item_fallback_node(self, context):
        l = []
        i = 0
        data = json.loads(self.fallback_node_items)
        for item in data:
            l.append((str(i) + "-" + str(item['node']) + "-" +
                     str(item['name']), str(item['name']), "", "", i))
            i += 1
        return l
    fallback_node: EnumProperty(
        name='Fallback Node', description="used if I/O hasn't an assigned node. New Fallback Nodes can be added in the preferences", items=item_fallback_node)

    def get_fallback(self):
        return self.fallback_node.split("-")[1]
    Fallback: StringProperty(name='Fallback Node', get=get_fallback)

    def get_fallbackname(self):
        return self.fallback_node.split("-")[2]
    FallbackName: StringProperty(name='Fallback Node', get=get_fallbackname)

    Update: BoolProperty()
    Version: StringProperty()
    Restart: BoolProperty()
    AutoUpdate: BoolProperty(
        default=True,
        name="Auto Update",
        description="automatically search for a new Update"
    )

    def get_node_width_items(self):
        return self.get("node_width_items", "[140, 190, 240]")

    def set_node_width_items(self, value):
        data = json.loads(self.get("node_width_items", "[140, 190, 240]"))
        if value[0] == 'd':
            data.pop(int(value[1:]))
        elif value[0] == 'a':
            data.append(int(value[1:]))
        else:
            data[fc.get_init_enum(self, 'node_width')] = value
        self["node_width_items"] = json.dumps(data)

    node_width_items: StringProperty(
        name="width items",
        default="[140, 190, 240]",
        set=set_node_width_items,
        get=get_node_width_items
    )

    def get_node_width_edit(self):
        if self.node_width == "":
            return 0
        return int(self.node_width.split("-")[1])

    def set_node_width_edit(self, value):
        self.node_width_items = str(value)

    node_width_edit: IntProperty(
        name="width edit",
        get=get_node_width_edit,
        set=set_node_width_edit,
        step=10
    )

    def item_node_width(self, context):
        l = []
        i = 0
        data = json.loads(self.node_width_items)
        for item in data:
            l.append((str(i) + "-" + str(item), str(item), "", "", i))
            i += 1
        return l

    node_width: EnumProperty(
        name='Node Width',
        description='changes the width of the active Node. New Widths can be added in the preferences',
        items=item_node_width
    )

    addon_keymaps = []

    def draw(self, context):
        ANE = bpy.context.preferences.addons[__package__].preferences
        layout = self.layout
        col = layout.column()
        col.prop(ANE, 'AutoUpdate')
        row = col.row()
        if ANE.Update:
            row.operator(update.ANE_OT_Update.bl_idname, text="Update")
        else:
            row.operator(update.ANE_OT_CheckUpdate.bl_idname,
                         text="Check For Updates")
            if ANE.Restart:
                row.operator(update.ANE_OT_Restart.bl_idname,
                             text="Restart to Finsih")
        if ANE.Version != '':
            if ANE.Update:
                col.label(
                    text="A new Version is available (" + ANE.Version + ")")
            else:
                col.label(
                    text="You are using the latest Vesion (" + ANE.Version + ")")
        # Edit distribute_offset List
        col.separator()
        row = col.row()
        row.prop(ANE, 'distribute_offset')
        row = col.row()
        row.prop(ANE, 'distribute_offset_edit')
        row.operator(
            node_alignment_and_distribut.ANE_OT_Add_DistributOffsetItem.bl_idname, text="", icon="ADD")
        row.operator(
            node_alignment_and_distribut.ANE_OT_Delete_DistributOffsetItem.bl_idname, text="", icon="X")
        # Edit Node_Width List
        col.separator()
        row = col.row()
        row.prop(ANE, 'node_width')
        row = col.row()
        row.prop(ANE, 'node_width_edit')
        row.operator(
            node_formatting.ANE_OT_Add_NodeWidthItem.bl_idname, text="", icon="ADD")
        row.operator(
            node_formatting.ANE_OT_Delete_NodeWidthItem.bl_idname, text="", icon="X")
        # Edit Fallback_Node List
        col.separator()
        row = col.row()
        row.prop(ANE, 'fallback_node')
        row.operator(
            node_refactoring.ANE_OT_Add_FallbackNodeItem.bl_idname, text="", icon="ADD")
        row.operator(
            node_refactoring.ANE_OT_Delete_FallbackNodeItem.bl_idname, text="", icon="X")


classes.append(ANE_Prop)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    for cls in node_alignment_and_distribut.classes:
        bpy.utils.register_class(cls)
    for cls in node_formatting.classes:
        bpy.utils.register_class(cls)
    for cls in node_group_editing.classes:
        bpy.utils.register_class(cls)
    for cls in node_refactoring.classes:
        bpy.utils.register_class(cls)
    for cls in update.classes:
        bpy.utils.register_class(cls)
    update.register()
    # keymap
    if bpy.context.window_manager.keyconfigs.addon:
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            name='Node Editor', space_type='NODE_EDITOR')
        ANE_Prop.addon_keymaps.append(km)
        kmi = km.keymap_items.new(
            node_formatting.ANE_OT_Ungroup.bl_idname, 'G', 'PRESS', ctrl=False, alt=True, shift=False)
    print("----- Registered Advanced Node Editing -----")


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    for cls in node_alignment_and_distribut.classes:
        bpy.utils.unregister_class(cls)
    for cls in node_formatting.classes:
        bpy.utils.unregister_class(cls)
    for cls in node_group_editing.classes:
        bpy.utils.unregister_class(cls)
    for cls in node_refactoring.classes:
        bpy.utils.unregister_class(cls)
    for cls in update.classes:
        bpy.utils.unregister_class(cls)
    update.unregister()
    # keymap
    bpy.context.window_manager.keyconfigs.addon.keymaps.remove(
        ANE_Prop.addon_keymaps[0])
    ANE_Prop.addon_keymaps.clear()  # Unregister Preview Collection
    print("----- Unregistered Advanced Node Editing -----")


if __name__ == "__main__":
    register()
