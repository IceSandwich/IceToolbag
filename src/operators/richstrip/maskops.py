import bpy, os
from .effects.base import EffectBase
from .effects.original import EffectOriginal

class ICETB_OT_RichStrip_Annotation2Mask(bpy.types.Operator):
    bl_idname = "icetb.richstrip_annotation2mask"
    bl_label = "Annotation to Mask"
    bl_options = {"REGISTER", "UNDO"}

    effectName_plusmaskId: bpy.props.StringProperty(name="The type of effect and id, should be `effectName`+'$$'+`rsid`+'_'+`effectId`+'$$'+'replace(true/false)?'")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context:bpy.context):
        self.effectName, self.maskId, self.isreplace = self.effectName_plusmaskId.split('$$')
        maskName = "IceTBMask%s"%self.maskId
        layerName = "IceTBMaskLayer"

        if len(bpy.data.grease_pencils.keys()) == 0:
            self.report({'ERROR'}, "No annotation detected.")
            return {"CANCELLED"}
        grease_pencils = bpy.data.grease_pencils[bpy.data.grease_pencils.keys()[-1]]
        grease_pencils_layers = grease_pencils.layers
        note_layer = grease_pencils_layers[grease_pencils_layers.keys()[-1]]

        mask = bpy.data.masks.get(maskName)
        if mask is None:
            mask = bpy.data.masks.new(name=maskName)

        # layer = mask.layers.get(layerName)
        # if layer is None:
        #     layer = mask.layers.new(name=layerName)
        #     layer.use_fill_holes = True
        if self.isreplace == "true":
            while len(mask.layers) != 0:
                mask.layers.remove(mask.layers[0])

        layer = mask.layers.new(name=layerName)
        layer.use_fill_holes = True

        renderX, renderY, renderPercentage = context.scene.render.resolution_x, context.scene.render.resolution_y, context.scene.render.resolution_percentage
        rangeY_max = 1/1.28
        rangeY_min = 1 - rangeY_max
        rangeY = rangeY_max - rangeY_min

        for stroke in note_layer.frames[0].strokes:
            spline = layer.splines.new()
            spline.points.add(len(stroke.points)-1)

            points = [ [p.co[0], p.co[1]] for p in stroke.points ]

            for i, point in enumerate(points[::-1]):
                xnormal = ((float)(point[0])+renderX/2.0)/(float)(renderX)
                ynormal = ((float)(point[1])+renderY/2.0)/(float)(renderY)*rangeY + rangeY_min
                spline.points[i].co[0] = xnormal
                spline.points[i].co[1] = ynormal
                # spline.points[i].weight # feather
                spline.points[i].handle_type = 'VECTOR'
                # spline.points[i].handle_type = 'ALIGNED_DOUBLESIDE'
            
            spline.use_cyclic = True

        grease_pencils_layers.remove(note_layer)
        bpy.data.grease_pencils.remove(grease_pencils)

        bpy.ops.icetb.richstrip_eventdelegate(effectName=self.effectName, eventType="MASK_SET", eventIdentify=mask.name)

        return {"FINISHED"}


class ICETB_OT_RichStrip_OpenMaskEditor(bpy.types.Operator):
    bl_idname = "icetb.richstrip_openmaskeditor"
    bl_label = "Open Mask Editor"
    bl_options = {"REGISTER", "UNDO"}

    maskName: bpy.props.StringProperty(name="Mask Name")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context:bpy.context):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data

        renderX, renderY, renderPercentage = context.scene.render.resolution_x, context.scene.render.resolution_y, context.scene.render.resolution_percentage

        context.scene.render.resolution_x = renderX/4*3
        context.scene.render.resolution_y = renderY/4*3
        context.scene.render.resolution_percentage = 100

        context.preferences.view.render_display_type = "WINDOW"
        bpy.ops.render.view_show("INVOKE_DEFAULT")

        area = context.window_manager.windows[-1].screen.areas[0]
        area.type = "CLIP_EDITOR"

        movieSeq = EffectBase.getMovieStrip(richstrip)
        fn = movieSeq.filepath
        bpy.ops.clip.open(directory=os.path.dirname(fn), files=[{"name":os.path.basename(fn)}], relative_path=True)
        area.spaces[0].mode = 'MASK'
        area.spaces[0].mask = bpy.data.masks.get(self.maskName)

        scale_x = EffectBase.getFloatProperty(data.Effects[0], "scale_x").value
        scale_y = EffectBase.getFloatProperty(data.Effects[0], "scale_y").value

        user_scale_x = movieSeq[EffectBase.genbinderName(data.Effects[0], "scale_x", False)]
        user_scale_y = movieSeq[EffectBase.genbinderName(data.Effects[0], "scale_y", False)]

        print("ux", user_scale_x, "sx", scale_x, "uy", user_scale_y, "sy", scale_y)
        # TODO: fix scale problem

        area.spaces[0].clip.display_aspect.x = user_scale_x * scale_x
        area.spaces[0].clip.display_aspect.y = user_scale_y * scale_y

        context.scene.render.resolution_x = renderX
        context.scene.render.resolution_y = renderY
        context.scene.render.resolution_percentage = renderPercentage

        return {"FINISHED"}