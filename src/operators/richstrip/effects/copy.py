import bpy
from .base import EffectBase

class EffectCopy(EffectBase):
    """
        EffectEnumProperties:
            [0]: Resize method
        EffectFloatProperties:
            [0]: Scale X
            [1]: Scale Y
    """
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

        tranfenum = effect.EffectEnumProperties.add() # the first enum property
        tranfenum.initForEffect(cls.getName(), 0)
        tranfenum.items.add().value = "Stretch"
        tranfenum.items.add().value = "Original"
        tranfenum.items.add().value = "Fit"
        tranfenum.items.add().value = "Full"

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1) #scale x
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1) #scale y

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        tranf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "transf"))

        layout.prop(effect.EffectEnumProperties[0], "value", text="Resize")
        layout.prop(tranf, "blend_type", text="Blend")
        row = layout.row(align=True)
        row.prop(effect.EffectFloatProperties[0], "value", text="Scale X")
        row.prop(effect.EffectFloatProperties[1], "value", text="Scale Y")

        layout.label(text="Position:")
        row = layout.row(align=True)
        row.prop(tranf, "translate_start_x", text="X")
        row.prop(tranf, "translate_start_y", text="Y")

        layout.label(text="Rotation:")
        layout.prop(tranf, "rotation_start")

        layout.label(text="Mirror:")
        row = layout.row(align=True)
        row.prop(tranf, "use_flip_x", toggle=1)
        row.prop(tranf, "use_flip_y", toggle=1)

        layout.label(text="Alpha:")
        layout.prop(tranf, "blend_alpha")

        layout.label(text="Color:")
        layout.prop(tranf, "color_saturation")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        if (type == "ENUM" and identify == 0) or type == 'FLOAT':  # tranfenum or scale changed
            resizeEnum = effect.EffectEnumProperties[0].value
            renderX, renderY = context.scene.render.resolution_x, context.scene.render.resolution_y
            movieX, movieY = data.ResolutionWidth, data.ResolutionHeight
            transf = firstlayer.sequences.get(cls.genRegularStripName(effect.EffectId, "transf"))
            user_scalex, user_scaley = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            if resizeEnum == "Stretch":
                transf.scale_start_x = 1 * user_scalex
                transf.scale_start_y = 1 * user_scaley
            elif resizeEnum ==  "Original":
                transf.scale_start_x = movieX / renderX * user_scalex
                transf.scale_start_y = movieY / renderY * user_scaley
            elif resizeEnum == "Fit":
                if movieY >= movieX:
                    transf.scale_start_x = 1 * user_scalex
                    transf.scale_start_y = (renderX / movieX) * movieY / renderY * user_scaley
                elif movieX > movieY:
                    transf.scale_start_x = (renderY / movieY) * movieX / renderX * user_scalex
                    transf.scale_start_y = 1 * user_scaley
            elif resizeEnum == "Full":
                if movieY >= movieX:
                    transf.scale_start_x = (renderY / movieY) * movieX / renderX * user_scalex
                    transf.scale_start_y = 1 * user_scaley
                elif movieX > movieY:
                    transf.scale_start_x = 1 * user_scalex
                    transf.scale_start_y = (renderX / movieX) * movieY / renderY * user_scaley

        return