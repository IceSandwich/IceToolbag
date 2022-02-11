import bpy, os, uuid
from .base import EffectBase
from ....datas import RichStripData, RichStripEffect
from ....datas.preference_helper import getCacheDir, getGmicQTPath, renderPreview
from ....datas.preference_helper import render_output_suffix as gmic_output_suffix
import subprocess, shutil
# from .widgets import xylock

def onFrameChanged(scene, depsgraph):
    if not scene.IceTB_richstrip_automatic_viewport_update: return
    print(">> change frame to", scene.frame_current)
    bpy.ops.icetb.richstrip_gmicprocessframe(stopAtExists=True)

@bpy.app.handlers.persistent
def onBlendLoaded(scene:bpy.types.Scene): # called when new blend file loaded, `scene` will be none all the time idk why.
    if onFrameChanged in bpy.app.handlers.frame_change_post: return

    for richstrip in bpy.context.scene.sequence_editor.sequences.values():
        if RichStripData.checkProperty(bpy.context, richstrip):
            for x in richstrip.IceTB_richstrip_data.Effects:
                if x.EffectType == "GMIC": # as long as have gmic effect
                    bpy.app.handlers.frame_change_post.append(onFrameChanged)
                    print("Register handler for framechange")
                    return

def fetchCommandFromGmic():
    """ use this after running gmic program, return commands dict """
    process = subprocess.Popen("%s --show-last"%getGmicQTPath(), stdout=subprocess.PIPE)
    commands = [ x.strip('\r').split(':') for x in bytes.decode(process.stdout.read()).split('\n') ]
    commands = { x[0]: ":".join(x[1:]).strip() for x in commands }
    return commands

class EffectGMIC(EffectBase):
    @classmethod
    def getName(cls):
        return "GMIC"

    @classmethod
    def SIG_Add(cls, context, is_setup): # called when add effect and remove effect
        if is_setup:
            if onFrameChanged not in bpy.app.handlers.frame_change_post:
                bpy.app.handlers.frame_change_post.append(onFrameChanged)
                print("Register handler for framechange")
        else:
            richstrip = context.selected_sequences[0]
            assert(RichStripData.checkProperty(context, richstrip))
            data:RichStripData = richstrip.IceTB_richstrip_data
            if onFrameChanged in bpy.app.handlers.frame_change_post and sum([1 for x in data.Effects if x.EffectType == cls.getName()]) == 0:
                bpy.app.handlers.frame_change_post.remove(onFrameChanged)
                print("Unregister handler for framechange")

    @classmethod
    def setupHandlers(cls, is_setup):
        if onBlendLoaded in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(onBlendLoaded)
            print("Unregister handler for blend load gmic")
        if is_setup:
            bpy.app.handlers.load_post.append(onBlendLoaded)
            print("Register handler for blend load gmic")

    @classmethod
    def _add(cls, context:bpy.types.Context, reportFunc): #override
        # Step 1. Get program path and check if save blend file.
        gmic_qt_path = getGmicQTPath()

        if gmic_qt_path == '':
            reportFunc({'ERROR'}, "Please set gmic qt program in the preferences window.")
            return False

        gmic_qt_path = os.path.realpath(gmic_qt_path)

        if not os.path.exists(gmic_qt_path):
            reportFunc({'ERROR'}, "Unable to detect gmic_qt.exe for path \"%s\""%gmic_qt_path)
            return False

        if not bpy.data.is_saved:
            reportFunc({'ERROR'}, "Please save this blend file to setup a cache folder.")
            return False

        # Step 2. Get current frame image
        renderfn = renderPreview()

        # Step 3. Run g'mic qt program

        outputfn = os.path.realpath("output.%s"%gmic_output_suffix)
        process = subprocess.Popen("%s --output \"%s\" \"%s\""%(gmic_qt_path, outputfn, renderfn), stdout=subprocess.PIPE)
        if "Writing output file" not in bytes.decode(process.stdout.read()):
            reportFunc({'ERROR'}, "Something wrong with gmic-qt.")
            return False

        # Step 4. Fetch user settings in g'mic
        commands = fetchCommandFromGmic()
        command = commands["Command"]
        name = commands["Name"]

        if command == "":
            print("No effect apply")
            return False

        # Step 5. Setup richstrip

        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect : RichStripEffect = data.addEffect(cls.getName())
        cls.add(context, richstrip, data, effect) # run stages functions. all properties will be defined in this function.

        # Step 6. Setup cache dir
        cacheId = cls.getStrProperty(effect, "uuid").value
        gmicCache = getCacheDir()
        print("cacheId:", cacheId)
        cachedir = bpy.path.abspath("%s//%s"%(gmicCache, cacheId))
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        # Step 7. The preview image rendered in step 2 can be reused.

        offset = context.scene.frame_current - richstrip.frame_final_start
        target = bpy.path.abspath("%s//%s//%d.%s"%(gmicCache, cacheId, offset, gmic_output_suffix))
        shutil.copy("output.%s"%gmic_output_suffix, target)
        print("copy to ", target)

        # Step 8. Set Properties.
        cls.getStrProperty(effect, "parameters").value = command
        cls.getStrProperty(effect, "fxname").value = name

        return True

    def stage_PropertyDefination(self):
        self.addStrProperty(self.effect, "parameters")
        self.addStrProperty(self.effect, "fxname")
        self.addStrProperty(self.effect, "uuid", uuid.uuid4().hex)

    def stage_SequenceDefination(self, relinkStage:bool):
        if relinkStage:
            # TODO: finish relink stage for g'mic
            # Step 1. fetch new cacheId
            self.getStrProperty(self.effect, "uuid").value = uuid.uuid4().hex
            # Step 2. change location of image strip
            # ...
            # Step 3. copy cache dir
            # ...
            return
            
        movieseq = self.getMovieStrip(self.richstrip)
        cacheId = self.getStrProperty(self.effect, "uuid").value
        effectlayer = self.addBuiltinImageStrip("gmicCache", bpy.path.abspath("%s//%s"%(getCacheDir(), cacheId)), [{
            "name": "%d.%s"%(i, gmic_output_suffix)
        } for i in range(movieseq.frame_final_duration)])

        self.addBuiltinEffectStrip('ADJUSTMENT', "adjust")

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

        layout.label(text="name:"+cls.getStrProperty(effect, "fxname").value)
        layout.label(text="command:"+cls.getStrProperty(effect, "parameters").value)
        layout.label(text="id:"+cls.getStrProperty(effect, "uuid").value)

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