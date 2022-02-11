import bpy
from .base import EffectBase
from ....datas import RichStripData, RichStripEffect
# from .widgets import xylock

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

When you click `add effect`, EffectBase class will do the following process. So you need to implement them.
┌──────────────┐    ┌──────────────────────────┐     ┌──────────────────────────┐   ┌────────────────────────┐    ┌─────────────┐
│              │    │                          │     │                          │   │                        │    │             │
│ stage_Before ├───►│ stage_PropertyDefination ├────►│ stage_SequenceDefination ├──►│ stage_BinderDefination ├───►│ stage_After │
│              │    │                          │     │                          │   │                        │    │             │
└──────────────┘    └──────────────────────────┘     └──────────────────────────┘   └────────────────────────┘    └─────────────┘


stage_Before(optional): 
    Usually select the latest effect strip. 
    It's optional. You don't have to implement it if you want to apply new effect strip to latest effect strip.


stage_PropertyDefination(optional):
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
            self.addPropertyWithBinding(self.transform, "size_y", "ExpBinder", [], "self.size_x")

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
            self.addPropertyWithBinding(self.transform, "size_y", "ExpBinder", [{
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


class EffectTemplate(EffectBase):
    @classmethod
    def getName(cls):
        return "DemoEffect"

    # def stage_Before(self):
    #     self.richstrip.sequences.get(self.data.Effects[-2].EffectStrips[-1].value).select = True
    #     return

    def stage_PropertyDefination(self):
        # addColorProperty, addFloatProperty, addIntProperty, addBoolProperty, addEnumProperty
        return

    def stage_SequenceDefination(self, relinkStage:bool):
        if relinkStage:
            # self.xx = self.getEffectStrip(self.richstrip, self.effect, "xx")
            return
        else:
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
        return

    @classmethod
    def update(cls, attr_type:str, attr_identify:str, context:bpy.types.Context, data:RichStripData, effect:RichStripEffect, richstrip:bpy.types.SequencesMeta):
        # if attr_type == 'INT' and attr_identify == "xxx":
        #   do something...
        #   return True
        
        return False