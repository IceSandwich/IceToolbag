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
        # effectlast = data.Effects[-2].EffectStrips[-1].value
        effectlast = data.getSelectedEffect().EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectlast).select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        transsmlayer = context.scene.sequence_editor.active_strip
        transsmlayer.blend_type = 'ALPHA_UNDER'
        transsmlayer.use_uniform_scale = True
        transsmlayer.scale_start_x = transsmlayer.scale_start_y = 1 / 100
        # transsmlayer.scale_start_y = (data.ResolutionWidth / data.ResolutionHeight) * transsmlayer.scale_start_x
        transsmlayer.interpolation = 'NONE'
        transsmlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "sm")

        data.EffectCurrentMaxChannel1 += 1
        transsmlayer.select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translglayer = context.scene.sequence_editor.active_strip
        translglayer.blend_type = 'REPLACE'
        translglayer.use_uniform_scale = False
        translglayer.scale_start_x = 1 / transsmlayer.scale_start_x
        translglayer.scale_start_y = 1 / transsmlayer.scale_start_y
        translglayer.interpolation = 'NONE'
        translglayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "lg")

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        # adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust")

        effect.EffectStrips.add().value = transsmlayer.name
        effect.EffectStrips.add().value = translglayer.name
        effect.EffectStrips.add().value = adjustlayer.name

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1 / transsmlayer.scale_start_x)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1 / transsmlayer.scale_start_y)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 2, 1)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 3, 1)

        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 0, True)
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 1, True)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        smtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "sm"))
        lgtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "lg"))

        layout.label(text="Pixelize Strong:")
        # layout.prop(effect.EffectFloatProperties[0], "value", text="Strong")
        xylock.draw(layout, effect.EffectFloatProperties[0], "value", effect.EffectFloatProperties[1], "value", effect.EffectBoolProperties[1], "value")

        layout.label(text="Fix Scale:")
        # layout.prop(effect.EffectFloatProperties[1], "value", text="Fix Scale")
        xylock.draw(layout, effect.EffectFloatProperties[2], "value", effect.EffectFloatProperties[3], "value", effect.EffectBoolProperties[0], "value")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        if type == 'FLOAT' or type == 'BOOL':
            smtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "sm"))
            lgtranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "lg"))
            # lgtranf.use_uniform_scale = False
            
            strong_x, strong_y = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            fix_scale_x, fix_scale_y = effect.EffectFloatProperties[2].value, effect.EffectFloatProperties[3].value
            # print("x:", fix_scale_x, "y:", fix_scale_y, "c:", effect.EffectBoolProperties[0].value)
            if effect.EffectBoolProperties[1].value:
                strong_y = strong_x
            if effect.EffectBoolProperties[0].value:
                fix_scale_y = fix_scale_x

            smtranf.scale_start_x = 1 / strong_x
            smtranf.scale_start_y = 1 / strong_y

            lgtranf.scale_start_x = strong_x * fix_scale_x
            lgtranf.scale_start_y = strong_y * fix_scale_y

        return