from .preference import ICETB_AP_AddonPreferences
from .richstrip_effects import ICETB_PT_RichStripEffects
from .richstrip_effect import ICETB_PT_RichStripEffect
from .richstrip_overctrl import ICETB_PT_RichStripEffectCTL
from .richstrip_effects import ICETB_UL_RichStripEffects_EffectListUI

from .gallerystrip import ICETB_PT_GalleryStripEffects

ICETB_PANELS_CLASSES = [
    ICETB_AP_AddonPreferences,
    
    ICETB_UL_RichStripEffects_EffectListUI,
    ICETB_PT_RichStripEffects,
    ICETB_PT_RichStripEffect,
    ICETB_PT_RichStripEffectCTL,
    
    ICETB_PT_GalleryStripEffects
]