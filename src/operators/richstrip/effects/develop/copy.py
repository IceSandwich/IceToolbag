import bpy, os
from .base import EffectBase
from .widgets import xylock

class EffectCopy(EffectBase):
    """
        EffectEnumProperties:
            [0]: Resize method (only available when copy from original effect)
        EffectFloatProperties:
            [0]: Scale X
            [1]: Scale Y
            [2]: Position X
            [3]: Position Y
        EffectBoolProperties:
            [0]: Union Scale?
            [1]: Flip X
            [2]: Flip Y
    """
    @classmethod
    def getName(cls):
        return "Copy"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        isCopyFromOriginal = (data.getSelectedEffect().EffectType == "Original")
        if isCopyFromOriginal:
            effectnamecopyfrom = "rs%d-movie"%data.RichStripID
        else:
            effectnamecopyfrom = data.getSelectedEffect().EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        # if isCopyFromOriginal:
        #     # data.EffectCurrentMaxChannel1 += 1
        #     MovieSeq = strips.get("rs%d-movie"%data.RichStripID)
        #     bpy.ops.sequencer.movie_strip_add(filepath=MovieSeq.filepath, directory=os.path.dirname(MovieSeq.filepath), frame_start=MovieSeq.frame_start, channel=data.EffectCurrentMaxChannel1, fit_method='ORIGINAL', sound=False, use_framerate=False)
        #     movielayer = context.scene.sequence_editor.active_strip
        #     movielayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf")

        #     data.EffectCurrentMaxChannel1 += 1
        #     bpy.ops.sequencer.effect_strip_add(type='SPEED', channel=data.EffectCurrentMaxChannel1)
        #     speed_strip = context.scene.sequence_editor.active_strip
        #     speed_strip.multiply_speed = strips.get("rs%d-fixfps"%data.RichStripID).multiply_speed
        #     speed_strip.use_frame_interpolate = True
        #     speed_strip.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "speed")

        #     effect.EffectStrips.add().value = movielayer.name
        #     effect.EffectStrips.add().value = speed_strip.name
        # else:
        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectnamecopyfrom).select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translayer = context.scene.sequence_editor.active_strip
        translayer.blend_type = 'ALPHA_OVER'
        translayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf")
        effect.EffectStrips.add().value = translayer.name

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust")

        effect.EffectStrips.add().value = adjustlayer.name

        if isCopyFromOriginal:
            tranfenum = effect.EffectEnumProperties.add() # the first enum property
            tranfenum.initForEffect(cls.getName(), 0)
            tranfenum.items.add().value = "Original"
            tranfenum.items.add().value = "Scale to Fit"
            tranfenum.items.add().value = "Scale to Fill"
            tranfenum.items.add().value = "Stretch to Fill"

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1) #scale x
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1) #scale y
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 2, 0) #pos y
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 3, 0) #pos y
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 0, False)
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 1, False) #flip x
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 2, False) #flip y

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        tranf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf"))

        layout.prop(tranf, "blend_type", text="Blend")

        box = layout.box()
        box.label(text="Position")
        row = box.row(align=True)
        # row.prop(tranf, "translate_start_x", text="X")
        # row.prop(tranf, "translate_start_y", text="Y")
        row.prop(effect.EffectFloatProperties[2], "value", text="X")
        row.prop(effect.EffectFloatProperties[3], "value", text="Y")

        box = layout.box()
        box.label(text="Scale")
        if len(effect.EffectEnumProperties) != 0:
            box.prop(effect.EffectEnumProperties[0], "value", text="Resize")
        xylock.draw(box, effect.EffectFloatProperties[0], "value", effect.EffectFloatProperties[1], "value", effect.EffectBoolProperties[0], "value")

        box = layout.box()
        box.label(text="Rotation")
        if tranf.type == "TRANSFORM":
            box.prop(tranf, "rotation_start", text="Degree")
        else:
            box.prop(tranf.transform, "rotation", text="Degree")

        box = layout.box()
        box.label(text="Mirror")
        row = box.row(align=True)
        # row.prop(tranf, "use_flip_x", toggle=1)
        # row.prop(tranf, "use_flip_y", toggle=1)
        row.prop(effect.EffectBoolProperties[1], "value", toggle=1, text="Flip X")
        row.prop(effect.EffectBoolProperties[2], "value", toggle=2, text="Flip Y")

        box = layout.box()
        box.label(text="Alpha")
        box.prop(tranf, "blend_alpha")

        box = layout.box()
        box.label(text="Color")
        box.prop(tranf, "color_saturation")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        transf = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf"))
        if (type == 'BOOL' and (identify == 1 or identify == 2)) or (type == 'FLOAT' and (identify == 2 or identify == 3)): #flip x/y
            transf.use_flip_x = effect.EffectBoolProperties[1].value
            transf.use_flip_y = effect.EffectBoolProperties[2].value
            if transf.type == "TRANSFORM":
                transf.translate_start_x = effect.EffectFloatProperties[2].value * (-1 if effect.EffectBoolProperties[1].value else 1)
                transf.translate_start_y = effect.EffectFloatProperties[3].value * (-1 if effect.EffectBoolProperties[2].value else 1)
            else:
                transf.transform.offset_x = effect.EffectFloatProperties[2].value * (-1 if effect.EffectBoolProperties[1].value else 1)
                transf.transform.offset_y = effect.EffectFloatProperties[3].value * (-1 if effect.EffectBoolProperties[2].value else 1)
            return
        if (type == "ENUM" and identify == 0) or type == 'FLOAT' or type == 'BOOL':  # tranfenum or scale changed
            renderX, renderY = context.scene.render.resolution_x, context.scene.render.resolution_y
            movieX, movieY = data.ResolutionWidth, data.ResolutionHeight
            user_scalex, user_scaley = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            if effect.EffectBoolProperties[0].value:
                user_scaley = user_scalex
            # MovieSeq = firstlayer.sequences.get("rs%d-movie"%data.RichStripID)
            # user_scalex = user_scalex / MovieSeq.scale_x # scale to (original size) * (user scale)
            # user_scaley = user_scaley / MovieSeq.scale_y

            if len(effect.EffectEnumProperties) == 0:
                if transf.type == "TRANSFORM":
                    transf.scale_start_x = user_scalex
                    transf.scale_start_y = user_scaley
                else:
                    transf.transform.scale_x = user_scalex
                    transf.transform.scale_y = user_scaley
            else:
                resizeEnum = effect.EffectEnumProperties[0].value
                fullx_y, fully_x = movieY * renderX / movieX, movieX * renderY / movieY
                if resizeEnum == "Scale to Fit":
                    if fullx_y <= renderY or fully_x > renderX:
                        final_scalex = final_scaley = renderX / movieX
                    elif fully_x <= renderX or fullx_y > renderY:
                        final_scalex = final_scaley = renderY / movieY
                elif resizeEnum == "Scale to Fill":
                    if fullx_y >= renderY or fully_x < renderX:
                        final_scalex = final_scaley = renderX / movieX
                    elif fully_x >= renderX or fullx_y < renderY:
                        final_scalex = final_scaley = renderY / movieY
                elif resizeEnum == "Stretch to Fill":
                    final_scalex, final_scaley = renderX / movieX, renderY / movieY
                elif resizeEnum == "Original":
                    final_scalex = final_scaley = 1

                if transf.type == "TRANSFORM":
                    transf.scale_start_x = final_scalex * user_scalex
                    transf.scale_start_y = final_scaley * user_scaley
                else:
                    transf.transform.scale_x = final_scalex * user_scalex
                    transf.transform.scale_y = final_scaley * user_scaley

        return