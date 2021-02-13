import bpy
from .base import EffectBase

class EffectOriginal(EffectBase):
    @classmethod
    def getName(cls):
        return "Original"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        strips, fstart, fend = cls.enterFistLayer(richstrip)

        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type='ADJUSTMENT', frame_start=fstart, frame_end=fend, channel=data.EffectCurrentMaxChannel1)
        adjustlayer = context.scene.sequence_editor.active_strip
        adjustlayer.use_translation = True
        adjustlayer.name = cls.genRegularStripName(effect.EffectId, "adjust")

        effect.EffectStrips.add().value = adjustlayer.name

        cls.leaveFirstLayer(data)
        return

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        audiolayer = firstlayer.sequences.get("GlobalBaseAudioStrip")
        # adjustlayer = firstlayer.sequences.get(effect.EffectStrips[-1].value)

        if audiolayer is not None:
            layout.label(text="Audio:")
            layout.prop(audiolayer, "volume")
            layout.prop(audiolayer, "mute", icon="MUTE_IPO_ON", toggle=1)

        # layout.label(text="Movie Transform:")
        # row = layout.row(align=True)
        # adjustoffset = adjustlayer.transform
        # row.prop(adjustoffset, "offset_x", text="X")
        # row.prop(adjustoffset, "offset_y", text="Y")

        # layout.label(text="Movie Color:")
        # layout.prop(adjustlayer, "color_saturation")
        # layout.prop(adjustlayer, "color_multiply")
        return