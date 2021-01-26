import bpy

class ICETB_MT_Main(bpy.types.Menu):
    bl_idname = "ICETB_MT_MAIN"
    bl_label = "Ice Toolbag"

    drawMenu = None

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
        layout.operator('icetb.marker_convert_to_richstrip')
