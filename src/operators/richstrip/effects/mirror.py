import bpy, os
from .base import EffectBase
from .widgets import exportbox

class EffectMirror(EffectBase):
    @classmethod
    def getName(cls):
        return "Mirror"

    def stage_PropertyDefination(self):
        self.addExportProperty(self.effect, [
            [ "scale", "img", "scaleFactor", True],
            [ "offset", "white", "offsetFactor", True]
        ])


    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.imgstrip = self.getEffectStrip(self.richstrip, self.effect, "img")
            self.white = self.getEffectStrip(self.richstrip, self.effect, "white")
            return

        copy = self.addBuiltinEffectStrip(self.context, self.richstrip, self.effect, 'TRANSFORM', "copy")
        color = self.addBuiltinEffectStrip(self.context, self.richstrip, self.effect, 'COLOR', 'mask') # this name will be replaced later.

        bpy.ops.sequencer.select_all(action='DESELECT')
        color.select = True
        self.context.scene.sequence_editor.active_strip = color
        bpy.ops.sequencer.meta_make()
        metastrip = self.context.scene.sequence_editor.active_strip

        # swap color and metastrip name
        tmp = color.name
        color.name = self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "base")
        metastrip.name = tmp

        bpy.ops.sequencer.meta_toggle() # enter meta strip
        bpy.ops.sequencer.select_all(action='DESELECT')

        color.channel = 1
        color.select = True

        self.white = self.addBuiltinEffectStrip(self.context, self.richstrip, self.effect, 'COLOR', 'white')
        self.data.EffectCurrentMaxChannel1 -= 1 # preserve channel cause addBuiltinEffectStrip will add 1
        self.white.color = (1, 1, 1)
        self.white.channel = 2
        self.white.blend_type = 'ADD'
        
        dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "..", "resources", "")
        bpy.ops.sequencer.image_strip_add(directory=dirpath, files=[{"name":"blackwhite.jpg", "name":"blackwhite.jpg"}], frame_start=self.richstrip.frame_final_start, frame_end=self.richstrip.frame_final_end, channel=2, fit_method='STRETCH', set_view_transform=False)
        imgstrip = self.context.scene.sequence_editor.active_strip
        imgstrip.name = self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "img")
        self.effect.EffectStrips.add().value = imgstrip.name
        imgstrip.blend_type = 'LIGHTEN'

        bpy.ops.sequencer.select_all(action='DESELECT') # leave meta strip
        bpy.ops.sequencer.meta_toggle()
        bpy.ops.sequencer.select_all(action='DESELECT')

        metastrip.mute = True
        modifier = copy.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "matte"), "MASK")
        modifier.input_mask_strip = metastrip
        self.imgstrip = imgstrip

        adjustlayer = self.addBuiltinEffectStrip(self.context, self.richstrip, self.effect, 'ADJUSTMENT', "adjust")

        return
    def stage_BinderDefination(self):
        expression = "max(1e-6, bind/%d)"%(self.context.scene.render.resolution_y)
        offsetbinderName = self.genbinderName(self.effect, "offsetFactor")
        self.addPropertyWithBinding(self.white, "transform.scale_y", "offsetFactor", [], expression, defaultValue=0.0)
        self.addPropertyWithDriver(self.context, self.white.transform, "offset_y", [{
            "name": "bind",
            "seqName": self.white.name,
            "seqProp": offsetbinderName,
            "isCustomProp": True
        }], "-(%d/2-bind)-bind/2+1"%(self.context.scene.render.resolution_y))

        self.addPropertyWithBinding(self.imgstrip, "transform.offset_y", "scaleFactor", [{
            "name": "offset",
            "seqName": self.white.name,
            "seqProp": offsetbinderName,
            "isCustomProp": True
        }], "-({0}-{0}*bind)/2+offset".format(self.context.scene.render.resolution_y), defaultValue=1.0, numRange=(0, self.NUMRANGE_MAX), description="Scale of gradient")
        self.addPropertyWithDriver(self.context, self.imgstrip.transform, "scale_y", [{
            "name": "bind",
            "seqName": self.imgstrip.name,
            "seqProp": self.genbinderName(self.effect, "scaleFactor"),
            "isCustomProp": True
        }], "max(1e-6, bind*%d/1080)"%(self.context.scene.render.resolution_y))

        return

    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        metastrip = cls.getEffectStrip(richstrip, effect, "mask")
        imgstrip = metastrip.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "img"))
        white = metastrip.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "white"))

        layout.label(text="Gradient:")
        layout.prop(metastrip, "mute", toggle=0, invert_checkbox=True, text="Only Mate")
        # layout.prop(white, cls.genbinderName(effect, "offsetFactor", True), text="Offset")
        exportbox.draw(layout, richstrip, "offset_export", white, cls.genbinderName(effect, "offsetFactor", True), "Offset")

        exportbox.draw(layout, richstrip, "scale_export", imgstrip, cls.genbinderName(effect, "scaleFactor", True), "Scale")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        return False