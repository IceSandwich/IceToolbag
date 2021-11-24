import bpy
from .....datas.richstrip import RichStripEffect, RichStripData
from ..base import EffectBase

def draw(layout:bpy.types.UILayout, effect:RichStripEffect, data:RichStripData, mask_modifier:bpy.types.SequenceModifier, mask_though=None):
    box = layout.box()
    box.label(text="Mask", icon="MOD_MASK")
    # box.prop_search(EffectBase.getStrProperty(effect, attrName), 'value', bpy.data, 'masks', text="")
    row = box.row(align=True)
    row.prop(mask_modifier, "input_mask_id", text="")
    maskName = ""
    if mask_modifier.input_mask_id is not None:
        maskName = mask_modifier.input_mask_id.name
        # row.prop(mask_modifier.input_mask_id.layers["IceTBMaskLayer"], "invert", toggle=1, icon="IMAGE_ALPHA", text="")

    row = box.row(align=True)
    row.operator("icetb.richstrip_annotation2mask", text="From Annotation", icon="GREASEPENCIL").effectName_plusmaskId = "%s$$%d_%d$$%s"%(effect.EffectType, data.RichStripID, effect.EffectId, "true" if maskName == "" else "false")
    row.operator("icetb.richstrip_openmaskeditor", text="Edit Mask", icon="EDITMODE_HLT").maskName = maskName

    if mask_though:
        box.prop(EffectBase.getBoolProperty(effect, mask_though), "value", toggle=1, text="Mask Through")
    # IPO_EASE_OUT
    # bpy.ops.transform.transform(mode='MASK_SHRINKFATTEN', value=(1.40525, 0, 0, 0), orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

