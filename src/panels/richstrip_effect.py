import bpy
from ..datas.richstrip import RichStripData
from ..operators.richstrip.effects import ICETB_EFFECTS_DICTS

class ICETB_PT_RichStripEffect(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "RichStrip"
    bl_idname = "ICETB_PT_RichStripEffect"
    bl_label = "Effect Property"

    @classmethod
    def poll(cls, context):
        if len(context.selected_sequences) != 1:
            return False
        seq = context.selected_sequences[0]
        if not RichStripData.checkProperty(context, seq):
            return False
        return True
        data = context.selected_sequences[0].IceTB_richstrip_data
        if data.EffectsCurrent >= len(data.Effects):
            return False
        return True

    def draw(self, context):
        layout = self.layout

        data = context.selected_sequences[0].IceTB_richstrip_data
        seleffecttype = data.getSelectedEffectType()
        layout.label(text="Type: " + seleffecttype)
    
        ICETB_EFFECTS_DICTS[seleffecttype]._draw(context, layout)
