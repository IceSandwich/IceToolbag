import bpy
from .effects import ICETB_EFFECTS_DICTS, ICETB_EFFECTS_NAMES

class ICETB_OT_RichStrip_Move(bpy.types.Operator):
    bl_idname = "icetb.richstrip_mveffect"
    bl_label = "Move Effect"
    bl_options = {"REGISTER", "UNDO"}

    dire: bpy.props.StringProperty(name="Move direction", default="UP")

    @classmethod
    def poll(cls, context):
        return True

    def mvlayer(self, richstrip, data, effect, seqs, framestart, frameend):
        cureffectIdx = data.EffectsCurrent
        effectadj = seqs.get(effect.EffectStrips[-1].value)
        effectinput = seqs.get(effect.EffectStrips[0].value)
        lenchannels = len(effect.EffectStrips)
        if cureffectIdx == 0: return # 0 is original effect which should not be moved.

        if self.dire == 'UP':
            targeteffectIdx = cureffectIdx - 1
            if targeteffectIdx <= 0: return # 0 is original effect which should not be moved.
            targeteffect = data.Effects[targeteffectIdx]
            lentargetchannels = len(targeteffect.EffectStrips)

            loweffectIdx = cureffectIdx + 1
            higheffectIdx = targeteffectIdx - 1

            higheffectadj = seqs.get(data.Effects[higheffectIdx].EffectStrips[-1].value)
            targetadj = seqs.get(targeteffect.EffectStrips[-1].value)
            targetinput = seqs.get(targeteffect.EffectStrips[0].value)

            channelstart = targetinput.channel
            channelend = effectadj.channel

            # break connection
            effectinput.input_1 = None
            targetinput.input_1 = None

            # move one part to empty space
            for buildinseqName in effect.EffectStrips:
                buildinseq = seqs.get(buildinseqName.value)
                if buildinseq.frame_start != frameend + 1:
                    buildinseq.frame_start = frameend + 1

            return

            # if 'input_1' in dir(targetinput) and targetinput.input_1 == higheffectadj:
            #     targetinput.input_1 = effectadj
            # if 'input_1' in dir(effectinput) and effectinput.input_1 == targetadj:
            #     effectinput.input_1 = higheffectadj
            # if loweffectIdx < len(data.Effects):
            #     loweffectinput = seqs.get(data.Effects[loweffectIdx].EffectStrips[0].value)
            #     if 'input_1' in dir(loweffectinput) and loweffectinput.input_1 == effectadj:
            #         loweffectinput.input_1 = targetadj

            # for buildinseqName in effect.EffectStrips:
            #     buildinseq = seqs.get(buildinseqName.value)
            #     buildinseq.frame_start = frameend + 1
            #     # print("Effect", buildinseq.name, "from", buildinseq.channel, "to", buildinseq.channel - lentargetchannels)
            #     # buildinseq.channel -= lentargetchannels

            # move another part
            for buildinseqName in targeteffect.EffectStrips:
                buildinseq = seqs.get(buildinseqName.value)
                print("TargetEffect", buildinseq.name, "from", buildinseq.channel, "to", buildinseq.channel + lenchannels)
                buildinseq.channel += lenchannels

            # move the first part back 
            for i, buildinseqName in enumerate(effect.EffectStrips):
                buildinseq = seqs.get(buildinseqName.value)
                if buildinseq.channel != i + channelstart:
                    buildinseq.channel = i + channelstart # change channel before setting frame_start. The order is important.
                    buildinseq.frame_start = framestart
                else:
                    buildinseq.channel = i + channelstart

            # recover connection
            effectinput.input_1 = higheffectadj
            targetinput.input_1 = effectadj
            if loweffectIdx < len(data.Effects):
                seqs.get(data.Effects[loweffectIdx].EffectStrips[0].value).input_1 = targetadj

            data.Effects.move(cureffectIdx, targeteffectIdx)

        else: # dire == 'DOWN'
            targeteffectIdx = cureffectIdx + 1
            if targeteffectIdx >= len(data.Effects): return {"FINISHED"} # already the last one
            targeteffect = data.Effects[targeteffectIdx]
            lentargetchannels = len(targeteffect.EffectStrips)

            for buildinseqName in effect.EffectStrips:
                buildinseq = seqs.get(buildinseqName.value)
                buildinseq.channel += lentargetchannels

            for buildinseqName in targeteffect.EffectStrips:
                buildinseq = seqs.get(buildinseqName.value)
                buildinseq.channel -= lenchannels

            loweffectIdx = targeteffect + 1
            higheffectIdx = cureffectIdx - 1

            higheffectadj = seqs.get(data.Effects[higheffectIdx].EffectStrips[-1].value)
            targetadj = seqs.get(targeteffect.EffectStrips[-1].value)
            targetinput = seqs.get(targeteffect.EffectStrips[0].value)
            if 'input_1' in dir(targetinput) and targetinput.input_1 == effectadj:
                targetinput.input_1 = higheffectadj
            if 'input_1' in dir(effectinput) and effectinput.input_1 == higheffectadj:
                effectinput.input_1 = targetadj
            if loweffectIdx < len(data.Effects):
                loweffectinput = seqs.get(data.Effects[loweffectIdx].EffectStrips[0].value)
                if 'input_1' in dir(loweffectinput) and loweffectinput.input_1 == targetadj:
                    loweffectinput.input_1 = effectadj

        data.Effects.move(cureffectIdx, targeteffectIdx)

    def execute(self, context):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        effectName = effect.EffectType

        if effectName in ICETB_EFFECTS_NAMES:
            cls = ICETB_EFFECTS_DICTS[effectName]
            seqs, framestart, frameend = cls.enterFistLayer(richstrip)
            self.mvlayer(richstrip, data, effect, seqs, framestart, frameend)
            cls.leaveFirstLayer(None)

        else:
            self.report({'ERROR'}, "Unknow effect name called " + effectName)
            return {'CANCELLED'}

        return {"FINISHED"}