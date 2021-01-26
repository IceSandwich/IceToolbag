import bpy
from ...datas.marker_layer import MarkerLayer_OneLayer as MarkerLayer_Collection

class ICETB_OT_Marker_RenameLayer(bpy.types.Operator):
    bl_idname = "icetb.marker_rename_layer"
    bl_label = "Rename Layer"
    bl_options = {"REGISTER", "UNDO"}

    newname_string: bpy.props.StringProperty(name="New Name", default="Untitled Layer")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.newname_string == "":
            return {"FINISHED"}
        
        layers_data, layers_curidx = MarkerLayer_Collection.getProperty(context, autocreate=True)
        layers_data[layers_curidx].layerName = self.newname_string

        return {"FINISHED"}

    def invoke(self, context, event):
        self.newname_string = MarkerLayer_Collection.getCurrentLayerName(context)

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
