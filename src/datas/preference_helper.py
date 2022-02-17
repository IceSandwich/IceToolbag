import bpy, os, tempfile

__PKGNAME__ = __package__.split('.')[0]
tmpDir = tempfile.TemporaryDirectory(prefix="IceToolbag_")
print("Create temp folder:", tmpDir.name)

render_output_suffix = "png"

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

def getAddonRoot() -> str:
    """ get addon root path """
    return os.path.abspath(os.path.join(os.path.split(__file__)[0], "..", ".."))

def getTempName(filename:str="") -> str:
    """ get temp folder for this addon """
    return os.path.join(tmpDir.name, filename)

def renderPreview(output_suffix=render_output_suffix):
    """ render current frame into addon directory, return the filepath of render image """
    bpy.ops.render.opengl(sequencer=True, view_context=False) 
    renderfn = getTempName(filename="render.%s"%output_suffix) # save into addon directory
    bpy.data.images[0].save_render(renderfn)
    return renderfn