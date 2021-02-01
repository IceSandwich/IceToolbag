import bpy

ICETB_MSGBUS_SOUND_ATTRS = [
    "volume",
    "mute"
]

ICETB_MSGBUS_SOUND = [ (bpy.types.SoundSequence, attrName) for attrName in ICETB_MSGBUS_SOUND_ATTRS ]