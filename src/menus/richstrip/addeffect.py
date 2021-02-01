import bpy
from ...operators.richstrip.effects import ICETB_EFFECTS_NAMES

class ICETB_MT_RichStripAddEffect(bpy.types.Menu):
    bl_idname = "ICETB_MT_RICHSTRIP_ADD"
    bl_label = "Add Effect"

    def draw(self, context):
        layout = self.layout

        for name in ICETB_EFFECTS_NAMES:
            if name != 'Original':
                layout.operator("icetb.richstrip_addeffect", text=name).effectName = name