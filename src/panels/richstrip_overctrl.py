import bpy
from ..datas.richstrip import RichStripData
from ..operators.richstrip.effects import ICETB_EFFECTS_DICTS

class ICETB_PT_RichStripEffectCTL(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "RichStrip"
    bl_idname = "ICETB_PT_RichStripEffectCTL"
    bl_label = "After Effect"

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

        richstrip = context.selected_sequences[0]
        firstlayer = richstrip.sequences.get("FirstLayerRichStrip")
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()

        adjustlayer = firstlayer.sequences.get(effect.EffectStrips[-1].value)

        layout.label(text="Transform:")
        row = layout.row(align=True)
        adjustoffset = adjustlayer.transform
        row.prop(adjustoffset, "offset_x", text="X")
        row.prop(adjustoffset, "offset_y", text="Y")

        layout.label(text="Mirror:")
        row = layout.row(align=True)
        row.prop(adjustlayer, "use_flip_x", toggle=1)
        row.prop(adjustlayer, "use_flip_y", toggle=1)

        layout.label(text="Color:")
        layout.prop(adjustlayer, "color_saturation")
        layout.prop(adjustlayer, "color_multiply")
