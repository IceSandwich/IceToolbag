import bpy
from .effects import ICETB_EFFECTS_DICTS
from .effects.gmic import onFrameChanged

class ICETB_OT_RichStrip_Add(bpy.types.Operator):
    bl_idname = "icetb.richstrip_addeffect"
    bl_label = "Add Effect To Rich Strip"
    bl_options = {"REGISTER", "UNDO"}

    effectName: bpy.props.StringProperty(name="Effect Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.effectName in ICETB_EFFECTS_DICTS.keys():
            clazz = ICETB_EFFECTS_DICTS[self.effectName]
            if clazz._add(context) and clazz.getName() == "GMIC" and onFrameChanged not in bpy.app.handlers.frame_change_post:
                bpy.app.handlers.frame_change_post.append(onFrameChanged)
                print("Register handler for framechange")
        else:
            self.report({'ERROR'}, "Unknow effect name called " + self.effectName)
            return {'CANCELLED'}

        return {"FINISHED"}