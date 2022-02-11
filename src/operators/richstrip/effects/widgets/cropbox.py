import bpy
from .....datas.bool_prop import BoolProperty

def draw(layout:bpy.types.UILayout, targetSeq:bpy.types.Sequence, enableProperty:BoolProperty):
    box = layout.box()
    box.label(text="Crop", icon="FULLSCREEN_ENTER")

    split = box.split(factor=1.0/3, align=True)
    col1, col2, col3 = split.column(), split.column(), split.column()
    col1.label(text="")
    col2.prop(targetSeq.crop, "max_y", text="")
    col3.label(text="")
    col1.prop(targetSeq.crop, "min_x", text="")
    col2.label(text="")
    col3.prop(targetSeq.crop, "max_x", text="")
    col1.label(text="")
    col2.prop(targetSeq.crop, "min_y", text="")
    col3.label(text="")

    box.prop(enableProperty, "value", text="Crop through", toggle=0)