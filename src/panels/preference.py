import bpy, os

__PKGNAME__ = __package__.split('.')[0]
# __CONFIG__ = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "config.json")

class ICETB_AP_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __PKGNAME__

    def draw(self, context:bpy.types.Context):
        layout:bpy.types.UILayout = self.layout
        layout.prop(self, "gmic_filename")
        layout.prop(self, "cache_dirname")
        # layout.prop(self, 'autoupdate_in_startup')


    gmic_filename: bpy.props.StringProperty(
        name="G'MIC Qt Program", 
        description="should be pointed to gmic_qt.exe", 
        subtype='FILE_PATH',
        default=R""
    )

    cache_dirname: bpy.props.StringProperty(
        name="Cache Dir Name",
        description="this folder will be created beside blend file",
        default="//IceTBCache",
    )

    autoupdate_in_startup: bpy.props.BoolProperty(
        name="Default Autoupdate",
        description="Enable auto update when blender startup but will make blender slower while modeling",
        default=True
    )
