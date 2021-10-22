import bpy
from .enum_prop import EnumProperty
from .string_prop import StringProperty

class GalleryStripScaleVector(bpy.types.PropertyGroup):
    X: bpy.props.FloatProperty(name="X scale factor", default=1.0)
    Y: bpy.props.FloatProperty(name="Y scale factor", default=1.0)

class GalleryStripData(bpy.types.PropertyGroup):
    # GalleryStrip information
    IsGalleryStrip: bpy.props.BoolProperty(name="Is it an gallery strip?", default=False)
    StripID: bpy.props.IntProperty(name="The unique id for gallery strip", default=-1)
    Version: bpy.props.IntProperty(name="The version of gallery strip", default=0) # compatibility

    # Strip information
    CanvasWidth: bpy.props.IntProperty(name="Width of canvas", default=-1, update=lambda cls, context: cls.make_delegate("Canvas Width"))
    CanvasHeight: bpy.props.IntProperty(name="Height of canvas", default=-1, update=lambda cls, context: cls.make_delegate("Canvas Height"))
    StripsName: bpy.props.CollectionProperty(type=StringProperty)
    StripsFitMethod: bpy.props.PointerProperty(type=EnumProperty)

    StripsScale: bpy.props.CollectionProperty(type=GalleryStripScaleVector)

    # Arrangement information
    ArrangementMethod: bpy.props.PointerProperty(type=EnumProperty)
    ArrangementMethodInt: bpy.props.IntProperty(name="The index of ArrangementMethod", default=0)

    GridWidth: bpy.props.IntProperty(name="Cell number of horizontal axis", default=1, update=lambda cls, context: self.make_delegate("Grid Width"))
    GridHeight: bpy.props.IntProperty(name="Cell number of vertical axis", default=1, update=lambda cls, context: self.make_delegate("Grid Height"))

    def make_delegate(self, eventIdentify):
        bpy.ops.icetb.gallerystrip_eventdelegate(eventIdentify=eventIdentify)
        return None

    @classmethod
    def genStripId(cls, ctx):
        ctx.scene.IceTB_gallerystrip_gen_id = ctx.scene.IceTB_gallerystrip_gen_id + 1
        return ctx.scene.IceTB_gallerystrip_gen_id

    @classmethod
    def setupProperty(cls, is_setup):
        from bpy.types import Sequence as sequence
        from bpy.types import Scene as scene
        if is_setup:
            sequence.IceTB_gallerystrip_data = bpy.props.PointerProperty(type=GalleryStripData)
            scene.IceTB_gallerystrip_gen_id = bpy.props.IntProperty(name="The id generator for gallery strip", default=0)
            print("Property gallerystrip defined")
        else:
            sequence.IceTB_gallerystrip_data = None
            print("Property gallerystrip uninstalled")

    @classmethod
    def checkProperty(cls, ctx, seq):
        return (hasattr(seq, 'IceTB_gallerystrip_data') and seq.IceTB_gallerystrip_data is not None and seq.IceTB_gallerystrip_data.IsGalleryStrip == True)

    @classmethod
    def initProperty(cls, gallerystrip, gsid, imgslist, canvasWidth, canvasHeight):
        if gallerystrip.type != 'META':
            # wrong sequence type
            # TODO: add more vaildate
            return False

        data = gallerystrip.IceTB_gallerystrip_data

        data.IsGalleryStrip = True
        data.StripID = gsid

        data.CanvasWidth, data.CanvasHeight = canvasWidth, canvasHeight
        
        data.StripsFitMethod.initForEffect("GalleryStrip", "Global", "FitMethod", None)
        for x in ["Scale to Fit", "Scale to Fill", "Stretch to Fill", "Original"]:
            data.StripsFitMethod.items.add().value = x

        data.ArrangementMethod.initForEffect("GalleryStrip", "Global", "Arrangement", None)
        # for x in ["Horizontal", "Vertical", "Grid"]:
        for x in ["Horizontal", "Vertical"]:
            data.ArrangementMethod.items.add().value = x
        data.ArrangementMethodInt = 0

        for x in imgslist:
            data.StripsName.add().value = x
            data.StripsScale.add()
