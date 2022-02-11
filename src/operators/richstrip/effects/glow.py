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
        glowlayer = cls.addBuiltinEffectStrip_ClassLevel(context, richstrip, effect, 'GLOW', "glow")
        adjustlayer = cls.addBuiltinEffectStrip_ClassLevel(context, richstrip, effect, 'ADJUSTMENT', "adjust")
        
        modifier = glowlayer.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'

        cls.addExportProperty(effect, [
            ["threshold", "glow", "threshold", False ],
            ["clamp", "glow", "clamp", False ],
            ["boost_factor", "glow", "boost_factor", False ],
            ["blur", "glow", "blur_radius", False ],
            ["quality", "glow", "quality", False ]
        ])
        cls.addBoolProperty(effect, "mask_through", False)

        cls.leaveEditMode(data)
        return

    @classmethod
    def relink(cls, context, richstrip, effect):
        return

    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        glowlayer = cls.getEffectStrip(richstrip, effect, "glow")

        box = layout.box()
        box.label(text="Glow", icon="LIGHT")
        exportbox.draw(box, richstrip, "threshold", glowlayer, "threshold", text="Threshold")
        exportbox.draw(box, richstrip, "clamp", glowlayer, "clamp", text="Clamp")
        exportbox.draw(box, richstrip, "boost_factor", glowlayer, "boost_factor", text="Boost Factor")
        box.prop(glowlayer, "use_only_boost", toggle=0)
        
        layout.separator()

        box = layout.box()
        box.label(text="Blur", icon="MATFLUID")
        exportbox.draw(box, richstrip, "blur", glowlayer, "blur_radius", text="Blur Radius")
        exportbox.draw(box, richstrip, "quality", glowlayer, "quality", text="Quality")

        layout.separator()

        maskbox.draw(layout, effect, data, glowlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask")), cls.getBoolProperty(effect, "mask_through"))

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "glow").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL':
            if identify == "mask_through":
                glowlayer = cls.getEffectStrip(richstrip, effect, "glow")
                glowlayer.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, identify).value else 'REPLACE'


