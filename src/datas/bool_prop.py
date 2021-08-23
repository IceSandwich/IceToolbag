import bpy

class BoolProperty(bpy.types.PropertyGroup):
    effectbelong: bpy.props.StringProperty(name="The parent", default="")
    effectidentify: bpy.props.StringProperty(name="The identify for update event")

    def initForEffect(self, belong, identify, value=None):
        self.effectbelong = belong
        self.effectidentify = identify
        if value is not None:
            self.value = value
            
    def updateitem(self, context):
        if self.effectbelong != "":
            bpy.ops.icetb.richstrip_eventdelegate(effectName=self.effectbelong, eventType="BOOL", eventIdentify=self.effectidentify)

    value: bpy.props.BoolProperty(name="Boolean Value", update=updateitem)