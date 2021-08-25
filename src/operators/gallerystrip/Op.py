import bpy

class GalleryStripOP:

    @classmethod
    def addBinder2Root(cls, context, gallerystrip, binderName, targetSeq, targetPropName, driverVars, binderExpression):
        driver = targetSeq.driver_add(targetPropName).driver
        for driverVar in driverVars:
            var = driver.variables.new()
            var.name = driverVar["name"]
            var.targets[0].id_type = 'SCENE'
            var.targets[0].id = context.scene
            if 'globalProp' in driverVar:
                var.targets[0].data_path = driverVar["globalProp"]
            else:
                var.targets[0].data_path = 'sequence_editor.sequences_all["%s"]%s%s%s'%(driverVar["seqName"], '["' if driverVar["isCustomProp"] else '.', driverVar["seqProp"], '"]' if driverVar["isCustomProp"] else "")
        var = driver.variables.new()
        var.name = 'bind'
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = context.scene
        var.targets[0].data_path = 'sequence_editor.sequences_all["%s"]["%s"]'%(gallerystrip.name, binderName)
        driver.use_self = True
        driver.expression = binderExpression

    @classmethod
    def addBinding(cls, context, gallerystrip):
        data = gallerystrip.IceTB_gallerystrip_data
        for i, stripName in enumerate(data.StripsName):
            seq = gallerystrip.sequences.get(stripName.value)
            cls.addBinder2Root(context, gallerystrip, "scale_x", seq.transform, "scale_x", [{
                "name": "scale",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.StripsScale[%d].X"%i,
                "isCustomProp": False
            }], 'bind * scale')
            cls.addBinder2Root(context, gallerystrip, "scale_y", seq.transform, "scale_y", [{
                "name": "scale",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.StripsScale[%d].Y"%i,
                "isCustomProp": False
            }], 'bind * scale')
            cls.addBinder2Root(context, gallerystrip, "controller", seq.transform, "offset_x", [{
                "name": "canvasWidth",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.CanvasWidth",
                "isCustomProp": False
            }, {
                "name": "canvasHeight",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.CanvasHeight",
                "isCustomProp": False
            }, {
                "name": "arrangement",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.ArrangementMethodInt",
                "isCustomProp": False
            }], '(-bind+%d) * canvasWidth if arrangement == 0 else 0'%i)
            cls.addBinder2Root(context, gallerystrip, "controller", seq.transform, "offset_y", [{
                "name": "canvasWidth",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.CanvasWidth",
                "isCustomProp": False
            }, {
                "name": "canvasHeight",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.CanvasHeight",
                "isCustomProp": False
            }, {
                "name": "arrangement",
                "seqName": gallerystrip.name,
                "seqProp": "IceTB_gallerystrip_data.ArrangementMethodInt",
                "isCustomProp": False
            }], '(bind-%d) * canvasHeight if arrangement == 1 else 0'%i)
            
