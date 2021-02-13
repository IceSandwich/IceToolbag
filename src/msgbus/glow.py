import bpy

ICETB_MSGBUS_GLOW_ATTRS = [ 
    "threshold",
    "clamp",
    "boost_factor",
    "blur_radius",
    "quality",
    "use_only_boost"
]

ICETB_MSGBUS_GLOW = [ (bpy.types.GlowSequence, attrName) for attrName in ICETB_MSGBUS_GLOW_ATTRS ]