import bpy, shutil, uuid, os
from .effects.base import EffectBase
from ...datas.preference_helper import renderPreview, getCacheDir, render_output_suffix

class ICETB_OT_RichStrip_FreezeFrame(bpy.types.Operator):
    bl_idname = "icetb.richstrip_freezeframe"
    bl_label = "Freeze Frame for selected meta sequence"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if len(context.selected_sequences) == 0:
            self.report({'ERROR'}, "Please select a meta sequence.")
            return {'CANCELLED'}

        richstrip:bpy.types.Sequence = context.selected_sequences[0]
        if not type(richstrip) is bpy.types.MetaSequence:
            self.report({'ERROR'}, "Selected sequence isn't a valid meta sequence.")
            return {'CANCELLED'}

        EffectBase.enterEditMode(richstrip)
        renderfn = renderPreview()
        EffectBase.leaveEditMode()

        targetDir = bpy.path.abspath("%s//Freezes"%getCacheDir())
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)

        freezeId = uuid.uuid4().hex
        targetName = "%s.%s"%(freezeId, render_output_suffix)

        shutil.copyfile(renderfn, os.path.join(targetDir, targetName))

        bpy.ops.sequencer.image_strip_add(directory=targetDir, files=[{
            "name": targetName
        }], relative_path=True, show_multiview=False, frame_start=richstrip.frame_final_start, frame_end=richstrip.frame_final_end, set_view_transform=False)

        return {"FINISHED"}
