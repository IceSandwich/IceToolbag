import bpy
from .base import EffectBase
from ....datas import RichStripData, RichStripEffect
# from .widgets import xylock

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