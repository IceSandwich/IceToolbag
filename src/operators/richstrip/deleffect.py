import bpy
from .effects import ICETB_EFFECTS_DICTS, ICETB_EFFECTS_NAMES

class ICETB_OT_RichStrip_Delete(bpy.types.Operator):
    bl_idname = "icetb.richstrip_deleffect"
    bl_label = "Are you sure to delete the selected effect which will take a few minutes to process?"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        data = context.selected_sequences[0].IceTB_richstrip_data
        if len(data.Effects) -1 == data.EffectsCurrent:
            return True
        return False

    def execute(self, context):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        effectName = effect.EffectType

        if effectName == "Original":
            self.report({'ERROR'}, "Can't delete original effect.")
            return {'CANCELLED'}

        if effectName in ICETB_EFFECTS_NAMES:
            cls = ICETB_EFFECTS_DICTS[effectName]
            cureffectIdx = data.EffectsCurrent
            cls.enterEditMode(richstrip)
            seqs = richstrip.sequences

            adjseq = seqs.get(effect.EffectStrips[-1].value)
            crossadjseq = seqs.get(data.Effects[cureffectIdx-1].EffectStrips[-1].value)

            channeloffset = adjseq.channel - crossadjseq.channel
            # move all sequences above this effect
            # channeloffset = len(effect.EffectStrips)
            # for i in range(cureffectIdx + 1, len(data.Effects)):
            #     for buildinseqName in data.Effects[i].EffectStrips:
            #         buildinseq = seqs.get(buildinseqName.value)
            #         buildinseq.channel -= channeloffset
            #         if 'input_1' in dir(buildinseq) and buildinseq.input_1 == adjseq:
            #             buildinseq.input_1 = crossadjseq

            # delete the sequences in this effect
            for buildinseqName in effect.EffectStrips:
                buildinseq = seqs.get(buildinseqName.value)
                if buildinseq is not None: # some strip will delete automatically, we don't need to do it again
                    buildinseq.select = True
                    bpy.ops.sequencer.delete()
            
            # delete this effect from list
            data.Effects.remove(cureffectIdx)
            data.EffectCurrentMaxChannel1 -= channeloffset

            # cls.delete(context, richstrip, data, effect)
            cls.leaveEditMode(data)
            bpy.ops.sequencer.refresh_all()

        else:
            self.report({'ERROR'}, "Unknow effect name called " + effectName)
            return {'CANCELLED'}

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)