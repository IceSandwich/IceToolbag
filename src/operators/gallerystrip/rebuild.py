import bpy, re
from ...datas.gallerystrip import GalleryStripData
from .Op import GalleryStripOP

class ICETB_OT_GalleryStrip_Rebuild(bpy.types.Operator):
    bl_idname = "icetb.gallerystrip_rebuild"
    bl_label = "Rebuild effect"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_sequences) == 1

    def execute(self, context):
        gallerystrip = context.selected_sequences[0]
        data = gallerystrip.IceTB_gallerystrip_data

        # rename meta strip
        suffix = re.compile(".*?(\\.[0-9]{1,3})$").match(gallerystrip.name).group(1)
        gallerystrip.name = gallerystrip.name[:-len(suffix)] + suffix.replace('.', '_')

        # assign new richstrip id
        oldgsid = "gs%d-"%data.StripID
        data.StripID = GalleryStripData.genStripId(context)

        # relink the base sequence
        newgsid = "gs%d-"%data.StripID
        for stripName in data.StripsName:
            newstripName = newgsid + stripName.value[len(oldgsid):]
            gallerystrip.sequences.get(stripName.value+suffix).name = newstripName
            stripName.value = newstripName

        GalleryStripOP.addBinding(context, gallerystrip)

        return {"FINISHED"}