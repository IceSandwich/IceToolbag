import bpy
from .base import EffectBase
from ....datas import RichStripData, RichStripEffect

import bpy
from .base import EffectBase
from .original import EffectOriginal
from .widgets import xylock, cropbox, maskbox, exportbox

class EffectCopy(EffectBase):
    @classmethod
    def getName(cls):
        return "Copy from original"

    def stage_Before(self):
        self.getMovieStrip(self.richstrip).select = True

    def stage_PropertyDefination(self):
        self.addBoolProperty(self.effect, "mask_through", False)
        self.addExportProperty(self.effect, [
            [ "pos_x", "copy", "transform.offset_x", False ],
            [ "pos_y", "copy", "transform.offset_y", False ],
            [ "rotation", "copy", "transform.rotation", False ],
            [ "scalex", "copy", "transform.scale_x", False ],
            [ "scaley", "copy", "transform.scale_y", False ],
            [ "alpha", "copy", "blend_alpha", False ]
        ])

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            return
        copylayer = self.addBuiltinEffectStrip('TRANSFORM', 'copy')
        modifier = copylayer.modifiers.new(self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "mask"), 'MASK')
        modifier.input_mask_type = 'ID'

        self.addBuiltinEffectStrip('ADJUSTMENT', "adjust")

    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        copylayer = cls.getEffectStrip(richstrip, effect, "copy")
        mask_modifier = copylayer.modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
        mask_through = cls.getBoolProperty(effect, "mask_through")

        box = layout.box()
        box.row().label(text="Translate", icon="ORIENTATION_LOCAL")
        xylock.drawWithExportBox_NoLock(box, richstrip, copylayer.transform, "offset_x", "pos_x", copylayer.transform, "offset_y", "pos_y" )

        layout.separator()

        box = layout.box()
        box.label(text="Scale", icon="FIXED_SIZE")
        xylock.drawWithExportBox_NoLock(box, richstrip, copylayer.transform, "scale_x", "scalex", copylayer.transform, "scale_y", "scaley")

        layout.separator()

        box = layout.box()
        box.label(text="Rotation", icon="DRIVER_ROTATIONAL_DIFFERENCE")
        exportbox.draw(box, richstrip, "rotation", copylayer.transform, "rotation", text="Rotation")

        layout.separator()

        box = layout.box()
        box.label(text="Mirror", icon="MOD_MIRROR")
        row = box.row(align=True)
        row.prop(copylayer, "use_flip_x", toggle=1, text="Flip X", icon="ARROW_LEFTRIGHT")
        row.prop(copylayer, "use_flip_y", toggle=1, text="Flip Y", icon="EMPTY_SINGLE_ARROW")

        layout.separator()

        box = layout.box()
        box.row().label(text="Blend", icon="OVERLAY")
        # box.row().prop(copylayer, "blend_alpha")
        exportbox.draw(box, richstrip, "alpha", copylayer, "blend_alpha", text="Opacity")
        box.row().prop(mask_through, "value", text="Through")

        layout.separator()

        cropbox.draw(layout, copylayer, mask_through)

        layout.separator()

        maskbox.draw(layout, effect, data, mask_modifier, mask_through)

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        if type == 'MASK_SET':
            mask_modifier = cls.getEffectStrip(richstrip, effect, "copy").modifiers.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask"))
            mask_modifier.input_mask_id = bpy.data.masks[identify]

        if type == 'BOOL':
            if identify == "mask_through":
                copylayer = cls.getEffectStrip(richstrip, effect, "copy")
                copylayer.blend_type = 'ALPHA_OVER' if cls.getBoolProperty(effect, "mask_through").value else 'REPLACE'

        return False