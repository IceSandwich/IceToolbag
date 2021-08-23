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
        # print(cls.getName() + " `add` function is not implemented yet.")
        cls.enterEditMode(richstrip)
        
        # call chain
        instance = object.__new__(cls)
        instance.__dict__["richstrip"] = richstrip
        instance.__dict__["effect"] = effect
        instance.__dict__["data"] = data
        instance.stage_Before()
        instance.stage_PropertyDefination()
        instance.stage_SequenceDefination()
        instance.stage_BinderDefination()

        cls.leaveEditMode(data)
        instance.stage_After()
        return

    def stage_Before(self):
        richstrip.sequences.get(data.Effects[-2].EffectStrips[-1].value).select = True
    def stage_PropertyDefination(self):
        return
    def stage_SequenceDefination(self):
        return
    def stage_BinderDefination(self):
        return
    def stage_After(self):
        return



    @classmethod
    def _update(cls, _type, identify, context):
        richstrip = context.selected_sequences[0]
        if type(richstrip) != bpy.types.MetaSequence: # some bug i don't know how to occur, just check if meta to solve right now.
            return
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        if cls.update(_type, identify, context, data, effect, richstrip):
            bpy.ops.sequencer.refresh_all()

    @classmethod
    def update(cls, type, identify, context, data, effect, richstrip):
        print(cls.getName() + " `update` function is not implemented yet.")
        return False

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
    def _relink(cls, context, richstrip, suffix, index, oldrsid):
        effect = richstrip.IceTB_richstrip_data.Effects[index]
        oldrsid_len = len("rs%d-"%oldrsid)
        newrsid = "rs%d-"%richstrip.RichStripID
        for stripName in effect.EffectStrips:
            richstrip.sequences.get(stripName).name = newrsid + stripName[oldrsid_len:]
        cls.relink(context, richstrip, effect)

    @classmethod
    def relink(cls, context, richstrip, effect):
        # print(cls.getName() + " `relink` function is not implemented yet.")
        instance = object.__new__(cls)
        instance.__dict__["richstrip"] = richstrip
        instance.__dict__["effect"] = effect
        instance.stage_BinderDefination()
        return    



    ################################################################
    ##   controller functions
    ################################################################

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




    ################################################################
    ##   get strip functions (utils)
    ################################################################

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




    ################################################################
    ##   add strip functions
    ################################################################

    @classmethod
    def addBuiltinEffectStrip(cls, context, richstrip, rseffect, effectType, effectName):
        data = richstrip.IceTB_richstrip_data
        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type=effectType, frame_start=richstrip.frame_final_start, frame_end=richstrip.frame_final_end, channel=data.EffectCurrentMaxChannel1)
        effectlayer = context.scene.sequence_editor.active_strip
        effectlayer.name = cls.genRegularStripName(data.RichStripID, rseffect.EffectId, effectName)
        rseffect.EffectStrips.add().value = effectlayer.name
        return effectlayer




    ################################################################
    ##   add property functions
    ################################################################

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
    def addPropertyWithBinding(cls, context, targetSeq, targetPropName, binderName, binderVars, binderExpression, storedSeq=None, numRange=(-100000, 100000), defaultValue=0, description=""):
        """ Example
        targetSeq(seq): rs1-movie
        targetPropName(string): transform.pos_x
        binderName(string): pos_x
        binderVar(list): [{ name: "flip", seqName: "rs1-movie", seqProp: "use_flip_x", isCustomProp: False }]
        binderExpression(string): 'bind * (-1 if flip == 1 else 1)'
        storedSeq(seq): rs1-movie
        """
        if storedSeq is None:
            storedSeq = targetSeq
        propParts = targetPropName.split('.') # make `targetSeq` to `rs1-movie.transform` and `targetPropName` to `pos_x`
        for x in propParts[:-1]:
            targetSeq = getattr(targetSeq, x)
        targetPropName = propParts[-1]

        # create binder(custom property)
        storedSeq[binderName] = defaultValue
        # TODO: the following command will popup a windows which we don't want. How to fix it? Just wanna set description and number range.
        # bpy.ops.wm.properties_edit("INVOKE_DEFAULT", data_path='scene.sequence_editor.sequences_all["%s"]'%storedSeq.name, property=binderName, value=str(defaultValue), default=str(defaultValue), min=numRange[0], max=numRange[1], is_overridable_library=True, description=description, subtype="NONE")
        
        # create a driver for target property and link to binder
        driver = targetSeq.driver_add(targetPropName).driver
        for binderVar in binderVars:
            var = driver.variables.new()
            var.name = binderVar["name"]
            var.targets[0].id_type = 'SCENE'
            var.targets[0].id = context.scene
            if 'globalProp' in binderVar:
                var.targets[0].data_path = binderVar["globalProp"]
            else:
                var.targets[0].data_path = 'sequence_editor.sequences_all["%s"]%s%s%s'%(binderVar["seqName"], '["' if binderVar["isCustomProp"] else '.', binderVar["seqProp"], '"]' if binderVar["isCustomProp"] else "")
        # create `bind` variable for the driver
        var = driver.variables.new()
        var.name = 'bind'
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = context.scene
        var.targets[0].data_path = 'sequence_editor.sequences_all["%s"]["%s"]'%(storedSeq.name, binderName)
        driver.use_self = True
        driver.expression = binderExpression

    @classmethod
    def addFloatProperty(cls, effect, floatName, floatDefault=0.0):
        cls.addBaseProperty(effect, "Float", effect.EffectFloatProperties, floatName, floatDefault)

    @classmethod
    def addBoolProperty(cls, effect, boolName, boolDefault=False):
        cls.addBaseProperty(effect, "Bool", effect.EffectBoolProperties, boolName, boolDefault)




    ################################################################
    ##   generate string/path functions (utils)
    ################################################################

    @classmethod
    def genbinderName(cls, effect, name, withPropModifier=False):
        """
            get custom property data_path in meta strip / movie strip ... etc
        """
        # if withPropModifier:
            # return '["%s/%s"]'%(effect.EffectName, name)
        # return "%s/%s"%(effect.EffectName, name)
        if withPropModifier:
            return '["%s"]'%name
        return "%s"%name

    @classmethod
    def genseqProp(cls, effect, propType, propName):
        """
            get property data_path in IceTB_richstrip_data structure
        """
        propIndex = cls.getBaseProperty(effect, propType, propName, retValue=False)
        return "IceTB_richstrip_data.Effects[%d].Effect%sProperties[%d].value"%(effect.EffectIndex, propType, propIndex)

    @classmethod
    def genRegularStripName(cls, rsid, effectid, descrip):
        return "rs%d-%s%d/%s"%(rsid, cls.getName(), effectid, descrip)




    ################################################################
    ##   get property functions
    ################################################################

    @classmethod
    def getBaseProperty(cls, effect, propType, propName, retValue=True):
        """
            propType: one of ['Bool', 'Enum', 'Float', 'Int']
            propName: prop String name
            ret: return property value if retValue is True, otherwise only return the index of property
        """
        assert(['Bool', 'Enum', 'Float', 'Int'].index(propType) != -1)
        propInstance = getattr(effect, "Effect%sProperties"%propType)
        propindex = json.loads(effect.EffectMappingJson)[propType][propName]
        assert(propindex is not None)
        if not retValue:
            return propindex
        return propInstance[propindex]

    @classmethod
    def getEnumProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, "Enum", propName)

    @classmethod
    def getIntProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Int', propName)

    @classmethod
    def getFloatProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Float', propName)
        
    @classmethod
    def getBoolProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Bool', propName)