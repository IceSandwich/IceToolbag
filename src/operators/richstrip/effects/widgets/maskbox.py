import bpy
from .....datas.richstrip import RichStripEffect, RichStripData
from .....datas.bool_prop import BoolProperty
from ..base import EffectBase

def draw(layout:bpy.types.UILayout, effect:RichStripEffect, data:RichStripData, mask_modifier:bpy.types.SequenceModifier, mask_through:BoolProperty=None):
    box = layout.box()
    box.label(text="Mask", icon="MOD_MASK")

    row = box.row(align=True)
    row.prop(mask_modifier, "input_mask_id", text="")

    maskName = ""
    if mask_modifier.input_mask_id is not None:
        maskName = mask_modifier.input_mask_id.name

    row.operator("icetb.richstrip_annotation2mask", text="", icon="GREASEPENCIL").effectName_plusmaskId = "%s$$%d_%d$$%s"%(effect.EffectType, data.RichStripID, effect.EffectId, "true" if maskName == "" else "false")
    row.operator("icetb.richstrip_openmaskeditor", text="", icon="EDITMODE_HLT").maskName = maskName

    if maskName != "":
        mask = mask_modifier.input_mask_id
        row.prop(mask.layers[mask.active_layer_index], "invert", toggle=1, icon="LOOP_FORWARDS", text="")

    if mask_through:
        box.prop(mask_through, "value", toggle=0, text="Mask through")
    # IPO_EASE_OUT
    # bpy.ops.transform.transform(mode='MASK_SHRINKFATTEN', value=(1.40525, 0, 0, 0), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

