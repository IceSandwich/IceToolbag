import bpy
from .base import EffectBase
from .widgets import xylock, exportbox, cropbox, maskbox

class EffectOriginal(EffectBase):
    @classmethod
    def getName(cls):
        return "Original"

    def stage_Before(self):
        lastSeq = self.richstrip.sequences.get("rs%d-fixfps"%self.data.RichStripID)
        if not lastSeq:
            lastSeq = self.getMovieStrip(self.richstrip)
        lastSeq.select = True

    def stage_PropertyDefination(self):
        self.addEnumProperty(self.effect, "transform_type", ["Scale to Fit", "Scale to Fill", "Stretch to Fill", "Original"])
        self.addFloatProperty(self.effect, "scale_x", 1) # float 0
        self.addFloatProperty(self.effect, "scale_y", 1) # float 1
        self.addBoolProperty(self.effect, "union_scale_lock", False)

        self.addExportProperty(self.effect, [
            [ "pos_x", "movie", "pos_x", True ],
            [ "pos_y", "movie", "pos_y", True ],
            [ "rotation", "movie", "rotation", True ],
            [ "scalex", "movie", "scale_x", True ],
            [ "scaley", "movie", "scale_y", True ]
        ])

    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            return
        self.addBuiltinEffectStrip('TRANSFORM', 'adjust')

    def stage_BinderDefination(self):
        movie = self.getMovieStrip(self.richstrip)

        self.addPropertyWithBinding(movie, "transform.offset_x", "pos_x", [{
            "name": "flip",
            "seqName": movie.name,
            "seqProp": "use_flip_x",
            "isCustomProp": False
        }], "bind * (-1 if flip == 1 else 1)", description="Offset X of movie")

        self.addPropertyWithBinding(movie, "transform.offset_y", "pos_y", [{
            "name": "flip",
            "seqName": movie.name,
            "seqProp": "use_flip_y",
            "isCustomProp": False
        }], "bind * (-1 if flip == 1 else 1)", description="Offset Y of movie")

        self.addPropertyWithBinding(movie, "transform.scale_x", "scale_x", [{
            "name": "scale",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Float", "scale_x"),
            "isCustomProp": False
        }], 'bind * scale', defaultValue=1.0)

        self.addPropertyWithBinding(movie, "transform.scale_y", "scale_y", [{
            "name": "scale",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Float", "scale_y"),
            "isCustomProp": False
        }, {
            "name": "lock",
            "seqName": self.richstrip.name,
            "seqProp": self.genseqProp(self.effect, "Bool", "union_scale_lock"),
            "isCustomProp": False
        }, {
            "name": "bindX",
            "seqName": movie.name,
            "seqProp": self.genbinderName(self.effect, "scale_x"),
            "isCustomProp": True
        }], '(bindX if lock == 1 else bind) * scale', defaultValue=1.0)

        self.addPropertyWithBinding(movie, "transform.rotation", "rotation", [{
            "name": "mirrorX",
            "seqName": movie.name,
            "seqProp": "use_flip_x",
            "isCustomProp": False
        }, {
            "name": "mirrorY",
            "seqName": movie.name,
            "seqProp": "use_flip_y",
            "isCustomProp": False
        }], '-radians(bind) if (mirrorX == 1) ^ (mirrorY == 1) else radians(bind)', defaultValue=0.0)

    def stage_After(self):
        self._update("ENUM", "transform_type", self.context) # set transform_type to first one


    @classmethod
    def draw(cls, context, layout:bpy.types.UILayout, data, effect, richstrip):
        movielayer = cls.getMovieStrip(richstrip)
        audiolayer = cls.getAudioStrip(richstrip)
        adjustlayer = cls.getEffectStrip(richstrip, effect, "adjust")

        box = layout.box()
        box.row().label(text="Translate", icon="ORIENTATION_LOCAL")
        xylock.drawWithExportBox_NoLock(box, richstrip, movielayer, cls.genbinderName(effect, "pos_x", True), "pos_x", movielayer, cls.genbinderName(effect, "pos_y", True), "pos_y" )

        layout.separator()

        box = layout.box()
        box.label(text="Scale", icon="FIXED_SIZE")
        box.prop(cls.getEnumProperty(effect, "transform_type"), "value", text="Resize")
        xylock.drawWithExportBox(box, richstrip, movielayer, cls.genbinderName(effect, "scale_x", True), "scalex", movielayer, cls.genbinderName(effect, "scale_y", True), "scaley", cls.getBoolProperty(effect, "union_scale_lock"), "value", union_label="Scale" )

        layout.separator()

        box = layout.box()
        box.label(text="Rotation", icon="DRIVER_ROTATIONAL_DIFFERENCE")
        exportbox.draw(box, richstrip, "rotation", movielayer, cls.genbinderName(effect, "rotation", True), text="Rotation")

        layout.separator()

        box = layout.box()
        box.label(text="Mirror", icon="MOD_MIRROR")
        row = box.row(align=True)
        row.prop(movielayer, "use_flip_x", toggle=1, text="Flip X", icon="ARROW_LEFTRIGHT")
        row.prop(movielayer, "use_flip_y", toggle=1, text="Flip Y", icon="EMPTY_SINGLE_ARROW")

        # box = layout.box()
        # box.row().label(text="Time (Only movie)")
        # box.prop(movielayer, "use_reverse_frames", toggle=1)

        if audiolayer is not None:
            layout.separator()
            box = layout.box()
            box.row().label(text="Audio")
            row = box.row(align=True)
            row.prop(audiolayer, "volume")
            row.prop(audiolayer, "mute", text="", toggle=0, icon="MUTE_IPO_ON")

        return

    @classmethod
    def calculateCanvasSize(cls, resizeEnum, data):
        renderX, renderY = bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y
        movieX, movieY = data.ResolutionWidth, data.ResolutionHeight

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

        return final_scalex, final_scaley

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        # don't trigger FLOAT type otherwise lead to forever loop
        if type == "ENUM" or type == 'BOOL':
            resizeEnum = cls.getEnumProperty(effect, "transform_type").value

            # FIXME: when movie resolution is bigger than render resolution
            # the following algorithmn can't perform very well due to the clipping of blender
            final_scalex, final_scaley = cls.calculateCanvasSize(resizeEnum, data)

            # the following caller will recall `update` function with type=='FLOAT' so we should block `FLOAT` type
            cls.getFloatProperty(effect, "scale_x").value = final_scalex
            cls.getFloatProperty(effect, "scale_y").value = final_scaley

            return True

        return False