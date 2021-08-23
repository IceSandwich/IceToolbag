import bpy
import os
from .base import EffectBase

class EffectMirror(EffectBase):
    @classmethod
    def getName(cls):
        return "Mirror"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
        copy = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', "copy")
        color = cls.addBuiltinEffectStrip(context, richstrip, effect, 'COLOR', 'mask')

        bpy.ops.sequencer.select_all(action='DESELECT')
        color.select = True
        context.scene.sequence_editor.active_strip = color
        bpy.ops.sequencer.meta_make()
        metastrip = context.scene.sequence_editor.active_strip

        # swap color and metastrip name
        tmp = color.name
        color.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "base")
        metastrip.name = tmp

        bpy.ops.sequencer.meta_toggle() # enter meta strip
        bpy.ops.sequencer.select_all(action='DESELECT')

        color.channel = 1
        color.select = True
        dirpath = os.path.dirname(os.path.abspath(os.path.join("resources", "blackwhite.jpg"))) + "\\"
        bpy.ops.sequencer.image_strip_add(directory=dirpath, files=[{"name":"blackwhite.jpg", "name":"blackwhite.jpg"}], frame_start=richstrip.frame_final_start, frame_end=richstrip.frame_final_end, channel=2, fit_method='STRETCH', set_view_transform=False)
        imgstrip = context.scene.sequence_editor.active_strip
        imgstrip.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "img")

        bpy.ops.sequencer.select_all(action='DESELECT') # leave meta strip
        bpy.ops.sequencer.meta_toggle()
        bpy.ops.sequencer.select_all(action='DESELECT')

        metastrip.mute = True
        modifier = copy.modifiers.new(cls.genRegularStripName(data.RichStripID, effect.EffectId, "matte"), "MASK")
        modifier.input_mask_strip = metastrip

        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'ADJUSTMENT', "adjust")

        cls.leaveEditMode(data)
        return

    @classmethod
    def relink(cls, context, richstrip, effect):
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        
        return