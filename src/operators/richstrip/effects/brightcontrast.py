import bpy
from .base import EffectBase
from .widgets import xylock, exportbox, maskbox

class EffectBrightContrast(EffectBase):
    @classmethod
    def getName(cls):
        return "BrightContrast"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        bc = adjustlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"), "BRIGHT_CONTRAST")
        bc.input_mask_type = 'ID'
        
        cls.addExportProperty(effect, [
            [ "bright", "adjust", "modifiers.%s.bright"%bc.name, False ],
            [ "contrast", "adjust", "modifiers.%s.contrast"%bc.name, False ]
        ])

        cls.leaveEditMode(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        adjustlayer = cls.getEffectStrip(richstrip, effect, "adjust")
        modifier = adjustlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"))

        exportbox.draw(layout, richstrip, "bright_export", modifier, "bright")
        exportbox.draw(layout, richstrip, "contrast_export", modifier, "contrast")

        maskbox.draw(layout, effect, data, modifier)
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "adjust").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]
        return False