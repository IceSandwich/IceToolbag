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
        cls.enterEditMode(richstrip)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        curves = adjustlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "curves"), "CURVES")
        mapping = curves.curve_mapping
        mapping.use_clip = False
        _, _, _, C = mapping.curves
        for i in range(1, 255):
            val = float(i)/255.0
            C.points.new(val, val)

        cls.addFloatProperty(effect, "blackpoint", 0.0)
        cls.addFloatProperty(effect, "whitepoint", 1.0)
        cls.addFloatProperty(effect, "lift", 0.0)
        cls.addFloatProperty(effect, "gain", 1.0)
        cls.addFloatProperty(effect, "multiply", 1.0)
        cls.addFloatProperty(effect, "offset", 0.0)
        cls.addFloatProperty(effect, "gamma", 1.0)

        cls.leaveEditMode(data)
        return

    @classmethod
    def relink(cls, context, richstrip, effect):
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):

        layout.prop(cls.getFloatProperty(effect, "blackpoint"), "value", text="Blackpoint")
        layout.prop(cls.getFloatProperty(effect, "whitepoint"), "value", text="Whitepoint")
        layout.prop(cls.getFloatProperty(effect, "lift"), "value", text="Lift")
        layout.prop(cls.getFloatProperty(effect, "gain"), "value", text="Gain")
        layout.prop(cls.getFloatProperty(effect, "multiply"), "value", text="Multiply")
        layout.prop(cls.getFloatProperty(effect, "offset"), "value", text="Offset")
        layout.prop(cls.getFloatProperty(effect, "gamma"), "value", text="Gamma")

        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'FLOAT':
            adjustlayer = cls.getEffectStrip(richstrip, "adjust")

            x1, x2 = cls.getFloatProperty(effect, "blackpoint").value, cls.getFloatProperty(effect, "whitepoint").value
            y1, y2 = cls.getFloatProperty(effect, "lift").value, cls.getFloatProperty(effect, "gain").value
            multiply = cls.getFloatProperty(effect, "multiply").value
            offset = cls.getFloatProperty(effect, "offset").value
            gamma = cls.getFloatProperty(effect, "gamma").value

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

            return True

        return False