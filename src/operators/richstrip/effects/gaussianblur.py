import bpy
from .base import EffectBase
from .widgets import xylock

class EffectGaussianBlur(EffectBase):
    """
        EffectBoolProperty:
            [0]: Lock size
    """
    @classmethod
    def getName(cls):
        return "GaussianBlur"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        blurlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'GAUSSIAN_BLUR', "blur")
        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        cls.addBoolProperty(effect, "union_size_lock", False)

        cls.addPropertyWithBinding(context, blurlayer, "size_y", cls.genbinderName(effect, "size_y"), [{
            "name": "lock",
            "seqName": richstrip.name,
            "seqProp": cls.genseqProp(effect, "Bool", "union_size_lock"),
            "isCustomProp": False
        }], "self.size_x if lock == 1 else bind")

        cls.leaveEditMode(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        blurlayer = cls.getEffectStrip(richstrip, "blur")

        layout.label(text="Blur Size:")
        xylock.draw(layout, blurlayer, "size_x", blurlayer, cls.genbinderName(effect, "size_y", True), cls.getBoolProperty(effect, "union_size_lock"), "value")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False