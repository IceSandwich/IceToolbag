import bpy

ICETB_MSGBUS_MOVIE_ATTRS = [
    "pos_x",
    "pos_y"
]

ICETB_MSGBUS_MOVIE = [ (bpy.types.MovieSequence, attrName) for attrName in ICETB_MSGBUS_MOVIE_ATTRS ]