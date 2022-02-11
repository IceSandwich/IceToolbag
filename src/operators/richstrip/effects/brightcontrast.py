import bpy
from .base import EffectBase
from .widgets import xylock, exportbox, maskbox, cropbox

class EffectBrightContrast(EffectBase):
    @classmethod
    def getName(cls):
        return "Bright Contrast"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        cls.addBoolProperty(effect, "mask_through", False)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        adjustlayer = cls.addBuiltinEffectStrip_ClassLevel(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        bc = adjustlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"), "BRIGHT_CONTRAST")
        bc.input_mask_type = 'ID'
        
        cls.addExportProperty(effect, [
            [ "bright", "adjust", "modifiers.%s.bright"%bc.name, False ],
            [ "contrast", "adjust", "modifiers.%s.contrast"%bc.name, False ],
            [ "alpha", "adjust", "blend_alpha", False]
        ])

        cls.addBuiltinEffectStrip_ClassLevel(context, richstrip, effect, 'ADJUSTMENT', "adjustend")

        cls.leaveEditMode(data)

    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        adjustlayer = cls.getEffectStrip(richstrip, effect, "adjust")
        modifier = adjustlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"))
        mask_through = cls.getBoolProperty(effect, "mask_through")

        box = layout.box()
        box.label(text="Blend", icon="OVERLAY")
        exportbox.draw(box, richstrip, "bright", modifier, "bright", "Bright")
        exportbox.draw(box, richstrip, "contrast", modifier, "contrast", "Contrast")
        exportbox.draw(box, richstrip, "alpha", adjustlayer, "blend_alpha", "Opacity")

        layout.separator()

        cropbox.draw(layout, adjustlayer, mask_through)

        layout.separator()

        maskbox.draw(layout, effect, data, modifier, mask_through=mask_through)

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "adjust").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL':
            if identify == "mask_through":
                adjustlayer = cls.getEffectStrip(richstrip, effect, "adjust")
                adjustlayer.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, identify).value else 'REPLACE'

        return False