import bpy

class ICETB_MT_Main(bpy.types.Menu):
    bl_idname = "ICETB_MT_MAIN"
    bl_label = "Ice Toolbag"

    drawMenu = None

    @classmethod
    def setupProperty(cls, is_setup):
        from bpy.types import Sequence as sequence
        from bpy.types import Scene as scene
        if is_setup:
            scene.IceTB_richstrip_automatic_viewport_update = bpy.props.BoolProperty(name="Enable Automatic Viewport Update", default=True)
            print("Property viewport update defined")
        else:
            sequence.IceTB_richstrip_data = None
            print("Property viewport update uninstalled")

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
        layout.prop(context.scene, "IceTB_richstrip_automatic_viewport_update")
