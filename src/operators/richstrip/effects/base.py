import bpy
import json

class EffectBase():
    @classmethod
    def getName(cls):
        """
            Effect type name. Not the name of effect.
        """
        return "Untitled Effect"

    @classmethod
    def _add(cls, context):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.addEffect(cls.getName())
        cls.add(context, richstrip, data, effect)

    @classmethod
    def add(cls, context, richstrip, data, effect):
        print(cls.getName() + " `add` function is not implemented yet.")
        return

    @classmethod
    def _update(cls, _type, identify, context):
        richstrip = context.selected_sequences[0]
        if type(richstrip) != bpy.types.MetaSequence: # some bug i don't know how to occur, just check if meta to solve right now.
            return
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        cls.update(_type, identify, context, data, effect, richstrip)
        bpy.ops.sequencer.refresh_all()

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        print(cls.getName() + " `update` function is not implemented yet.")
        return

    @classmethod
    def _draw(cls, context, layout):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        cls.draw(context, layout, data, effect, richstrip)

    @classmethod
    def draw(cls, context, layout, data, effect, richstrip):
        print(cls.getName() + " `draw` function is not implemented yet.")
        return

    @classmethod
    def enterEditMode(cls, richstrip):
        data = richstrip.IceTB_richstrip_data
        richstrip.select = True
        bpy.ops.sequencer.meta_toggle() # enter meta strip
        bpy.ops.sequencer.select_all(action='DESELECT')
        # TODO: if audiolayer is none, return movielayer frame start and end
        # return richstrip.sequences, richstrip.frame_final_start, richstrip.frame_final_end

    @classmethod
    def leaveEditMode(cls, data=None):
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave meta strip
        if data is not None:
            data.EffectsCurrent = len(data.Effects) - 1

    @classmethod
    def genRegularStripName(cls, rsid, effectid, descrip):
        return "rs%d-%s%d/%s"%(rsid, cls.getName(), effectid, descrip)

    @classmethod
    def getEffectStrip(cls, richstrip, effectName):
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        return richstrip.sequences.get(cls.genRegularStripName(data.RichStripID, effect.EffectId, effectName))

    @classmethod
    def getMovieStrip(cls, richstrip):
        data = richstrip.IceTB_richstrip_data
        return richstrip.sequences.get("rs%d-movie"%data.RichStripID)
    
    @classmethod
    def getAudioStrip(cls, richstrip):
        data = richstrip.IceTB_richstrip_data
        return richstrip.sequences.get("rs%d-audio"%data.RichStripID)

    ## utils

    @classmethod
    def addBuiltinEffectStrip(cls, context, richstrip, rseffect, effectType, effectName):
        data = richstrip.IceTB_richstrip_data
        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type=effectType, frame_start=richstrip.frame_final_start, frame_end=richstrip.frame_final_end, channel=data.EffectCurrentMaxChannel1)
        effectlayer = context.scene.sequence_editor.active_strip
        effectlayer.name = cls.genRegularStripName(data.RichStripID, rseffect.EffectId, effectName)
        rseffect.EffectStrips.add().value = effectlayer.name
        return effectlayer


    @classmethod
    def addBaseProperty(cls, effect, propType, propInstance, propName, propValue):
        ret = propInstance.add()
        ret.initForEffect(cls.getName(), propName, propValue)
        mapping = json.loads(effect.EffectMappingJson)
        mapping[propType][propName] = len(propInstance)-1
        effect.EffectMappingJson = json.dumps(mapping)
        return ret

    @classmethod
    def addEnumProperty(cls, effect, enumName, enumData=[]):
        enumprop = cls.addBaseProperty(effect, "Enum", effect.EffectEnumProperties, enumName, None)
        for x in enumData:
            enumprop.items.add().value = x

    @classmethod
    def addIntProperty(cls, effect, intName, intDefault=0):
        cls.addBaseProperty(effect, "Int", effect.EffectIntProperties, intName, intDefault)

    @classmethod
    def addFloatProperty(cls, effect, floatName, floatDefault=0.0):
        cls.addBaseProperty(effect, "Float", effect.EffectFloatProperties, floatName, floatDefault)

    @classmethod
    def addBoolProperty(cls, effect, boolName, boolDefault=False):
        cls.addBaseProperty(effect, "Bool", effect.EffectBoolProperties, boolName, boolDefault)

    @classmethod
    def getBaseProperty(cls, effect, propType, propInstance, propName):
        propindex = json.loads(effect.EffectMappingJson)[propType][propName]
        assert(propindex is not None)
        return propInstance[propindex]

    @classmethod
    def getEnumProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, "Enum", effect.EffectEnumProperties, propName)

    @classmethod
    def getIntProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Int', effect.EffectIntProperties, propName)

    @classmethod
    def getFloatProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Float', effect.EffectFloatProperties, propName)
        
    @classmethod
    def getBoolProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Bool', effect.EffectBoolProperties, propName)