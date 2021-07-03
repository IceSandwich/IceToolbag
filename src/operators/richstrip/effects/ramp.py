import bpy
from .base import EffectBase

class EffectRamp(EffectBase):
    """
        EffectEnumProperties:
            [0]: Channel - CRGB
        EffectFloatProperties:
            [0]: blackpoint     ( x value of first point )
            [1]: whitepoint     ( x value of second point )
            [2]: lift           ( y value of first point )
            [3]: gain           ( y value of second point )
            [4]: multiply       ( same as gain )
            [5]: offset
            [6]: gamma
    
        Ref: https://blender.stackexchange.com/questions/46784/can-python-access-control-points-of-hue-modifier

        cur = context.selected_sequences[0].modifiers.new("abc", "CURVES")
        mapping = cur.curve_mapping
        R, G, B, C = mapping.curves
        C.points[0].location.x
        mapping.update()
        bpy.ops.sequencer.refresh_all()


        C.points.new(X, Y)

        Gamma:
        for( int i = 0; i < 256; i++ )    
        {    
            lut[i] = pow((float)(i/255.0), fGamma) * 255.0;
        }    
        x^fGamma

        bpy.ops.sequencer.strip_modifier_add(type='HUE_CORRECT')

    """
    @classmethod
    def getName(cls):
        return "Ramp"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        effectlast = data.Effects[-2].EffectStrips[-1].value
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        # adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust")

        effect.EffectStrips.add().value = adjustlayer.name

        curves = adjustlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "curves"), "CURVES")
        mapping = curves.curve_mapping
        mapping.use_clip = False
        _, _, _, C = mapping.curves
        for i in range(1, 255):
            val = float(i)/255.0
            C.points.new(val, val)

        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 0, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 1, 1)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 2, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 3, 1)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 4, 1)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 5, 0)
        effect.EffectFloatProperties.add().initForEffect(cls.getName(), 6, 1)

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):

        layout.prop(effect.EffectFloatProperties[0], "value", text="Blackpoint")
        layout.prop(effect.EffectFloatProperties[1], "value", text="Whitepoint")
        layout.prop(effect.EffectFloatProperties[2], "value", text="Lift")
        layout.prop(effect.EffectFloatProperties[3], "value", text="Gain")
        layout.prop(effect.EffectFloatProperties[4], "value", text="Multiply")
        layout.prop(effect.EffectFloatProperties[5], "value", text="Offset")
        layout.prop(effect.EffectFloatProperties[6], "value", text="Gamma")

        return

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        if type == 'FLOAT':
            adjustlayer = firstlayer.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "adjust"))

            x1, x2 = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            y1, y2 = effect.EffectFloatProperties[2].value, effect.EffectFloatProperties[3].value
            multiply, offset, gamma = effect.EffectFloatProperties[4].value, effect.EffectFloatProperties[5].value, effect.EffectFloatProperties[6].value

            curves = adjustlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "curves"))
            mapping = curves.curve_mapping
            R, G, B, C = mapping.curves
            
            C.points[0].location.y = y1+offset
            C.points[0].location.x = x1
            step = 1 / 255.0
            k = float(y2*multiply+offset-y1)/float(x2-x1+0.00001)
            for i in range(1, 256):
                C.points[i].location.x = C.points[i-1].location.x + step
                C.points[i].location.y = k*pow(C.points[i].location.x - C.points[0].location.x, gamma)+C.points[0].location.y

            mapping.update()
            bpy.ops.sequencer.refresh_all()

        return