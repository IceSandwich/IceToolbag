import bpy, re
from ...datas.richstrip import RichStripData
from effects import ICETB_EFFECTS_DICTS

class ICETB_OT_RichStrip_Rebuild(bpy.types.Operator):
    bl_idname = "icetb.richstrip_rebuild"
    bl_label = "Rebuild effect"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_sequences) == 1

    def execute(self, context):
        obj = context.selected_sequences[0]
        data = obj.IceTB_richstrip_data

        suffix = re.compile(".*?(\\.[0-9]{1,3})$").match(obj.name).group(1)
        obj.name = obj.name[:-len(suffix)] + suffix.replace('.', '_')

        rsid_old = data.RichStripID
        data.RichStripID = RichStripData.genRichStripId(context)

        for index, effect in enumerate(data.Effects):
            ICETB_EFFECTS_DICTS[effect.EffectType].relink(context, obj, suffix, index, rsid_old)

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