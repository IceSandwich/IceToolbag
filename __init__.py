# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy, os
from .src import *

bl_info = {
    "name" : "IceToolbag",
    "author" : "IceSandwich",
    "description" : "A blender addon for VSE, made for personal use.",
    "blender" : (2, 93, 0),
    "version" : (0, 0, 6),
    "location" : "Sequencer Editor",
    "warning" : "This addon is still in develop. Use at your own risk.",
    "category" : "Sequencer",
    "wiki_url" : "https://github.com/IceSandwich/IceToolbag",
    "tracker_url":  "https://github.com/IceSandwich/IceToolbag/issues"
}

classes = ICETB_CLASSES
seqmsgbus = ICETB_MSGBUS

seqPreview_km = None # Key map for sequence preview window
addon_keymaps = []

def updateSequenceViewport():
    bpy.ops.sequencer.refresh_all()

def register():
    global seqPreview_km
    global addon_keymaps
    
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg is not None:
        seqPreview_km = kcfg.keymaps.new(name="IceToolbag_seqPreview", space_type="SEQUENCE_EDITOR", region_type="WINDOW")
    for cls in classes:
        bpy.utils.register_class(cls)
        if kcfg and hasattr(cls, 'setupKey'):
            cls.setupKey(seqPreview_km)
        if hasattr(cls, 'setupMenu'):
            cls.setupMenu(True)
        if hasattr(cls, 'setupProperty'):
            cls.setupProperty(True)
        if hasattr(cls, 'setupHandlers'):
            cls.setupHandlers(True)
    
    if kcfg is not None:
        addon_keymaps.append(seqPreview_km)

    for msgbus in seqmsgbus:
        bpy.msgbus.subscribe_rna(
            key=msgbus,
            owner=seqmsgbus,
            args=(),
            notify=updateSequenceViewport,
        )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

        if hasattr(cls, 'setupMenu'):
            cls.setupMenu(False)
        if hasattr(cls, 'setupProperty'):
            cls.setupProperty(False)
        if hasattr(cls, 'setupHandlers'):
            cls.setupHandlers(False)

    for km in addon_keymaps:
        bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)

    addon_keymaps.clear()

    # bpy.msgbus.clear_by_owner(seqmsgbus)


#https://docs.blender.org/api/current/bpy.app.handlers.html
#https://blender.stackexchange.com/questions/3313/animate-string-property
#https://developer.blender.org/T77126
#https://devtalk.blender.org/t/update-property-when-active-tool-changes/11467/13