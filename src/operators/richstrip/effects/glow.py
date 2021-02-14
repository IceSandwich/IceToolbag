import bpy
from .base import EffectBase

class EffectGlow(EffectBase):
    @classmethod
    def getName(cls):
        return "Glow"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        # effectlast = data.Effects[-2].EffectStrips[-1].value
        effectlast = data.getSelectedEffect().EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectlast).select = True
        bpy.ops.sequencer.effect_strip_add(type='GLOW', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        glowlayer = context.scene.sequence_editor.active_strip
        glowlayer.name = cls.genRegularStripName(effect.EffectId, "glow")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        # adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = glowlayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        glowlayer = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "glow"))

        layout.label(text="Glow:")
        layout.prop(glowlayer, "threshold", text="Threshold")
        layout.prop(glowlayer, "clamp", text="Clamp")
        layout.prop(glowlayer, "boost_factor", text="Boost Factor")
        layout.prop(glowlayer, "use_only_boost", toggle=1)
        
        layout.label(text="Additional:")
        layout.prop(glowlayer, "blur_radius", text="Blur Radius")
        layout.prop(glowlayer, "quality", text="Quality")
        return