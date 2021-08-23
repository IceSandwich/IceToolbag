import bpy
from .base import EffectBase
from .widgets import xylock

class EffectOriginal(EffectBase):
    """
        EffectEnumProperties:
            [0]: Resize method
        EffectFloatProperties:
            [0]: Scale X
            [1]: Scale Y
        EffectBoolProperties:
            [0]: Union Scale
    """
    @classmethod
    def getName(cls):
        return "Original"

    @classmethod
    def add(cls, context, richstrip, data, effect):
        cls.enterEditMode(richstrip)

        richstrip.sequences.get("rs%d-fixfps"%data.RichStripID).select = True
        adjustlayer = cls.addBuiltinEffectStrip(context, richstrip, effect, 'TRANSFORM', 'adjust')
        
        cls.addEnumProperty(effect, "transform_type", ["Scale to Fit", "Scale to Fill", "Stretch to Fill", "Original"])
        cls.addFloatProperty(effect, "scale_x", 1) # float 0
        cls.addFloatProperty(effect, "scale_y", 1) # float 1
        cls.addBoolProperty(effect, "union_scale_lock", False)

        movie = cls.getMovieStrip(richstrip)

        cls.addPropertyWithBinding(context, movie, "transform.offset_x", cls.genbinderName(effect, "pos_x"), [{
            "name": "flip",
            "seqName": movie.name,
            "seqProp": "use_flip_x",
            "isCustomProp": False
        }], "bind * (-1 if flip == 1 else 1)", description="Offset X of movie")

        cls.addPropertyWithBinding(context, movie, "transform.offset_y", cls.genbinderName(effect, "pos_y"), [{
            "name": "flip",
            "seqName": movie.name,
            "seqProp": "use_flip_y",
            "isCustomProp": False
        }], "bind * (-1 if flip == 1 else 1)", description="Offset Y of movie")

        cls.addPropertyWithBinding(context, movie, "transform.scale_x", cls.genbinderName(effect, "scale_x"), [{
            "name": "scale",
            "seqName": richstrip.name,
            "seqProp": cls.genseqProp(effect, "Float", "scale_x"),
            "isCustomProp": False
        }], 'bind * scale', defaultValue=1.0)

        cls.addPropertyWithBinding(context, movie, "transform.scale_y", cls.genbinderName(effect, "scale_y"), [{
            "name": "scale",
            "seqName": richstrip.name,
            "seqProp": cls.genseqProp(effect, "Float", "scale_y"),
            "isCustomProp": False
        }, {
            "name": "lock",
            "seqName": richstrip.name,
            "seqProp": cls.genseqProp(effect, "Bool", "union_scale_lock"),
            "isCustomProp": False
        }, {
            "name": "bindX",
            "seqName": movie.name,
            "seqProp": cls.genbinderName(effect, "scale_x"),
            "isCustomProp": True
        }], '(bindX if lock == 1 else bind) * scale', defaultValue=1.0)

        cls.leaveEditMode(data)

        cls._update("ENUM", "transform_type", context) # set transform_type to first one
        return

    @classmethod
    def relink()

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        movielayer = cls.getMovieStrip(richstrip)
        audiolayer = cls.getAudioStrip(richstrip)
        adjustlayer = cls.getEffectStrip(richstrip, "adjust")

        box = layout.box()
        box.row().label(text="Translate")
        row = box.row(align=True)
        row.prop(movielayer, cls.genbinderName(effect, "pos_x", True), text="X")
        row.prop(movielayer, cls.genbinderName(effect, "pos_y", True), text="Y")

        box = layout.box()
        box.label(text="Scale")
        box.prop(cls.getEnumProperty(effect, "transform_type"), "value", text="Resize")
        xylock.draw(box, movielayer, cls.genbinderName(effect, "scale_x", True), movielayer, cls.genbinderName(effect, "scale_y", True), cls.getBoolProperty(effect, "union_scale_lock"), "value")

        box = layout.box()
        box.label(text="Rotation")
        box.prop(adjustlayer.transform, "rotation", text="Degree")

        box = layout.box()
        box.label(text="Mirror")
        row = box.row(align=True)
        row.prop(movielayer, "use_flip_x", toggle=1, text="Flip X")
        row.prop(movielayer, "use_flip_y", toggle=1, text="Flip Y")

        # box = layout.box()
        # box.row().label(text="Time (Only movie)")
        # box.prop(movielayer, "use_reverse_frames", toggle=1)

        if audiolayer is not None:
            box = layout.box()
            box.row().label(text="Audio")
            row = box.row(align=True)
            row.prop(audiolayer, "volume")
            row.prop(audiolayer, "mute", icon="MUTE_IPO_ON", toggle=1)

        # layout.label(text="Movie Transform:")
        # row = layout.row(align=True)
        # adjustoffset = adjustlayer.transform
        # row.prop(adjustoffset, "offset_x", text="X")
        # row.prop(adjustoffset, "offset_y", text="Y")

        # layout.label(text="Movie Color:")
        # layout.prop(adjustlayer, "color_saturation")
        # layout.prop(adjustlayer, "color_multiply")
        return

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        # don't trigger FLOAT type otherwise lead to forever loop
        if type == "ENUM" or type == 'BOOL':
            renderX, renderY = context.scene.render.resolution_x, context.scene.render.resolution_y
            movieX, movieY = data.ResolutionWidth, data.ResolutionHeight

            resizeEnum = cls.getEnumProperty(effect, "transform_type").value

            # FIXME: when movie resolution is bigger than render resolution
            # the following algorithmn can't perform very well due to the clipping of blender

            fullx_y, fully_x = movieY * renderX / movieX, movieX * renderY / movieY
            if resizeEnum == "Scale to Fit":
                if fullx_y <= renderY or fully_x > renderX:
                    final_scalex = final_scaley = renderX / movieX
                elif fully_x <= renderX or fullx_y > renderY:
                    final_scalex = final_scaley = renderY / movieY
            elif resizeEnum == "Scale to Fill":
                if fullx_y >= renderY or fully_x < renderX:
                    final_scalex = final_scaley = renderX / movieX
                elif fully_x >= renderX or fullx_y < renderY:
                    final_scalex = final_scaley = renderY / movieY
            elif resizeEnum == "Stretch to Fill":
                final_scalex, final_scaley = renderX / movieX, renderY / movieY
            elif resizeEnum == "Original":
                final_scalex = final_scaley = 1

            # the following caller will recall `update` function with type=='FLOAT' so we should block `FLOAT` type
            cls.getFloatProperty(effect, "scale_x").value = final_scalex
            cls.getFloatProperty(effect, "scale_y").value = final_scaley

            return True

        return False