import bpy
from .effects import ICETB_EFFECTS_DICTS

class ICETB_OT_RichStrip_Add(bpy.types.Operator):
    bl_idname = "icetb.richstrip_addeffect"
    bl_label = "Add Effect To Rich Strip"
    bl_options = {"REGISTER", "UNDO"}

    effectName: bpy.props.StringProperty(name="Effect Name")

    @classmethod
    def poll(cls, context):
        return True

    @classmethod
    def setupHandlers(cls, is_setup):
        for clazz in ICETB_EFFECTS_DICTS.values():
            if hasattr(clazz, "setupHandlers"):
                clazz.setupHandlers(is_setup)

    def execute(self, context):
        if self.effectName in ICETB_EFFECTS_DICTS.keys():
            clazz = ICETB_EFFECTS_DICTS[self.effectName]
            if clazz._add(context, self.report):
                if hasattr(clazz, 'SIG_Add'):
                    clazz.SIG_Add(context, True)
            else:
                return {'CANCELLED'} # Error messages should be printed by _add function cause it use reportFunc
        else:
            self.report({'ERROR'}, "Unknow effect name called " + self.effectName)
            return {'CANCELLED'}

        return {"FINISHED"}