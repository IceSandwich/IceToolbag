import bpy
from ..datas.richstrip import RichStripData

class ICETB_OT_ConvertToRichStrip(bpy.types.Operator):
    bl_idname = "icetb.convert_to_richstrip"
    bl_label = "Convert to Rich strip"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(context.selected_sequences) > 2 or len(context.selected_sequences) == 0:
            self.report({'ERROR'}, "Please select one or two strips.")
            return {"CANCELLED"}
        
        MovieSeq = None
        AudioSeq = None

        for seq in context.selected_sequences:
            if seq.type == 'MOVIE':
                if MovieSeq is not None:
                    self.report({'ERROR'}, "You should select a movie strip and a audio strip.")
                    return {"CANCELLED"}
                else:
                    MovieSeq = seq
            elif seq.type == 'SOUND':
                if AudioSeq is not None:
                    self.report({'ERROR'}, "You should select a movie strip and a audio strip.")
                    return {"CANCELLED"}
                else:
                    AudioSeq = seq
            else:
                self.report({'ERROR'}, "Unknow strip type: %s" % seq.type)
                return {"CANCELLED"}
        if MovieSeq is None:
            self.report({'ERROR'}, "Must contain one movie strip.")
            return {"CANCELLED"}

        # read information

        meta_frameend = MovieSeq.frame_final_end
        if AudioSeq is not None:
            meta_frameend = AudioSeq.frame_final_end
        MovieSeq.use_proxy = False # we must read fps when not use proxy, otherwise we got 0
        moviefps = MovieSeq.fps
        MovieSeq.use_proxy = True

        # read scene fps, because the fps of scene will change automatically. i don't know why.
        render_fps, render_fps_base = context.scene.render.fps, context.scene.render.fps_base

        # assemsemby sequences

        bpy.ops.sequencer.meta_make()
        meta_strip = context.scene.sequence_editor.active_strip
        meta_strip.blend_type = "ALPHA_OVER"
        bpy.ops.sequencer.meta_toggle() # enter meta_strip

        MovieSeq.channel = 2
        if AudioSeq is not None:
            AudioSeq.channel = 1
            AudioSeq.select = True
            AudioSeq.sound.use_memory_cache = True # A/V sync

        # make submeta_strip, in submeta_strip, audio in channel 1, movie in channel 2, speed control in channel 3, adjustment in channel 4
        MovieSeq.select = True
        # AudioSeq.select = True # we selected audioseq just now, we don't need to do it again.
        bpy.ops.sequencer.meta_make()
        submeta_strip = context.scene.sequence_editor.active_strip
        # submeta_strip.blend_type = "ALPHA_OVER"
        bpy.ops.sequencer.meta_toggle() # enter submeta

        # add speed control to movieseq
        MovieSeq.select = True
        AudioSeq.select = False
        bpy.ops.sequencer.effect_strip_add(type='SPEED', channel=3)
        speed_strip = context.scene.sequence_editor.active_strip
        speed_strip.multiply_speed = moviefps / (render_fps / render_fps_base)
        speed_strip.use_frame_interpolate = True
        print("scene fps:", render_fps / render_fps_base)
        print("movie fps:", moviefps)
        print("speed:", speed_strip.multiply_speed)

        if AudioSeq is not None:
            lastMovieSeq = MovieSeq

            while lastMovieSeq.frame_final_end < AudioSeq.frame_final_end:
                bpy.ops.sequencer.movie_strip_add(filepath=MovieSeq.filepath, relative_path=True, channel=2, sound=False, frame_start=lastMovieSeq.frame_final_end)
                SubMovieSeq = context.scene.sequence_editor.active_strip

                # shift sub movie sequence
                offset = (lastMovieSeq.frame_final_end - MovieSeq.frame_final_start)*speed_strip.multiply_speed
                bpy.ops.sequencer.slip(offset=-offset)
                SubMovieSeq.frame_still_end = 0
                SubMovieSeq.use_proxy = True

                # add speed control for sub movie sequence
                SubMovieSeq.select = True
                bpy.ops.sequencer.effect_strip_add(type='SPEED', channel=3)
                subspeed_strip = context.scene.sequence_editor.active_strip
                subspeed_strip.multiply_speed = speed_strip.multiply_speed
                subspeed_strip.use_frame_interpolate = True

                lastMovieSeq = SubMovieSeq

        AudioSeq.name = "GlobalBaseAudioStrip"
        
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave submeta_strip

        submeta_strip.frame_final_end = meta_frameend
        submeta_strip.channel = 1
        submeta_strip.name = "FirstLayerRichStrip"
        
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave meta_strip

        meta_strip.frame_final_end = meta_frameend
        meta_strip.select = True
        RichStripData.initProperty(meta_strip, MovieSeq, AudioSeq)

        # i don't know why the fps of blender will change automatically. we need to recover them.
        context.scene.render.fps = render_fps
        context.scene.render.fps_base = render_fps_base

        return {"FINISHED"}
