import bpy
from ..datas.string_prop import StringProperty
from ..datas.int_prop import IntProperty
from ..datas.enum_prop import EnumProperty
from ..datas.float_prop import FloatProperty
from ..datas.bool_prop import BoolProperty

class RichStripColorEffect(bpy.types.PropertyGroup):
    EffectName: bpy.props.StringProperty(name="The name of effect", default="Untitled effect")
    EffectType: bpy.props.StringProperty(name="The type of effect", default="Untitled type")

    EffectIndex: bpy.props.IntProperty(name="The index of effect in list", default=-1)
    EffectId: bpy.props.IntProperty(name="Unique id of effect", default=-1)

    # the following are what you need to parse in operator func.

    EffectStrips: bpy.props.StringProperty(name="The name of strip")

    EffectStrProperties: bpy.props.CollectionProperty(type=StringProperty)
    EffectIntProperties: bpy.props.CollectionProperty(type=IntProperty)
    EffectFloatProperties: bpy.props.CollectionProperty(type=FloatProperty)
    EffectEnumProperties: bpy.props.CollectionProperty(type=EnumProperty)
    EffectBoolProperties: bpy.props.CollectionProperty(type=BoolProperty)

class RichStripEffect(bpy.types.PropertyGroup):
    EffectName: bpy.props.StringProperty(name="The name of effect", default="Untitled effect")
    EffectType: bpy.props.StringProperty(name="The type of effect", default="Untitled type")

    EffectIndex: bpy.props.IntProperty(name="The index of effect in list", default=-1)
    EffectId: bpy.props.IntProperty(name="Unique id of effect", default=-1)
    EffectInputId: bpy.props.IntProperty(name="Effect input effect in index", default=-1)

    EffectColor: bpy.props.CollectionProperty(type=RichStripColorEffect)
    EffectColorCurrent: bpy.props.IntProperty(name="Current Color Effect Index", default=0)

    EffectAfterEffect: bpy.props.CollectionProperty(type=RichStripColorEffect)
    # EffectAfterEffect_ScaleBoolProperty: bpy.props.BoolProperty(name="For AE Scale look", default=False) # TODO
    EffectAECurrent: bpy.props.IntProperty(name="Current After Effect Index", default=0)

    # the following are what you need to parse in operator func.

    EffectStrips: bpy.props.CollectionProperty(type=StringProperty)

    EffectStrProperties: bpy.props.CollectionProperty(type=StringProperty)
    EffectIntProperties: bpy.props.CollectionProperty(type=IntProperty)
    EffectFloatProperties: bpy.props.CollectionProperty(type=FloatProperty)
    EffectEnumProperties: bpy.props.CollectionProperty(type=EnumProperty)
    EffectBoolProperties: bpy.props.CollectionProperty(type=BoolProperty)
    EffectMappingJson: bpy.props.StringProperty(name="Mapping property name to index", default='{"Str":{},"Int":{},"Float":{},"Enum":{},"Bool":{}}')

class RichStripData(bpy.types.PropertyGroup):
    # RichStrip information
    IsRichStrip: bpy.props.BoolProperty(name="Is it an rich strip?", default=False)
    RichStripID: bpy.props.IntProperty(name="The unique id for rich strip", default=-1)

    # Strip information
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
    # EffectCurrentMaxChannel2: bpy.props.IntProperty(name="The current max channel in effect, modify by effect", default=1) #abandon

    @classmethod
    def genRichStripId(cls, ctx):
        ctx.scene.IceTB_richstrip_gen_richstripid = ctx.scene.IceTB_richstrip_gen_richstripid + 1
        return ctx.scene.IceTB_richstrip_gen_richstripid
        
    @classmethod
    def setupProperty(cls, is_setup):
        from bpy.types import Sequence as sequence
        from bpy.types import Scene as scene
        if is_setup:
            sequence.IceTB_richstrip_data = bpy.props.PointerProperty(type=RichStripData)
            scene.IceTB_richstrip_gen_richstripid = bpy.props.IntProperty(name="The id generator for rich strip", default=0)
            print("Property defined")
        else:
            sequence.IceTB_richstrip_data = None
            print("Property uninstalled")

    @classmethod
    def initProperty(cls, richstrip, rsid, moviestrip, audiostrip=None):
        if richstrip.type != 'META':
            # wrong sequence type
            # TODO: add more vaildate
            return False

        richstrip.IceTB_richstrip_data.IsRichStrip = True
        richstrip.IceTB_richstrip_data.RichStripID = rsid

        # richstrip.IceTB_richstrip_data.AdjustName = adjuststrip.name
        if audiostrip is None:
            richstrip.IceTB_richstrip_data.HasAudio = False
        else:
            richstrip.IceTB_richstrip_data.HasAudio = True

        richstrip.IceTB_richstrip_data.ResolutionWidth = moviestrip.elements[0].orig_width
        richstrip.IceTB_richstrip_data.ResolutionHeight = moviestrip.elements[0].orig_height
        richstrip.IceTB_richstrip_data.Fps = moviestrip.fps

        richstrip.IceTB_richstrip_data.Effects.clear()
        richstrip.IceTB_richstrip_data.EffectsCurrent = 0

        bpy.ops.icetb.richstrip_addeffect('EXEC_DEFAULT', effectName = "Original")
        return True

    @classmethod
    def checkProperty(cls, ctx, seq):
        return (hasattr(seq, 'IceTB_richstrip_data') and seq.IceTB_richstrip_data is not None and seq.IceTB_richstrip_data.IsRichStrip == True)

    @classmethod
    def getProperty(cls, seq):
        return seq.IceTB_richstrip_data

    def addEffect(self, effectType):
        effect = self.Effects.add()
        effect.EffectType = effectType
        effect.EffectIndex = len(self.Effects)
        if effectType == "Copy":
            effect.EffectInputId = self.EffectsCurrent
        else:
            effect.EffectInputId = -1
        effect.EffectId = self.EfeectsCounter
        effect.EffectName = effectType + "_" + str(effect.EffectId)
        self.EfeectsCounter += 1
        return effect
    
    def getSelectedEffect(self):
        return self.Effects[self.EffectsCurrent]

    def getLastEffect(self):
        return self.Effects[len(self.Effects)-1]

    def getSelectedEffectType(self):
        return self.getSelectedEffect().EffectType

    def getSelectedId(self):
        return self.getSelectedEffect().EffectId
