import bpy

class FloatProperty(bpy.types.PropertyGroup):
    effectbelong: bpy.props.StringProperty(name="The parent", default="")
    effectidentify: bpy.props.IntProperty(name="The identify number for update event")

    def initForEffect(self, belong, identify, value=None):
        self.effectbelong = belong
        self.effectidentify = identify
        if value is not None:
            self.value = value
            
    def updateitem(self, context):
        if self.effectbelong != "":
            bpy.ops.icetb.richstrip_eventdelegate(effectName=self.effectbelong, eventType="FLOAT", eventIdentify=self.effectidentify)

    value: bpy.props.FloatProperty(name="Float Value", update=updateitem)