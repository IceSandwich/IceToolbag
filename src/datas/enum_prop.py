import bpy
from .string_prop import StringProperty

class EnumProperty(bpy.types.PropertyGroup):
    items: bpy.props.CollectionProperty(type=StringProperty)

    effectbelong: bpy.props.StringProperty(name="The parent", default="")
    effectidentify: bpy.props.IntProperty(name="The identify number for update event")

    def initForEffect(self, belong, identify, value=None):
        self.effectbelong = belong
        self.effectidentify = identify
        if value is not None:
            self.value = value

    def getitems(self, context):
        return ( (x.value, x.value, x.value) for x in self.items )
    
    def updateitem(self, context):
        if self.effectbelong != "":
            bpy.ops.icetb.richstrip_eventdelegate(effectName=self.effectbelong, eventType="ENUM", eventIdentify=self.effectidentify)
        
    value: bpy.props.EnumProperty(
        name="EnumValue",
        items=getitems,
        default=None,
        update=updateitem
    )
