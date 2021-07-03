import bpy
from .base import EffectBase
from .widgets import xylock

class EffectFastBlur(EffectBase):
    """
        EffectFloatProperties:
            [0]: blur strong x
            [1]: blur strong y
            [2]: fix blur x
            [3]: fix blur y
        # EffectBoolProperties:
        #     [0]: fix blur union?
    """
    @classmethod
    def getName(cls):
        return "FastBlur"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        effectlast = data.Effects[-2].EffectStrips[-1].value
        # effectlast = data.getSelectedEffect().EffectStrips[-1].value
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
        transsmlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "sm")

        data.EffectCurrentMaxChannel1 += 1
        transsmlayer.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        transmdlayer = context.scene.sequence_editor.active_strip
        transmdlayer.blend_type = 'ALPHA_UNDER'
        transmdlayer.use_uniform_scale = True
        transmdlayer.scale_start_x = 1.2
        transmdlayer.interpolation = 'BILINEAR'
        transmdlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "md")

        data.EffectCurrentMaxChannel1 += 1
        transmdlayer.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translglayer = context.scene.sequence_editor.active_strip
        translglayer.blend_type = 'REPLACE'
        translglayer.use_uniform_scale = True
        translglayer.scale_start_x = 1 / transsmlayer.scale_start_y * 1.3
        translglayer.interpolation = 'BICUBIC'
        translglayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "lg")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        # adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust")

        effect.EffectStrips.add().value = transsmlayer.name
        effect.EffectStrips.add().value = transmdlayer.name
        effect.EffectStrips.add().value = translglayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1 / transsmlayer.scale_start_x)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1 / transsmlayer.scale_start_y)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 2, 1.3)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 3, 1.3)

        # effect.EffectBoolProperties.add().initForEffect(cls.getName(), 0, True)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        smtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "sm"))
        mdtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "md"))
        lgtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "lg"))

        layout.label(text="Blur Strong:")
        xylock.draw(layout, effect.EffectFloatProperties[0], "value", effect.EffectFloatProperties[1], "value", smtranf, "use_uniform_scale")

        layout.label(text="Fix Strong:")
        layout.prop(mdtranf, "scale_start_x", text="Multiply Strong")

        layout.label(text="Fix Scale:")
        xylock.draw(layout, effect.EffectFloatProperties[2], "value", effect.EffectFloatProperties[3], "value", lgtranf, "use_uniform_scale")

        layout.label(text="Alpha:")
        layout.prop(lgtranf, "blend_alpha")

        layout.label(text="Color:")
        layout.prop(lgtranf, "color_saturation")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        
        if type == 'FLOAT' or type == 'BOOL':
            smtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "sm"))
            lgtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "lg"))

            scale_factor_x, scale_factor_y = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            scale_fix_x, scale_fix_y = effect.EffectFloatProperties[2].value, effect.EffectFloatProperties[3].value

            # if data.ResolutionWidth < data.ResolutionHeight:
            #     smtranf.scale_start_x = 1 / scale_factor
            #     smtranf.scale_start_y = (data.ResolutionWidth / data.ResolutionHeight) * smtranf.scale_start_x
            # else:
            #     smtranf.scale_start_y = 1 / scale_factor
            #     smtranf.scale_start_x = (data.ResolutionHeight / data.ResolutionWidth) * smtranf.scale_start_y
            smtranf.scale_start_x = 1 / scale_factor_x
            smtranf.scale_start_y = 1 / scale_factor_y

            lgtranf.scale_start_x = 1 / smtranf.scale_start_x * scale_fix_x
            lgtranf.scale_start_y = 1 / smtranf.scale_start_y * scale_fix_y

        return