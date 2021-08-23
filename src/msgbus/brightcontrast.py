import bpy

ICETB_MSGBUS_BRIGHTCONTRAST_ATTRS = [ 
    "bright",
    "contrast"
]

ICETB_MSGBUS_BRIGHTCONTRAST = [ (bpy.types.BrightContrastModifier, attrName) for attrName in ICETB_MSGBUS_BRIGHTCONTRAST_ATTRS ]