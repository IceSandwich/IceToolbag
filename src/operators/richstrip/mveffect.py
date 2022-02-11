import bpy
from .effects import ICETB_EFFECTS_DICTS, ICETB_EFFECTS_NAMES
from ...datas.richstrip import RichStripEffect, RichStripData

class ICETB_OT_RichStrip_Move(bpy.types.Operator):
    bl_idname = "icetb.richstrip_mveffect"
    bl_label = "Move Effect"
    bl_options = {"REGISTER", "UNDO"}

    dire: bpy.props.StringProperty(name="Move direction", default="UP")

    @classmethod
    def poll(cls, context):
        return True

    def getcoverChannel(self, richstrip:bpy.types.MetaSequence, effect:RichStripEffect):
        inputstripChannel = richstrip.sequences.get(effect.EffectStrips[0].value).channel
        adjuststripChannel = richstrip.sequences.get(effect.EffectStrips[-1].value).channel
        coverChannel = adjuststripChannel - inputstripChannel + 1
        return coverChannel

    def mvlayer(self, context, richstrip:bpy.types.MetaSequence, data:RichStripData, effect:RichStripEffect):
        if data.EffectsCurrent == 0 or (data.EffectsCurrent == 1 and self.dire == 'UP') or (data.EffectsCurrent == len(data.Effects) - 1 and self.dire == 'DOWN'):
            self.report({'ERROR'}, "Cannot move this effect in this direction.")
            return {'CANCELLED'}
            
        # calculate this effect cover n channels
        tarEffect = data.Effects[data.EffectsCurrent + (-1 if self.dire == 'UP' else 1)]
        curCover = self.getcoverChannel(richstrip, effect)
        tarCover = self.getcoverChannel(richstrip, tarEffect)

        emptyChannel = richstrip.sequences.get(data.Effects[-1].EffectStrips[-1].value).channel + tarCover + curCover

        # TODO: assert emptyChannel < MAX_CHANNEL

        def moveupStrips(effect:RichStripEffect, targetChannel):
            stripsInstances = [ richstrip.sequences.get(x.value) for x in effect.EffectStrips if richstrip.sequences.get(x.value) ]
            for i, seq in enumerate(stripsInstances[::-1]):
                seq.channel = targetChannel - i
            return targetChannel - len(stripsInstances)

        for aboveEffects in data.Effects[data.EffectsCurrent + (1 if self.dire == 'UP' else 2):]:
            emptyChannel = moveupStrips(aboveEffects, emptyChannel)

        up, down = data.Effects[data.EffectsCurrent + (0 if self.dire == 'UP' else 1)], data.Effects[data.EffectsCurrent + (-1 if self.dire == 'UP' else 0)]
        upup = data.Effects[data.EffectsCurrent + (1 if self.dire == 'UP' else 2)] if data.EffectsCurrent + (1 if self.dire == 'UP' else 2) < len(data.Effects) else None
        downdownSeq = richstrip.sequences.get(data.Effects[data.EffectsCurrent + (-2 if self.dire == 'UP' else -1)].EffectStrips[-1].value)

        # Swap
        emptyChannel = moveupStrips(down, emptyChannel)
        emptyChannel = moveupStrips(up, emptyChannel)

        def replaceInput(richstrip:bpy.types.MetaSequence, effect:RichStripEffect, source:bpy.types.Sequence, to:bpy.types.Sequence):
            for strip in effect.EffectStrips:
                seq = richstrip.sequences.get(strip.value)
                if seq and hasattr(seq, "input_1") and seq.input_1 == source:
                    seq.input_1 = to

        if upup:
            replaceInput(richstrip, upup, richstrip.sequences.get(up.EffectStrips[-1].value), richstrip.sequences.get(down.EffectStrips[-1].value))
        replaceInput(richstrip, down, downdownSeq, richstrip.sequences.get(up.EffectStrips[-1].value))
        replaceInput(richstrip, up, richstrip.sequences.get(down.EffectStrips[-1].value), downdownSeq)

        # upup          ->      upup (Nullable)
        # up            ->      down
        # down          ->      up
        # downdown      ->      downdown
        # original      ->      original

        data.Effects.move(data.EffectsCurrent, data.EffectsCurrent + (-1 if self.dire == 'UP' else 1))
        down.EffectIndex -= 1
        up.EffectIndex += 1

        def movedownStrips(effect:RichStripEffect, targetChannel):
            stripsInstances = [ richstrip.sequences.get(x.value) for x in effect.EffectStrips if richstrip.sequences.get(x.value) ]
            for i, seq in enumerate(stripsInstances):
                seq.channel = targetChannel + i
            return targetChannel + len(stripsInstances)

        emptyChannel -= tarCover + curCover - 1
        for aboveEffects in data.Effects[data.EffectsCurrent + (1 if self.dire == 'UP' else 2) - 2:]:
            emptyChannel = movedownStrips(aboveEffects, emptyChannel)

        oldEffectIdx = data.EffectsCurrent
        data.EffectsCurrent = data.EffectsCurrent + (-1 if self.dire == 'UP' else 1)

        self.correctDrivers(context, richstrip, data, tarEffect, oldEffectIdx, data.EffectsCurrent)
        self.correctDrivers(context, richstrip, data, effect, data.EffectsCurrent, oldEffectIdx)

        return {"FINISHED"}

    def correctDrivers(self, context, richstrip:bpy.types.MetaSequence, data:RichStripData, effect:RichStripEffect, oldEffectIdx:int, newEffectIdx:int):
        oldpattern = 'IceTB_richstrip_data.Effects[%d]'%oldEffectIdx
        newpattern = 'IceTB_richstrip_data.Effects[%d]'%newEffectIdx
        patternRichstrip = 'sequence_editor.sequences_all["%s"].%s'%(richstrip.name, oldpattern)
        for x in context.scene.animation_data.drivers:
            for seqName in effect.EffectStrips:
                pattern = 'sequence_editor.sequences_all["%s"]'%(seqName.value)
                if x.data_path.startswith(pattern): # fliter driver related to this effect
                    for variable in x.driver.variables:
                        if variable.targets[0].data_path.startswith(patternRichstrip): # fliter driver related to IceTB_richstrip_data
                            variable.targets[0].data_path = variable.targets[0].data_path.replace(oldpattern, newpattern)
        return

    def execute(self, context):
        richstrip = context.selected_sequences[0]
        data:RichStripData = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        effectName = effect.EffectType

        if effectName in ICETB_EFFECTS_NAMES:
            cls = ICETB_EFFECTS_DICTS[effectName]
            cls.enterEditMode(richstrip)
            ret = self.mvlayer(context, richstrip, data, effect)
            cls.leaveEditMode()
            return ret
        else:
            self.report({'ERROR'}, "Unknow effect name called " + effectName)
            return {'CANCELLED'}

        return {"FINISHED"}