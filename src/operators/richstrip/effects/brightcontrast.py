import bpy
from .base import EffectBase
from .widgets import xylock

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

        cls.leaveEditMode(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        adjustlayer = cls.getEffectStrip(richstrip, "adjust")
        modifier = adjustlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "bc"))

        layout.prop(modifier, "bright")
        layout.prop(modifier, "contrast")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False