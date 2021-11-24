import bpy
from .base import EffectBase
from .widgets import exportbox, maskbox

class EffectGlow(EffectBase):
    @classmethod
    def getName(cls):
        return "Glow"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        glowlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'GLOW', "glow")
        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")
        
        modifier = glowlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'

        cls.addExportProperty(effect, [
            ["threshold", "glow", "threshold", False ],
            ["clamp", "glow", "clamp", False ],
            ["boost_factor", "glow", "boost_factor", False ],
            ["blur", "glow", "blur_radius", False ],
            ["quality", "glow", "quality", False ]
        ])
        cls.addBoolProperty(effect, "mask_though", False)

        cls.leaveEditMode(data)
        return

    @classmethod
    def relink(cls, context, richstrip, effect):
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        glowlayer = cls.getEffectStrip(richstrip, effect, "glow")

        layout.label(text="Glow:")
        exportbox.draw(layout, richstrip, "threshold_export", glowlayer, "threshold", text="Threshold")
        exportbox.draw(layout, richstrip, "clamp_export", glowlayer, "clamp", text="Clamp")
        exportbox.draw(layout, richstrip, "boost_factor_export", glowlayer, "boost_factor", text="Boost Factor")
        layout.prop(glowlayer, "use_only_boost", toggle=1)
        
        layout.label(text="Additional:")
        exportbox.draw(layout, richstrip, "blur_export", glowlayer, "blur_radius", text="Blur Radius")
        exportbox.draw(layout, richstrip, "quality_export", glowlayer, "quality", text="Quality")

        maskbox.draw(layout, effect, data, glowlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask")), mask_though="mask_though")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "glow").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL':
            if identify == "mask_though":
                glowlayer = cls.getEffectStrip(richstrip, effect, "glow")
                glowlayer.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, identify).value else 'REPLACE'


