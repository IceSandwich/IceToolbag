import bpy
from .base import EffectBase
from .widgets import xylock

class EffectGaussianBlur(EffectBase):
    """
        EffectFloatProperty:
            [0]: Blur X
        EffectBoolProperty:
            [0]: Lock size
    """
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
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = blurlayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, blurlayer.size_x)
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 0, False)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        blurlayer = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "blur"))
        size_float = effect.EffectFloatProperties[0]
        lock_bool = effect.EffectBoolProperties[0]

        layout.label(text="Blur Size:")
        xylock.draw(layout, size_float, "value", blurlayer, "size_y", lock_bool, "value")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        blurlayer = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "blur"))
        if type == 'FLOAT' and identify == 0:
            blurlayer.size_x = effect.EffectFloatProperties[0].value
        if effect.EffectBoolProperties[0].value == True:
            blurlayer.size_y = blurlayer.size_x