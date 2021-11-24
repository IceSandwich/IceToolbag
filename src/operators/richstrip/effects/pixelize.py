import bpy
from .base import EffectBase
from .widgets import xylock, exportbox, maskbox

class EffectPixelize(EffectBase):
    """
        EffectBoolProperties:
            [0]: Fix Scale union?
            [1]: Strong union?
            [3]: Mask though?
    """
    @classmethod
    def getName(cls):
        return "Pixelize"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "fixScale", boolDefault=True)
        self.addBoolProperty(self.effect, "strong", boolDefault=True)
        self.addBoolProperty(self.effect, "mask_though", False)

        self.addExportProperty(self.effect, [ 
            ["fixX", "lg", "fixX", True], 
            ["fixY", "lg", "fixY", True], 
            ["strongX", "sm", "strongX", True], 
            ["strongY", "sm", "strongY", True]
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

        self.translglayer = self.addBuiltinStrip('TRANSFORM', "lg")
        self.translglayer.blend_type = 'REPLACE'
        self.translglayer.use_uniform_scale = False
        self.translglayer.interpolation = 'NONE'
        modifier = self.translglayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'

        self.addBuiltinStrip('ADJUSTMENT', "adjust")

    def stage_BinderDefination(self):
        self.addPropertyWithBinding(self.transsmlayer, "scale_start_x", "strongX", [], "1.0 / (bind+1e-6)", defaultValue=100.0)
        self.addPropertyWithBinding(self.transsmlayer, "scale_start_y", "strongY", [], "1.0 / (bind+1e-6)", defaultValue=100.0)

        fixXbinderName = self.genbinderName(self.effect, "fixX")
        self.addPropertyWithBinding(self.translglayer, "scale_start_x", "fixX", [{
            "name": "strong",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }], "strong * bind", defaultValue=1.0)
        self.addPropertyWithBinding(self.translglayer, "scale_start_y", "fixY", [{
            "name": "strongY",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongY"),
            "isCustomProp": True
        }, {
            "name": "strongX",
            "seqName": self.transsmlayer.name,
            "seqProp": self.genbinderName(self.effect, "strongX"),
            "isCustomProp": True
        }, {
            "name": "locksm",
            "seqName": self.transsmlayer.name,
            "seqProp": "use_uniform_scale",
            "isCustomProp": False
        }, {
            "name": "locklg",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "fixScale"),
            "isCustomProp": False
        }], '(strongX if locksm == 1 else strongY) * (bind if locklg == 0 else self["%s"])'%fixXbinderName, defaultValue=1.0)

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        smtranf = cls.getEffectStrip(richstrip, effect, "sm")
        lgtranf = cls.getEffectStrip(richstrip, effect, "lg")
        mask_modifier = lgtranf.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))

        layout.label(text="Pixelize Strong:")
        xylock.drawWithExportBox(layout, richstrip, smtranf, cls.genbinderName(effect, "strongX", True), "strongX_export", smtranf, cls.genbinderName(effect, "strongY", True), "strongY_export", smtranf, "use_uniform_scale")
        
        layout.label(text="Fix Scale:")
        xylock.drawWithExportBox(layout, richstrip, lgtranf, cls.genbinderName(effect, "fixX", True), "fixX_export", lgtranf, cls.genbinderName(effect, "fixY", True), "fixY_export", cls.getBoolProperty(effect, "fixScale"), "value")

        maskbox.draw(layout, effect, data, mask_modifier, mask_though="mask_though")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "lg").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL' and identify == "mask_though":
            lgtransf = cls.getEffectStrip(richstrip, effect, "lg")
            lgtransf.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, identify).value else 'REPLACE'

        return False