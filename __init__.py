import bpy
import numpy
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import EnumProperty, StringProperty, FloatProperty, BoolProperty
from . import node_formatting, node_alignment_and_distribut, node_group_editing, node_refactoring

bl_info = {
    "name" : "Advanced Node Editing",
    "author" : "Rivin",
    "description" : "Allows you to format, align, edit your Nodes easily",
    "blender" : (2, 80, 9),
    "version" : (0, 0, 4),
    "location" : "Node > UI",
    "category" : "Node"
}

classes = []

class ANE_Prop(AddonPreferences):
    bl_idname = __name__

    MainNode : StringProperty(name= "Main Node", default= "")
    MainLable : StringProperty(name= "Main Lable", default= "")
    selectionItems = [("I", "Inputs", ""), ("O", "Output", ""), ("A", "All", ""), ("S", "Selection", "")]
    SelectionTypeRename : EnumProperty(items= selectionItems)
    SelectionTypeSort : EnumProperty(items= selectionItems)
    DistributOffset : FloatProperty(name= "Offset", default= 1)

    SocketItems = [('NodeSocketBool','Bool','boolean'),
                    ('NodeSocketString', 'String', 'string'),
                    ('NodeSocketFloat', 'Float', 'float in [-inf, inf]'),
                    ('NodeSocketFloatAngle', 'Float (Angle)', 'float in [-inf, inf]'),
                    ('NodeSocketFloatFactor', 'Float (Factor)', 'float in [0, 1]'),
                    ('NodeSocketFloatPercentage', 'Float (Percentage)', 'float in [-inf, inf]'),
                    ('NodeSocketFloatTime', 'Float (Time)', 'float in [-inf, inf]'),
                    ('NodeSocketFloatUnsigned', 'Float (Unsigned)', 'float in [0, inf]'),
                    ('NodeSocketInt', 'Int', 'int in [-inf, inf]'),
                    ('NodeSocketIntFactor', 'Int (Factor)', 'int in [0, inf]'),
                    ('NodeSocketIntPercentage', 'Int (Percentage)', 'int in [0, inf]'),
                    ('NodeSocketIntUnsigned', 'Int (Unsigned)', 'int in [0, inf]'),
                    ('NodeSocketVector', 'Vector', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketVectorAcceleration', 'Vector (Acceleration)', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketVectorDirection', 'Vector (Direction)', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketVectorEuler', 'Vector (Euler)', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketVectorTranslation', 'Vector (Translation)', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketVectorVelocity', 'Vector (Velocity)', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketVectorXYZ', 'Vector (XYZ)', 'float array of 3 items in [-inf, inf]'),
                    ('NodeSocketColor', 'Color', 'float array of 4 items in [0, inf]'),
                    ('NodeSocketImage', 'Image', 'type Image'),
                    ('NodeSocketShader', 'Shader', ''),
                    ('NodeSocketObject', 'Object', 'type Object')]
    NodeSockets : EnumProperty(items= SocketItems, name='Sockets', description='All available Sockets for a Node')
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
    print("----- Unregistered Advanced Node Editing -----")

if __name__ == "__main__":
    register()
