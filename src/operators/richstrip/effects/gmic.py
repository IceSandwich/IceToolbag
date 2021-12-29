import bpy, os
from .base import EffectBase
from ....datas import RichStripData, RichStripEffect
import subprocess, shutil
# from .widgets import xylock

gmic_qt_path = "src/extra/gmic-3.0.0-qt-win64/gmic_qt.exe"
gmic_cache = "//IceTBCache"
gmic_output_suffix = "jpg"

def onFrameChanged(scene, depsgraph): # called by `addeffect.py`
    if not scene.IceTB_richstrip_automatic_viewport_update: return
    print(">> change frame to", scene.frame_current)
    bpy.ops.icetb.richstrip_gmicprocessframe(stopAtExists=True)

class EffectGMIC(EffectBase):
    @classmethod
    def getName(cls):
        return "GMIC"

    @classmethod
    def _add(cls, context:bpy.context): #override
        if not os.path.exists(os.path.realpath(gmic_qt_path)):
            print("Unable to detect gmic_qt.exe, please install it in %s."%os.path.realpath(gmic_qt_path))
            return False

        bpy.ops.render.opengl(sequencer=True, view_context=False)

        renderfn = os.path.realpath("render.%s"%gmic_output_suffix)
        outputfn = os.path.realpath("output.%s"%gmic_output_suffix)
        print("render filename:", renderfn, "output filename:", outputfn)
        bpy.data.images[0].save_render(renderfn)

        process = subprocess.Popen("%s --output \"%s\" \"%s\""%(gmic_qt_path, outputfn, renderfn), stdout=subprocess.PIPE)
        if "Writing output file" not in bytes.decode(process.stdout.read()):
            print("something wrong with gmic-qt")
            return False
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
            return False

        # process = subprocess.Popen("%s -c \"%s\" --output output.jpg 3.jpg"%(gmic_qt_path, command), stdout=subprocess.PIPE)
        # process.wait()
        # print("finish 4")


        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect : RichStripEffect = data.addEffect(cls.getName())
        cls.add(context, richstrip, data, effect) # run stages functions

        cachedir = bpy.path.abspath(gmic_cache+"//%s"%effect.EffectName)
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        target = bpy.path.abspath("%s//%s//%d.%s"%(gmic_cache, effect.EffectName, context.scene.frame_current, gmic_output_suffix))
        shutil.copy("output.%s"%gmic_output_suffix, target)
        print("copy to ", target)

        cls.getStrProperty(effect, "parameters").value = command
        cls.getStrProperty(effect, "fxname").value = name

        return True

    def stage_PropertyDefination(self):
        # addColorProperty, addFloatProperty, addIntProperty, addBoolProperty, addEnumProperty
        self.addStrProperty(self.effect, "parameters")
        self.addStrProperty(self.effect, "fxname")
        return

    def stage_SequenceDefination(self, relinkStage:bool):
        if relinkStage:
            # self.xx = self.getEffectStrip(self.richstrip, self.effect, "xx")
            return
            
        movieseq = self.getMovieStrip(self.richstrip)
        self.data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.image_strip_add(directory=bpy.path.abspath(gmic_cache+"//%s"%self.effect.EffectName), files=[{
            "name": "%d.%s"%(i, gmic_output_suffix)
        } for i in range(movieseq.frame_final_start, movieseq.frame_final_end)], relative_path=True, show_multiview=False, frame_start=movieseq.frame_final_start, frame_end=movieseq.frame_final_end, channel=self.data.EffectCurrentMaxChannel1, set_view_transform=False)
        effectlayer = self.context.scene.sequence_editor.active_strip
        effectlayer.name = self.genRegularStripName(self.data.RichStripID, self.effect.EffectId, "gmicCache")
        self.effect.EffectStrips.add().value = effectlayer.name

        # self.xx = self.addBuiltinStrip('XXX', "xx")

        self.addBuiltinStrip('ADJUSTMENT', "adjust")
        return

    def stage_BinderDefination(self):
        # self.addPropertyWithDriver(self.context, self.xx, "xxx", [{
        #     "name": "var",
        #     "seqName": self.xx.name,
        #     "seqProp": xx,
        #     "isCustomProp": True/False
        # }], "var*bind")
        return

    # def stage_After(self):
    #     return


    @classmethod
    def draw(cls, context:bpy.types.Context, layout:bpy.types.UILayout, data:RichStripData, effect:RichStripEffect, richstrip:bpy.types.SequencesMeta):
        # xx = cls.getEffectStrip(richstrip, effect, "xx")
        
        # layout.label(text="Hello world")

        layout.label(text="command:"+cls.getStrProperty(effect, "parameters").value)
        layout.label(text="name:"+cls.getStrProperty(effect, "fxname").value)

        layout.operator("icetb.richstrip_gmicprocessframe", text="Process current frame for only current effect").effectidx = effect.EffectIndex
        layout.operator("icetb.richstrip_gmicprocessframe", text="Process current frame for all effect")
        layout.operator("icetb.richstrip_gmicbakeall")
        layout.operator("icetb.richstrip_gmicmodify")
        return

    @classmethod
    def update(cls, attr_type:str, attr_identify:str, context:bpy.types.Context, data:RichStripData, effect:RichStripEffect, richstrip:bpy.types.SequencesMeta):
        # if attr_type == 'INT' and attr_identify == "xxx":
        #   do something...
        #   return True
        
        return False