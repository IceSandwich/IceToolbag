import bpy, re
from ..datas.richstrip import RichStripData
from ..operators.richstrip.effects import ICETB_EFFECTS_DICTS
from ..operators.richstrip.effects.widgets import xylock

class ICETB_PT_RichStripEffectCTL(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "RichStrip"
    bl_idname = "ICETB_PT_RichStripEffectCTL"
    bl_label = "Additional control"

    @classmethod
    def poll(cls, context):
        if len(context.selected_sequences) != 1:
            return False
        seq = context.selected_sequences[0]
        if not RichStripData.checkProperty(context, seq):
            return False
        data = seq.IceTB_richstrip_data
        if not data.ForceNoDuplicateTip and re.compile(".*?\\.[0-9]{1,3}$").match(seq.name):
            return False
        # if data.EffectsCurrent >= len(data.Effects):
        #     return False
        return True

    def draw(self, context):
        layout = self.layout

        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()

        # if effect.EffectType == "Original":
        #     layout.label(text="This effect doesn't support after effect.")
        #     return

        adjustlayer = richstrip.sequences.get(effect.EffectStrips[-1].value)

        trans = layout.box()
        row = trans.row()
        #row.prop(adjustlayer, "use_translation", text="") #for 2.8
        row.label(text="Translate", icon="ORIENTATION_LOCAL")
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
        box.label(text="Scale", icon="FIXED_SIZE")
        # xylock.draw(box, adjtransf, "scale_x", adjtransf, "scale_y", effect, "EffectAfterEffect_ScaleBoolProperty")
        row = box.row(align=True)
        row.prop(adjtransf, "scale_x", text="X")
        row.prop(adjtransf, "scale_y", text="Y")

        box = layout.box()
        box.label(text="Rotation", icon="DRIVER_ROTATIONAL_DIFFERENCE")
        # xylock.draw(box, adjtransf, "scale_x", adjtransf, "scale_y", effect, "EffectAfterEffect_ScaleBoolProperty")
        row = box.row(align=True)
        row.prop(adjtransf, "rotation", text="Degree")

        box = layout.box()
        box.row().label(text="Mirror", icon="MOD_MIRROR")
        row = box.row(align=True)
        row.prop(adjustlayer, "use_flip_x", toggle=1, icon="ARROW_LEFTRIGHT")
        row.prop(adjustlayer, "use_flip_y", toggle=1, icon="EMPTY_SINGLE_ARROW")

        box = layout.box()
        box.row().label(text="Color", icon="COLOR")
        box.prop(adjustlayer, "color_saturation")
        box.prop(adjustlayer, "color_multiply")

        # box = layout.box()
        # box.label(text="Mask")
        # box.prop_search(context.scene, 'arma_name', bpy.data, 'masks')