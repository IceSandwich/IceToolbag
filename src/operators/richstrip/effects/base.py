import bpy
import json
from ....datas.richstrip import RichStripData, RichStripEffect

class EffectBase():
    NUMRANGE_MAX = 1000000000.0

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

        return True

    @classmethod
    def add(cls, context, richstrip, data, effect):
        # print(cls.getName() + " `add` function is not implemented yet.")
        cls.enterEditMode(richstrip)
        
        # call chain
        instance = object.__new__(cls)
        instance.__dict__["richstrip"] = richstrip
        instance.__dict__["effect"] = effect
        instance.__dict__["data"] = data
        instance.__dict__["context"] = context
        instance.stage_Before()
        instance.stage_PropertyDefination()
        instance.stage_SequenceDefination(relinkStage=False)
        instance.stage_BinderDefination()

        cls.leaveEditMode(data)
        instance.stage_After()
        return

    def stage_Before(self):
        self.richstrip.sequences.get(self.data.Effects[-2].EffectStrips[-1].value).select = True
    def stage_PropertyDefination(self):
        return
    def stage_SequenceDefination(self, relinkStage):
        return
    def stage_BinderDefination(self):
        return
    def stage_After(self):
        return



    @classmethod
    def _update(cls, _type:str, identify:str, context):
        richstrip = context.selected_sequences[0]
        if type(richstrip) != bpy.types.MetaSequence: # some bug i don't know how to occur, just check if meta to solve right now.
            return
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()

        # deal with '_export' varible
        if _type == 'BOOL' and identify.endswith("_export"):
            mapping = json.loads(effect.EffectMappingJson)["Export"][identify]
            seq = cls.getEffectStrip(richstrip, effect, mapping[0])
            attrName = cls.genbinderName(effect, mapping[1], True) if mapping[2] else mapping[1] # mapping[2]: iscustomprop

            if cls.getBoolProperty(effect, identify).value: # add driver
                cls.exportTo(context, richstrip, attrName, seq)
            else: # remove driver
                cls.exportToReverse(context, richstrip, attrName, seq)

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
        newrsid = "rs%d-"%richstrip.IceTB_richstrip_data.RichStripID

        for stripName in effect.EffectStrips:
            newName = newrsid + stripName.value[oldrsid_len:]
            seq = richstrip.sequences.get(stripName.value+suffix)
            if seq is None:
                seq = context.scene.sequence_editor.sequences_all.get(stripName.value+suffix)
            seq.name = newName
            stripName.value = newName

            for modifier_oldname, modifier in seq.modifiers.items():
                modifier.name = newrsid + modifier.name[oldrsid_len:]
        cls.relink(context, richstrip, effect)

    @classmethod
    def relink(cls, context, richstrip, effect):
        # print(cls.getName() + " `relink` function is not implemented yet.")
        instance = object.__new__(cls)
        instance.__dict__["richstrip"] = richstrip
        instance.__dict__["effect"] = effect
        instance.__dict__["data"] = richstrip.IceTB_richstrip_data
        instance.__dict__["context"] = context
        instance.stage_SequenceDefination(relinkStage=True)
        instance.stage_BinderDefination()
        return    



    ################################################################
    ##   controller functions
    ################################################################

    @classmethod
    def enterEditMode(cls, richstrip):
        # data = richstrip.IceTB_richstrip_data
        richstrip.select = True
        bpy.context.scene.sequence_editor.active_strip = richstrip
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
    def getEffectStrip(cls, richstrip, effect, effectName) -> bpy.types.AdjustmentSequence:
        data = richstrip.IceTB_richstrip_data
        seqname = cls.genRegularStripName(data.RichStripID, effect.EffectId, effectName)
        ret = richstrip.sequences.get(seqname)
        if ret is None:
            return bpy.context.scene.sequence_editor.sequences_all.get(seqname)
        return ret

    @classmethod
    def getMovieStrip(cls, richstrip) -> bpy.types.MovieClipSequence:
        data = richstrip.IceTB_richstrip_data
        return richstrip.sequences.get("rs%d-movie"%data.RichStripID)
    
    @classmethod
    def getAudioStrip(cls, richstrip) -> bpy.types.SoundSequence:
        data = richstrip.IceTB_richstrip_data
        return bpy.context.scene.sequence_editor.sequences_all.get("rs%d-audio"%data.RichStripID)

    @classmethod
    def getSubdriesStrip(cls, richstrip) -> bpy.types.MetaSequence:
        data = richstrip.IceTB_richstrip_data
        return bpy.context.scene.sequence_editor.sequences_all.get("rs%d-subdries"%data.RichStripID)





    ################################################################
    ##   add strip functions
    ################################################################

    @classmethod
    def addBuiltinEffectStrip(cls, context, richstrip, rseffect, effectType, effectName):
        """
            return exists strip if already created.
        """
        data = richstrip.IceTB_richstrip_data
        stripName = cls.genRegularStripName(data.RichStripID, rseffect.EffectId, effectName)
        seq = richstrip.sequences.get(stripName)
        if seq is not None:
            return seq
        data.EffectCurrentMaxChannel1 += 1
        bpy.ops.sequencer.effect_strip_add(type=effectType, frame_start=richstrip.frame_final_start, frame_end=richstrip.frame_final_end, channel=data.EffectCurrentMaxChannel1)
        effectlayer = context.scene.sequence_editor.active_strip
        effectlayer.name = stripName
        rseffect.EffectStrips.add().value = effectlayer.name
        return effectlayer
    def addBuiltinStrip(self, effectType, effectName): # for instance function
        return self.addBuiltinEffectStrip(self.context, self.richstrip, self.effect, effectType, effectName)
    @classmethod
    def addMaskStripInSubdries(cls, effect:RichStripEffect, data:RichStripData, maskName):
        cls.enterEditMode(richstrip)
        subdries = cls.getSubdriesStrip(richstrip)
        cls.enterEditMode(subdries)
        bpy.ops.sequencer.mask_strip_add(frame_start=richstrip.frame_final_start, channel=1, mask=maskName)
        maskSeq = context.scene.sequence_editor.active_strip
        maskSeq.name = cls.genRegularStripName(data.RichStripID, effect.EffectId, "mask_"+maskName)
        maskSeq.mute = True
        cls.leaveEditMode()
        cls.leaveEditMode()





    ################################################################
    ##   binding / driver helper
    ################################################################

    @classmethod
    def addPropertyWithDriver(cls, context, targetSeq, targetPropName, driverVars, dirverExpression):
        driver = targetSeq.driver_add(targetPropName).driver
        for driverVar in driverVars:
            var = driver.variables.new()
            var.name = driverVar["name"]
            var.targets[0].id_type = 'SCENE'
            var.targets[0].id = context.scene
            if 'globalProp' in driverVar:
                var.targets[0].data_path = driverVar["globalProp"]
            else:
                var.targets[0].data_path = 'sequence_editor.sequences_all["%s"]%s%s%s'%(driverVar["seqName"], '["' if driverVar["isCustomProp"] else '.', driverVar["seqProp"], '"]' if driverVar["isCustomProp"] else "")
        driver.use_self = True
        driver.expression = dirverExpression
    
    @classmethod
    def getSeqOrPathUsingPath(cls, deepSeq, pathSplit, returnPath=False):
        path = ""
        for x in pathSplit: 
            if x.startswith('modifiers["'): #modifiers["rs2-BrightContrast8/bc"].bright
                x = x[len('modifiers["'): x.index('"]')]
                deepSeq = deepSeq.modifiers
                path += ".modifiers"

            if type(deepSeq) == bpy.types.bpy_prop_collection:
                deepSeq = deepSeq.get(x)
                path += '["%s"]'%x
            else:
                deepSeq = getattr(deepSeq, x)
                path += ".%s"%x
        return path if returnPath else deepSeq

    @classmethod
    def addPropertyWithBinding_ClassLevel(cls, context, targetSeq, targetPropName, binderName, binderVars, binderExpression, storedSeq=None, numRange=(-NUMRANGE_MAX, NUMRANGE_MAX), defaultValue=0, description=""):
        """ Example:
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

        targetSeq = cls.getSeqOrPathUsingPath(targetSeq, propParts[:-1])
        targetPropName = propParts[-1]

        # create binder(custom property) if doesn't exist
        if storedSeq.get(binderName) is None:
            storedSeq[binderName] = defaultValue
            if storedSeq.get("_RNA_UI") == None:
                storedSeq["_RNA_UI"] = {}
            storedSeq["_RNA_UI"].update({
                binderName: {
                    # "name": "",
                    "min": numRange[0],
                    "max": numRange[1],
                    "soft_min": numRange[0],
                    "soft_max": numRange[1],
                    "description": description,
                    "default": defaultValue
                }
            })
        
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
    def addPropertyWithBinding(self, targetSeq, targetPropName, binderName, binderVars, binderExpression, storedSeq=None, numRange=(-100000, 100000), defaultValue=0, description=""):
        self.addPropertyWithBinding_ClassLevel(self.context, targetSeq, targetPropName, self.genbinderName(self.effect, binderName), binderVars, binderExpression, storedSeq=storedSeq, numRange=numRange, defaultValue=defaultValue, description=description)





    ################################################################
    ##   add property functions
    ################################################################

    @classmethod
    def addBaseProperty(cls, effect, propType, propInstance, propName, propValue):
        ret = propInstance.add()
        ret.initForEffect("RichStrip", cls.getName(), propName, propValue)
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
    def addColorProperty(cls, effect, colorName, colorDefault=(0, 0, 0)):
        cls.addBaseProperty(effect, "Color", effect.EffectColorProperties, colorName, colorDefault)
    @classmethod
    def addStrProperty(cls, effect, strName, strDefault=""):
        cls.addBaseProperty(effect, "Str", effect.EffectStrProperties, strName, strDefault)
    @classmethod
    def addBoolProperty(cls, effect, boolName, boolDefault=False):
        cls.addBaseProperty(effect, "Bool", effect.EffectBoolProperties, boolName, boolDefault)
    @classmethod
    def addExportProperty(cls, effect, data): # add a batch of bool properties with '_export' suffix.
        """
        data: [
            [ "AttrName", "SeqName", "SeqAttr", IsCustomProp? ]
        ]
        """
        mapping = json.loads(effect.EffectMappingJson)

        for package in data:
            exportName = "%s_export"%package[0]

            # add bool property
            ret = effect.EffectBoolProperties.add()
            ret.initForEffect("RichStrip", cls.getName(), exportName, False)
            mapping["Bool"][exportName] = len(effect.EffectBoolProperties)-1

            mapping["Export"][exportName] = [package[1], package[2], package[3]]

        effect.EffectMappingJson = json.dumps(mapping)



    ################################################################
    ##   generate string/path functions (utils)
    ################################################################

    @classmethod
    def genbinderName(cls, effect, name, withPropModifier=False):
        """
            get custom property data_path in meta strip / movie strip ... etc
        """
        if withPropModifier:
            return '["%s/%s"]'%(effect.EffectName, name)
        return "%s/%s"%(effect.EffectName, name)
        # if withPropModifier:
        #     return '["%s"]'%name
        # return "%s"%name

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
            propType: one of ['Bool', 'Enum', 'Float', 'Int', 'Color', 'Str']
            propName: prop String name
            ret: return property value if retValue is True, otherwise only return the index of property
        """
        #assert(['Bool', 'Enum', 'Float', 'Int', 'Color', 'Str'].index(propType) != -1)
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
    @classmethod
    def getColorProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Color', propName)
    @classmethod
    def getStrProperty(cls, effect, propName):
        return cls.getBaseProperty(effect, 'Str', propName)

    



    ################################################################
    ##   export driver functions
    ################################################################
    @classmethod
    def exportTo(cls, context, richstrip, attrName, targetSeq):
        effect = richstrip.IceTB_richstrip_data.getSelectedEffect()

        isBinding = attrName[:2] == '["'
        attrNameWithoutModifier = attrName.replace('["', '').replace('"]', '')

        if isBinding:
            val = targetSeq[attrNameWithoutModifier]
            data_path = 'sequence_editor.sequences_all["%s"]%s'%(targetSeq.name, attrName)
        else:
            attrSplit = attrNameWithoutModifier.split('.')
            val = cls.getSeqOrPathUsingPath(targetSeq, attrSplit)

            attrNameWithoutModifier = cls.genbinderName(effect, attrSplit[-1], False) # new name
            data_path = 'sequence_editor.sequences_all["%s"]%s'%(targetSeq.name, cls.getSeqOrPathUsingPath(targetSeq, attrSplit, returnPath=True))


        richstrip[attrNameWithoutModifier] = val
        if richstrip.get("_RNA_UI") == None: richstrip["_RNA_UI"] = {}
        if isBinding:
            if targetSeq.get("_RNA_UI"):
                targetProperty = targetSeq["_RNA_UI"].get(attrNameWithoutModifier)
                richstrip["_RNA_UI"].update({
                    attrNameWithoutModifier: {
                        # "name": "",
                        "min": targetProperty["min"],
                        "max": targetProperty["max"],
                        "soft_min": targetProperty["soft_min"],
                        "soft_max": targetProperty["soft_max"],
                        "description": targetProperty["description"],
                        "default": targetProperty["default"]
                    }
                })
        else:
            richstrip["_RNA_UI"].update({
                attrNameWithoutModifier: {
                    # "name": "",
                    "min": -cls.NUMRANGE_MAX,
                    "max": cls.NUMRANGE_MAX,
                    "soft_min": -cls.NUMRANGE_MAX,
                    "soft_max": cls.NUMRANGE_MAX,
                    "description": "",
                    "default": 0.0
                }
            })

        if context.scene.animation_data.action is not None:
            fcurves = context.scene.animation_data.action.fcurves
            search = [ i for i, x in enumerate(fcurves) if x.data_path == data_path ]
            if len(search) == 1: # has animation
                fcurves[search[0]].data_path = 'sequence_editor.sequences_all["%s"]["%s"]'%(richstrip.name, attrNameWithoutModifier)

        cls.addPropertyWithBinding_ClassLevel(context, targetSeq, attrName, attrNameWithoutModifier, [], "bind", storedSeq=richstrip, defaultValue=0.0 if type(val) == float else 0)
    @classmethod
    def exportToReverse(cls, context, richstrip, attrName, targetSeq):
        effect = richstrip.IceTB_richstrip_data.getSelectedEffect()

        isBinding = attrName[:2] == '["'
        attrName:str
        attrNameWithoutModifier = attrName.lstrip('["').rstrip(']"')
        attrSplit = attrNameWithoutModifier.split('.')

        if isBinding:
            targetSeq.driver_remove(attrName)
            data_path = 'sequence_editor.sequences_all["%s"]%s'%(targetSeq.name, attrName)
        else:
            attrNameWithoutModifier = cls.genbinderName(effect, attrSplit[-1], False) # new name
            cls.getSeqOrPathUsingPath(targetSeq, attrSplit[:-1]).driver_remove(attrSplit[-1])
            data_path = 'sequence_editor.sequences_all["%s"]%s'%(targetSeq.name, cls.getSeqOrPathUsingPath(targetSeq, attrSplit, returnPath=True))

        if context.scene.animation_data.action is not None:
            rsdata_path = 'sequence_editor.sequences_all["%s"]["%s"]'%(richstrip.name, attrNameWithoutModifier)
            fcurves = context.scene.animation_data.action.fcurves
            search = [ i for i, x in enumerate(fcurves) if x.data_path == rsdata_path ]
            if len(search) == 1: # has animation
                fcurves[search[0]].data_path = data_path

        del richstrip[attrNameWithoutModifier]