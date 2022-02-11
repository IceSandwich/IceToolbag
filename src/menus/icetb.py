import bpy
from bpy.app.handlers import persistent
from ..datas.preference_helper import getIsAutoupdateWhenStartup

depsgraphUpdateDisable = False # lock

@persistent
def updateSequenceViewportPersistent(scene):
    global depsgraphUpdateDisable
    # bpy.app.handlers.depsgraph_update_post.remove(updateSequenceViewportPersistent)
    if not depsgraphUpdateDisable:
        depsgraphUpdateDisable = True
        # print("update from depsgraph")
        bpy.ops.sequencer.refresh_all()
        depsgraphUpdateDisable = False
    # bpy.app.handlers.depsgraph_update_post.append(updateSequenceViewportPersistent)

def activeDepsgraphHandler(cls, obj): # can deactive handler
    if type(obj) == bpy.types.Scene:
        scene = obj
    if type(obj) == bpy.types.Context:
        scene = obj.scene
    if scene.IceTB_richstrip_automatic_viewport_update and updateSequenceViewportPersistent not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(updateSequenceViewportPersistent)
        print("Register handler for desgraph")
    if not scene.IceTB_richstrip_automatic_viewport_update and updateSequenceViewportPersistent in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(updateSequenceViewportPersistent)
        print("Unregister handler for desgraph")
        
class ICETB_MT_Main(bpy.types.Menu):
    bl_idname = "ICETB_MT_MAIN"
    bl_label = "Ice Toolbag"

    drawMenu = None

    @classmethod
    def setupProperty(cls, is_setup):
        from bpy.types import Sequence as sequence
        from bpy.types import Scene as scene
        if is_setup:
            scene.IceTB_richstrip_automatic_viewport_update = bpy.props.BoolProperty(name="Enable Automatic Viewport Update", default=True, update=activeDepsgraphHandler)
            print("Property viewport update defined")
        else:
            sequence.IceTB_richstrip_data = None
            print("Property viewport update uninstalled")

    @classmethod
    def setupHandlers(cls, is_setup):
        if activeDepsgraphHandler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(activeDepsgraphHandler)
            print("Unregister handler for load depsgraph")
        if is_setup:
            bpy.app.handlers.load_post.append(activeDepsgraphHandler)
            print("Register handler for load depsgraph")

    @classmethod
    def setupMenu(cls, is_setup):
        def drawFunc(cls, context):
            layout = cls.layout
            layout.menu("ICETB_MT_MAIN")

        if is_setup:
            cls.drawMenu = drawFunc
            bpy.types.SEQUENCER_HT_header.append(cls.drawMenu)
        else:
            bpy.types.SEQUENCER_HT_header.remove(cls.drawMenu)

    def draw(self, context):
        layout = self.layout

        # layout.label("version: 0.1 alpha")
        layout.separator()
        layout.menu("ICETB_MT_MARKER")
        layout.operator('icetb.convert_to_richstrip')
        layout.operator('icetb.convert_to_gallerystrip')
        layout.operator('icetb.richstrip_freezeframe')

        layout.prop(context.scene, "IceTB_richstrip_automatic_viewport_update")
