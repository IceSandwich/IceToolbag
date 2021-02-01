import bpy
from ..datas.string_prop import StringProperty
from ..datas.int_prop import IntProperty

class RichStripEffect(bpy.types.PropertyGroup):
    EffectName: bpy.props.StringProperty(name="The name of effect", default="Untitled effect")
    EffectType: bpy.props.StringProperty(name="The type of effect", default="Untitled type")

    EffectIndex: bpy.props.IntProperty(name="The index of effect in list", default=-1)
    EffectId: bpy.props.IntProperty(name="Unique id of effect", default=-1)

    # the following are what you need to parse in operator func.

    EffectStrips: bpy.props.CollectionProperty(type=StringProperty)

    EffectStrProperties: bpy.props.CollectionProperty(type=StringProperty)
    EffectIntProperties: bpy.props.CollectionProperty(type=IntProperty)

class RichStripData(bpy.types.PropertyGroup):
    # RichStrip information
    IsRichStrip: bpy.props.BoolProperty(name="Is it an rich strip?", default=False)

    # Strip information
    MovieName: bpy.props.StringProperty(name="Movie Strip Name", default="Untitled name")
    AudioName: bpy.props.StringProperty(name="Audio Strip Name", default="Untitled name")
    # AdjustName: bpy.props.StringProperty(name="Adjust Strip Name", default="Untitled name")
    HasAudio: bpy.props.BoolProperty(name="If this rich strip contains audio", default=False)

    # Movie Strip information
    ResolutionWidth: bpy.props.IntProperty(name="Width of movie", default=-1)
    ResolutionHeight: bpy.props.IntProperty(name="Height of movie", default=-1)
    Fps: bpy.props.FloatProperty(name="FPS of movie", default=0.0) # we cannot modify the fps of audio so we don't need that

    # Effect inforamtion
    Effects: bpy.props.CollectionProperty(type=RichStripEffect)
    EffectsCurrent: bpy.props.IntProperty(name="Current Effect Index", default=0)

    # Effect Global inforamtion
    EfeectsCounter: bpy.props.IntProperty(name="The counter of effects layer for uid", default=0)
    EffectCurrentMaxChannel1: bpy.props.IntProperty(name="The current max channel in effect, modify by effect", default=3)
    EffectCurrentMaxChannel2: bpy.props.IntProperty(name="The current max channel in effect, modify by effect", default=1)

    @classmethod
    def setupProperty(cls, is_setup):
        from bpy.types import Sequence as sequence
        if is_setup:
            sequence.IceTB_richstrip_data = bpy.props.PointerProperty(type=RichStripData)
            print("Property defined")
        else:
            sequence.IceTB_richstrip_data = None
            print("Property uninstalled")

    @classmethod
    def initProperty(cls, richstrip, moviestrip, audiostrip=None):
        if richstrip.type != 'META':
            # wrong sequence type
            # TODO: add more vaildate
            return False
        
        richstrip.IceTB_richstrip_data.MovieName = moviestrip.name
        # richstrip.IceTB_richstrip_data.AdjustName = adjuststrip.name
        if audiostrip is None:
            richstrip.IceTB_richstrip_data.HasAudio = False
        else:
            richstrip.IceTB_richstrip_data.HasAudio = True
            richstrip.IceTB_richstrip_data.AudioName = audiostrip.name

        richstrip.IceTB_richstrip_data.ResolutionWidth = moviestrip.elements[0].orig_width
        richstrip.IceTB_richstrip_data.ResolutionHeight = moviestrip.elements[0].orig_height
        richstrip.IceTB_richstrip_data.Fps = moviestrip.fps
        richstrip.IceTB_richstrip_data.EffectsCurrent = 0
        richstrip.IceTB_richstrip_data.Effects.clear()

        richstrip.IceTB_richstrip_data.IsRichStrip = True

        bpy.ops.icetb.richstrip_addeffect('EXEC_DEFAULT', effectName = "Original")
        return True

    @classmethod
    def checkProperty(cls, ctx, seq):
        return ('IceTB_richstrip_data' in dir(seq) and seq.IceTB_richstrip_data is not None and seq.IceTB_richstrip_data.IsRichStrip == True)

    @classmethod
    def getProperty(cls, seq):
        return seq.IceTB_richstrip_data

    def addEffect(self, effectType):
        effect = self.Effects.add()
        effect.EffectType = effectType
        effect.EffectIndex = len(self.Effects)
        effect.EffectId = self.EfeectsCounter
        effect.EffectName = effectType + "_" + str(effect.EffectId)
        self.EfeectsCounter += 1
        return effect
    
    def getSelectedEffect(self):
        return self.Effects[self.EffectsCurrent]

    def getSelectedEffectType(self):
        return self.getSelectedEffect().EffectType

    def getSelectedId(self):
        return self.getSelectedEffect().EffectId
