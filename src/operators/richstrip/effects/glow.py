import bpy
from .base import EffectBase

class EffectGlow(EffectBase):
    @classmethod
    def getName(cls):
        return "Glow"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        glowlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'GLOW', "glow")
        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        cls.leaveEditMode(data)
        return

    @classmethod
    def relink(cls, context, richstrip, effect):
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        glowlayer = cls.getEffectStrip(richstrip, effect, "glow")

        layout.label(text="Glow:")
        layout.prop(glowlayer, "threshold", text="Threshold")
        layout.prop(glowlayer, "clamp", text="Clamp")
        layout.prop(glowlayer, "boost_factor", text="Boost Factor")
        layout.prop(glowlayer, "use_only_boost", toggle=1)
        
        layout.label(text="Additional:")
        layout.prop(glowlayer, "blur_radius", text="Blur Radius")
        layout.prop(glowlayer, "quality", text="Quality")
        return