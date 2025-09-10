#! python 2

import System
from System.Collections.Generic import List
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import Rhino.Geometry as rg
import os
import Eto
import Eto.Drawing as drawing
import Eto.Forms as forms
import math
from sliders import SliderGroup
import SpatialData
import Rhino.RhinoApp as app
from components import ComponentGenerator as cg
from pipeline import DrawConduit
from pipeline import ColorsAndMaterials as cam

macro = rs.AliasMacro('wdGem')
wd1gem_script = macro.replace('!_-RunPythonScript ', '')
wd1gem_script = wd1gem_script.replace('"', '')
script_folder = os.path.dirname(wd1gem_script)
data_folder = os.path.join(script_folder, "data")

is_free = True if "Free" in script_folder else False

def IsGem(rhino_ob, geo, component_index):
    is_gem = False
    name = rhino_ob.Name
    if name == 'wdGem': is_gem = True
    return is_gem    
    
class wdDialog(forms.Dialog):
    def __init__(self):
        super(wdDialog, self).__init__()
        # form stuff        
        self.LabelWidth = 94
        self.Title = 'Gem Outlines'
        self.Padding = drawing.Padding(15)
        self.AutoSize = True if rs.ExeVersion() > 6 else False
        self.Layout = None
        self.Closing += self.OnDialogClosing
        if rs.ExeVersion() >= 8:
            Rhino.UI.EtoExtensions.UseRhinoStyle(self)

        # overlay visualization stuff
        self.Conduit = DrawConduit(self)
        self.Conduit.Enabled = True
        self.RenderObjects = []
        self.OverlayObjects = []

        # handy variables
        self.GemIDs = []
        self.BaseOutlines = []
        self.GemPlanes = []
        self.Outlines = []      
        self.HasHeartGem = False  
       
        # input controls
        self.UseHeartBaseCheckBoxGroup, self.UseHeartBaseCheckBox = cg.CreateCheckBoxGroup('Use Heart Base: ', self.LabelWidth, False, self.OnFormChanged)
        self.HOffsetSliderGroup = cg.CreateSliderGroup('Horizontal Offset: ', self.LabelWidth, -2.0, 2.0, 2, 0.0, self.Solve)
        self.VOffsetSliderGroup = cg.CreateSliderGroup('Vertical Offset: ', self.LabelWidth, -1.0, 1.0, 2, 0.0, self.Solve)          
        

        # bottom buttons
        self.SetButton = cg.CreateButton('Set Gems', self.OnSetButtonClick)
        self.FinalizeButton = cg.CreateButton('Finalize', self.OnFinalizeButtonClick)
        self.CancelButton = cg.CreateButton('Cancel', self.OnCancelButtonClick)

        # the default button must be set for Macs (might as well set the abort button, too.)
        self.DefaultButton = self.SetButton
        self.AbortButton = self.CancelButton
        
        # lay it out and run the solver
        self.LayoutForm()
        self.Solve(self)

    def DisposeObject(self, ob):
        if hasattr(ob,'Dispose'): ob.Dispose()

    def DisposeObjects(self, obs):
        for ob in obs:
            self.DisposeObject(ob)

    def DisposeRenderObjects(self):
        if hasattr(self, 'RenderObjects'):
            for ob in self.RenderObjects:
                self.DisposeObject(ob)

        if hasattr(self, 'OverlayObjects'):
            for ob in self.OverlayObjects:
                self.DisposeObject(ob)

        if hasattr(self, 'EdgeCurves'):
            for ob in self.EdgeCurves:
                self.DisposeObject(ob)
        
    def LayoutForm(self):
        if rs.ExeVersion() < 7:
            self.Height = 212 if self.HasHeartGem else 180            
        
        if self.Layout:
            self.Layout.Clear()

        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)

        self.Layout.BeginVertical()
        self.Layout.AddRow(self.HOffsetSliderGroup)
        self.Layout.AddRow(self.VOffsetSliderGroup)
        if self.HasHeartGem:
            self.Layout.AddRow(self.UseHeartBaseCheckBoxGroup)
        self.Layout.EndVertical()
        
        self.Layout.BeginVertical()
        self.Layout.AddRow(cg.CreateVerticalSpacer(15))
        self.Layout.AddSpace()
        self.Layout.AddRow(None, self.SetButton, self.FinalizeButton, self.CancelButton)
        self.Layout.EndVertical()

        self.Layout.Create()        
        self.Content = self.Layout

    def LoadBaseOutline(self, gem_id):
        gem_shape = rs.GetUserText(gem_id, 'shape')
        gem_type = rs.GetUserText(gem_id, 'type')
        if gem_shape == 'Heart' and self.UseHeartBaseCheckBox.Checked:
            gem_shape = 'Heart Base'
        base_outline = None
        gem_folder = script_folder.replace("scripts", "gems")
        outline_folder = os.path.join(gem_folder, '5Outlines')
        if 'Cabochon' in gem_type:
            outline_folder = os.path.join(outline_folder, 'Cabochons')
        filename = gem_shape + '.3dm'
        fullpath = os.path.join(outline_folder, filename)
        outline_file = Rhino.FileIO.File3dm.Read(fullpath)
        base_outline = outline_file.Objects.FindByLayer('gem profiles')[0].Geometry
        return base_outline

    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        if len(self.Outlines) > 0:
            if not rs.IsLayer('gem outlines'):
                rs.AddLayer('gem outlines', System.Drawing.Color.FromArgb(210, 0, 0), True, False, None)

            layer = sc.doc.Layers.FindName('gem outlines')
            atts = Rhino.DocObjects.ObjectAttributes()
            atts.LayerIndex = layer.Index

            # add objects to document            
            ob_ids = []
            for ob in self.Outlines:            
                ob_id = sc.doc.Objects.Add(ob, atts)
                ob_ids.append(ob_id)

            # make group, if needed
            if len(ob_ids) > 1:
                grp = rs.AddGroup()
                rs.AddObjectsToGroup(ob_ids, grp)

            sc.doc.Views.Redraw()
        
        self.DisposeObjects(self.BaseOutlines)
        self.DisposeObjects(self.GemPlanes)
        self.DisposeObjects(self.Outlines)
        self.DisposeRenderObjects()

        self.Close()

    def OnFormChanged(self, sender, e):
        self.UseHeartBase = self.UseHeartBaseCheckBox.Checked

        if sender == self.UseHeartBaseCheckBox:
            if len(self.GemIDs) > 0:
                for outline in self.BaseOutlines:
                    outline.Dispose()
                self.BaseOutlines = []
                for gem_id in self.GemIDs:
                    self.BaseOutlines.append(self.LoadBaseOutline(gem_id))

        self.LayoutForm()
        self.Solve(sender)

    def OnSetButtonClick(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        
    def OnPushPickButton(self, sender, e):
        try:
            self.SetGems(sender)
        except Exception as e:
            app.WriteLine("line 195: " + str(e))
        
    def SetGems(self, sender):
        self.DisposeObjects(self.BaseOutlines)
        self.DisposeObjects(self.GemPlanes)

        self.BaseOutlines = []
        self.GemPlanes = []
        self.Shapes = []
        gem_ids = []
        selected_obs = rs.GetObjects('Select one or more gems to add cutters to', rs.filter.polysurface, preselect = True, custom_filter = IsGem)
        if selected_obs:
            for ob in selected_obs:
                name = rs.ObjectName(ob)
                if name == 'wdGem':
                    gem_ids.append(ob)
        rs.UnselectAllObjects()

        if len(gem_ids) == 0:
            rs.MessageBox('No gems were selected.')
        else:
            self.GemIDs = gem_ids

            for gem_id in gem_ids:
                gem_pln = SpatialData.GetPlane(gem_id)
                self.GemPlanes.append(gem_pln)

                outline = self.LoadBaseOutline(gem_id)
                self.BaseOutlines.append(outline)

            self.HasHeartGem = False
            for gem_id in gem_ids:
                gem_shape = rs.GetUserText(gem_id, 'shape')
                if gem_shape == 'Heart':
                    self.HasHeartGem = True
                    break

        self.LayoutForm()
        self.Solve(sender)

    def Solve(self, sender):
        self.DisposeObjects(self.Outlines)
        self.DisposeRenderObjects()
        self.Outlines = []
        self.RenderObjects = []
        self.OverlayObjects = []

        for i in range(len(self.GemIDs)):
            gem_id = self.GemIDs[i]
            gem_pln = self.GemPlanes[i]

            # get gem width and length
            gem = rs.coercebrep(gem_id)
            bbox = gem.GetBoundingBox(gem_pln)
            width = bbox.Max.X - bbox.Min.X
            length = bbox.Max.Y - bbox.Min.Y

            # duplicate the base outline, and get its width and length
            outline = self.BaseOutlines[i]
            outline = rs.coercecurve(outline)
            outline = outline.DuplicateCurve()
            bbox2 = outline.GetBoundingBox(True)
            width2 = bbox2.Max.X - bbox2.Min.X
            length2 = bbox2.Max.Y - bbox2.Min.Y

            # get scale factors
            widthF = width / width2
            lengthF = length / length2

            # scale it to fit the gem
            xform = rg.Transform.Scale(rg.Plane.WorldXY, widthF, lengthF, 1)
            outline.Transform(xform)

            # offset outline
            hoffset = self.HOffsetSliderGroup.Value
            if hoffset != 0:
                outline2 = outline.Offset(rg.Plane.WorldXY, -hoffset, 0.001, rg.CurveOffsetCornerStyle.Sharp)
                if outline2:
                    outline = outline2[0]
                else:
                    outline.Scale(0.01)

                outline = outline.ToNurbsCurve()

            # move up or down
            voffset = self.VOffsetSliderGroup.Value
            if voffset != 0:
                outline.Translate(0, 0, voffset)

            # move to gem plane
            xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, gem_pln)
            outline.Transform(xform)

            self.Outlines.append(outline)

        # render objects
        # for obj in self.RenderObjects:
        #     if hasattr(obj, 'Dispose'): obj.Dispose()
        # self.RenderObjects = []
        # for outline in self.Outlines:
        #     self.RenderObjects.append([outline, cam.CurveColor])

        for outline in self.Outlines:
            self.OverlayObjects.append([outline, cam.CurveColor])
        
        # redraw                
        sc.doc.Views.Redraw()

        
# the main code
if __name__ == "__main__":        
    dialog = wdDialog()
    if rs.ExeVersion() > 6:
        parent = Rhino.UI.RhinoEtoApp.MainWindowForDocument(sc.doc)
    else:
        parent = Rhino.UI.RhinoEtoApp.MainWindow
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, sc.doc, parent)