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

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        cls.addBoolProperty(effect, "fixScale", boolDefault=True)
        cls.addBoolProperty(effect, "strong", boolDefault=True)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        transsmlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', "sm")
        transsmlayer.blend_type = 'ALPHA_UNDER'
        transsmlayer.use_uniform_scale = True
        transsmlayer.interpolation = 'NONE'
        cls.addPropertyWithBinding(context, transsmlayer, "scale_start_x", "strongX", [], "1.0 / bind", defaultValue=100.0)
        cls.addPropertyWithBinding(context, transsmlayer, "scale_start_y", "strongY", [], "1.0 / bind", defaultValue=100.0)

        translglayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', "lg")
        translglayer.blend_type = 'REPLACE'
        translglayer.use_uniform_scale = False
        translglayer.interpolation = 'NONE'
        cls.addPropertyWithBinding(context, translglayer, "scale_start_x", "fixX", [{
            "name": "strong",
            "seqName": transsmlayer.name,
            "seqProp": cls.genbinderName(effect, "strongX"),
            "isCustomProp": True
        }], "strong * bind", defaultValue=1.0)
        cls.addPropertyWithBinding(context, translglayer, "scale_start_y", "fixY", [{
            "name": "strong",
            "seqName": transsmlayer.name,
            "seqProp": cls.genbinderName(effect, "strongY"),
            "isCustomProp": True
        }], 'strong * bind', defaultValue=1.0)

        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        cls.leaveEditMode(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, "sm")
        lgtranf = cls.getEffectStrip(richstrip, "lg")

        layout.label(text="Pixelize Strong:")
        xylock.draw(layout, smtranf, cls.genbinderName(effect, "strongX", True), smtranf, cls.genbinderName(effect, "strongY", True), smtranf, "use_uniform_scale")

        layout.label(text="Fix Scale:")
        xylock.draw(layout, lgtranf, cls.genbinderName(effect, "fixX", True), lgtranf, cls.genbinderName(effect, "fixY", True), lgtranf, "use_uniform_scale")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False