import bpy
from .base import EffectBase

class EffectPixelize(EffectBase):
    """
        EffectFloatProperties:
            [0]: Strong
            [1]: Fix Scale
    """
    @classmethod
    def getName(cls):
        return "Pixelize"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        # effectlast = data.Effects[-2].EffectStrips[-1].value
        effectlast = data.getSelectedEffect().EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectlast).select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        transsmlayer = context.scene.sequence_editor.active_strip
        transsmlayer.blend_type = 'ALPHA_UNDER'
        transsmlayer.scale_start_x = 1 / 100
        transsmlayer.scale_start_y = (data.ResolutionWidth / data.ResolutionHeight) * transsmlayer.scale_start_x
        transsmlayer.interpolation = 'NONE'
        transsmlayer.name = cls.genRegularStripName(effect.EffectId, "sm")

        data.EffectCurrentMaxChannel1 += 1
        transsmlayer.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translglayer = context.scene.sequence_editor.active_strip
        translglayer.blend_type = 'REPLACE'
        translglayer.use_uniform_scale = True
        translglayer.scale_start_x = 100
        translglayer.scale_start_y = 100
        translglayer.interpolation = 'NONE'
        translglayer.name = cls.genRegularStripName(effect.EffectId, "lg")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = transsmlayer.name
        effect.EffectStrips.add().value = translglayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 100)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        smtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "sm"))
        lgtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "lg"))

        layout.label(text="Pixelize:")
        layout.prop(effect.EffectFloatProperties[0], "value", text="Strong")
        layout.prop(effect.EffectFloatProperties[1], "value", text="Fix Scale")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        if type == 'FLOAT':
            smtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "sm"))
            lgtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "lg"))
            
            strong, fix_scale = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value

            smtranf.scale_start_x =  1 / strong
            smtranf.scale_start_y = (data.ResolutionWidth / data.ResolutionHeight) * smtranf.scale_start_x

            lgtranf.scale_start_x = strong * fix_scale
            lgtranf.scale_start_y = strong * fix_scale

        return