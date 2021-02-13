from .original import EffectOriginal
from .copy import EffectCopy
from .fastblur import EffectFastBlur
from .pixelize import EffectPixelize
from .glow import EffectGlow
from .gaussianblur import EffectGaussianBlur

ICETB_EFFECTS_CLASSES = [
    EffectOriginal,
    EffectCopy,
    EffectFastBlur,
    EffectPixelize,
    EffectGlow,
    EffectGaussianBlur
]

ICETB_EFFECTS_NAMES = [ x.getName() for x in ICETB_EFFECTS_CLASSES ]
ICETB_EFFECTS_DICTS = { x.getName(): x for x in ICETB_EFFECTS_CLASSES }