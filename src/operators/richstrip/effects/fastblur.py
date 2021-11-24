import bpy
from .base import EffectBase
from .widgets import xylock, exportbox, maskbox

class EffectFastBlur(EffectBase):
    @classmethod
    def getName(cls):
        return "FastBlur"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "union_fix_lock", boolDefault=True)

        self.addExportProperty(self.effect, [
            ["strongX", "sm", "strongX", True ],
            ["strongY", "sm", "strongY", True ],
            ["mulstrong", "md", "scale_start_x", False ],
            ["fixX", "lg", "fixX", True ],
            ["fixY", "lg", "fixY", True ],
            ["opacity", "lg", "blend_alpha", False ],
            ["saturation", "lg", "color_saturation", False ],
        ])

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.transsmlayer = self.getEffectStrip(self.richstrip, self.effect, "sm")
            self.translglayer = self.getEffectStrip(self.richstrip, self.effect, "lg")
            return

        self.transsmlayer = self.addBuiltinStrip('TRANSFORM', "sm")
        self.transsmlayer.blend_type = 'ALPHA_UNDER'
        self.transsmlayer.use_uniform_scale = True
        self.transsmlayer.interpolation = 'NONE'

        transmdlayer = self.addBuiltinStrip('TRANSFORM', "md")
        transmdlayer.blend_type = 'ALPHA_UNDER'
        transmdlayer.use_uniform_scale = True
        transmdlayer.scale_start_x = 1.2
        transmdlayer.interpolation = 'BICUBIC'

        self.translglayer = self.addBuiltinStrip('TRANSFORM', "lg")
        self.translglayer.blend_type = 'REPLACE'
        # self.translglayer.use_uniform_scale = True
        self.translglayer.interpolation = 'BICUBIC'
        modifier = self.translglayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'

        self.addBuiltinStrip('ADJUSTMENT', "adjust")

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.transsmlayer, "scale_start_x", "strongX", [], "1.0 / (bind+1e-6)", defaultValue=200.0)
        self.addPropertyWithBinding(self.transsmlayer, "scale_start_y", "strongY", [], "1.0 / (bind+1e-6)", defaultValue=200.0)

        fixXbinderName = self.genbinderName(self.effect, "fixX")
        self.addPropertyWithBinding(self.translglayer, "scale_start_x", "fixX", [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }], 'strong * bind', defaultValue=1.3)
        self.addPropertyWithBinding(self.translglayer, "scale_start_y", "fixY", [{
            "name": "strongX",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }, {
            "name": "strongY",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongY"),
            "isCustomProp": True
        }, {
            "name": "locklg",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_fix_lock"),
            "isCustomProp": False
        }, {
            "name": "locksm",
            "seqName": self.transsmlayer.name,
            "seqProp": "use_uniform_scale",
            "isCustomProp": False
        }], '(strongX if locksm == 1 else strongY) * (self["%s"] if locklg == 1 else bind)'%fixXbinderName, defaultValue=1.3)


    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, effect, "sm")
        mdtranf = cls.getEffectStrip(richstrip, effect, "md")
        lgtranf = cls.getEffectStrip(richstrip, effect, "lg")

        layout.label(text="Blur Strong:")
        xylock.drawWithExportBox(layout, richstrip, smtranf, cls.genbinderName(effect, "strongX", True), "strongX_export", smtranf, cls.genbinderName(effect, "strongY", True), "strongY_export", smtranf, "use_uniform_scale")

        layout.label(text="Fix Strong:")
        exportbox.draw(layout, richstrip, "mulstrong_export", mdtranf, "scale_start_x", text="Multiply Strong")

        layout.label(text="Fix Scale:")
        xylock.drawWithExportBox(layout, richstrip, lgtranf, cls.genbinderName(effect, "fixX", True), "fixX_export", lgtranf, cls.genbinderName(effect, "fixY", True), "fixY_export", cls.getBoolProperty(effect, "union_fix_lock"), "value")

        layout.label(text="Alpha:")
        exportbox.draw(layout, richstrip, "opacity_export", lgtranf, "blend_alpha", text="Blend Opacity")

        layout.label(text="Color:")
        exportbox.draw(layout, richstrip, "saturation_export", lgtranf, "color_saturation", text="Saturation")

        maskbox.draw(layout, effect, data, lgtranf.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask")))
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "lg").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        return False