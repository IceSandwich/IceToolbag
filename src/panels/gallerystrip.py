import bpy, re
from ..datas.gallerystrip import GalleryStripData

class ICETB_PT_GalleryStripEffects(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "GalleryStrip"
    bl_idname = "ICETB_PT_GalleryStrip"
    bl_label = "Global Structure"

    duplicatedNameMatcher = re.compile(".*?\\.[0-9]{1,3}$")

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if len(context.selected_sequences) != 1 or not GalleryStripData.checkProperty(context, context.selected_sequences[0]):
            layout.label(text="No Gallery Strip Selected.")
            return

        obj = context.selected_sequences[0]
        data = obj.IceTB_gallerystrip_data

        if self.duplicatedNameMatcher.match(obj.name):
            layout.label(text="Do you duplicated a strip? We need to rebuild it.")
            layout.operator("icetb.gallerystrip_rebuild", text="Yes, i have duplicated this strip.")
            return

        # layout.label(text= "Name: " + obj.name)

        layout.label(text="Hello world")
        layout.prop(data.StripsFitMethod, "value", text="Fit Method")
        layout.prop(data.ArrangementMethod, "value", text="Arrangement Method")
        layout.prop(data, "CanvasWidth", text="Width")
        layout.prop(data, "CanvasHeight", text="Height")
        layout.prop(obj, '["scale_x"]', text="Size X")
        layout.prop(obj, '["scale_y"]', text="Size Y")
        layout.prop(obj, '["controller"]', text="Controller")