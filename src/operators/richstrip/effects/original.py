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
        EffectIntProperties:
            [0]: Translate X
            [1]: Translate Y
        EffectBoolProperties:
            [0]: Union Scale?
            [1]: Flip X
            [2]: Flip Y
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
        cls.addFloatProperty(effect, "scale_x", 1)
        cls.addFloatProperty(effect, "scale_y", 1)
        cls.addIntProperty(effect, "pos_x", 0)
        cls.addIntProperty(effect, "pos_y", 0)
        cls.addBoolProperty(effect, "union_scale_lock", False)
        cls.addBoolProperty(effect, "flip_x", False)
        cls.addBoolProperty(effect, "flip_y", False)

        movie = cls.getMovieStrip(richstrip)
        audiolayer = cls.getAudioStrip(richstrip)

        audiolayer["pos_x"] = 0
        driver = movie.transform.driver_add("offset_x").driver
        flip = driver.variables.new()
        flip.name = 'flip'
        flip.targets[0].id_type = 'SCENE'
        flip.targets[0].id = context.scene
        flip.targets[0].data_path = 'sequence_editor.sequences_all["%s"].use_flip_x'%movie.name
        pos = driver.variables.new()
        pos.name = 'pos'
        pos.targets[0].id_type = 'SCENE'
        pos.targets[0].id = context.scene
        pos.targets[0].data_path = 'sequence_editor.sequences_all["%s"]["pos_x"]'%audiolayer.name
        driver.use_self = True
        driver.expression = 'pos * (-1 if flip == 1 else 1)'

        audiolayer["pos_y"] = 0
        driver = movie.transform.driver_add("offset_y").driver
        flip = driver.variables.new()
        flip.name = 'flip'
        flip.targets[0].id_type = 'SCENE'
        flip.targets[0].id = context.scene
        flip.targets[0].data_path = 'sequence_editor.sequences_all["%s"].use_flip_y'%movie.name
        pos = driver.variables.new()
        pos.name = 'pos'
        pos.targets[0].id_type = 'SCENE'
        pos.targets[0].id = context.scene
        pos.targets[0].data_path = 'sequence_editor.sequences_all["%s"]["pos_y"]'%audiolayer.name
        driver.use_self = True
        driver.expression = 'pos * (-1 if flip == 1 else 1)'


        cls.leaveEditMode(data)

        cls._update("ENUM", "transform_type", context) # set transform_type to first one
        return

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        movielayer = cls.getMovieStrip(richstrip)
        audiolayer = cls.getAudioStrip(richstrip)
        adjustlayer = cls.getEffectStrip(richstrip, "adjust")

        box = layout.box()
        box.row().label(text="Translate")
        row = box.row(align=True)
        # row.prop(cls.getIntProperty(effect, "pos_x"), "value", text="X")
        # row.prop(cls.getIntProperty(effect, "pos_y"), "value", text="Y")
        row.prop(audiolayer, '["pos_x"]', text="X")
        row.prop(audiolayer, '["pos_y"]', text="Y")

        box = layout.box()
        box.label(text="Scale")
        box.prop(cls.getEnumProperty(effect, "transform_type"), "value", text="Resize")
        xylock.draw(box, cls.getFloatProperty(effect, "scale_x"), "value", cls.getFloatProperty(effect, "scale_y"), "value", cls.getBoolProperty(effect, "union_scale_lock"), "value")

        box = layout.box()
        box.label(text="Rotation")
        box.prop(adjustlayer.transform, "rotation", text="Degree")
        # box.prop(movielayer.transform, "rotation", text="Degree")

        box = layout.box()
        box.label(text="Mirror")
        row = box.row(align=True)
        # row.prop(cls.getBoolProperty(effect, "flip_x"), "value", toggle=1, text="Flip X")
        # row.prop(cls.getBoolProperty(effect, "flip_y"), "value", toggle=1, text="Flip Y")
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
        adjustlayer = cls.getEffectStrip(richstrip, "adjust")

        if (type == 'BOOL' and (identify != "union_scale_lock")) or (type == 'INT'): #flip x/y
            adjustlayer.use_flip_x = effect.EffectBoolProperties[1].value
            adjustlayer.use_flip_y = effect.EffectBoolProperties[2].value
            adjustlayer.transform.offset_x = effect.EffectIntProperties[0].value * (-1 if effect.EffectBoolProperties[1].value else 1)
            adjustlayer.transform.offset_y = effect.EffectIntProperties[1].value * (-1 if effect.EffectBoolProperties[2].value else 1)
            return

        if (type == "ENUM" and identify == "transform_type") or type == 'FLOAT' or type == 'BOOL':  

            renderX, renderY = context.scene.render.resolution_x, context.scene.render.resolution_y
            movieX, movieY = data.ResolutionWidth, data.ResolutionHeight
            # MovieSeq = firstlayer.sequences.get("rs%d-movie"%data.RichStripID)

            user_scalex, user_scaley = effect.EffectFloatProperties[0].value, effect.EffectFloatProperties[1].value
            resizeEnum = effect.EffectEnumProperties[0].value
            if effect.EffectBoolProperties[0].value:
                user_scaley = user_scalex

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

            adjustlayer.transform.scale_x = final_scalex * user_scalex
            adjustlayer.transform.scale_y = final_scaley * user_scaley

            bpy.ops.sequencer.refresh_all()

        return