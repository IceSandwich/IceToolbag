import bpy, re
from ..datas.richstrip import RichStripData
from ..operators.richstrip.effects import ICETB_EFFECTS_DICTS

class ICETB_PT_RichStripEffect(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "RichStrip"
    bl_idname = "ICETB_PT_RichStripEffect"
    bl_label = "Effect Property"

    @classmethod
    def poll(cls, context):
        if len(context.selected_sequences) != 1:
            return False
        seq = context.selected_sequences[0]
        if not RichStripData.checkProperty(context, seq):
            return False
        data = seq.IceTB_richstrip_data
        if not data.ForceNoDuplicateTip and re.compile(".*?\\.[0-9]{1,3}$").match(seq.name):
            return False
        # if data.EffectsCurrent >= len(data.Effects):
        #     return False
        return True

    def draw(self, context):
        layout = self.layout

        data = context.selected_sequences[0].IceTB_richstrip_data
        curidx = data.EffectsCurrent
        seleffecttype = data.Effects[curidx].EffectType
        # seleffecttype = data.getSelectedEffectType()
    
        layout.label(text="Type: " + seleffecttype)
        # if curidx == 0:
        #     layout.label(text="Input: Disk Sequences")
        # elif seleffecttype == "Copy":
        #     layout.label(text="Input: " + data.Effects[data.Effects[curidx].EffectInputId].EffectName)
        # else:
        #     layout.label(text="Input: Last one")
    
        ICETB_EFFECTS_DICTS[seleffecttype]._draw(context, layout)
