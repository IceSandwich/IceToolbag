import bpy
import json

"""
┌───────────────────────────────────────────────┐
│ EffectBase                                    │
│ ┌───────┐     ┌──────────┐     ┌────────────┐ │
│ │  add  │     │   draw   │     │   update   │ │
│ └───────┘     └──────────┘     └────────────┘ │
│                                               │
└───────┬──────────┬─────────────┬────────┬─────┘
        │          │             │        │
        │          │             │        │
        │          │             │        │
  ┌─────┴───┐  ┌───┴────┐   ┌────┴───┐  ┌─▼─┐
  │ original│  │fastblur│   │pixelize│  │...│
  └─────────┘  └────────┘   └────────┘  └───┘

When you click add effect, EffectBase class will do the following process.
┌──────────────┐    ┌──────────────────────────┐     ┌──────────────────────────┐   ┌────────────────────────┐    ┌─────────────┐
│              │    │                          │     │                          │   │                        │    │             │
│ stage_Before ├───►│ stage_PropertyDefination ├────►│ stage_SequenceDefination ├──►│ stage_BinderDefination ├───►│ stage_After │
│              │    │                          │     │                          │   │                        │    │             │
└──────────────┘    └──────────────────────────┘     └──────────────────────────┘   └────────────────────────┘    └─────────────┘


stage_Before(optional): 
    Usually select the latest effect strip. 
    It's optional. You don't have to implement it if you want to apply new effect strip to latest effect strip.


stage_PropertyDefination(requirement):
    Define properties using following functions:
        addColorProperty, addFloatProperty, addIntProperty, addBoolProperty, addEnumProperty
    All properties must have default value except for Enum.
    All properties can't be animated! If you want, please use `addPropertyWithBinding` in `stage_BinderDefination`.

    e.g. self.addFloatProperty(self.effect, "PropertyName", 1.0)    # default value: 1.0
    e.g. self.addBoolProperty(self.effect, "lock", True)    # default value: True
    e.g. self.addEnumProperty(self.effect, "enumPropertyName", ["The first one", "The second one"])  
        # add a combo box in panel. Specially, enum doesn't have default value. You need to set it in `stage_After`.


stage_SequenceDefination(requirement):
    Define or retrieve blender effect strips using following functions:
        addBuiltinStrip

    `relinkStage` means we already have defined sequences, we just use `getEffectStrip` to retrieve it.

    e.g.
    def stage_SequenceDefination(self, relinkStage):
        if relinkStage:
            self.transform = self.getEffectStrip(self.richstrip, self.effect, "trans") # retrieve sequence named `trans`
        else:
            self.transform = self.addBuiltinStrip('TRANSFORM', "trans") # define transform sequence named `trans`
            self.transform.size_x = 10 # change sth of transform sequence


stage_BinderDefination(requirement):
    Define blender drivers using following functions:
        addPropertyWithBinding, addPropertyWithDriver

    Both two can define drivers in blender, what's different?
    addPropertyWithDriver: low-level api to add driver but faster.
    addPropertyWithBinding: high-level api to add driver but slower.

    e.g. I want to let `transform.size_y` equals to `transform.size_x` when user changes `transform.size_x`. (simple keeping ratio problem)
        context: must use `self.context`
        targetSeq: which sequence you want to add driver. e.g. `self.transform`
        targetPropName: which native property you want to add driver. e.g. `size_y`
        binderName: name this driver whatever you want, but you must use `genbinderName` to generate the name.
            e.g. `self.genbinderName(self.effect, "ExpBinder")` # "ExpBinder" is the name of driver.
        binderVars(list): the input variables for the driver.
            e.g. `[]` # In this example, `size_x` is own value instead of other sequence's value, so we don't need any input variables.
        binderExpression: python expression.
            e.g. `self.size_x`
        So far, combine them together:
            self.addPropertyWithBinding(self.context, self.transform, "size_y", self.genbinderName(self.effect, "ExpBinder"), 
                [], "self.size_x")

    Advance. I want to keep ratio according to bool property defined in `stage_PropertyDefination`.
        binderVars: we need the bool property as input variable.
            e.g. `[{
                "name": "lock",
                "seqName": self.richstrip.name,     # all properties store in richstrip
                "seqProp": self.genseqProp(self.effect, "Bool", "lock"),    # get bool property named `lock` defined in `stage_PropertyDefination`
                "isCustomProp": False   # all properties defined in `stage_PropertyDefination` isn't custom prop.
            }]`
        binderExpression: logical change.
            e.g. `self.size_x if lock == 1 else bind`   # as u see, 1 stands for True, 0 stands for False. use `bind` stands for `transform.size_y`.
        Combine them together:
            self.addPropertyWithBinding(self.context, self.transform, "size_y", self.genbinderName(self.effect, "ExpBinder"), [{
                "name": "lock",
                "seqName": self.richstrip.name,
                "seqProp": self.genseqProp(self.effect, "Bool", "lock"),
                "isCustomProp": False
            }], "self.size_x if lock == 1 else bind")


stage_After(optional):
    Call some initial function. For example, enum doesn't have default value so you need to set it in this stage.
    e.g. `self._update("ENUM", "enumPropertyName", self.context)` # set property `enumPropertyName` to first one.
    As u see, we can set any properties using `self._update`

draw:
    Draw UI element. Use the following functions to retrieve strips:
        getMovieStrip, getAudioStrip, getEffectStrip

    `layout` is blender api, so this part you can refer to blender manual.

update:
    When user interacts the UI elements which link to properties defined in `stage_PropertyDefination`, this function will be called.


Q: Why we need to define property which can't be animated? It seems `addPropertyWithBinding` is a better choice?
A: Properties can emit signal to `update` function and we can do some pythonic-logical controls. Driver has limitations and it's complicated to define it.
"""

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
        newrsid = "rs%d-"%richstrip.IceTB_richstrip_data.RichStripID

        for stripName in effect.EffectStrips:
            newName = newrsid + stripName.value[oldrsid_len:]
            richstrip.sequences.get(stripName.value+suffix).name = newName
            stripName.value = newName
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
    def getEffectStrip(cls, richstrip, effect, effectName):
        data = richstrip.IceTB_richstrip_data
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
    def addBuiltinStrip(self, effectType, effectName):
        return self.addBuiltinEffectStrip(self.context, self.richstrip, self.effect, effectType, effectName)




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

        # create binder(custom property) if doesn't exist
        if storedSeq.get(binderName) is None:
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

    def addColorProperty(cls, effect, colorName, colorDefault=(0, 0, 0)):
        cls.addBaseProperty(effect, "Color", effect.EffectColorProperties, colorName, colorDefault)

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
            propType: one of ['Bool', 'Enum', 'Float', 'Int', 'Color']
            propName: prop String name
            ret: return property value if retValue is True, otherwise only return the index of property
        """
        #assert(['Bool', 'Enum', 'Float', 'Int', 'Color'].index(propType) != -1)
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