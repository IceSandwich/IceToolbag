from ..base import EffectBase
import bpy

def draw(layout, richstrip, boolName:str, targetSeq, binderName, text=None):
    effect = richstrip.IceTB_richstrip_data.getSelectedEffect()
    bproperty = EffectBase.getBoolProperty(effect, boolName)

    row = layout.row(align=True)
    if bproperty.value:
        if binderName[:2] == '["':
            row.prop(richstrip, binderName, text=text)
        else:
            row.prop(richstrip, EffectBase.genbinderName(effect, binderName, True), text=text)
    else:
        row.prop(targetSeq, binderName, text=text)
    row.prop(bproperty, "value", toggle=0, icon="DECORATE_DRIVER", text="")