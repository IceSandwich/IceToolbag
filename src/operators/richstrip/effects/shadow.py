import bpy
from .base import EffectBase
from .widgets import xylock, exportbox

class EffectShadow(EffectBase):
    @classmethod
    def getName(cls):
        return "Shadow"

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "union_size_lock", True)

        self.addExportProperty(self.effect, [
            [ "strongX", "blur", "size_x", False ], 
            [ "strongY", "blur", "size_y", True ], 
            [ "offset", "black", "offset", True ], 
            [ "angle", "black", "angle", True ], 
            [ "scaleX", "black", "scale_start_x", False ], 
            [ "scaleY", "black", "scale_start_y", False ], 
            [ "opacity", "blur", "blend_alpha", False ]
        ])

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.blacklayer = self.getEffectStrip(self.richstrip, self.effect, "black")
            self.blurlayer = self.getEffectStrip(self.richstrip, self.effect, "blur")
            self.copylayer = self.getEffectStrip(self.richstrip, self.effect, "copy")
            return
        lastseq = self.context.selected_sequences[0]
        self.blacklayer = self.addBuiltinEffectStrip('TRANSFORM', 'black')
        self.blacklayer.use_uniform_scale = True
        self.blurlayer = self.addBuiltinEffectStrip('GAUSSIAN_BLUR', "blur")
        self.blurlayer.select = False
        lastseq.select = True
        self.context.scene.sequence_editor.active_strip = lastseq
        self.copylayer = self.addBuiltinEffectStrip('TRANSFORM', 'copy')
        self.addBuiltinEffectStrip('ADJUSTMENT', "adjust")

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

        self.addPropertyWithBinding(self.blurlayer, "size_y", "size_y", [{
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_size_lock"),
            "isCustomProp": False
        }], "self.size_x if lock == 1 else bind", defaultValue=100.0)


    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        blurlayer = cls.getEffectStrip(richstrip, effect, "blur")
        blacklayer = cls.getEffectStrip(richstrip, effect, "black")
        copylayer = cls.getEffectStrip(richstrip, effect, "copy")

        box = layout.box()
        box.label(text="Shadow", icon="MATERIAL")
        cb = blacklayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "cb"))
        split = box.split(factor=0.2)
        split.column().label(text="Color")
        split.column().prop(cb.color_balance, "gain", text="")
        exportbox.draw(box, richstrip, "offset", blacklayer, cls.genbinderName(effect, "offset", True), "Offset")
        exportbox.draw(box, richstrip, "angle", blacklayer, cls.genbinderName(effect, "angle", True), "Direction")
        xylock.drawWithExportBox(box, richstrip, blacklayer, "scale_start_x", "scaleX", blacklayer, "scale_start_y", "scaleY", blacklayer, "use_uniform_scale", union_label="Scale")
        exportbox.draw(box, richstrip, "opacity", blurlayer, "blend_alpha", "Shadow opacity")
        box.prop(copylayer, "mute", toggle=1, text="Only Shadow", icon='GHOST_ENABLED')

        layout.separator()

        box = layout.box()
        box.label(text="Blur", icon="MATFLUID")
        xylock.drawWithExportBox(box, richstrip, blurlayer, "size_x", "strongX", blurlayer, cls.genbinderName(effect, "size_y", True), "strongY", cls.getBoolProperty(effect, "union_size_lock"), "value", union_label="Strong")

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False