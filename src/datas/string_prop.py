import bpy

class StringProperty(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(name="String Value")