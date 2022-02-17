import bpy
import subprocess, os
from .effects.gmic import EffectGMIC, fetchCommandFromGmic
from ...datas.preference_helper import renderPreview, getCacheDir, getGmicQTPath
from ...datas.preference_helper import render_output_suffix as gmic_output_suffix
from ...datas.richstrip import RichStripEffect, RichStripData

def hiddenLayers(data, effectidx):
    availableList = []
    for i in range(effectidx, len(data.Effects)):
        availableList.append(data.Effects[i].EffectAvailable)
        if data.Effects[i].EffectAvailable:
            # bpy.ops.icetb.richstrip_effectavailable(effectidx = i)
            data.Effects[i].EffectAvailable = False

        print("hidden ", data.Effects[i].EffectName)

    return availableList

def recoverLayers(data, effectidx, availableList):
    for i in range(effectidx, len(data.Effects)):
        if availableList[i-effectidx]:
            data.Effects[i].EffectAvailable = True
        # data.Effects[i].EffectAvailable = availableList[i-data.EffectsCurrent]

class ICETB_OT_RichStrip_GmicProcessFrame(bpy.types.Operator):
    bl_idname = "icetb.richstrip_gmicprocessframe"
    bl_label = "Process current frame"
    bl_options = {"REGISTER"}

    effectidx: bpy.props.IntProperty(name="Effect Idx", description="which effect need to change visibility.", default=-1)
    stopAtExists: bpy.props.BoolProperty(name="Stop when exist", default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if not hasattr(context, "selected_sequences"):
            # TODO: warn users and stop animation process or use another way to fix.
            self.report({'ERROR'}, "Please turn off \"Ice Toolbag > Automatic Viewport Update\" before rendering animation.")
            # raise Exception("Automatic Viewport is running")

        richstrip = context.selected_sequences[0]
        if not RichStripData.checkProperty(context, richstrip): return {"FINISHED"}
        data:RichStripData = richstrip.IceTB_richstrip_data

        gmic_qt_path = getGmicQTPath()

        if not os.path.exists(gmic_qt_path):
            self.report({'ERROR'}, "Unable to detect gmic_qt.exe for path \"%s\""%gmic_qt_path)
            return {"CANCELLED"}

        if self.effectidx != -1:
            return self.process(context, richstrip, data, data.Effects[self.effectidx], self.effectidx, gmic_qt_path)

        for idx, x in enumerate(data.Effects):
            if x.EffectType == "GMIC":
                print("&& process frame on ", x.EffectName)
                self.process(context, richstrip, data, data.Effects[idx], idx, gmic_qt_path)

        return {"FINISHED"}


    def process(self, context, richstrip, data, effect, effectidx, gmic_qt_path):
        cacheId = EffectGMIC.getStrProperty(effect, "uuid").value
        offset = context.scene.frame_current - richstrip.frame_final_start

        target = bpy.path.abspath("%s//%s//%d.%s"%(getCacheDir(), cacheId, offset, gmic_output_suffix))
        if self.stopAtExists and os.path.exists(target):
            return {"FINISHED"}

        availableList = hiddenLayers(data, effectidx)
        EffectGMIC.enterEditMode(richstrip) # should use EffectBase, but i don't want to import another class so i reuse it.
        renderfn = renderPreview()
        EffectGMIC.leaveEditMode()
        recoverLayers(data, effectidx, availableList)

        command = EffectGMIC.getStrProperty(effect, "parameters").value
        process = subprocess.Popen("\"%s\" --apply -c \"%s\" --output \"%s\" \"%s\""%(gmic_qt_path, command, target, renderfn), stdout=subprocess.PIPE)
        process.wait()

        return {"FINISHED"}

class ICETB_OT_RichStrip_GmicBakeAll(bpy.types.Operator):
    bl_idname = "icetb.richstrip_gmicbakeall"
    bl_label = "Bake All frames"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context:bpy.types.Context):
        richstrip:bpy.types.Sequence = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        assert(effect.EffectType == EffectGMIC.getName())

        # store informations
        fp = context.scene.render.filepath
        ff = context.scene.render.image_settings.file_format
        sf = context.scene.render.image_settings.color_mode
        fs = context.scene.frame_start
        fe = context.scene.frame_end

        finalfs = max(fs, richstrip.frame_final_start)
        finalfe = min(fe, richstrip.frame_final_end)
        framecr = context.scene.frame_current

        print("from", finalfs, "to", finalfe, "range", finalfe - finalfs)

        for frame in range(finalfs, finalfe+1):
            context.scene.frame_set(frame)
            print("render ", frame)

        # cacheId = EffectGMIC.getStrProperty(effect, "uuid").value
        # context.scene.render.filepath = bpy.path.abspath("%s//%s//#.%s"%(gmic_cache, cacheId, gmic_output_suffix))
        # context.scene.render.image_settings.file_format = 'PNG' if gmic_output_suffix == 'png' else 'JPEG'
        # context.scene.render.image_settings.color_mode = 'RGBA' if gmic_output_suffix == 'png' else 'RGB'

        # context.scene.frame_start = finalfs
        # context.scene.frame_end = finalfe


        # cachestrip = EffectGMIC.getEffectStrip(richstrip, effect, "gmicCache")
        # cachestrip.mute = True

        # context.scene.frame_set()
        # bpy.ops.render.render(animation=True, use_viewport=False)

        # cachestrip.mute = False

        # # recover informations
        # context.scene.render.filepath = fp
        # context.scene.render.image_settings.file_format = ff
        # context.scene.render.image_settings.color_mode = sf
        # context.scene.frame_start = fs
        # context.scene.frame_end = fe

        # command = EffectGMIC.getStrProperty(effect, "parameters").value
        # print("get command:", command)

        # # for i in range(finalfs, finalfe + 1):
        # #     target = bpy.path.abspath(EffectGMIC.gmic_cache+"//%d.png"%(i))
        # #     process = subprocess.Popen("%s --apply -c \"%s\" --output \"%s\" \"%s\""%(gmic_qt_path, command, target, target), stdout=subprocess.PIPE)
        # #     process.wait()
        # #     print("finish ", i)

        # target = bpy.path.abspath(gmic_cache+"//%s//%%f"%(effect.EffectName))
        # srcs = [ '"%s"'%bpy.path.abspath(gmic_cache+"//%s//%d.%s"%(effect.EffectName,i,gmic_output_suffix)) for i in range(finalfs, finalfe + 1) ]
        # print(srcs)
        # print(target)

        # gmic_qt_path = getGmicQTPath()
        # process = subprocess.Popen("%s --apply -c \"%s\" --output \"%s\" %s"%(gmic_qt_path, command, target, " ".join(srcs)), stdout=subprocess.PIPE)
        # process.wait()
        # print("finish all")

        return {"FINISHED"}

class ICETB_OT_RichStrip_GmicModifiy(bpy.types.Operator):
    bl_idname = "icetb.richstrip_gmicmodify"
    bl_label = "Edit in GMIC"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        richstrip:bpy.types.Sequence = context.selected_sequences[0]
        data:RichStripData = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        
        offset = context.scene.frame_current - richstrip.frame_final_start
        cacheId = EffectGMIC.getStrProperty(effect, "uuid").value
        target = bpy.path.abspath("%s//%s//%d.%s"%(getCacheDir(), cacheId, offset, gmic_output_suffix))

        effectidx = data.EffectsCurrent
        cachestrip = EffectGMIC.getEffectStrip(richstrip, effect, "gmicCache")
        # cachestrip.mute = True
        availableList = hiddenLayers(data, effectidx)
        EffectGMIC.enterEditMode(richstrip) # should use EffectBase, but i don't want to import another class so i reuse it.
        renderfn = renderPreview()
        EffectGMIC.leaveEditMode()
        # cachestrip.mute = False
        recoverLayers(data, effectidx, availableList)

        gmic_qt_path = getGmicQTPath()
        command = EffectGMIC.getStrProperty(effect, "parameters").value
        process = subprocess.Popen("\"%s\" -c \"%s\" --output \"%s\" \"%s\""%(gmic_qt_path, command, target, renderfn), stdout=subprocess.PIPE)
        gmic_output_console = bytes.decode(process.stdout.read())
        if "Writing output file" not in gmic_output_console:
            self.report({'ERROR'}, "Something wrong with G'mic-qt. See console log.")
            print("G'mic output(reason: no path): >>>")
            print(gmic_output_console)
            print("<<<")
            return {'CANCELLED'}

        commands = fetchCommandFromGmic()
        command = commands["Command"]
        name = commands["Name"]

        if command == "":
            print("No effect apply")
            return {'CANCELLED'}

        EffectGMIC.getStrProperty(effect, "parameters").value = command
        EffectGMIC.getStrProperty(effect, "fxname").value = name

        return {"FINISHED"}