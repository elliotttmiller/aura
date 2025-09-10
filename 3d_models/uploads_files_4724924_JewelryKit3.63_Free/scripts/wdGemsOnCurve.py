#! python 2

import System
from System.Collections.Generic import List
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import Rhino.RhinoApp as app
import Rhino.Geometry as rg
import Rhino.Display as rd
import os
import Eto
import Eto.Drawing as drawing
import Eto.Forms as forms
import math
from sliders import SliderGroup
from components import ComponentGenerator as cg
import SpatialData
from pipeline import DrawConduit
from pipeline import ColorsAndMaterials as cam

macro = rs.AliasMacro('wdGem')
wd1gem_script = macro.replace('!_-RunPythonScript ', '')
wd1gem_script = wd1gem_script.replace('"', '')
script_folder = os.path.dirname(wd1gem_script)
data_folder = os.path.join(script_folder, "data")

is_free = False
if "Free" in script_folder:
    is_free = True
    
    
class wdDialog(forms.Dialog):
    def __init__(self):
        super(wdDialog, self).__init__()
        # form stuff        
        self.LabelWidth = 115
        self.Title = 'Gems on Curve'
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
        self.EdgeCurves = []
        self.EdgeCurves2 = []
        self.EdgeCurves3 = []
        self.TempObs = []
        self.Conduit.EdgeColor = cam.GemColorLight
        self.Conduit.EdgeColor2 = cam.GemColorDark
        self.Conduit.EdgeColor3 = cam.TransparentProngColor
        # self.Conduit.EdgeColor = System.Drawing.Color.FromArgb(100, 175, 255)
        # self.Conduit.EdgeColor = System.Drawing.Color.FromArgb(50, 150, 255)

        # background stuff
        self.BaseGem = None
        self.BasePreviewGem = None

        # inputs
        self.PushPickButton = None
        self.CurveID = None
        self.Curve = None
        self.SurfaceID = None
        self.Surface = None
        self.Mode = 'Basic'
        self.Alignment = 'Girdle'
        self.FlipDirection = False
        self.StartPos = 1
        self.GemSize = 2.0
        self.GemStartSize = 2.0
        self.GemEndSize = 1.0
        self.GemSizeList = []
        self.GemCount = 5
        self.Gap = 0.2
        self.VerticalAdj = 0.0
        self.InitialT = 0.0

        # calculated values
        self.AxialData = None
        self.CurveLength = 0

        # outputs
        self.Gems = []
        self.PreviewGems = []
        self.StartPoint = None
        self.GemPoints = []
        self.BaseCurve = None
        self.TextDots = []
        self.GemSizes = []
        self.GemPlanes = []
        self.Sphere = None
       
        # input controls
        self.ModeDropDownGroup, self.ModeDropDown = cg.CreateDropDownGroup('Mode: ', self.LabelWidth, ['Basic', 'Tapered', 'List'], self.OnFormChanged)
        self.AlignmentDropDownGroup, self.AlignmentDropDown =  cg.CreateDropDownGroup('Alignment: ', self.LabelWidth, ['Girdles', 'Tables'], self.OnFormChanged) 
        
        self.FlipGemsCheckBoxGroup, self.FlipGemsCheckBox = cg.CreateCheckBoxGroup('Flip Gems: ', self.LabelWidth, False, self.OnFormChanged)  
        self.FlipDirectionCheckBoxGroup, self.FlipDirectionCheckBox = cg.CreateCheckBoxGroup('Flip Direction: ', self.LabelWidth, False, self.OnFormChanged) 
        self.FlipCurveCheckBoxGroup, self.FlipCurveCheckBox = cg.CreateCheckBoxGroup('Flip Curve: ', self.LabelWidth, False, self.OnFormChanged)     
        
        self.StartSliderGroup = cg.CreateSliderGroup('Start Position: ', self.LabelWidth, 0.0, 1.0, 4, self.StartPos, self.Solve)
        self.FineTuneSliderGroup = cg.CreateSliderGroup('Fine Tune Start: ', self.LabelWidth, -0.02, 0.02, 4, 0, self.Solve)
        self.GemSizeSliderGroup = cg.CreateSliderGroup('Gem Size: ', self.LabelWidth, 0.5, 5.0, 2, self.GemSize, self.Solve)
        self.GemStartSizeSliderGroup = cg.CreateSliderGroup('Gem Start Size: ', self.LabelWidth, 0.5, 5.0, 2, self.GemStartSize, self.Solve)
        self.GemEndSizeSliderGroup = cg.CreateSliderGroup('Gem End Size: ', self.LabelWidth, 0.5, 5.0, 2, self.GemEndSize, self.Solve)
        self.GemCountSliderGroup = cg.CreateSliderGroup('Gem Count: ', self.LabelWidth, 1, 30, 0, self.GemCount, self.Solve)
        self.GemSizeListTextBoxGroup, self.GemSizeListTextBox = cg.CreateTextBoxGroup('Gem Size List: ', self.LabelWidth, '2.0, 1.0, 1.85, 0.95, 1.92', self.OnFormChanged)
        self.GapSliderGroup = cg.CreateSliderGroup('Gap: ', self.LabelWidth, 0.0, 2.0, 2, self.Gap, self.Solve)
        self.VerticalAdjustmentSliderGroup = cg.CreateSliderGroup('Vertical Adj: ', self.LabelWidth, -1.0, 1.0, 2, self.VerticalAdj, self.Solve)

        self.ShowProngsCheckBoxGroup, self.ShowProngsCheckBox = cg.CreateCheckBoxGroup('Show Prong Guides? ', self.LabelWidth, False, self.OnFormChanged)
        self.ProngSizeSliderGroup = cg.CreateSliderGroup('Prong Size: ', self.LabelWidth, 0.4, 2.0, 2, 0.8, self.Solve)
        self.OverlapSliderGroup = cg.CreateSliderGroup('Overlap Factor: ', self.LabelWidth, 0.0, 0.5, 2, 0.2, self.Solve)
        
        # bottom buttons
        self.SetCurveButton = cg.CreateButton('Set Curve', self.OnSetCurve)
        self.SetSurfaceButton = cg.CreateButton('Set Surface', self.OnSetSurface) 
        self.FinalizeButton = cg.CreateButton('Finalize', self.OnFinalizeButtonClick)
        self.CancelButton = cg.CreateButton('Cancel', self.OnCancelButtonClick)

        # the default button must be set for Macs (might as well set the abort button, too.)
        self.DefaultButton = self.SetCurveButton
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

        if hasattr(self, 'EdgeCurves2'):
            for ob in self.EdgeCurves2:
                self.DisposeObject(ob)

        if hasattr(self, 'EdgeCurves3'):
            for ob in self.EdgeCurves3:
                self.DisposeObject(ob)
        
        if hasattr(self, 'TempObs'):
            for ob in self.TempObs:
                self.DisposeObject(ob)
        
    def LayoutForm(self):
        global is_free

        if self.Layout:
            self.Layout.Clear()

        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)

        if self.ModeDropDown.SelectedValue == 'Basic':
            self.LayoutBasicForm()        
        elif self.ModeDropDown.SelectedValue == 'Tapered':
            self.LayoutTaperedForm()
        elif self.ModeDropDown.SelectedValue == 'List':
            self.LayoutListForm()

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.ShowProngsCheckBoxGroup)
        self.Layout.AddRow(self.ProngSizeSliderGroup)
        self.Layout.AddRow(self.OverlapSliderGroup)
        
        self.Layout.BeginVertical()
        self.Layout.AddSpace()
        self.Layout.AddSpace()
        self.Layout.AddSpace()
        self.Layout.AddRow(None, self.SetCurveButton, self.SetSurfaceButton, self.FinalizeButton, self.CancelButton)
        self.Layout.EndVertical()

        self.Layout.Create()        
        self.Content = self.Layout

    def LayoutBasicForm(self):  
        if rs.ExeVersion() == 6: self.Height = 674 #489#436      
        self.Layout.BeginVertical()

        self.Layout.AddRow(self.ModeDropDownGroup)
        self.Layout.AddRow(self.AlignmentDropDownGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.FlipGemsCheckBoxGroup)
        self.Layout.AddRow(self.FlipDirectionCheckBoxGroup)
        self.Layout.AddRow(self.FlipCurveCheckBoxGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.StartSliderGroup)
        self.Layout.AddRow(self.FineTuneSliderGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.GemSizeSliderGroup)
        self.Layout.AddRow(self.GemCountSliderGroup)
        self.Layout.AddRow(self.GapSliderGroup)
        self.Layout.AddRow(self.VerticalAdjustmentSliderGroup)            
        self.Layout.EndVertical()

    def LayoutListForm(self):  
        if rs.ExeVersion() == 6: self.Height = 640 #455      
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)
        self.Layout.AddRow(self.AlignmentDropDownGroup)
        
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))        
        
        self.Layout.AddRow(self.FlipGemsCheckBoxGroup)
        self.Layout.AddRow(self.FlipDirectionCheckBoxGroup)
        self.Layout.AddRow(self.FlipCurveCheckBoxGroup)
        
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))        
        
        self.Layout.AddRow(self.StartSliderGroup)
        self.Layout.AddRow(self.FineTuneSliderGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.GemSizeListTextBoxGroup)
        self.Layout.AddRow(self.GapSliderGroup)
        self.Layout.AddRow(self.VerticalAdjustmentSliderGroup)            
        self.Layout.EndVertical()

    def LayoutTaperedForm(self): 
        if rs.ExeVersion() == 6: self.Height = 708 #523       
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)
        self.Layout.AddRow(self.AlignmentDropDownGroup)
        
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        
        self.Layout.AddRow(self.FlipGemsCheckBoxGroup)
        self.Layout.AddRow(self.FlipDirectionCheckBoxGroup)
        self.Layout.AddRow(self.FlipCurveCheckBoxGroup)
        
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        
        self.Layout.AddRow(self.StartSliderGroup)
        self.Layout.AddRow(self.FineTuneSliderGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.GemStartSizeSliderGroup)
        self.Layout.AddRow(self.GemEndSizeSliderGroup)
        self.Layout.AddRow(self.GemCountSliderGroup)
        self.Layout.AddRow(self.GapSliderGroup)
        self.Layout.AddRow(self.VerticalAdjustmentSliderGroup)            
        self.Layout.EndVertical()

    def LoadGem(self):      
        gemfolder = script_folder.replace("scripts", "gems")
        filename = "Round.3dm"
        fullpath = os.path.join(gemfolder, filename)
        gem_file = Rhino.FileIO.File3dm.Read(fullpath)
        self.BaseGem =  gem_file.Objects.FindByLayer('gems')[0].Geometry
        self.AxialData = SpatialData.CaptureAxialData(self.BaseGem)

    def LoadPreviewGem(self):      
        gemfolder = script_folder.replace("scripts", "gems")
        filename = "RoundPreview.3dm"
        fullpath = os.path.join(gemfolder, filename)
        gem_file = Rhino.FileIO.File3dm.Read(fullpath)
        self.BasePreviewGem =  gem_file.Objects.FindByLayer('gems')[0].Geometry
        self.AxialData = SpatialData.CaptureAxialData(self.BasePreviewGem)
        
    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        if len(self.PreviewGems) > 0:
            layer_name = 'gems'
            if not rs.IsLayer(layer_name):
                rs.AddLayer(layer_name, System.Drawing.Color.FromArgb(150, 200, 255))

            layer = sc.doc.Layers.FindName(layer_name)
            atts = Rhino.DocObjects.ObjectAttributes()
            atts.LayerIndex = layer.Index

            # create the real gems from the preview gems
            self.LoadGem()
            for i in range(len(self.PreviewGems)):
                # create gem and scale it
                gem = self.BaseGem.DuplicateBrep()
                if 'Table' in self.Alignment: gem.Translate(0, 0, -1.85)
                xform = rg.Transform.Scale(rg.Point3d.Origin, self.GemSizes[i]/10)
                gem.Transform(xform)

                # move gem to preview gem's plane
                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, self.GemPlanes[i])
                gem.Transform(xform)

                # add real gem to gem list
                self.Gems.append(gem)

            # add the real gems to the document        
            gem_ids = []
            for i in range(len(self.Gems)):
                gem = self.Gems[i]
                gem_id = sc.doc.Objects.AddBrep(gem, atts)
                gem_ids.append(gem_id)
                size = self.GemSizes[i]
                SpatialData.WriteSpatialData(gem_id, self.AxialData, [size/10, size/10, size/10])
                rs.ObjectName(gem_id, 'wdGem')
                rs.SetUserText(gem_id, 'width', str(size))
                rs.SetUserText(gem_id, 'length', str(size))

                bbox = self.BaseGem.GetBoundingBox(True)
                depth = bbox.Max.Z - bbox.Min.Z
                depth = round(depth * (size / 10), 2)

                rs.SetUserText(gem_id, 'depth', str(depth))
                rs.SetUserText(gem_id, 'type', 'Fancy')
                rs.SetUserText(gem_id, 'shape', 'Round')

            if len(gem_ids) > 0:
                grp = rs.AddGroup()
                rs.AddObjectsToGroup(gem_ids, grp)

        sc.doc.Views.Redraw()
        self.DisposeObject(self.BaseCurve)
        self.DisposeObject(self.Sphere)
        self.DisposeObject(self.BaseGem)
        self.DisposeObjects(self.Gems)
        self.DisposeObjects(self.PreviewGems)
        self.DisposeObjects(self.TextDots)
        self.DisposeRenderObjects()            
        self.Close()

    def OnFormChanged(self, sender, e):
        global is_free
        if sender == self.ModeDropDown:
            if is_free:
                if self.ModeDropDown.SelectedValue == 'Tapered':
                    rs.MessageBox('Tapered mode is only available in the full version.')
                    self.ModeDropDown.SelectedIndex = 0
                elif self.ModeDropDown.SelectedValue == 'List':
                    rs.MessageBox('List mode is only available in the full version.')
                    self.ModeDropDown.SelectedIndex = 0
                else:
                    self.LayoutForm()
                    self.Solve(sender)
            else:
                self.LayoutForm()
                self.Solve(sender)
        else:
            self.Solve(sender)
        
    def OnSetCurve(self, sender, e):
        self.PushPickButton = sender
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)

    def OnSetSurface(self, sender, e):
        self.PushPickButton = sender
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        
    def OnPushPickButton(self, sender, e):
        if self.PushPickButton == self.SetCurveButton:
            self.SetCurve(sender)
        else:
            self.SetSurface(sender)
        
    def SetCurve(self, sender):
        result = rs.GetCurveObject('Select curve', False, False)
        self.DisposeObject(self.Curve)
        self.Curve = None

        self.DisposeObject(self.BaseCurve)
        self.BaseCurve = None
        
        if result:
            self.CurveID = result[0]
            crv = rs.coercecurve(self.CurveID)
            self.Curve = crv.ToNurbsCurve()
            crv.Dispose()
            self.InitialT = result[4]
            distance_from_start = self.Curve.GetLength(rg.Interval(self.Curve.Domain.T0, self.InitialT))
            self.CurveLength = self.Curve.GetLength()
            percent_of_length = distance_from_start / self.CurveLength
            self.StartSliderGroup.SetValue(percent_of_length)
            self.BaseCurve = rg.Line(rg.Point3d.Origin, rg.Point3d(self.CurveLength, 0, 0)).ToNurbsCurve()
            if percent_of_length < 0.50:
                self.BaseCurve.Reverse()
                self.StartSliderGroup.Unsubscribe(self.Solve)
                self.StartSliderGroup.SetValue(1 - self.StartPos)
                self.StartSliderGroup.Subscribe(self.Solve)
                self.StartPos = self.StartSliderGroup.Value
            # self.FlipCurveCheckBox.Checked = False

            try:
                self.Solve(sender)
            except Exception as e:
                Rhino.RhinoApp.WriteLine(str(e))        
        else:
            rs.MessageBox('No curve selected')

    def SetSurface(self, sender):
        self.SurfaceID = rs.GetObject('Select surface', rs.filter.surface | rs.filter.polysurface | rs.filter.subd)
        if self.SurfaceID:
            geom = rs.coercegeometry(self.SurfaceID)
            if not isinstance(geom, Rhino.Geometry.Brep): geom = geom.ToBrep()
            self.Surface = geom

            try:
                self.Solve(sender)
            except Exception as e:
                Rhino.RhinoApp.WriteLine(str(e))
        else:
            rs.MessageBox('No surface selected.')

    def MeshFromBrep(self, brep):
        meshing_params = Rhino.Geometry.MeshingParameters.FastRenderMesh
        meshes = Rhino.Geometry.Mesh.CreateFromBrep(brep, meshing_params)
        the_mesh = Rhino.Geometry.Mesh()
        for mesh in meshes:
            the_mesh.Append(mesh)
        the_mesh.Normals.ComputeNormals()
        return the_mesh

    def AddEdgeCurves(self, brep):
        for edge in brep.Edges:
            crv = edge.DuplicateCurve()
            if crv.IsValid:
                self.EdgeCurves.append(crv)

    def AddEdgeCurves2(self, brep):
        for edge in brep.Edges:
            crv = edge.DuplicateCurve()
            if crv.IsValid:
                self.EdgeCurves2.append(crv)

    def AddEdgeCurves3(self, brep):
        for edge in brep.Edges:
            crv = edge.DuplicateCurve()
            if crv.IsValid:
                self.EdgeCurves3.append(crv)

    def GetExtendedCurve(self, crv, dist0, dist1):
        extended_crv = None

        # create curve with line extensions on each end
        crv0 = crv.Extend(rg.CurveEnd.Start, dist0, rg.CurveExtensionStyle.Line)
        self.TempObs.append(crv0)

        crv0 = crv0.Extend(rg.CurveEnd.End, dist1, rg.CurveExtensionStyle.Line)
        self.TempObs.append(crv0)

        # create curve with arc extensions on each end
        crv1 = crv.Extend(rg.CurveEnd.Start, dist0, rg.CurveExtensionStyle.Arc)
        self.TempObs.append(crv1)

        crv1 = crv1.Extend(rg.CurveEnd.End, dist1, rg.CurveExtensionStyle.Arc)
        self.TempObs.append(crv1)


        # get average between the arc and line curves and return that
        results = rg.Curve.CreateTweenCurves(crv0, crv1, 1, 0.001)
        if len(results) > 0:
            extended_crv = results[0]
        else:
            app.WriteLine('Could not create tween curve')

        return extended_crv
        
    def Solve(self, sender):
        self.DisposeObject(self.Sphere)
        self.DisposeObjects(self.PreviewGems)
        self.DisposeObjects(self.TextDots)
        self.DisposeRenderObjects()

        self.RenderObjects = []
        self.EdgeCurves = []
        self.EdgeCurves2 = []
        self.EdgeCurves3 = []
        self.OverlayObjects = []
        self.Sphere = None
        self.PreviewGems = []
        self.TextDots = []
        self.GemSizes = []

        # load gem if needed
        if not self.BasePreviewGem: self.LoadPreviewGem()

        # update inputs
        self.Mode = self.ModeDropDown.SelectedValue
        self.Alignment = self.AlignmentDropDown.SelectedValue
        self.FlipGems = self.FlipGemsCheckBox.Checked
        self.FlipDirection = self.FlipDirectionCheckBox.Checked
        self.GemSize = self.GemSizeSliderGroup.Value
        self.GemStartSize = self.GemStartSizeSliderGroup.Value
        self.GemEndSize = self.GemEndSizeSliderGroup.Value
        self.GemCount = int(self.GemCountSliderGroup.Value)
        self.Gap = self.GapSliderGroup.Value
        self.VerticalAdj = self.VerticalAdjustmentSliderGroup.Value

        self.StartPos = self.StartSliderGroup.Value + self.FineTuneSliderGroup.Value
        if self.StartPos > 1:
            self.StartPos = 1
        if self.StartPos < 0:
            self.StartPos = 0

        # calculate delta (only needed for tapered gems?)
        delta = 0
        if self.GemCount > 1: delta = (self.GemStartSize - self.GemEndSize) / (self.GemCount - 1)

        # get entered sizes
        self.ListSizes = []

        if self.Mode == 'List':
            if self.GemSizeListTextBox.Text != '':
                entered_sizes = self.GemSizeListTextBox.Text
                entered_sizes = entered_sizes.replace(' ', '')
                entered_sizes = entered_sizes.split(',')
                for i in range(len(entered_sizes)):
                    try:
                        sz = float(entered_sizes[i])
                        if sz < 0.5:
                            sz = 0.5
                            Rhino.RhinoApp.WriteLine('A size less than 0.5mm was entered. It will be replaced with 0.5mm')
                        self.ListSizes.append(sz)
                    except Exception as e:
                        Rhino.RhinoApp.WriteLine('Non-number inputs will be replaced with a size of 1.0mm')
                        self.ListSizes.append(1)
            else:
                Rhino.RhinoApp.WriteLine('No sizes were entered, so a single gem of size 1.0mm will be placed on the curve.')
                self.ListSizes.append(1)

        # add a dummy size (will be used in next part to prevent out-of-index error)
        self.ListSizes.append(0)

        # enable / disable controls as needed

        # gem points on curve
        if self.Curve and self.BaseCurve:
            self.GemPoints = []
            if sender == self.FlipDirectionCheckBox:
                self.BaseCurve.Reverse()
            if sender == self.FlipCurveCheckBox:
                self.BaseCurve.Reverse()
                # you have to unsubscribe from solve or 
                # changing the slider's value will trigger
                # solve again unnecessarily
                self.StartSliderGroup.Unsubscribe(self.Solve)
                self.StartSliderGroup.SetValue(1 - self.StartPos)
                self.StartSliderGroup.Subscribe(self.Solve)
                self.StartPos = self.StartSliderGroup.Value

            x = self.StartPos * self.CurveLength

            if self.Mode == 'Basic':
                # make points
                for i in range(self.GemCount):
                    pnt3d = rg.Point3d(x, 0, 0)
                    pnt = rg.Point(pnt3d)
                    flow_morph = rg.Morphs.FlowSpaceMorph(self.BaseCurve, self.Curve, False, self.FlipDirection, False)
                    flow_morph.Morph(pnt)
                    self.GemPoints.append(pnt.Location)
                    if self.FlipDirection:
                        x += self.GemSize + self.Gap
                        if x > self.CurveLength: break
                    else:
                        x -= self.GemSize + self.Gap
                        if x < 0: break

            elif self.Mode == 'Tapered':
                # make points
                radius = self.GemStartSize/2
                for i in range(self.GemCount):
                    pnt3d = rg.Point3d(x, 0, 0)
                    pnt = rg.Point(pnt3d)
                    flow_morph = rg.Morphs.FlowSpaceMorph(self.BaseCurve, self.Curve, False, self.FlipDirection, False)
                    flow_morph.Morph(pnt)
                    self.GemPoints.append(pnt.Location)
                    if self.FlipDirection:
                        x += radius + self.Gap + (radius - (delta/2))
                        radius -= delta/2
                        if x > self.CurveLength: break
                    else:
                        x -= radius + self.Gap + (radius - (delta/2))
                        radius -= delta/2
                        if x < 0: break

            elif self.Mode == 'List':
                # make points
                for i in range(len(self.ListSizes)-1):
                    pnt3d = rg.Point3d(x, 0, 0)
                    pnt = rg.Point(pnt3d)
                    flow_morph = rg.Morphs.FlowSpaceMorph(self.BaseCurve, self.Curve, False, self.FlipDirection, False)
                    flow_morph.Morph(pnt)
                    self.GemPoints.append(pnt.Location)
                    if self.FlipDirection:
                        x += self.ListSizes[i]/2 + self.Gap + self.ListSizes[i+1]/2
                        if x > self.CurveLength: break
                    else:
                        x -= self.ListSizes[i]/2 + self.Gap + self.ListSizes[i+1]/2
                        if x < 0: break

        # gem planes
        frames = []
        if len(self.GemPoints) > 0:
            for pnt in self.GemPoints:
                r, t = self.Curve.ClosestPoint(pnt)                
                if self.Surface:
                    y_axis = self.Curve.TangentAt(t)
                    z_axis = self.Surface.ClosestPoint(pnt, 0.001)[5]
                    pln = rg.Plane(pnt, z_axis)
                    angle = rg.Vector3d.VectorAngle(pln.YAxis, y_axis, pln)
                    pln.Rotate(angle + (0.5 * math.pi), pln.ZAxis)
                    # pln = rg.Plane.CreateFromNormalYup(pnt, z_axis, y_axis)
                    # pln.Rotate(math.radians(90), pln.ZAxis)
                else:
                    r, pln = self.Curve.PerpendicularFrameAt(t)
                    pln.Rotate(math.radians(-90), pln.XAxis)
                    pln.Rotate(math.radians(-90), pln.ZAxis)

                if self.FlipGems:
                    pln.Rotate(math.radians(180), pln.XAxis)
                    # pln.Flip()
                    # pln.Rotate(math.radians(90), pln.ZAxis)

                frames.append(pln)

        self.GemPlanes = frames

        # create gems
        if self.BasePreviewGem and len(self.GemPoints) > 0:
            for i in range(len(self.GemPoints)):
                # create the gem
                gem = self.BasePreviewGem.DuplicateBrep()

                # align to table, if needed
                if self.Alignment == 'Tables':
                    xform = rg.Transform.Translation(0,0,-1.85)
                    gem.Transform(xform)

                # scale the gem
                if self.Mode == 'Basic':
                    xform = rg.Transform.Scale(rg.Point3d.Origin, self.GemSize/10)
                    self.GemSizes.append(self.GemSize)
                elif self.Mode == 'Tapered':
                    size = 1
                    if i == 0: size = self.GemStartSize
                    else: size = self.GemStartSize - (i*delta)
                    size = round(size, 2)
                    xform = rg.Transform.Scale(rg.Point3d.Origin, size/10)
                    self.GemSizes.append(size)
                elif self.Mode == 'List':
                    size = self.ListSizes[i]
                    xform = rg.Transform.Scale(rg.Point3d.Origin, size/10)
                    self.GemSizes.append(size)
                gem.Transform(xform)
                
                # move it up / down
                xform = rg.Transform.Translation(0, 0, self.VerticalAdj)
                gem.Transform(xform)                    

                # move to plane on curve
                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, frames[i])
                gem.Transform(xform)
                self.PreviewGems.append(gem)

                # make render gem:
                mesh = self.MeshFromBrep(gem)
                if i == 0:
                    self.RenderObjects.append([mesh, cam.GemMaterialDark])
                else:
                    self.RenderObjects.append([mesh, cam.GemMaterialLight])

                # add edge curves
                if i == 0:
                    self.AddEdgeCurves2(gem)
                else:
                    self.AddEdgeCurves(gem)

                dot = rg.TextDot(str(self.GemSizes[i]), self.GemPoints[i])
                self.TextDots.append(dot)
                self.OverlayObjects.append([dot, None])

        if self.ShowProngsCheckBox.Checked and self.Curve:
            # get largest gem size
            max_size = 0
            for sz in self.GemSizes:
                if sz > max_size: max_size = sz

            crown_heights = []
            total_heights = []
            pavilion_depths = []
            for i in range(len(self.PreviewGems)):
                gem = self.PreviewGems[i]
                frame = frames[i]
                bbox = gem.GetBoundingBox(frame)
                total_height = bbox.Max.Z - bbox.Min.Z
                total_heights.append(total_height)
                crown_heights.append(0.35*total_height)
                pavilion_depths.append(0.65*total_height)

            # create north and south points
            north_points = []
            south_points = []
            for pln in frames:
                r = max_size / 2 + 2
                np = rg.Point3d(0, r, 0)
                sp = rg.Point3d(0, -r, 0)
                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, pln)
                np.Transform(xform)
                sp.Transform(xform)

                north_points.append(np)
                south_points.append(sp)

            # create north curve, center curve, and south curve
            north_curve = rg.Curve.CreateInterpolatedCurve(north_points, 3)
            self.TempObs.append(north_curve)

            center_curve = rg.Curve.CreateInterpolatedCurve(self.GemPoints, 3)
            self.TempObs.append(center_curve)

            south_curve = rg.Curve.CreateInterpolatedCurve(south_points, 3)
            self.TempObs.append(south_curve)

            # calculate the sizes of the dummy gems
            if self.ModeDropDown.SelectedValue == 'Basic':
                dummy_size_0 = self.GemSizes[0]
                dummy_size_1 = dummy_size_0 
            elif self.ModeDropDown.SelectedValue == 'Tapered':
                dummy_size_0 = self.GemSizes[0] + delta
                dummy_size_1 = self.GemSizes[-1] - delta
            else:
                # it's a list
                dummy_size_0 = self.GemSizes[1]
                dummy_size_1 = self.GemSizes[-2]

            # extend curves
            extend_length_0 = (self.GemSizes[0] / 2) + (dummy_size_0 / 2) + self.Gap
            extend_length_1 = (self.GemSizes[-1] / 2) + (dummy_size_1 / 2) + self.Gap

            north_curve = self.GetExtendedCurve(north_curve, extend_length_0, extend_length_1)
            self.TempObs.append(north_curve)

            center_curve = self.GetExtendedCurve(center_curve, extend_length_0, extend_length_1)
            self.TempObs.append(center_curve)

            south_curve = self.GetExtendedCurve(south_curve, extend_length_0, extend_length_1)
            self.TempObs.append(south_curve)

            # extension_style = rg.CurveExtensionStyle.Arc

            # north_curve = north_curve.Extend(rg.CurveEnd.Start, extend_length_0, extension_style)
            # self.TempObs.append(north_curve)

            # north_curve = north_curve.Extend(rg.CurveEnd.End, extend_length_1, extension_style)
            # self.TempObs.append(north_curve)

            # center_curve = center_curve.Extend(rg.CurveEnd.Start, extend_length_0, extension_style)
            # self.TempObs.append(center_curve)

            # center_curve = center_curve.Extend(rg.CurveEnd.End, extend_length_1, extension_style)
            # self.TempObs.append(center_curve)  

            # north_curve = north_curve.Extend(rg.CurveEnd.Start, extend_length_0, extension_style)
            # self.TempObs.append(north_curve)

            # south_curve = south_curve.Extend(rg.CurveEnd.End, extend_length_1, extension_style)
            # self.TempObs.append(south_curve)

            # make surface
            srf = None
            results = rg.Brep.CreateFromLoft([north_curve, south_curve], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)
            if results and len(results) == 1:
                srf = results[0]
            else:
                app.WriteLine('Could not make gem surface')

            if srf and self.FlipGems:
                srf.Flip()  

            # get extra two center points
            center_point_0 = center_curve.PointAtStart
            center_point_1 = center_curve.PointAtEnd

            # make spheres
            prong_size = self.ProngSizeSliderGroup.Value
            prong_radius = prong_size / 2
            prong_overlap = prong_size * self.OverlapSliderGroup.Value
            spheres = []
            spheres.append(rg.Sphere(center_point_0, dummy_size_0/2 + prong_radius - prong_overlap))
            for i in range(len(self.GemSizes)):
                spheres.append(rg.Sphere(self.GemPoints[i], self.GemSizes[i]/2 + prong_radius - prong_overlap))
            spheres.append(rg.Sphere(center_point_1, dummy_size_1/2 + prong_radius - prong_overlap))

            prong_pairs = len(self.GemPoints) + 1
            prong_point_pairs = []
            for i in range(prong_pairs):
                sphereA = spheres[i]
                sphereB = spheres[i+1]

                intersection_type, circle = rg.Intersect.Intersection.SphereSphere(sphereA, sphereB)
                if circle:
                    circle = circle.ToNurbsCurve()
                    self.TempObs.append(circle)

                    success, crvs, pnts = rg.Intersect.Intersection.CurveBrep(circle, srf, 0.001)
                    if success and len(pnts) == 2:
                        prong_point_pairs.append(pnts)

            # make prong cylinders
            srf_face = srf.Faces[0]
            for i in range(len(prong_point_pairs)):
                point_pair = prong_point_pairs[i]
                j = i if i < len(crown_heights) - 1 else i-1
                h = crown_heights[j]
                h2 = h * 1.2
                # # if self.Alignment == 'Girdles': h *= 2

                # d = pavilion_depths[j] # if not self.FlipGemsCheckBox.Checked else -pavilion_depths[j]
                d = pavilion_depths[j]
                th = total_heights[j]
                for pnt in point_pair:
                    success, u, v = srf_face.ClosestPoint(pnt)                    
                    normal = srf_face.NormalAt(u,v)
                    normal.Unitize()

                    pln = rg.Plane(pnt, normal)

                    prong = rg.Cylinder(rg.Circle(prong_radius), h2+d).ToBrep(True, True)
                    prong.Translate(0, 0, -(h2+d)/2)
                    self.TempObs.append(prong)

                    if 'Table' in self.Alignment:
                        prong.Translate(0, 0, -h)

                        if self.FlipGems:
                            prong.Translate(0, 0, 2*h)

                    xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, pln)
                    prong.Transform(xform)                    

                    mesh = self.MeshFromBrep(prong)
                    self.RenderObjects.append([mesh, cam.VeryTransparentProngMaterial])

                    self.AddEdgeCurves3(prong)
            

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