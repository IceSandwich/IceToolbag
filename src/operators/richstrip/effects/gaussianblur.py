import bpy
from .base import EffectBase

class EffectGaussianBlur(EffectBase):
    @classmethod
    def getName(cls):
        return "GaussianBlur"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        # effectlast = data.Effects[-2].EffectStrips[-1].value
        effectlast = data.getSelectedEffect().EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectlast).select = True
        bpy.ops.sequencer.effect_strip_add(type='GAUSSIAN_BLUR', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        blurlayer = context.scene.sequence_editor.active_strip
        blurlayer.name = cls.genRegularStripName(effect.EffectId, "blur")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = blurlayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        blurlayer = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "blur"))

        layout.label(text="Blur Size:")
        layout.prop(blurlayer, "size_x", text="X")
        layout.prop(blurlayer, "size_y", text="Y")
        return