import bpy
from .base import EffectBase
from .widgets import xylock

class EffectMatte(EffectBase):
    """
        EffectFloatProperties:
            [0] Foreground
            [1] Background
            [2] Black clip
            [3] White clip
            [4] Blur X
            [5] Despill Amount
            [6] Despill Range
        EffectBoolProperties:
            [0]: Blur union
    """
    @classmethod
    def getName(cls):
        return "Matte"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        effectlast = data.Effects[-2].EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectlast).select = True
        bpy.ops.sequencer.effect_strip_add(type='GAUSSIAN_BLUR', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.size_x = adjustlayer.size_y = 10
        adjustlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust")

        data.EffectCurrentMaxChannel1 += 1
        strips.get(effectlast).select = True
        bpy.ops.sequencer.effect_strip_add(type='TRANSFORM', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        translayer = context.scene.sequence_editor.active_strip
        translayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf")

        effect.EffectStrips.add().value = adjustlayer.name
        effect.EffectStrips.add().value = translayer.name
        
        # green band
        bandWidth = 1.0/6
        greenStart = bandWidth*1+bandWidth*0.5
        greenEnd = bandWidth*2+bandWidth*0.5
        greenThirdp1 = greenStart + bandWidth/3.0/2.0 #narrow
        greenThirdp2 = greenEnd - bandWidth/3.0/2.0
        yelloStart = bandWidth*0.5
        yelloMid = bandWidth
        yelloNearMid = yelloMid + bandWidth/3.0/2.0
        cyanMid = bandWidth*3
        cyanNearMid = cyanMid - bandWidth/3.0/2.0
        cyanEnd = bandWidth*3+bandWidth*0.5

        mapping = adjustlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "matte_curves"), "HUE_CORRECT").curve_mapping
        _, S, V = mapping.curves
        for p in S.points:
            p.location.y = 0
        for i in range(len(V.points)-1, -1, -1):
            if V.points[i].location.x == 1 or V.points[i].location.x == 0:
                V.points[i].location.y = 1
            else:
                V.points.remove(V.points[i])

        V.points.new(yelloMid, 1)
        V.points.new(yelloNearMid, 0)
        V.points.new(cyanNearMid, 0)
        V.points.new(cyanMid, 1)

        adjustlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "matte_adjust"), "CURVES")



        translayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"), "MASK").input_mask_strip = adjustlayer
        mapping = translayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "despill_curves"), "HUE_CORRECT").curve_mapping
        _, S, _ = mapping.curves
        for i in range(len(S.points)-1, -1, -1):
            if S.points[i].location.x == 1 or S.points[i].location.x == 0:
                S.points[i].location.y = 0.5
            else:
                S.points.remove(S.points[i])
        
        S.points.new(yelloMid, 0.5)
        S.points.new(yelloNearMid, 0)
        S.points.new(cyanNearMid, 0)
        S.points.new(cyanMid, 0.5)

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 1)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 2, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 3, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 4, adjustlayer.size_x)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 5, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 6, 0)

        effect.EffectBoolProperties.add().initForEffect(cls.getName(), 0, True)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        transflayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf"))
        adjustlayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust"))

        layout.prop(transflayer, "mute", toggle=0, text="Only Matte")

        layout.prop(effect.EffectFloatProperties[0], "value", text="Foreground")
        layout.prop(effect.EffectFloatProperties[1], "value", text="Background")
        layout.prop(effect.EffectFloatProperties[2], "value", text="Black Clip")
        layout.prop(effect.EffectFloatProperties[3], "value", text="White Clip")

        layout.prop(effect.EffectFloatProperties[5], "value", text="Despill Amount")
        layout.prop(effect.EffectFloatProperties[6], "value", text="Despill Range")

        layout.label(text="Blur:")
        xylock.draw(layout, effect.EffectFloatProperties[4], "value", adjustlayer, "size_y", effect.EffectBoolProperties[0], "value")

        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        if type == 'FLOAT':
            adjustlayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust"))
            transflayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "transf"))

            fg, bg, bc, wc = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value, effect.EffectFloatProperties[2].value, effect.EffectFloatProperties[3].value
            blurx, despill_amount, despill_range = effect.EffectFloatProperties[4].value, effect.EffectFloatProperties[5].value, effect.EffectFloatProperties[6].value
            
            adjustlayer.size_x = blurx
            if effect.EffectBoolProperties[0].value:
                adjustlayer.size_y = blurx


            # green band
            bandWidth = 1.0/6
            greenStart = bandWidth*1+bandWidth*0.5
            greenEnd = bandWidth*2+bandWidth*0.5
            greenThirdp1 = greenStart + bandWidth/3.0/2.0 #narrow
            greenThirdp2 = greenEnd - bandWidth/3.0/2.0
            yelloStart = bandWidth*0.5
            yelloMid = bandWidth
            yelloNearMid = yelloMid + bandWidth/3.0/2.0
            cyanMid = bandWidth*3
            cyanNearMid = cyanMid - bandWidth/3.0/2.0
            cyanEnd = bandWidth*3+bandWidth*0.5


            mapping = adjustlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "matte_adjust")).curve_mapping
            _, _, _, C = mapping.curves
            C.points[0].location.x = bc
            C.points[1].location.x = 1-wc
            mapping.update()

            # TODO: control foreground and blackground

            # curves = adjustlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "curves"))
            # mapping = curves.curve_mapping
            # R, G, B, C = mapping.curves
            # k = float(y2-y1)/float(x2-x1+0.00001)

            # C.points[0].location.x = x1
            # C.points[0].location.y = y1 + offset
            # C.points[1].location.x = x2
            # C.points[1].location.y = y2*multiply + offset

            mapping = transflayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "despill_curves")).curve_mapping
            _, S, _ = mapping.curves
            S.points[1].location.x = yelloMid-despill_range*bandWidth*0.5
            S.points[4].location.x = cyanMid+despill_range*bandWidth*0.5
            S.points[2].location.x = S.points[1].location.x + bandWidth/3.0/2.0
            S.points[3].location.x = S.points[4].location.x - bandWidth/3.0/2.0
            S.points[2].location.y = S.points[3].location.y = 0.5-despill_amount*0.5

            mapping.update()

            bpy.ops.sequencer.refresh_all()

        return