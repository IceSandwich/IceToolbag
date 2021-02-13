import bpy

ICETB_MSGBUS_GAUSSIANBLUR_ATTRS = [ 
    "size_x",
    "size_y"
]

ICETB_MSGBUS_GAUSSIANBLUR = [ (bpy.types.GaussianBlurSequence, attrName) for attrName in ICETB_MSGBUS_GAUSSIANBLUR_ATTRS ]