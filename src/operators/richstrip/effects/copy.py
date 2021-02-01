import bpy
from .base import EffectBase

class EffectCopy(EffectBase):
    @classmethod
    def getName(cls):
        return "Copy"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        effectnamecopyfrom = data.getSelectedEffect().EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectnamecopyfrom).select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translayer = context.scene.sequence_editor.active_strip
        translayer.blend_type = 'ALPHA_OVER'
        translayer.name = cls.genRegularStripName(effect.EffectId, "transf")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = translayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, data, layout):
        layout.label(text="The copy effect pannel")
        return