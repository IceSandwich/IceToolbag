import bpy
from .base import EffectBase
from .widgets import xylock, maskbox, exportbox, cropbox

class EffectGaussianBlur(EffectBase):
    """
        EffectBoolProperty:
            [0]: Lock size
    """
    @classmethod
    def getName(cls):
        return "GaussianBlur"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "union_size_lock", True)
        self.addBoolProperty(self.effect, "mask_through", False)

        self.addExportProperty(self.effect, [
            ["strongX", "blur", "size_x", False],
            ["strongY", "blur", "size_y", True]
        ])


    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.blurlayer = self.getEffectStrip(self.richstrip, self.effect, "blur")
            return
        self.blurlayer = self.addBuiltinEffectStrip('GAUSSIAN_BLUR', "blur")
        modifier = self.blurlayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'
        
        self.addBuiltinEffectStrip('ADJUSTMENT', "adjust")


    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.blurlayer, "size_y", "size_y", [{
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_size_lock"),
            "isCustomProp": False
        }], "self.size_x if lock == 1 else bind", defaultValue=50.0)


    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        blurlayer = cls.getEffectStrip(richstrip, effect, "blur")
        mask_modifier = blurlayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))

        box = layout.box()
        box.label(text="Blur", icon="MATFLUID")
        xylock.drawWithExportBox(box, richstrip, blurlayer, "size_x", "strongX", blurlayer, cls.genbinderName(effect, "size_y", True), "strongY", cls.getBoolProperty(effect, "union_size_lock"), "value")

        layout.separator()

        mask_through = cls.getBoolProperty(effect, "mask_through")
        cropbox.draw(layout, blurlayer, mask_through)

        layout.separator()

        maskbox.draw(layout, effect, data, mask_modifier, mask_through=mask_through)

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "blur").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL':
            if identify == "mask_through":
                blurlayer = cls.getEffectStrip(richstrip, effect, "blur")
                blurlayer.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, identify).value else 'REPLACE'

        return False