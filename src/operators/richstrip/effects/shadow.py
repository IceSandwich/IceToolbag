import bpy
from .base import EffectBase
from .widgets import xylock

class EffectShadow(EffectBase):
    """
        EffectBoolProperty:
            [0]: Lock size
    """
    @classmethod
    def getName(cls):
        return "Shadow"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "union_size_lock", True)

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.blacklayer = self.getEffectStrip(self.richstrip, self.effect, "black")
            self.blurlayer = self.getEffectStrip(self.richstrip, self.effect, "blur")
            self.copylayer = self.getEffectStrip(self.richstrip, self.effect, "copy")
            return
        lastseq = self.context.selected_sequences[0]
        self.blacklayer = self.addBuiltinStrip('TRANSFORM', 'black')
        self.blurlayer = self.addBuiltinStrip('GAUSSIAN_BLUR', "blur")
        self.blurlayer.select = False
        lastseq.select = True
        self.context.scene.sequence_editor.active_strip = lastseq
        self.copylayer = self.addBuiltinStrip('TRANSFORM', 'copy')
        self.addBuiltinStrip('ADJUSTMENT', "adjust")

        bc = self.blacklayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "bc"), "BRIGHT_CONTRAST")
        bc.bright = 100
        cb = self.blacklayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "cb"), "COLOR_BALANCE")
        cb.color_balance.gamma = (1, 1, 1)
        cb.color_balance.lift = (2, 2, 2)
        cb.color_balance.gain = (0, 0, 0)
        self.copylayer.blend_type = "ALPHA_OVER"
        self.blurlayer.blend_type = "REPLACE"
        self.blurlayer.size_x = 100
        self.blacklayer.mute = True

    def stage_BinderDefination(self):
        offsetPropertyName = self.genbinderName(self.effect, "offset")
        anglePropertyName = self.genbinderName(self.effect, "angle")
        if self.blacklayer.get(offsetPropertyName) is None: self.blacklayer[offsetPropertyName] = 0
        if self.blacklayer.get(anglePropertyName) is None: self.blacklayer[anglePropertyName] = 0

        self.addPropertyWithDriver(self.context, self.blacklayer.transform, "offset_x", [{
            "name": "angle",
            "seqName": self.blacklayer.name,
            "seqProp": anglePropertyName,
            "isCustomProp": True
        }, {
            "name": "bind",
            "seqName": self.blacklayer.name,
            "seqProp": offsetPropertyName,
            "isCustomProp": True
        }], "cos(radians(angle))*bind")

        self.addPropertyWithDriver(self.context, self.blacklayer.transform, "offset_y", [{
            "name": "angle",
            "seqName": self.blacklayer.name,
            "seqProp": anglePropertyName,
            "isCustomProp": True
        }, {
            "name": "bind",
            "seqName": self.blacklayer.name,
            "seqProp": offsetPropertyName,
            "isCustomProp": True
        }], "sin(radians(angle))*bind")

        # self.addPropertyWithDriver(self.context, self.blacklayer.transform, "scale_y", [], "self.scale_x")

        self.addPropertyWithBinding(self.blurlayer, "size_y", "size_y", [{
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_size_lock"),
            "isCustomProp": False
        }], "self.size_x if lock == 1 else bind")


    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        blurlayer = cls.getEffectStrip(richstrip, effect, "blur")
        blacklayer = cls.getEffectStrip(richstrip, effect, "black")

        layout.label(text="Strong:")
        xylock.draw(layout, blurlayer, "size_x", blurlayer, cls.genbinderName(effect, "size_y", True), cls.getBoolProperty(effect, "union_size_lock"), "value")

        layout.label(text="Color:")
        cb = blacklayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "cb"))
        layout.prop(cb.color_balance, "gain", text="Shadow Color")
        
        layout.label(text="Offset:")
        layout.prop(blacklayer, cls.genbinderName(effect, "offset", True), text="Shadow offset")

        layout.label(text="Angle:")
        layout.prop(blacklayer, cls.genbinderName(effect, "angle", True), text="Shadow direction")

        layout.label(text="Scale:")
        layout.prop(blacklayer.transform, "scale_x", text="Shadow Scale X")
        layout.prop(blacklayer.transform, "scale_y", text="Shadow Scale Y")

        layout.label(text="Opacity:")
        layout.prop(blurlayer, "blend_alpha", text="Shadow opacity")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False