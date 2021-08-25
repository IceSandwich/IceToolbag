import bpy

class IntProperty(bpy.types.PropertyGroup):
    effectbelong: bpy.props.StringProperty(name="The parent", default="")
    effectidentify: bpy.props.StringProperty(name="The identify for update event")
    effecttrigger: bpy.props.StringProperty(name="The trigger type")

    def initForEffect(self, trigger, belong, identify, value=None):
        self.effecttrigger = trigger
        self.effectbelong = belong
        self.effectidentify = identify
        if value is not None:
            self.value = value
            
    def updateitem(self, context):
        if self.effecttrigger == "RichStrip" and self.effectbelong != "":
            bpy.ops.icetb.richstrip_eventdelegate(effectName=self.effectbelong, eventType="INT", eventIdentify=self.effectidentify)

    value: bpy.props.IntProperty(name="Integer Value", update=updateitem)