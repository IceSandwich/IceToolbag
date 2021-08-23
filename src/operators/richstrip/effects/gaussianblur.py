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

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "union_size_lock", False)

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.blurlayer = self.getEffectStrip(self.richstrip, self.effect, "blur")
            return
        self.blurlayer = self.addBuiltinStrip('GAUSSIAN_BLUR', "blur")
        self.addBuiltinStrip('ADJUSTMENT', "adjust")

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.context, self.blurlayer, "size_y", self.genbinderName(self.effect, "size_y"), [{
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_size_lock"),
            "isCustomProp": False
        }], "self.size_x if lock == 1 else bind")


    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        blurlayer = cls.getEffectStrip(richstrip, effect, "blur")

        layout.label(text="Blur Size:")
        xylock.draw(layout, blurlayer, "size_x", blurlayer, cls.genbinderName(effect, "size_y", True), cls.getBoolProperty(effect, "union_size_lock"), "value")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False