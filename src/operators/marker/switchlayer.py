import bpy
from ...datas.marker_layer import MarkerLayer_OneLayer as MarkerLayer_Collection

class ICETB_OT_Marker_SwitchLayer(bpy.types.Operator):
    bl_idname = "icetb.marker_switch_layer"
    bl_label = "Layer Name"
    bl_description = "Description that shows in blender tooltips"
    bl_options = {"REGISTER", "UNDO"}

    layerIdx: bpy.props.IntProperty(name="Layer Index", default=-1)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # print("switch to " + str(self.layerIdx + 1))
        layers_data, layers_curidx = MarkerLayer_Collection.getProperty(context, autocreate=True)
        layers_data[layers_curidx].parseFromCurrentScene(context, replace=True) #apply current markers to layer
        if layers_curidx != self.layerIdx:
            layers_data[self.layerIdx].loadToCurrentScene(context, clearBefore=True)

        return {"FINISHED"}
