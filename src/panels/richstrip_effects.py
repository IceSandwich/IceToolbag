import bpy, re
from ..datas.richstrip import RichStripData

class ICETB_UL_RichStripEffects_EffectListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "EffectName", text="", emboss=False, icon_value=icon)

class ICETB_PT_RichStripEffects(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "RichStrip"
    bl_idname = "ICETB_PT_RichStripEffects"
    bl_label = "Effects"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if len(context.selected_sequences) != 1 or not RichStripData.checkProperty(context, context.selected_sequences[0]):
            layout.label(text="No Rich Strip Selected.")
            return

        obj = context.selected_sequences[0]
        data = obj.IceTB_richstrip_data

        if not data.ForceNoDuplicateTip and re.compile(".*?\\.[0-9]{1,3}$").match(obj.name):
            layout.label(text="Do you duplicated a strip? We need to rebuild it.")
            layout.operator("icetb.richstrip_rebuild", text="Yes, i have duplicated this strip.")
            return

        # layout.label(text= "Name: " + obj.name)

        row = layout.row()

        col = row.column()
        col.template_list("ICETB_UL_RichStripEffects_EffectListUI", "", data, "Effects", data, "EffectsCurrent", rows=1)

        col = row.column(align=True)
        col.operator("wm.call_menu", icon="ADD", text="").name = "ICETB_MT_RICHSTRIP_ADD"
        col.operator("icetb.richstrip_deleffect", icon="TRASH", text="")
        # col.operator("icetb.richstrip_mveffect", icon='TRIA_UP', text="").dire = 'UP'
        # col.operator("icetb.richstrip_mveffect", icon='TRIA_DOWN', text="").dire = 'DOWN'