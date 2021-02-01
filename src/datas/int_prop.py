import bpy

class IntProperty(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(name="Integer Value")