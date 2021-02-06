import bpy

class EffectBase():
    @classmethod
    def getName(cls):
        """
            Effect type name. Not the name of effect.
        """
        return "Untitled Effect"

    @classmethod
    def _add(cls, context):
        richstrip = context.selected_sequences[0]
        data = richstrip.IceTB_richstrip_data
        effect = data.addEffect(cls.getName())
        cls.add(context, richstrip, data, effect)

    @classmethod
    def add(cls, context, richstrip, data, effect):
        return

    @classmethod
    def _update(cls, _type, identify, context):
        richstrip = context.selected_sequences[0]
        if type(richstrip) != bpy.types.MetaSequence: # some bug i don't know how to occur, just check if meta to solve right now.
            return
        firstlayer = richstrip.sequences.get("FirstLayerRichStrip")
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        cls.update(_type, identify, context, data, effect, firstlayer)
        bpy.ops.sequencer.refresh_all()

    @classmethod
    def update(cls, type, identify, context, data, effect, firstlayer):
        return

    @classmethod
    def _draw(cls, context, layout):
        richstrip = context.selected_sequences[0]
        firstlayer = richstrip.sequences.get("FirstLayerRichStrip")
        data = richstrip.IceTB_richstrip_data
        effect = data.getSelectedEffect()
        cls.draw(context, layout, data, effect, firstlayer)

    @classmethod
    def draw(cls, context, layout, data, effect, firstlayer):
        return

    @classmethod
    def enterFistLayer(cls, richstrip):
        firstlayerrs = richstrip.sequences.get("FirstLayerRichStrip")
        # audiolayer = firstlayerrs.sequences.get("GlobalBaseAudioStrip")
        # assert(firstlayerrs is not None)
        richstrip.select = True
        bpy.ops.sequencer.meta_toggle() # enter meta strip
        bpy.ops.sequencer.select_all(action='DESELECT')
        firstlayerrs.select = True
        bpy.context.scene.sequence_editor.active_strip = firstlayerrs
        bpy.ops.sequencer.meta_toggle() # enter sub meta strip
        bpy.ops.sequencer.select_all(action='DESELECT')
        # TODO: if audiolayer is none, return movielayer frame start and end
        # return richstrip.sequences, richstrip.frame_final_start, richstrip.frame_final_end
        return firstlayerrs.sequences, firstlayerrs.frame_final_start, firstlayerrs.frame_final_end

    @classmethod
    def leaveFirstLayer(cls, data=None):
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave sub meta strip
        bpy.ops.sequencer.select_all(action='DESELECT')
        bpy.ops.sequencer.meta_toggle() # leave meta strip
        if data is not None:
            data.EffectsCurrent = len(data.Effects) - 1

    @classmethod
    def genRegularStripName(cls, effectid, descrip):
        return cls.getName() + "_" + str(effectid) + "_" + descrip
