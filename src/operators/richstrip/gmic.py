import bpy
import subprocess, os
from .effects.gmic import EffectGMIC, gmic_cache, gmic_qt_path, gmic_output_suffix
from ...datas.richstrip import RichStripEffect, RichStripData

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
        richstrip = context.selected_sequences[0]
        data:RichStripData = richstrip.IceTB_richstrip_data

        if self.effectidx != -1:
            return self.process(context, richstrip, data, data.Effects[self.effectidx], self.effectidx)

        for idx, x in enumerate(data.Effects):
            if x.EffectType == "GMIC":
                print("process frame on ", x.EffectName)
                self.process(context, richstrip, data, data.Effects[idx], idx)
        return {"FINISHED"}


    def process(self, context, richstrip, data, effect, effectidx):
        target = bpy.path.abspath(gmic_cache+"//%s//%d.%s"%(effect.EffectName, context.scene.frame_current, gmic_output_suffix))
        if self.stopAtExists and os.path.exists(target):
            return {"FINISHED"}

        availableList = []
        for i in range(effectidx, len(data.Effects)):
            availableList.append(data.Effects[i].EffectAvailable)
            if data.Effects[i].EffectAvailable:
                # bpy.ops.icetb.richstrip_effectavailable(effectidx = i)
                data.Effects[i].EffectAvailable = False

            print("hidden ", data.Effects[i].EffectName)
        
        bpy.ops.render.opengl(sequencer=True, view_context=False)
        renderfn = os.path.realpath("render.%s"%gmic_output_suffix)
        bpy.data.images[0].save_render(renderfn)

        command = EffectGMIC.getStrProperty(effect, "parameters").value
        print("get command:", command)

        process = subprocess.Popen("%s --apply -c \"%s\" --output \"%s\" \"%s\""%(gmic_qt_path, command, target, renderfn), stdout=subprocess.PIPE)
        process.wait()
        print("finish 1")

        for i in range(effectidx, len(data.Effects)):
            if availableList[i-effectidx]:
                data.Effects[i].EffectAvailable = True
            # data.Effects[i].EffectAvailable = availableList[i-data.EffectsCurrent]

        # bpy.ops.sequencer.refresh_all()

        return {"FINISHED"}

class ICETB_OT_RichStrip_GmicBakeAll(bpy.types.Operator):
    bl_idname = "icetb.richstrip_gmicbakeall"
    bl_label = "Bake All frames"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        richstrip:bpy.types.Sequence = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        assert(effect.EffectType == EffectGMIC.getName())

        fp = context.scene.render.filepath
        ff = context.scene.render.image_settings.file_format
        sf = context.scene.render.image_settings.color_mode
        fs = context.scene.frame_start
        fe = context.scene.frame_end

        finalfs = max(fs, richstrip.frame_final_start)
        finalfe = min(fe, richstrip.frame_final_end)

        context.scene.render.filepath = bpy.path.abspath(gmic_cache+"//%s//#.%s"%(effect.EffectName,gmic_output_suffix))
        context.scene.render.image_settings.file_format = 'PNG' if gmic_output_suffix == 'png' else 'JPEG'
        context.scene.render.image_settings.color_mode = 'RGBA' if gmic_output_suffix == 'png' else 'RGB'

        context.scene.frame_start = finalfs
        context.scene.frame_end = finalfe

        print("from", finalfs, "to", finalfe, "range", finalfe - finalfs)

        cachestrip = EffectGMIC.getEffectStrip(richstrip, effect, "gmicCache")
        cachestrip.mute = True

        bpy.ops.render.render(animation=True, use_viewport=False)

        cachestrip.mute = False

        context.scene.render.filepath = fp
        context.scene.render.image_settings.file_format = ff
        context.scene.render.image_settings.color_mode = sf

        context.scene.frame_start = fs
        context.scene.frame_end = fe

        command = EffectGMIC.getStrProperty(effect, "parameters").value
        print("get command:", command)

        # for i in range(finalfs, finalfe + 1):
        #     target = bpy.path.abspath(EffectGMIC.gmic_cache+"//%d.png"%(i))
        #     process = subprocess.Popen("%s --apply -c \"%s\" --output \"%s\" \"%s\""%(gmic_qt_path, command, target, target), stdout=subprocess.PIPE)
        #     process.wait()
        #     print("finish ", i)

        target = bpy.path.abspath(gmic_cache+"//%s//%%f"%(effect.EffectName))
        srcs = [ '"%s"'%bpy.path.abspath(gmic_cache+"//%s//%d.%s"%(effect.EffectName,i,gmic_output_suffix)) for i in range(finalfs, finalfe + 1) ]
        print(srcs)
        print(target)
        process = subprocess.Popen("%s --apply -c \"%s\" --output \"%s\" "%(gmic_qt_path, command, target)+" ".join(srcs), stdout=subprocess.PIPE)
        process.wait()
        print("finish all")

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
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        
        command = EffectGMIC.getStrProperty(effect, "parameters").value

        cachestrip = EffectGMIC.getEffectStrip(richstrip, effect, "gmicCache")
        renderfn = os.path.realpath("render."+gmic_output_suffix)
        
        target = bpy.path.abspath(gmic_cache+"//%s//%d.%s"%(effect.EffectName, context.scene.frame_current, gmic_output_suffix))

        cachestrip.mute = True
        bpy.ops.render.opengl(sequencer=True, view_context=False)
        bpy.data.images[0].save_render(renderfn)
        cachestrip.mute = False

        process = subprocess.Popen("%s -c \"%s\" --output \"%s\" \"%s\""%(gmic_qt_path, command, target, renderfn), stdout=subprocess.PIPE)
        if "Writing output file" not in bytes.decode(process.stdout.read()):
            print("something wrong with gmic-qt")
            return {'CANCELLED'}
        print("finish 1")

        process = subprocess.Popen("%s --show-last"%gmic_qt_path, stdout=subprocess.PIPE)
        commands = [ x.strip('\r').split(':') for x in bytes.decode(process.stdout.read()).split('\n') ]
        commands = { x[0]: ":".join(x[1:]).strip() for x in commands }
        print(commands)
        print("finish 2")

        command = commands["Command"]
        name = commands["Name"]
        print(command)
        print(name)
        print("finish 3")

        if command == "":
            print("No effect apply")
            return {'CANCELLED'}

        EffectGMIC.getStrProperty(effect, "parameters").value = command
        EffectGMIC.getStrProperty(effect, "fxname").value = name

        # bpy.ops.sequencer.refresh_all()

        return {"FINISHED"}