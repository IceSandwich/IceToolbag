import bpy, os

__PKGNAME__ = __package__.split('.')[0]

render_output_suffix = "jpg"

def getGmicQTPath() -> str:
    """ get gmic qt path from preferences, can be empty string """
    return bpy.context.preferences.addons[__PKGNAME__].preferences.gmic_filename.strip()

def getCacheDir() -> str:
    """ get gmic cache folder, return cache dir """
    return bpy.context.preferences.addons[__PKGNAME__].preferences.cache_dirname.strip()

def getIsAutoupdateWhenStartup() -> bool:
    """ get autoupdate_in_startup from preferences """
    print(__PKGNAME__)
    if bpy.context.preferences.addons[__PKGNAME__].preferences:
        print("got ", bpy.context.preferences.addons[__PKGNAME__].preferences.autoupdate_in_startup)
        return bpy.context.preferences.addons[__PKGNAME__].preferences.autoupdate_in_startup
    else:
        return True # default is true

def renderPreview(output_suffix=render_output_suffix):
    """ render current frame into addon directory, return the filepath of render image """
    bpy.ops.render.opengl(sequencer=True, view_context=False) 
    renderfn = os.path.realpath("render.%s"%output_suffix) # save into addon directory
    bpy.data.images[0].save_render(renderfn)
    return renderfn