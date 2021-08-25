import bpy
from .base import EffectBase
from .widgets import xylock

class EffectPixelize(EffectBase):
    """
        EffectFloatProperties:
            [0]: Strong x
            [1]: Strong y
            [2]: Fix Scale x
            [3]: Fix Scale y
        EffectBoolProperties:
            [0]: Fix Scale union?
            [1]: Strong union?
    """
    @classmethod
    def getName(cls):
        return "Pixelize"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "fixScale", boolDefault=True)
        self.addBoolProperty(self.effect, "strong", boolDefault=True)

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.transsmlayer = self.getEffectStrip(self.richstrip, self.effect, "sm")
            self.translglayer = self.getEffectStrip(self.richstrip, self.effect, "lg")
            return

        self.transsmlayer = self.addBuiltinStrip('TRANSFORM', "sm")
        self.transsmlayer.blend_type = 'ALPHA_UNDER'
        self.transsmlayer.use_uniform_scale = True
        self.transsmlayer.interpolation = 'NONE'

        self.translglayer = self.addBuiltinStrip('TRANSFORM', "lg")
        self.translglayer.blend_type = 'REPLACE'
        self.translglayer.use_uniform_scale = False
        self.translglayer.interpolation = 'NONE'

        self.addBuiltinStrip('ADJUSTMENT', "adjust")

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.context, self.transsmlayer, "scale_start_x", self.genbinderName(self.effect, "strongX"), [], "1.0 / bind", defaultValue=100.0)
        self.addPropertyWithBinding(self.context, self.transsmlayer, "scale_start_y", self.genbinderName(self.effect, "strongY"), [], "1.0 / bind", defaultValue=100.0)

        self.addPropertyWithBinding(self.context, self.translglayer, "scale_start_x", self.genbinderName(self.effect, "fixX"), [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }], "strong * bind", defaultValue=1.0)
        self.addPropertyWithBinding(self.context, self.translglayer, "scale_start_y", self.genbinderName(self.effect, "fixY"), [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongY"),
            "isCustomProp": True
        }], 'strong * bind', defaultValue=1.0)

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, effect, "sm")
        lgtranf = cls.getEffectStrip(richstrip, effect, "lg")

        layout.label(text="Pixelize Strong:")
        xylock.draw(layout, smtranf, cls.genbinderName(effect, "strongX", True), smtranf, cls.genbinderName(effect, "strongY", True), smtranf, "use_uniform_scale")

        layout.label(text="Fix Scale:")
        xylock.draw(layout, lgtranf, cls.genbinderName(effect, "fixX", True), lgtranf, cls.genbinderName(effect, "fixY", True), lgtranf, "use_uniform_scale")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False