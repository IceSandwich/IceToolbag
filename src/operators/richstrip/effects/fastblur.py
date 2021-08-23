import bpy
from .base import EffectBase
from .widgets import xylock

class EffectFastBlur(EffectBase):
    @classmethod
    def getName(cls):
        return "FastBlur"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "union_fix_lock", boolDefault=True)

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.transsmlayer = self.getEffectStrip(self.richstrip, self.effect, "sm")
            self.translglayer = self.getEffectStrip(self.richstrip, self.effect, "lg")
            return

        self.transsmlayer = self.addBuiltinStrip('TRANSFORM', "sm")
        self.transsmlayer.blend_type = 'ALPHA_UNDER'
        self.transsmlayer.use_uniform_scale = True
        self.transsmlayer.interpolation = 'NONE'

        transmdlayer = self.addBuiltinStrip('TRANSFORM', "md")
        transmdlayer.blend_type = 'ALPHA_UNDER'
        transmdlayer.use_uniform_scale = True
        transmdlayer.scale_start_x = 1.2
        transmdlayer.interpolation = 'BILINEAR'

        self.translglayer = self.addBuiltinStrip('TRANSFORM', "lg")
        self.translglayer.blend_type = 'REPLACE'
        self.translglayer.use_uniform_scale = True
        self.translglayer.interpolation = 'BICUBIC'

        self.addBuiltinStrip('ADJUSTMENT', "adjust")

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.context, self.transsmlayer, "scale_start_x", "strongX", [], "1.0 / (bind+1e-6)", defaultValue=200.0)
        self.addPropertyWithBinding(self.context, self.transsmlayer, "scale_start_y", "strongY", [], "1.0 / (bind+1e-6)", defaultValue=200.0)

        self.addPropertyWithBinding(self.context, self.translglayer, "scale_start_x", "fixX", [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }], 'strong * bind', defaultValue=1.3)
        self.addPropertyWithBinding(self.context, self.translglayer, "scale_start_y", "fixY", [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongY"),
            "isCustomProp": True
        }, {
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_fix_lock"),
            "isCustomProp": False
        }], 'strong * (self["fixX"] if lock == 1 else bind)', defaultValue=1.3)


    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, effect, "sm")
        mdtranf = cls.getEffectStrip(richstrip, effect, "md")
        lgtranf = cls.getEffectStrip(richstrip, effect, "lg")

        layout.label(text="Blur Strong:")
        xylock.draw(layout, smtranf, cls.genbinderName(effect, "strongX", True), smtranf, cls.genbinderName(effect, "strongY", True), smtranf, "use_uniform_scale")

        layout.label(text="Fix Strong:")
        layout.prop(mdtranf, "scale_start_x", text="Multiply Strong")

        layout.label(text="Fix Scale:")
        xylock.draw(layout, lgtranf, cls.genbinderName(effect, "fixX", True), lgtranf, cls.genbinderName(effect, "fixY", True), cls.getBoolProperty(effect, "union_fix_lock"), "value")

        layout.label(text="Alpha:")
        layout.prop(lgtranf, "blend_alpha")

        layout.label(text="Color:")
        layout.prop(lgtranf, "color_saturation")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False