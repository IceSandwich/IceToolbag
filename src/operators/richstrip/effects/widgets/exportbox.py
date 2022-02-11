from ..base import EffectBase
from .....datas.bool_prop import BoolProperty
import bpy

def draw(layout, richstrip, exportName:str, targetSeq, binderName:str, text=None):
    effect = richstrip.IceTB_richstrip_data.getSelectedEffect()
    bproperty = EffectBase.getBoolProperty(effect, exportName + "_export")

    row = layout.row(align=True)
    if bproperty.value:
        if binderName[:2] == '["':
            row.prop(richstrip, binderName, text=text)
        else:
            row.prop(richstrip, EffectBase.genbinderName(effect, binderName, True), text=text)
    else:
        row.prop(targetSeq, binderName, text=text)
    row.prop(bproperty, "value", toggle=0, icon="DECORATE_DRIVER", text="")