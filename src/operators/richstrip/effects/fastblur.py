import bpy
from .base import EffectBase

class EffectFastBlur(EffectBase):
    """
        EffectFloatProperties:
            [0]: blur strong
            [1]: fix blur
    """
    @classmethod
    def getName(cls):
        return "FastBlur"

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
        transsmlayer.use_uniform_scale = True
        transsmlayer.scale_start_x = transsmlayer.scale_start_y = 1 / 200
        # if data.ResolutionWidth < data.ResolutionHeight:
        #     transsmlayer.scale_start_x = 1 / 200
        #     transsmlayer.scale_start_y = (data.ResolutionWidth / data.ResolutionHeight) * transsmlayer.scale_start_x
        # else:
        #     transsmlayer.scale_start_y = 1 / 200
        #     transsmlayer.scale_start_x = (data.ResolutionHeight / data.ResolutionWidth) * transsmlayer.scale_start_y
        transsmlayer.interpolation = 'NONE'
        transsmlayer.name = cls.genRegularStripName(effect.EffectId, "sm")

        data.EffectCurrentMaxChannel1 += 1
        transsmlayer.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        transmdlayer = context.scene.sequence_editor.active_strip
        transmdlayer.blend_type = 'ALPHA_UNDER'
        transmdlayer.use_uniform_scale = True
        transmdlayer.scale_start_x = 1.2
        transmdlayer.interpolation = 'BILINEAR'
        transmdlayer.name = cls.genRegularStripName(effect.EffectId, "md")

        data.EffectCurrentMaxChannel1 += 1
        transmdlayer.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translglayer = context.scene.sequence_editor.active_strip
        translglayer.blend_type = 'REPLACE'
        translglayer.use_uniform_scale = True
        translglayer.scale_start_x = 1 / transsmlayer.scale_start_y * 1.3
        translglayer.interpolation = 'BICUBIC'
        translglayer.name = cls.genRegularStripName(effect.EffectId, "lg")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = transsmlayer.name
        effect.EffectStrips.add().value = transmdlayer.name
        effect.EffectStrips.add().value = translglayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1 / transsmlayer.scale_start_x)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1.3)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        mdtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "md"))
        lgtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "lg"))

        layout.label(text="Blur:")
        layout.prop(effect.EffectFloatProperties[0], "value", text="Strong")
        layout.prop(mdtranf, "scale_start_x", text="Fix Strong")
        layout.prop(effect.EffectFloatProperties[1], "value", text="Fix Scale")

        layout.label(text="Alpha:")
        layout.prop(lgtranf, "blend_alpha")

        layout.label(text="Color:")
        layout.prop(lgtranf, "color_saturation")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        
        if type == 'FLOAT':
            smtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "sm"))
            lgtranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "lg"))

            scale_factor = effect.EffectFloatProperties[0].value
            scale_fix = effect.EffectFloatProperties[1].value

            # if data.ResolutionWidth < data.ResolutionHeight:
            #     smtranf.scale_start_x = 1 / scale_factor
            #     smtranf.scale_start_y = (data.ResolutionWidth / data.ResolutionHeight) * smtranf.scale_start_x
            # else:
            #     smtranf.scale_start_y = 1 / scale_factor
            #     smtranf.scale_start_x = (data.ResolutionHeight / data.ResolutionWidth) * smtranf.scale_start_y
            smtranf.scale_start_x = smtranf.scale_start_y = 1 / scale_factor

            lgtranf.scale_start_x = 1 / smtranf.scale_start_y * scale_fix
            lgtranf.scale_start_y = 1 / smtranf.scale_start_y * scale_fix

        return