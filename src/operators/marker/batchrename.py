import bpy
import re

class ICETB_OT_Marker_BatchRename(bpy.types.Operator):
    bl_idname = "icetb.marker_batch_rename"
    bl_label = "Batch Rename"
    bl_options = {"REGISTER", "UNDO"}

    newname_string: bpy.props.StringProperty(name="New Name", default="F_%02d")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(self.markers) == 1:
            if self.newname_string == "":
                self.newname_string = "F_%02d" % self.markers[0].frame
            self.markers[0].name = self.newname_string
            return {"FINISHED"}

        if self.newname_string == "":
            self.newname_string = "F_%02d"
        elif re.search('[a-zA-Z0-9\\_]*\\%[0-9]*d', self.newname_string) == None:
            self.newname_string = self.newname_string + "_%02d"

        for i, marker in enumerate(self.markers):
            marker.name = self.newname_string % (i+1)
            
        return {"FINISHED"}

    def invoke(self, context, event):
        self.markers = sorted([ marker for _, marker in context.scene.timeline_markers.items() if marker.select ], key=lambda m: m.frame)
        if len(self.markers) == 0:
            self.report({'ERROR'}, "No markers selected.")
            return {"FINISHED"}

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
