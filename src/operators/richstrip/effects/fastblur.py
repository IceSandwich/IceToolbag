import bpy
from .base import EffectBase
from .widgets import xylock, exportbox, maskbox

class EffectFastBlur(EffectBase):
    @classmethod
    def getName(cls):
        return "FastBlur"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "mask_through", False)
        self.addExportProperty(self.effect, [
            ["strongX", "sm", "strongX", True ],
            ["strongY", "sm", "strongY", True ],
            ["mulstrong", "md", 'mulstrong', True ],
            ["fixX", "lg", "scale_start_x", False ],
            ["fixY", "lg", "scale_start_y", False ],
            ["opacity", "lg", "blend_alpha", False ],
            ["saturation", "lg", "color_saturation", False ],
        ])


    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.transsmlayer = self.getEffectStrip(self.richstrip, self.effect, "sm")
            self.transmdlayer = self.getEffectStrip(self.richstrip, self.effect, "md")
            self.translglayer = self.getEffectStrip(self.richstrip, self.effect, "lg")
            return

        self.transsmlayer = self.addBuiltinEffectStrip('TRANSFORM', "sm")
        self.transsmlayer.blend_type = 'ALPHA_UNDER'
        self.transsmlayer.use_uniform_scale = True
        self.transsmlayer.interpolation = 'BICUBIC'

        self.transmdlayer = self.addBuiltinEffectStrip('TRANSFORM', "md")
        self.transmdlayer.blend_type = 'ALPHA_UNDER'
        self.transmdlayer.use_uniform_scale = True
        self.transmdlayer.scale_start_x = 1.2
        self.transmdlayer.interpolation = 'BICUBIC'

        self.translglayer = self.addBuiltinEffectStrip('TRANSFORM', "lg")
        self.translglayer.blend_type = 'REPLACE'
        self.translglayer.use_uniform_scale = True
        self.translglayer.interpolation = 'BICUBIC'
        modifier = self.translglayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'

        self.addBuiltinEffectStrip('ADJUSTMENT', "adjust")

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.transsmlayer, "scale_start_x", "strongX", [], "1.0 / (bind+1e-6)", defaultValue=200.0)
        self.addPropertyWithBinding(self.transsmlayer, "scale_start_y", "strongY", [], "1.0 / (bind+1e-6)", defaultValue=200.0)

        mulstrongbinderName = self.genbinderName(self.effect, "mulstrong")
        self.addPropertyWithBinding(self.transmdlayer, "scale_start_x", "mulstrong", [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }], 'strong * bind', defaultValue=1.3)

        self.addPropertyWithDriver(self.context, self.transmdlayer, "scale_start_y", [{
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
            "name": "locksm",
            "seqName": self.transsmlayer.name,
            "seqProp": "use_uniform_scale",
            "isCustomProp": False
        }], 'self["%s"] * (strongX if locksm == 1 else strongY)'%mulstrongbinderName)

    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, effect, "sm")
        mdtranf = cls.getEffectStrip(richstrip, effect, "md")
        lgtranf = cls.getEffectStrip(richstrip, effect, "lg")

        box = layout.box()
        box.label(text="Blur", icon="MATFLUID")
        xylock.drawWithExportBox(box, richstrip, smtranf, cls.genbinderName(effect, "strongX", True), "strongX", smtranf, cls.genbinderName(effect, "strongY", True), "strongY", smtranf, "use_uniform_scale", union_label="Blur Strong")
        exportbox.draw(box, richstrip, "mulstrong", mdtranf, cls.genbinderName(effect, "mulstrong", True), text="Multiply Strong")
        xylock.drawWithExportBox(box, richstrip, lgtranf, "scale_start_x", "fixX", lgtranf, "scale_start_y", "fixY", lgtranf, "use_uniform_scale", union_label="Fix Scale")

        layout.separator()

        box = layout.box()
        box.label(text="Color", icon="COLOR")
        exportbox.draw(box, richstrip, "opacity", lgtranf, "blend_alpha", text="Opacity")
        exportbox.draw(box, richstrip, "saturation", lgtranf, "color_saturation", text="Saturation")

        layout.separator()

        maskbox.draw(layout, effect, data, lgtranf.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask")), mask_through=cls.getBoolProperty(effect, "mask_through"))

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "lg").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL':
            if identify == "mask_through":
                lglayer = cls.getEffectStrip(richstrip, effect, "lg")
                lglayer.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, identify).value else 'REPLACE'

        return False