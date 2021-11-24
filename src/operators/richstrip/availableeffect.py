import bpy, json
from ...datas.richstrip import RichStripData, RichStripEffect

class ICETB_OT_RichStrip_EffectAvailable(bpy.types.Operator):
    bl_idname = "icetb.richstrip_effectavailable"
    bl_label = "Change the available for effect(Private use only)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        richstrip = context.selected_sequences[0]
        data:RichStripData = richstrip.IceTB_richstrip_data

        seqGet = context.scene.sequence_editor.sequences_all.get

        curEffect = data.Effects[data.EffectsCurrent]
        curadjust = seqGet(curEffect.EffectStrips[-1].value)

        lastEffect = data.Effects[data.EffectsCurrent-1]
        lastadjust = seqGet(lastEffect.EffectStrips[-1].value)

        nextEffect = data.Effects[data.EffectsCurrent+1] if data.EffectsCurrent + 1 < len(data.Effects) else None

        available = curEffect.EffectAvailable
        mapping = json.loads(curEffect.EffectAvailableJson)

        if nextEffect:
            for strip in nextEffect.EffectStrips:
                seq = seqGet(strip.value)
                if not hasattr(seq, "input_1"): continue
                if available:
                    if seq.input_1 == lastadjust:
                        seq.input_1 = curadjust
                else:
                    if seq.input_1 == curadjust:
                        seq.input_1 = lastadjust

        for strip in curEffect.EffectStrips:
            seq = seqGet(strip.value)
            if available: # recover
                seq.mute = mapping[seq.name]
            else:
                mapping[seq.name] = seq.mute
                seq.mute = True

        if available:
            curEffect.EffectAvailableJson = '{}'
        else:
            curEffect.EffectAvailableJson = json.dumps(mapping)
        
        return {"FINISHED"}