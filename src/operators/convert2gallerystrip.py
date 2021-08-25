import bpy
from ..datas.gallerystrip import GalleryStripData
from .gallerystrip.Op import GalleryStripOP

class ICETB_OT_ConvertToGalleryStrip(bpy.types.Operator):
    bl_idname = "icetb.convert_to_gallerystrip"
    bl_label = "Convert to Gallery Strip"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def check(self, context):
        if len(context.selected_sequences) <= 1:
            self.report({'ERROR'}, "require at least two selected sequences.")
            return False
        channel = context.selected_sequences[0].channel
        for strip in context.selected_sequences:
            if strip.type not in ["IMAGE"]: #, "MOVIE"]:
                self.report({'ERROR'}, "unsupported type %s for sequence %s."%(strip.type, strip.name))
                return False
            if strip.channel != channel:
                self.report({'ERROR'}, "all strips should be in one channel without overlapping.")
                return False
        
        return True

    def build(self, context):
        bpy.ops.sequencer.meta_make()
        meta_strip = context.scene.sequence_editor.active_strip
        meta_strip.blend_type = "ALPHA_OVER"
        bpy.ops.sequencer.meta_toggle() # enter meta_strip

        seqOrder = sorted([(x.name, x.frame_final_start) for x in meta_strip.sequences], key=lambda x: x[1])
        frame_end = meta_strip.sequences.get(seqOrder[-1][0]).frame_final_end
        occupy_channel = meta_strip.sequences.get(seqOrder[0][0]).channel
        def dealStrip(seq, i): # i starts from 1
            seq.frame_final_start = seqOrder[0][1]
            seq.frame_final_end = frame_end
            seq.blend_type = "ALPHA_OVER"
            seq.transform.scale_x = seq.transform.scale_y = 1
            seq.name = "gs%d-base%d"%(self.gsid, i+1)
        for i, (seqName, _) in enumerate(seqOrder):
            if (i+1 == occupy_channel): continue
            seq = meta_strip.sequences.get(seqName)
            seq.channel = i+1
            dealStrip(seq, i)
        dealStrip(meta_strip.sequences.get(seqOrder[occupy_channel-1][0]), occupy_channel-1)
        self.imgslist = [ "gs%d-base%d"%(self.gsid, i+1) for i in range(len(seqOrder)) ]

        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave meta_strip

        meta_strip["scale_x"] = 1.0
        meta_strip["scale_y"] = 1.0
        # TODO: scale can be randomized by exporession maybe?
        # https://blender.stackexchange.com/questions/7758/how-can-i-get-a-random-number-that-is-constant-per-object-in-a-driver
        # TODO: add step animation to controller, user can decide the delay time.
        meta_strip["controller"] = 0.0

        return meta_strip

    def execute(self, context):
        if not self.check(context):
            return {"CANCELLED"}

        # assemsemby sequences
        self.gsid = GalleryStripData.genStripId(context)
        meta_strip = self.build(context)

        canvasWidth, canvasHeight = context.scene.render.resolution_x, context.scene.render.resolution_y

        GalleryStripData.initProperty(meta_strip, self.gsid, self.imgslist, canvasWidth, canvasHeight)

        # run init property
        data = meta_strip.IceTB_gallerystrip_data
        data.StripsFitMethod.value = "Scale to Fit"
        data.ArrangementMethod.value = "Horizontal"
        bpy.ops.icetb.gallerystrip_eventdelegate(eventIdentify="FitMethod")

        GalleryStripOP.addBinding(context, meta_strip)
    
        bpy.ops.sequencer.refresh_all()

        return {"FINISHED"}