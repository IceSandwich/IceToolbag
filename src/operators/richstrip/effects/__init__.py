from .original import EffectOriginal
# from .copy import EffectCopy
from .fastblur import EffectFastBlur
from .pixelize import EffectPixelize
from .glow import EffectGlow
from .gaussianblur import EffectGaussianBlur
from .brightcontrast import EffectBrightContrast
from .shadow import EffectShadow
from .mirror import EffectMirror
from .ramp import EffectRamp
from .matte import EffectMatte
from .gmic import EffectGMIC

ICETB_EFFECTS_CLASSES = [
    EffectOriginal,
    # EffectCopy,
    EffectFastBlur,
    EffectPixelize,
    EffectGlow,
    EffectGaussianBlur,
    EffectBrightContrast,
    EffectShadow,
    EffectMirror,
    EffectRamp,
    EffectMatte,
    EffectGMIC
]

ICETB_EFFECTS_NAMES = [ x.getName() for x in ICETB_EFFECTS_CLASSES ]
ICETB_EFFECTS_DICTS = { x.getName(): x for x in ICETB_EFFECTS_CLASSES }