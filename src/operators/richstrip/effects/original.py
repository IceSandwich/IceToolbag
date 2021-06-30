import bpy
from .base import EffectBase
from .widgets import xylock

class EffectOriginal(EffectBase):
    """
        EffectEnumProperties:
            [0]: Resize method
        EffectFloatProperties:
            [0]: Scale X
            [1]: Scale Y
        EffectIntProperties:
            [0]: Translate X
            [1]: Translate Y
        EffectBoolProperties:
            [0]: Union Scale?
            [1]: Flip X
            [2]: Flip Y
    """
    @classmethod
    def getName(cls):
        return "Original"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        # bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        richstrip.sequences.get("rs%d-strip"%data.RichStripID).sequences.get("rs%d-fixfps"%data.RichStripID).select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        # adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust")

        effect.EffectStrips.add().value = adjustlayer.name

        tranfenum = effect.EffectEnumProperties.add()
        tranfenum.initForEffect(cls.getName(), 0)
        tranfenum.items.add().value = "Scale to Fit"
        tranfenum.items.add().value = "Scale to Fill"
        tranfenum.items.add().value = "Stretch to Fill"
        tranfenum.items.add().value = "Original"

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1) #scale x
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1) #scale y
        effect.EffectIntProperties.add().initForEffect(cls.getName(), 0, 0) #pos x
        effect.EffectIntProperties.add().initForEffect(cls.getName(), 1, 0) #pos y
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 0, False) 
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 1, False) #flip x
        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 2, False) #flip y

        cls.leaveFirstLayer(data)

        cls._update("ENUM", 0, context)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        movielayer = firstlayer.sequences.get("rs%d-movie"%data.RichStripID)
        audiolayer = firstlayer.sequences.get("rs%d-audio"%data.RichStripID)
        adjustlayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust"))

        box = layout.box()
        box.row().label(text="Translate")
        row = box.row(align=True)
        # row.prop(adjustlayer.transform, "offset_x", text="X")
        # row.prop(adjustlayer.transform, "offset_y", text="Y")
        row.prop(effect.EffectIntProperties[0], "value", text="X")
        row.prop(effect.EffectIntProperties[1], "value", text="Y")

        box = layout.box()
        box.label(text="Scale")
        box.prop(effect.EffectEnumProperties[0], "value", text="Resize")
        xylock.draw(box, effect.EffectFloatProperties[0], "value", effect.EffectFloatProperties[1], "value", effect.EffectBoolProperties[0], "value")

        box = layout.box()
        box.label(text="Rotation")
        box.prop(adjustlayer.transform, "rotation", text="Degree")

        box = layout.box()
        box.label(text="Mirror")
        row = box.row(align=True)
        # row.prop(adjustlayer, "use_flip_x", toggle=1)
        # row.prop(adjustlayer, "use_flip_y", toggle=1)
        row.prop(effect.EffectBoolProperties[1], "value", toggle=1, text="Flip X")
        row.prop(effect.EffectBoolProperties[2], "value", toggle=1, text="Flip Y")

        # box = layout.box()
        # box.row().label(text="Time (Only movie)")
        # box.prop(movielayer, "use_reverse_frames", toggle=1)

        if audiolayer is not None:
            box = layout.box()
            box.row().label(text="Audio")
            row = box.row(align=True)
            row.prop(audiolayer, "volume")
            row.prop(audiolayer, "mute", icon="MUTE_IPO_ON", toggle=1)

        # layout.label(text="Movie Transform:")
        # row = layout.row(align=True)
        # adjustoffset = adjustlayer.transform
        # row.prop(adjustoffset, "offset_x", text="X")
        # row.prop(adjustoffset, "offset_y", text="Y")

        # layout.label(text="Movie Color:")
        # layout.prop(adjustlayer, "color_saturation")
        # layout.prop(adjustlayer, "color_multiply")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        adjustlayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust"))

        if (type == 'BOOL' and (identify == 1 or identify == 2)) or (type == 'INT' and (identify == 0 or identify == 1)): #flip x/y
            adjustlayer.use_flip_x = effect.EffectBoolProperties[1].value
            adjustlayer.use_flip_y = effect.EffectBoolProperties[2].value
            adjustlayer.transform.offset_x = effect.EffectIntProperties[0].value * (-1 if effect.EffectBoolProperties[1].value else 1)
            adjustlayer.transform.offset_y = effect.EffectIntProperties[1].value * (-1 if effect.EffectBoolProperties[2].value else 1)
            return

        if (type == "ENUM" and identify == 0) or type == 'FLOAT' or type == 'BOOL':  

            renderX, renderY = context.scene.render.resolution_x, context.scene.render.resolution_y
            movieX, movieY = data.ResolutionWidth, data.ResolutionHeight
            # MovieSeq = firstlayer.sequences.get("rs%d-movie"%data.RichStripID)

            user_scalex, user_scaley = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            resizeEnum = effect.EffectEnumProperties[0].value
            if effect.EffectBoolProperties[0].value:
                user_scaley = user_scalex

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

            adjustlayer.transform.scale_x = final_scalex * user_scalex
            adjustlayer.transform.scale_y = final_scaley * user_scaley

            bpy.ops.sequencer.refresh_all()

        return