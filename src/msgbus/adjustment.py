import bpy

ICETB_MSGBUS_ADJUSTMENT_ATTRS = [
    "color_saturation",
    "color_multiply",
    "use_flip_x",
    "use_flip_y"
]

ICETB_MSGBUS_ADJUSTMENT = [ (bpy.types.AdjustmentSequence, attrName) for attrName in ICETB_MSGBUS_ADJUSTMENT_ATTRS ]