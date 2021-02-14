import bpy

ICETB_MSGBUS_TRANSLATE_ATTRS = [ 
    "translate_start_x",
    "translate_start_y",
    "rotation_start",
    "use_flip_x",
    "use_flip_y",
    "blend_alpha",
    "color_saturation",
    "use_uniform_scale"
]

ICETB_MSGBUS_TRANSLATE = [ (bpy.types.TransformSequence, attrName) for attrName in ICETB_MSGBUS_TRANSLATE_ATTRS ]