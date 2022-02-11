from ..base import EffectBase

def draw(layout, obj_x, x_attr, obj_y, y_attr, obj_lock, lock_attr, x_label="X", y_label="Y", union_label="Size"):
    viewbool = getattr(obj_lock, lock_attr)

    row = layout.row(align=True)
    if viewbool:
        row.prop(obj_x, x_attr, text=union_label)
    else:
        row.prop(obj_x, x_attr, text=x_label)
        row.prop(obj_y, y_attr, text=y_label)
    row.prop(obj_lock, lock_attr, text="", icon="LOCKED" if viewbool else "UNLOCKED")

def drawWithExportBox(layout, richstrip, obj_x, x_attr, x_exportName:str, obj_y, y_attr, y_exportName:str, obj_lock, lock_attr, x_label="X", y_label="Y", union_label="Size"):
    effect = richstrip.IceTB_richstrip_data.getSelectedEffect()
    bxproperty, byproperty = EffectBase.getBoolProperty(effect, x_exportName + "_export"), EffectBase.getBoolProperty(effect, y_exportName + "_export")
    viewbool = getattr(obj_lock, lock_attr)

    x_binder, y_binder = x_attr, y_attr
    if x_attr[:2] != '["': x_binder = EffectBase.genbinderName(effect, x_attr, True)
    if y_attr[:2] != '["': y_binder = EffectBase.genbinderName(effect, y_attr, True)

    row = layout.row(align=True)
    if viewbool: # only x
        if bxproperty.value:
            row.prop(richstrip, x_binder, text=union_label)
        else:
            row.prop(obj_x, x_attr, text=union_label)
    else: # x, y both
        if bxproperty.value:
            row.prop(richstrip, x_binder, text=x_label)
        else:
            row.prop(obj_x, x_attr, text=x_label)

        if byproperty.value:
            row.prop(richstrip, y_binder, text=y_label)
        else:
            row.prop(obj_y, y_attr, text=y_label)

    row.prop(obj_lock, lock_attr, text="", icon="LOCKED" if viewbool else "UNLOCKED")

    row.prop(bxproperty, "value", toggle=0, icon="DECORATE_DRIVER", text="")
    if not viewbool: # x, y both
        row.prop(byproperty, "value", toggle=0, icon="DECORATE_DRIVER", text="")

def drawWithExportBox_NoLock(layout, richstrip, obj_x, x_attr, x_exportName:str, obj_y, y_attr, y_exportName:str, x_label="X", y_label="Y"):
    effect = richstrip.IceTB_richstrip_data.getSelectedEffect()
    bxproperty, byproperty = EffectBase.getBoolProperty(effect, x_exportName + "_export"), EffectBase.getBoolProperty(effect, y_exportName + "_export")

    x_binder, y_binder = x_attr, y_attr
    if x_attr[:2] != '["': x_binder = EffectBase.genbinderName(effect, x_attr, True)
    if y_attr[:2] != '["': y_binder = EffectBase.genbinderName(effect, y_attr, True)

    row = layout.row(align=True)
    if bxproperty.value:
        row.prop(richstrip, x_binder, text=x_label)
    else:
        row.prop(obj_x, x_attr, text=x_label)

    if byproperty.value:
        row.prop(richstrip, y_binder, text=y_label)
    else:
        row.prop(obj_y, y_attr, text=y_label)

    row.prop(bxproperty, "value", toggle=0, icon="DECORATE_DRIVER", text="")
    row.prop(byproperty, "value", toggle=0, icon="DECORATE_DRIVER", text="")