import bpy
from ..datas.richstrip import RichStripData
from ..operators.richstrip.effects import ICETB_EFFECTS_DICTS
from ..operators.richstrip.effects.widgets import xylock

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
        data = richstrip.IceTB_richstrip_data
        firstlayer = richstrip.sequences.get("rs%d-strip"%data.RichStripID)
        effect = data.getSelectedEffect()

        if effect.EffectType == "Original":
            layout.label(text="This effect doesn't support after effect.")
            return

        adjustlayer = firstlayer.sequences.get(effect.EffectStrips[-1].value)

        trans = layout.box()
        row = trans.row()
        #row.prop(adjustlayer, "use_translation", text="") #for 2.8
        row.label(text="Translate")
        # if adjustlayer.use_translation:
        #     row = trans.row(align=True)
        #     adjustoffset = adjustlayer.transform
        #     row.prop(adjustoffset, "offset_x", text="X")
        #     row.prop(adjustoffset, "offset_y", text="Y")
        row = trans.row(align=True)
        adjtransf = adjustlayer.transform
        row.prop(adjtransf, "offset_x", text="X")
        row.prop(adjtransf, "offset_y", text="Y")

        # layout.label(text="Translate:")
        # row = layout.row(align=True)
        # adjustoffset = adjustlayer.transform
        # row.prop(adjustoffset, "offset_x", text="X")
        # row.prop(adjustoffset, "offset_y", text="Y")

        box = layout.box()
        box.label(text="Scale")
        # xylock.draw(box, adjtransf, "scale_x", adjtransf, "scale_y", effect, "EffectAfterEffect_ScaleBoolProperty")
        row = box.row(align=True)
        row.prop(adjtransf, "scale_x", text="X")
        row.prop(adjtransf, "scale_y", text="Y")

        box = layout.box()
        box.label(text="Rotation")
        # xylock.draw(box, adjtransf, "scale_x", adjtransf, "scale_y", effect, "EffectAfterEffect_ScaleBoolProperty")
        row = box.row(align=True)
        row.prop(adjtransf, "rotation", text="Degree")

        box = layout.box()
        box.row().label(text="Mirror")
        row = box.row(align=True)
        row.prop(adjustlayer, "use_flip_x", toggle=1)
        row.prop(adjustlayer, "use_flip_y", toggle=1)

        box = layout.box()
        box.row().label(text="Color")
        box.prop(adjustlayer, "color_saturation")
        box.prop(adjustlayer, "color_multiply")
