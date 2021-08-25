import bpy

from .richstrip.effects.base import EffectBase

class ICETB_OT_GallyerStrip_EventDelegate(bpy.types.Operator):
    bl_idname = "icetb.gallerystrip_eventdelegate"
    bl_label = "Delegate for some props(Private use only)"
    bl_options = {"REGISTER"}

    eventIdentify: bpy.props.StringProperty(name="The identify of event")

    @classmethod
    def poll(cls, context):
        return True

    def fitmethod_changed(self, context, gallerystrip, data):
        renderX, renderY = data.CanvasWidth, data.CanvasHeight
        resizeEnum = data.StripsFitMethod.value

        for i, stripName in enumerate(data.StripsName):
            imgseq = gallerystrip.sequences.get(stripName.value)
            movieX, movieY = imgseq.elements[0].orig_width, imgseq.elements[0].orig_height

            # FIXME: copy from orignal.py
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

            data.StripsScale[i].X = final_scalex
            data.StripsScale[i].Y = final_scaley

    def arrangement_changed(self, context, gallerystrip, data):
        data.ArrangementMethodInt = ["Horizontal", "Vertical", "Grid"].index(data.ArrangementMethod.value)

    def execute(self, context):
        if len(context.selected_sequences) < 1: # i don't know why
            return {'FINISHED'}

        gallerystrip = context.selected_sequences[0]
        data = gallerystrip.IceTB_gallerystrip_data
        
        if self.eventIdentify == "Grid Width":
            return
        elif self.eventIdentify == "Grid Height":
            return
        elif self.eventIdentify == "Canvas Width" or self.eventIdentify == "Canvas Height" or self.eventIdentify == "FitMethod":
            self.fitmethod_changed(context, gallerystrip, data)
        elif self.eventIdentify == "Arrangement":
            self.arrangement_changed(context, gallerystrip, data)

        return {"FINISHED"}