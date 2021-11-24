from .marker.renamelayer import ICETB_OT_Marker_RenameLayer
from .marker.switchlayer import ICETB_OT_Marker_SwitchLayer
from .marker.align2marker import ICETB_OT_Marker_AlignToMarker
from .marker.beatmatch import ICETB_OT_Marker_BeatMatch
from .marker.batchrename import ICETB_OT_Marker_BatchRename

from .convert2richstrip import ICETB_OT_ConvertToRichStrip
from .convert2gallerystrip import ICETB_OT_ConvertToGalleryStrip

from .richstrip.maskops import ICETB_OT_RichStrip_Annotation2Mask, ICETB_OT_RichStrip_OpenMaskEditor
from .richstrip.addeffect import ICETB_OT_RichStrip_Add
from .richstrip.deleffect import ICETB_OT_RichStrip_Delete
from .richstrip.mveffect import ICETB_OT_RichStrip_Move
from .eventdelegate import ICETB_OT_RichStrip_EventDelegate
from .richstrip.rebuild import ICETB_OT_RichStrip_Rebuild
from .richstrip.availableeffect import ICETB_OT_RichStrip_EffectAvailable

from .gallerystrip_eventdelegate import ICETB_OT_GallyerStrip_EventDelegate
from .gallerystrip.rebuild import ICETB_OT_GalleryStrip_Rebuild

ICETB_OPERATORS_CLASSES = [
    ICETB_OT_Marker_RenameLayer,
    ICETB_OT_Marker_SwitchLayer,
    ICETB_OT_Marker_BatchRename,
    ICETB_OT_Marker_AlignToMarker,
    ICETB_OT_Marker_BeatMatch,

    ICETB_OT_ConvertToRichStrip,
    ICETB_OT_ConvertToGalleryStrip,

    ICETB_OT_RichStrip_Annotation2Mask,
    ICETB_OT_RichStrip_OpenMaskEditor,
    ICETB_OT_RichStrip_Add,
    ICETB_OT_RichStrip_Delete,
    ICETB_OT_RichStrip_Move,
    ICETB_OT_RichStrip_EventDelegate,
    ICETB_OT_RichStrip_Rebuild,
    ICETB_OT_RichStrip_EffectAvailable,

    ICETB_OT_GallyerStrip_EventDelegate,
    ICETB_OT_GalleryStrip_Rebuild
]