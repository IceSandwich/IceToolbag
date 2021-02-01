import bpy

class ICETB_OT_Marker_AlignToMarker(bpy.types.Operator):
    bl_idname = "icetb.marker_aligntomarker"
    bl_label = "Align To Marker"
    bl_options = {"REGISTER"}

    seq1_name: bpy.props.StringProperty(name="The name of Sequence 1", options={'HIDDEN'})
    seq2_name: bpy.props.StringProperty(name="The name of Sequence 2", options={'HIDDEN'})
    marker1_name: bpy.props.StringProperty(name="The name of Marker 1", options={'HIDDEN'})
    marker2_name: bpy.props.StringProperty(name="The name of Marker 2", options={'HIDDEN'})

    # privatly use only. not available for user.
    use_customframe: bpy.props.BoolProperty(name="Use custom frame for 2 Markers instend of using markerx_name(privatly use only)", options={'HIDDEN'}, default=False)
    customframe_formarker1: bpy.props.IntProperty(name="Use custom frame for Marker1 instend of using marker1_name(privatly use only)", options={'HIDDEN'}, default=-1)
    customframe_formarker2: bpy.props.IntProperty(name="Use custom frame for Marker2 instend of using marker2_name(privatly use only)", options={'HIDDEN'}, default=-1)

    def getSeqCallback(self, context):
        return ( (x, x, "Sequence Name") for x in [ self.seq1_name, self.seq2_name ] )
    def getMarkerCallback(self, context):
        return ( (x, x, "Marker Name") for x in [ self.marker1_name, self.marker2_name ] )

    align_marker1: bpy.props.EnumProperty(
        name="Align Marker 1",
        description="Select marker to match clip 1",
        items=getMarkerCallback,
        default=None
    )
    align_seq1: bpy.props.EnumProperty(
        name="Align Sequence 1",
        description="Select sequence to match the marker 1",
        items=getSeqCallback,
        default=None
    )
    align_marker2: bpy.props.EnumProperty(
        name="Align Marker 2",
        description="Select marker to match clip 2",
        items=getMarkerCallback,
        default=None
    )
    align_seq2: bpy.props.EnumProperty(
        name="Align Sequence 2",
        description="Select sequence to match the marker 2",
        items=getSeqCallback,
        default=None
    )
    still_marker: bpy.props.EnumProperty(
        name="Still Sequence",
        description="Select a sequence which is still",
        items=(
            ("0", "Sequence 1", "Just move sequence 2 and leave sequence 1 alone."),
            ("1", "Sequence 2", "Just move sequence 1 and leave sequence 2 alone.")
        ),
        default=None
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.use_customframe:
            seq1 = [ x for x in context.selected_sequences if x.name == self.seq1_name ][0]
            seq2 = [ x for x in context.selected_sequences if x.name == self.seq2_name ][0]
            marker1_frame = self.customframe_formarker1
            marker2_frame = self.customframe_formarker2
        else:
            seq1 = [ x for x in context.selected_sequences if x.name == self.align_seq1 ][0]
            seq2 = [ x for x in context.selected_sequences if x.name == self.align_seq2 ][0]
            marker1_frame = context.scene.frame_current if self.marker1_name == 'Current Frame' else [ x.frame for _, x in context.scene.timeline_markers.items() if x.select == True and x.name == self.marker1_name ][0]
            marker2_frame = context.scene.frame_current if self.marker2_name == 'Current Frame' else [ x.frame for _, x in context.scene.timeline_markers.items() if x.select == True and x.name == self.marker2_name ][0]

        print("got frame:", marker1_frame, marker2_frame)

        if self.use_customframe == False and ( self.align_marker1 == self.align_marker2 or self.marker1_name == self.marker2_name ):
            self.report({'ERROR'}, "Sequence and marker should be different individually.")
            return {'CANCELLED'}
        if (marker1_frame < seq1.frame_final_start or marker1_frame > seq1.frame_final_end) or (marker2_frame < seq2.frame_final_start or marker2_frame > seq2.frame_final_end):
            self.report({'ERROR'}, "Marker don't inside of sequence. Cannot match them.")
            return {'CANCELLED'}

        if self.still_marker == "0":
            offset = marker1_frame - marker2_frame
            seq2.frame_start += offset
            # seq2.frame_final_start += offset
            # seq2.frame_final_end += offset
        else:
            offset = marker2_frame - marker1_frame
            seq1.frame_start += offset
            # seq1.frame_final_start += offset
            # seq1.frame_final_end += offset

        return {"FINISHED"}

    def invoke(self, context, event):
        markers = [ marker.name for _, marker in context.scene.timeline_markers.items() if marker.select ]
        seqs = context.selected_sequences

        if (len(markers) != 1 and len(markers) != 2) or len(seqs) != 2:
            self.report({'ERROR'}, "Please just select 1 or 2 markers and 2 clips.")
            return {'CANCELLED'}
        if len(markers) == 2 and markers[0] == markers[1]:
            self.report({'ERROR'}, "The markers should not has the same name.")
            return {'CANCELLED'}
        self.marker1_name = markers[0]
        self.marker2_name = markers[1] if len(markers) == 2 else 'Current Frame'
        
        if seqs[0].channel == seqs[1].channel:
            self.report({'ERROR'}, "All selected clips must have different channel.")
            return {'CANCELLED'}
        if seqs[0].name == seqs[1].name:
            self.report({'ERROR'}, "The sequences should not has the same name.")
            return {'CANCELLED'}
        self.seq1_name = seqs[0].name
        self.seq2_name = seqs[1].name

        return context.window_manager.invoke_props_dialog(self)
