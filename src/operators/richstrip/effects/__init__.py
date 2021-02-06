from .original import EffectOriginal
from .copy import EffectCopy
from .fastblur import EffectFastBlur

ICETB_EFFECTS_CLASSES = [
    EffectOriginal,
    EffectCopy,
    EffectFastBlur
]

ICETB_EFFECTS_NAMES = [ x.getName() for x in ICETB_EFFECTS_CLASSES ]
ICETB_EFFECTS_DICTS = { x.getName(): x for x in ICETB_EFFECTS_CLASSES }