import bpy

ICETB_MSGBUS_TRANSFORM_ATTRS = [ 
    "offset_x",
    "offset_y"
]

ICETB_MSGBUS_TRANSFORM = [ (bpy.types.SequenceTransform, attrName) for attrName in ICETB_MSGBUS_TRANSFORM_ATTRS ]