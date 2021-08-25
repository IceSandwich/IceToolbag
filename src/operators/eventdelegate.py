import bpy
from .richstrip.effects import ICETB_EFFECTS_DICTS
from .richstrip.effects import ICETB_EFFECTS_NAMES

class ICETB_OT_RichStrip_EventDelegate(bpy.types.Operator):
    bl_idname = "icetb.richstrip_eventdelegate"
    bl_label = "Delegate for some props(Private use only)"
    bl_options = {"REGISTER"}

    effectName: bpy.props.StringProperty(name="The type of effect")
    eventType: bpy.props.StringProperty(name="The type of event")
    eventIdentify: bpy.props.StringProperty(name="The identify of event")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(context.selected_sequences) < 1: # i don't know why
            return {'FINISHED'}
        if self.effectName in ICETB_EFFECTS_NAMES:
            ICETB_EFFECTS_DICTS[self.effectName]._update(self.eventType, self.eventIdentify, context)
        else:
            self.report({'ERROR'}, "Unknow effect name called " + self.effectName)
            return {'CANCELLED'}

        return {"FINISHED"}