import bpy
from ..datas.marker_layer import MarkerLayer_OneLayer as MarkerLayer_Collection

class ICETB_MT_SwitchLayer(bpy.types.Menu):
    bl_idname = "ICETB_MT_MARKER_SWITCH_LAYER"
    bl_label = "Switch Layer"

    def draw(self, context):
        # import bpy.types.Scene as scene
        layout = self.layout
        layers_data, layers_curidx = MarkerLayer_Collection.getProperty(context, autocreate=False)
        if layers_data == None:
            layersName = MarkerLayer_Collection.getFakeProperty()
            for i, layerName in enumerate(layersName):
                layout.operator("icetb.marker_switch_layer", text=layerName).layerIdx = i
            return
            
        for i, layer in enumerate(layers_data):
            switchoperator = layout.operator("icetb.marker_switch_layer", text=layer.layerName)
            switchoperator.layerIdx = i


class ICETB_MT_Marker(bpy.types.Menu):
    bl_idname = "ICETB_MT_MARKER"
    bl_label = "Marker"

    def draw(self, context):
        layout = self.layout

        # layout.label("version:1")
        layout.operator("icetb.marker_batch_rename")
        layout.operator("icetb.marker_aligntomarker")
        layout.separator()
        layout.menu(ICETB_MT_SwitchLayer.bl_idname, text=ICETB_MT_SwitchLayer.bl_label + " (Current: %s)" % MarkerLayer_Collection.getCurrentLayerName(context))
        layout.operator("icetb.marker_rename_layer")
        layout.operator("icetb.marker_beatmatch")

