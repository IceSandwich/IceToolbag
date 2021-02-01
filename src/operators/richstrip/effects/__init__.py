from .original import EffectOriginal
from .copy import EffectCopy

ICETB_EFFECTS_CLASSES = [
    EffectOriginal,
    EffectCopy
]

ICETB_EFFECTS_NAMES = [ x.getName() for x in ICETB_EFFECTS_CLASSES ]
ICETB_EFFECTS_DICTS = { x.getName(): x for x in ICETB_EFFECTS_CLASSES }