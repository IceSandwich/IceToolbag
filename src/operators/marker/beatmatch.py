import bpy
from ...datas.marker_layer import MarkerLayer_OneLayer as MarkerLayer_Collection
from ...datas.string_prop import StringProperty

class ICETB_OT_Marker_BeatMatch(bpy.types.Operator):
    bl_idname = "icetb.marker_beatmatch"
    bl_label = "Beat Match"
    bl_options = {"REGISTER"}

    layerNames: bpy.props.CollectionProperty(type=StringProperty, options={'HIDDEN'})

    def getLayerCallback(self, context):
        return ( (str(i), layer_name.value, "Layer Name") for i, layer_name in enumerate(self.layerNames) )

    align_layer1: bpy.props.EnumProperty(
        name="Movie Marker Layer",
        description="Layer contains markers which identify the beat of movie.",
        items=getLayerCallback,
        default=None
    )
    align_layer2: bpy.props.EnumProperty(
        name="Audio Marker Layer",
        description="Layer contains markers which identify the beat of audio.",
        items=getLayerCallback,
        default=None
    )

    def getMovieSeqAndAudioSeq(self, context):
        MovieSeq = None
        AudioSeq = None

        for seq in context.selected_sequences:
            if seq.type == 'MOVIE':
                if MovieSeq is not None:
                    self.report({'ERROR'}, "You should select a movie strip and a audio strip.")
                    return None, None
                else:
                    MovieSeq = seq
            elif seq.type == 'SOUND':
                if AudioSeq is not None:
                    self.report({'ERROR'}, "You should select a movie strip and a audio strip.")
                    return None, None
                else:
                    AudioSeq = seq
            else:
                self.report({'ERROR'}, "Unknow strip type: %s" % seq.type)
                return None, None

        return MovieSeq, AudioSeq

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        MovieSeq, AudioSeq = self.getMovieSeqAndAudioSeq(context) 
        # assert(MovieSeq is not None and AudioSeq is not None) # both should not be None
        layer_data, layers_curidx = MarkerLayer_Collection.getProperty(context, autocreate=False)
        # assert(layer_data is not None) # layer_data should not be None
        layer_data[layers_curidx].parseFromCurrentScene(context, replace=True) # apply current markers

        movie_markers = layer_data[int(self.align_layer1)].markers
        audio_markers = layer_data[int(self.align_layer2)].markers

        if len(movie_markers) != len(audio_markers):
            self.report({'ERROR'}, "The length of markers should be same.")
            return {'CANCELLED'}

        # align to marker
        movie_strip_framestart = MovieSeq.frame_final_start
        movie_strip_frameend = MovieSeq.frame_final_end
        align2marker_parameter = {
            "seq1_name": MovieSeq.name,
            "seq2_name": AudioSeq.name, 

            # useless, parse them in case
            "marker1_name": movie_markers[0].markerName,
            "marker2_name": audio_markers[0].markerName,
            # "align_marker1": "custom", 
            # "align_marker2": "custom",

            "align_seq1": MovieSeq.name,
            "align_seq2": AudioSeq.name,
            "still_marker": "1", # make audio still
            "use_customframe": True,
            "customframe_formarker1": movie_markers[0].markerFrame,
            "customframe_formarker2": audio_markers[0].markerFrame
        }
        bpy.ops.icetb.marker_aligntomarker('EXEC_DEFAULT', **align2marker_parameter)

        # adjust movieseq frame range
        movie_strip_offset = MovieSeq.frame_final_start - movie_strip_framestart
        print("movie_strip_offset:", movie_strip_offset)
        MovieSeq.frame_final_end = audio_markers[-1].markerFrame + (movie_strip_frameend - movie_markers[-1].markerFrame) + movie_strip_offset # AudioSeq.frame_final_end
        currentFrame = context.scene.frame_current

        # add speed_strip
        AudioSeq.select = False
        MovieSeq.select = True
        bpy.ops.sequencer.effect_strip_add(type='SPEED')
        speed_strip = context.scene.sequence_editor.active_strip
        speed_strip.use_default_fade = False # bacause multiply speed cannot animate, we need to use speed_factor
        speed_strip.use_frame_interpolate = True
        # speed_strip.speed_factor = 1
        # speed_strip.keyframe_insert("speed_factor", frame=MovieSeq.frame_final_start)

        # add fcurve to speed_strip
        if context.scene.animation_data.action is None:
            context.scene.animation_data.action = bpy.data.actions.new("MarkerBeatMatchAction")
        fcurve = context.scene.animation_data.action.fcurves.new(speed_strip.path_from_id("speed_factor"))
        fcurve.keyframe_points.insert(MovieSeq.frame_final_start, 1).interpolation = 'CONSTANT'

        mf_before = movie_markers[0].markerFrame + movie_strip_offset
        af_before = audio_markers[0].markerFrame

        for i in range(1, len(movie_markers)):
            mf = movie_markers[i].markerFrame + movie_strip_offset # noticed that movie clip has been slip
            af = audio_markers[i].markerFrame

            # speed_strip.speed_factor = (mf - mf_before) / (af - af_before)
            # speed_strip.keyframe_insert("speed_factor", frame=af_before)
            speed_factor = (mf - mf_before) / (af - af_before)
            fcurve.keyframe_points.insert(af_before, speed_factor).interpolation = 'CONSTANT'

            mf_before = mf
            af_before = af

        # speed_strip.speed_factor = 1
        # speed_strip.keyframe_insert("speed_factor", frame=af_before)
        fcurve.keyframe_points.insert(af_before, 1).interpolation = 'CONSTANT'

        return {"FINISHED"}

    def invoke(self, context, event):
        if len(context.selected_sequences) != 2:
            self.report({'ERROR'}, "You should select a movie strip and a audio strip.")
            return {'CANCELLED'}

        MovieSeq, AudioSeq = self.getMovieSeqAndAudioSeq(context)
        if MovieSeq is None or AudioSeq is None:
            return {'CANCELLED'} # already show error message in getMovieSeqAndAudioSeq function.

        layer_data, _ = MarkerLayer_Collection.getProperty(context, autocreate=True)
        for layer in layer_data:
            self.layerNames.add().value = layer.layerName

        return context.window_manager.invoke_props_dialog(self)
