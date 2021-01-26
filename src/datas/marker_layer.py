import bpy

class MarkerLayer_OneMarker(bpy.types.PropertyGroup):
    markerName: bpy.props.StringProperty(name="Marker Name", default="Untitled Marker")
    markerFrame: bpy.props.IntProperty(name="Marker Frame Number", default=0)

    def parseFromTimelineMarker(self, timeline_marker):
        self.markerName = timeline_marker.name
        self.markerFrame = timeline_marker.frame

    def loadToTimelineMarker(self, ctx):
        marker = ctx.scene.timeline_markers.new(self.markerName)
        marker.frame = self.markerFrame
        marker.select = False

class MarkerLayer_OneLayer(bpy.types.PropertyGroup):
    layerName: bpy.props.StringProperty(name="Layer Name", default="Untitled layer")
    layerIndex: bpy.props.IntProperty(name="Layer Index", default=-1)
    markers: bpy.props.CollectionProperty(type=MarkerLayer_OneMarker)

    layerNum = 8 # Const

    @classmethod
    def setupProperty(cls, is_setup):
        from bpy.types import Scene as scene
        if is_setup:
            scene.IceTB_marker_layers_current = bpy.props.IntProperty(name="Current Layer Index", default=0)
            scene.IceTB_marker_layers_data = bpy.props.CollectionProperty(type=MarkerLayer_OneLayer)
            print("Property defined")
        else:
            scene.IceTB_marker_layers_current = None
            scene.IceTB_marker_layers_data = None
            print("Property uninstalled")

    @classmethod
    def initProperty(cls, ctx):
        # cls.setupProperty(True)
        ctx.scene.IceTB_marker_layers_data.clear()
        ctx.scene.IceTB_marker_layers_current = 0
        for i in range(cls.layerNum):
            layer = ctx.scene.IceTB_marker_layers_data.add()
            layer.layerName = "Layer " + str(i+1)
            layer.layerIndex = i
    
    @classmethod
    def checkProperty(cls, ctx):
        return ('IceTB_marker_layers_data' in dir(ctx.scene) and ctx.scene.IceTB_marker_layers_data is not None) and ('IceTB_marker_layers_current' in dir(ctx.scene) and ctx.scene.IceTB_marker_layers_current is not None) and (len(ctx.scene.IceTB_marker_layers_data) != 0)

    @classmethod
    def getFakeProperty(cls): #blender doesn't allow us to create property outside of `execute` function
        return [ "Layer " + str(i+1) for i in range(cls.layerNum) ]

    @classmethod
    def getCurrentLayerName(cls, ctx):
        if ctx.scene.IceTB_marker_layers_data is not None and len(ctx.scene.IceTB_marker_layers_data) != 0:
            return ctx.scene.IceTB_marker_layers_data[ctx.scene.IceTB_marker_layers_current].layerName
        return 'Layer 1'
    
    @classmethod
    def getProperty(cls, ctx, autocreate=False):
        if cls.checkProperty(ctx) == False:
            if autocreate:
                cls.initProperty(ctx)
                print("Property created")
            else:
                return None, None
        return ctx.scene.IceTB_marker_layers_data, ctx.scene.IceTB_marker_layers_current
        
    def parseFromCurrentScene(self, ctx, replace=True):
        # from bpy.context.scene import timeline_markers
        if replace:
            self.markers.clear()
        for _, timeline_marker in ctx.scene.timeline_markers.items():
            self.markers.add().parseFromTimelineMarker(timeline_marker)

    def loadToCurrentScene(self, ctx, clearBefore=True):
        if clearBefore:
            ctx.scene.timeline_markers.clear()
        for marker in self.markers:
            marker.loadToTimelineMarker(ctx)
        print("load to", self.layerIndex)
        ctx.scene.IceTB_marker_layers_current = self.layerIndex
