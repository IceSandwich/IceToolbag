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

    def stage_PropertyDefination(self):
        self.addFloatProperty(self.effect, "foreground", 1)
        self.addFloatProperty(self.effect, "background", 0)
        self.addFloatProperty(self.effect, "blackclip", 0)
        self.addFloatProperty(self.effect, "whiteclip", 0)
        self.addFloatProperty(self.effect, "despillamount", 0)
        self.addFloatProperty(self.effect, "despillrange", 0)

        self.addBoolProperty(self.effect, "union_size_lock", True)

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.adjustlayer = self.getEffectStrip(self.richstrip, self.effect, "adjust")
            return

        self.adjustlayer = self.addBuiltinStrip('GAUSSIAN_BLUR', "adjust")
        self.adjustlayer.size_x = self.adjustlayer.size_y = 10

        self.richstrip.sequences.get(self.data.Effects[-2].EffectStrips[-1].value).select = True
        self.translayer = self.addBuiltinStrip('TRANSFORM', "transf")

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

        mapping = self.adjustlayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "matte_curves"), "HUE_CORRECT").curve_mapping
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

        self.adjustlayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "matte_adjust"), "CURVES")


        self.translayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "mask"), "MASK").input_mask_strip = self.adjustlayer
        mapping = self.translayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "despill_curves"), "HUE_CORRECT").curve_mapping
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

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.context, self.adjustlayer, "size_y", self.genbinderName(self.effect, "size_y"), [{
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_size_lock"),
            "isCustomProp": False
        }], "self.size_x if lock == 1 else bind")
        self.addPropertyWithDriver(self.context, self.adjustlayer, "mute", [{
            "name": "onlymatte",
            "seqName": self.translayer.name,
            "seqProp": "mute",
            "isCustomProp": False
        }], '1 if onlymatte == 0 else 0')

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        transflayer = cls.getEffectStrip(richstrip, effect, "transf")
        adjustlayer = cls.getEffectStrip(richstrip, effect, "adjust")

        layout.prop(transflayer, "mute", toggle=0, text="Only Matte")

        layout.prop(cls.getFloatProperty(effect, "foreground"), "value", text="Foreground")
        layout.prop(cls.getFloatProperty(effect, "background"), "value", text="Background")
        layout.prop(cls.getFloatProperty(effect, "blackclip"), "value", text="Black Clip")
        layout.prop(cls.getFloatProperty(effect, "whiteclip"), "value", text="White Clip")

        layout.prop(cls.getFloatProperty(effect, "despillamount"), "value", text="Despill Amount")
        layout.prop(cls.getFloatProperty(effect, "despillrange"), "value", text="Despill Range")

        layout.label(text="Blur:")
        xylock.draw(layout, adjustlayer, "size_x", adjustlayer, cls.genbinderName(effect, "size_y", True), cls.getBoolProperty(effect, "union_size_lock"), "value")

        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'FLOAT':
            adjustlayer = cls.getEffectStrip(richstrip, effect, "adjust")
            transflayer = cls.getEffectStrip(richstrip, effect, "transf")

            fg = cls.getFloatProperty(effect, "foreground").value
            bg = cls.getFloatProperty(effect, "background").value
            bc = cls.getFloatProperty(effect, "blackclip").value
            wc = cls.getFloatProperty(effect, "whiteclip").value
            despill_amount = cls.getFloatProperty(effect, "despillamount").value
            despill_range = cls.getFloatProperty(effect, "despillrange").value

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

            return True

        return False