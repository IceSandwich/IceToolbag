# import submenu first

#from .customMenu import customMenu
from .marker import ICETB_MT_SwitchLayer
from .marker import ICETB_MT_Marker 



# make sure import main menu finally
from .icetb import ICETB_MT_Main

ICETB_MENUS_CLASSES = [
    ICETB_MT_SwitchLayer,
    ICETB_MT_Marker,
    ICETB_MT_Main
]