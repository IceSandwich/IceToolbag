import bpy
import time
from ..datas.richstrip import RichStripData
from ..datas.gallerystrip import GalleryStripData

class ICETB_OT_ConvertToRichStrip(bpy.types.Operator):
    bl_idname = "icetb.convert_to_richstrip"
    bl_label = "Convert to Rich strip"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def seperate_strips(self, context):
        # seperate selected strips into `self.movie`, `self.audio`
        # auctually `movie` can be another meta strip which has been defined as rich strip
        self.movie = None
        self.audio = None

        for seq in context.selected_sequences:
            if seq.type == 'MOVIE' or seq.type == 'META':
                if self.movie is not None:
                    self.report({'ERROR'}, "More than one either movie strip nor rich strip were detected.")
                    return False
                else:
                    if seq.type == 'META':
                        if not RichStripData.checkProperty(context, seq) and not GalleryStripData.checkProperty(context, seq):
                            self.report({'ERROR'}, "Selected meta strip isn't a valid rich/gallery strip.")
                            return False
                    self.movie = seq
            elif seq.type == 'SOUND':
                if self.audio is not None:
                    self.report({'ERROR'}, "More than one audio strip were detected.")
                    return False
                else:
                    self.audio = seq
            else:
                self.report({'ERROR'}, "Unknow strip type: %s" % seq.type)
                return False
        if self.movie is None:
            self.report({'ERROR'}, "Must contain one either movie strip nor rich strip.")
            return False

        return True

    def read_info(self, context):
        self.frame_end = self.movie.frame_final_end
        if self.audio is not None:
            self.frame_end = self.audio.frame_final_end
            self.audio_duration = self.audio.frame_final_duration
        self.movie_name = self.movie.name

        # read scene fps, because the fps of scene will change automatically. i don't know why.
        self.scene_fps, self.scene_fps_base = context.scene.render.fps, context.scene.render.fps_base

        self.movie.use_proxy = False # we must read fps when not using proxy, otherwise we got 0
        bpy.ops.sequencer.refresh_all() # blender 2.9 will automatically build proxy, so we need refresh all
        self.movie_fps = self.movie.fps if hasattr(self.movie, "fps") else self.scene_fps
        self.movie.use_proxy = True


    def recover_info(self, context):
        # i don't know why the fps of blender will change automatically. we need to recover them.
        context.scene.render.fps = self.scene_fps
        context.scene.render.fps_base = self.scene_fps_base
        # if self.audio is not None:
        #     self.audio.frame_final_duration = self.audio_duration

    def build_richstrip(self, context):
        bpy.ops.sequencer.meta_make()
        meta_strip = context.scene.sequence_editor.active_strip
        meta_strip.blend_type = "ALPHA_OVER"
        bpy.ops.sequencer.meta_toggle() # enter meta_strip

        self.movie.channel = 2
        self.movie.name = "rs%d-movie"%(self.rsid)
        self.movie.transform.scale_x = self.movie.transform.scale_y = 1
        self.movie.transform.rotation = 0
        self.movie.transform.offset_x = self.movie.transform.offset_y = 0
        # self.movie['fps'] = self.movie_fps
        # self.movie['width'] = self.movie.elements[0].orig_width
        # self.movie['height'] = self.movie.elements[0].orig_height
        if self.audio is not None:
            self.audio.channel = 1
            self.audio.select = True
            self.audio.sound.use_memory_cache = True # A/V sync

            self.movie.select = False
            self.audio.select = True
            bpy.ops.sequencer.meta_make()
            submeta = context.scene.sequence_editor.active_strip
            bpy.ops.sequencer.meta_toggle()

            submeta.name = "rs%d-subdries"%(self.rsid)
            self.audio.name = "rs%d-audio"%(self.rsid)

            bpy.ops.sequencer.select_all(action='DESELECT')
            bpy.ops.sequencer.meta_toggle() # leave meta_strip

        # add speed control to movieseq
        self.movie.select = True
        if self.audio is not None:
            self.audio.select = False

        print("scene fps:", self.scene_fps / self.scene_fps_base)
        print("movie fps:", self.movie_fps)

        if (self.movie.frame_final_end-self.movie.frame_final_start != self.frame_end-self.movie.frame_final_start):
            speed = float(self.movie.frame_final_end-self.movie.frame_final_start) / float(self.frame_end-self.movie.frame_final_start)
            bpy.ops.sequencer.effect_strip_add(type='SPEED', channel=3)
            speed_strip = context.scene.sequence_editor.active_strip
            if bpy.app.version[0] == 3: # for blender 3
                speed_strip.speed_control = 'MULTIPLY'
                speed_strip.speed_length = speed
            else:
                speed_strip.multiply_speed = speed

            speed_strip.use_frame_interpolate = True
            speed_strip.name = "rs%d-fixfps"%self.rsid

            print("speed:", speed)

        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave meta_strip

        meta_strip.name = self.movie_name
        meta_strip.frame_final_start = self.movie.frame_final_start 
        meta_strip.frame_final_end = self.frame_end

        return meta_strip

    def execute(self, context):
        if len(context.selected_sequences) > 2 or len(context.selected_sequences) == 0:
            self.report({'ERROR'}, "Please select one or two strips.")
            return {"CANCELLED"}
        
        if not self.seperate_strips(context):
            return {"CANCELLED"}

        self.read_info(context)

        # assemsemby sequences
        self.rsid = RichStripData.genRichStripId(context)
        meta_strip = self.build_richstrip(context)

        RichStripData.initProperty(context, meta_strip, self.rsid, self.movie, self.audio)
        
        self.recover_info(context)
        return {"FINISHED"}