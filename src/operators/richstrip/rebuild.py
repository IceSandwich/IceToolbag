import bpy, re
from ...datas.richstrip import RichStripData
from .effects import ICETB_EFFECTS_DICTS

class ICETB_OT_RichStrip_Rebuild(bpy.types.Operator):
    bl_idname = "icetb.richstrip_rebuild"
    bl_label = "Rebuild effect"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_sequences) == 1

    def execute(self, context):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data

        # rename meta strip
        suffix = re.compile(".*?(\\.[0-9]{1,3})$").match(richstrip.name).group(1)
        richstrip.name = richstrip.name[:-len(suffix)] + suffix.replace('.', '_')

        # assign new richstrip id
        rsid_old = data.RichStripID
        data.RichStripID = RichStripData.genRichStripId(context)

        # relink the base sequence
        newrsid = "rs%d-"%data.RichStripID
        from context.scene.sequence_editor import sequences_all
        # if data.HasAudio:
        #     richstrip.sequences.get(("rs%d-audio"%rsid_old)+suffix).name = "%saudio"%newrsid
        # richstrip.sequences.get(("rs%d-movie"%rsid_old)+suffix).name = "%smovie"%newrsid
        # richstrip.sequences.get(("rs%d-fixfps"%rsid_old)+suffix).name = "%sfixfps"%newrsid
        if data.HasAudio:
            sequences_all.get(("rs%d-audio"%rsid_old)+suffix).name = "%saudio"%newrsid
        sequences_all.get(("rs%d-movie"%rsid_old)+suffix).name = "%smovie"%newrsid
        sequences_all.get(("rs%d-fixfps"%rsid_old)+suffix).name = "%sfixfps"%newrsid

        # relink all effects
        for index, effect in enumerate(data.Effects):
            ICETB_EFFECTS_DICTS[effect.EffectType]._relink(context, richstrip, suffix, index, rsid_old)

        return {"FINISHED"}

class ICETB_OT_RichStrip_NoRebuild(bpy.types.Operator):
    bl_idname = "icetb.richstrip_norebuild"
    bl_label = "Don't rebuild effect and neglect tip"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_sequences) == 1

    def execute(self, context):
        obj = context.selected_sequences[0]
        data = obj.IceTB_richstrip_data
        data.ForceNoDuplicateTip = True
        return {"FINISHED"}