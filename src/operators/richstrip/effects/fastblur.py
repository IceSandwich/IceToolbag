import bpy
from .base import EffectBase
from .widgets import xylock

class EffectFastBlur(EffectBase):
    @classmethod
    def getName(cls):
        return "FastBlur"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        cls.addBoolProperty(effect, "union_fix_lock", boolDefault=True)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        transsmlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', "sm")
        transsmlayer.blend_type = 'ALPHA_UNDER'
        transsmlayer.use_uniform_scale = True
        transsmlayer.interpolation = 'NONE'
        cls.addPropertyWithBinding(context, transsmlayer, "scale_start_x", "strongX", [], "1.0 / (bind+1e-6)", defaultValue=200.0)
        cls.addPropertyWithBinding(context, transsmlayer, "scale_start_y", "strongY", [], "1.0 / (bind+1e-6)", defaultValue=200.0)

        transmdlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', "md")
        transmdlayer.blend_type = 'ALPHA_UNDER'
        transmdlayer.use_uniform_scale = True
        transmdlayer.scale_start_x = 1.2
        transmdlayer.interpolation = 'BILINEAR'

        translglayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', "lg")
        translglayer.blend_type = 'REPLACE'
        translglayer.use_uniform_scale = True
        translglayer.interpolation = 'BICUBIC'
        cls.addPropertyWithBinding(context, translglayer, "scale_start_x", "fixX", [{
            "name": "strong",
            "seqName": transsmlayer.name,
            "seqProp": cls.genbinderName(effect, "strongX"),
            "isCustomProp": True
        }], 'strong * bind', defaultValue=1.3)
        cls.addPropertyWithBinding(context, translglayer, "scale_start_y", "fixY", [{
            "name": "strong",
            "seqName": transsmlayer.name,
            "seqProp": cls.genbinderName(effect, "strongY"),
            "isCustomProp": True
        }, {
            "name": "lock",
            "seqName": richstrip.name,
            "seqProp": cls.genseqProp(effect, "Bool", "union_fix_lock"),
            "isCustomProp": False
        }], 'strong * (self["fixX"] if lock == 1 else bind)', defaultValue=1.3)

        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        cls.leaveEditMode(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, "sm")
        mdtranf = cls.getEffectStrip(richstrip, "md")
        lgtranf = cls.getEffectStrip(richstrip, "lg")

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