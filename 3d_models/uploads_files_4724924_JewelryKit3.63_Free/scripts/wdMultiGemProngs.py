#! python 2

import System
from System.Collections.Generic import List
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
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
import Rhino.RhinoApp as app
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

def IsGem(rhino_ob, geo, component_index):
    is_gem = False
    name = rhino_ob.Name
    if name == 'wdGem': is_gem = True
    return is_gem

class wdDialog(forms.Dialog):
    def __init__(self):
        super(wdDialog, self).__init__()
        # form stuff        
        self.LabelWidth = 90
        self.Title = 'Multi-Gem Prongs'
        self.Padding = drawing.Padding(15)
        self.AutoSize = True
        self.Layout = None
        self.Closing += self.OnDialogClosing
        if rs.ExeVersion() >= 8:
            Rhino.UI.EtoExtensions.UseRhinoStyle(self)

        # overlay visualization stuff
        self.Conduit = DrawConduit(self)
        self.Conduit.Enabled = True
        self.RenderObjects = []
        self.EdgeCurves = []
        self.Conduit.EdgeColor = cam.ProngColor
        self.TempObs = []

        # variables
        self.PushPickButton = None
        self.GemPlanes = []
        self.GemBoundingBoxes = []
        self.GemRadii = []
        self.CrownHeights = []
        self.PavilionDepths = []
        self.CenterPoints = []
        self.NorthPoints = []
        self.SouthPoints = []
        self.NorthProngPoints = []
        self.SouthProngPoints = []
        self.NorthNormals = []
        self.SouthNormals = []
        self.CenterCurve = None
        self.NorthCurve = None
        self.SouthCurve = None
        self.Points = []
        self.GemIDs = []
        self.Prongs = []
        self.Spheres = []
        self.Surface = None
        self.MinProngSize = 0.4
        self.MaxProngSize = 2.0
        self.ProngSizes = []
        self.ProngStartSize = 0.8
        self.ProngEndSize = 0.5
        self.ProngHeight = 0.0
        self.ProngDepth = 0.1
        self.ProngPoints1 = []
        self.ProngPoints2 = []
        self.ProngMeshes = []
        self.Overlap = 0.2
        self.MaxOverlap = 0.5
        self.NorthPlanes = []
        self.SouthPlanes = []
        self.ProngLines = []
        self.ListSizes = []
        self.TiltAngle = 0
        self.LargestY = 0
        self.AvgGap = 0
        self.Delta = 0
        self.ProngCutter = None
        self.BaseCurve = None
        self.BaseSurface = None
        self.BaseCenterPoints = []
        self.RotationAngle = 0
        self.Corner1 = None
        self.Corner2 = None

        # input controls
        self.ModeDropDownGroup, self.ModeDropDown = cg.CreateDropDownGroup('Mode: ', self.LabelWidth, ['Basic', 'Tapered', 'List'], self.OnFormChanged)    
        self.ProngSizeSliderGroup = cg.CreateSliderGroup('Prong Size: ', self.LabelWidth, self.MinProngSize, self.MaxProngSize, 2, self.ProngStartSize, self.Solve)
        self.ProngStartSizeSliderGroup = cg.CreateSliderGroup('Prong Start Size: ', self.LabelWidth, self.MinProngSize, self.MaxProngSize, 2, self.ProngStartSize, self.Solve)
        self.ProngEndSizeSliderGroup = cg.CreateSliderGroup('Prong End Size: ', self.LabelWidth, self.MinProngSize, self.MaxProngSize, 2, self.ProngEndSize, self.Solve)
        self.ProngSizeListTextBoxGroup, self.ProngSizeListTextBox = cg.CreateTextBoxGroup('Prong Size List: ', self.LabelWidth, '0.8, 0.9, 0.6', self.OnFormChanged)
        self.ProngHeightSliderGroup = cg.CreateSliderGroup('Prong Height: ', self.LabelWidth, -0.2, 3.0, 2, self.ProngHeight, self.Solve)
        self.ProngDepthSliderGroup = cg.CreateSliderGroup('Prong Depth: ', self.LabelWidth, 0.1, 10.0, 2, self.ProngDepth, self.Solve)
        # self.FilletSG = cg.CreateSliderGroup('Fillet (%): ', self.LabelWidth, 0, 95, 0, 95, self.Solve)
        self.FilletDDG, self.FilletDD = cg.CreateDropDownGroup('Fillet (%): ', self.LabelWidth, [0, 25, 50, 75, 100], self.OnFormChanged)
        self.TiltSliderGroup = cg.CreateSliderGroup('Tilt Angle: ', self.LabelWidth, -15.0, 15.0, 2, self.TiltAngle, self.Solve)
        self.RotationSliderGroup = cg.CreateSliderGroup('Rotation Angle: ', self.LabelWidth, -15.0, 15.0, 2, self.RotationAngle, self.Solve)
        self.FlareSG = cg.CreateSliderGroup('Flare (%): ', self.LabelWidth, 0.00, 50.00, 0, 0, self.Solve)
        # self.FlareDDG, self.FlareDD = cg.CreateDropDownGroup('Flare (%): ', self.LabelWidth, [0, 10, 20, 30, 40, 50], self.OnFormChanged)
        self.OverlapSliderGroup = cg.CreateSliderGroup('Overlap (%): ', self.LabelWidth, 0, 30, 2, 20, self.Solve)
        self.LinesDropDownGroup, self.LinesDropDown = cg.CreateDropDownGroup('Prongs / Lines: ', self.LabelWidth, ['Prongs Only', 'Prongs and Lines', 'Lines Only'], self.OnFormChanged)
        self.FlipCheckBoxGroup, self.FlipCheckBox = cg.CreateCheckBoxGroup('Flip Prongs: ', self.LabelWidth, False, self.OnFormChanged)
        
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


    def AddObjectsToDocument(self, objects, layer_name, layer_color, object_name = None):
        if not rs.IsLayer(layer_name):
            rs.AddLayer(layer_name, layer_color)

        layer = sc.doc.Layers.FindName(layer_name)
        atts = Rhino.DocObjects.ObjectAttributes()
        atts.LayerIndex = layer.Index
        
        obj_ids = []
        for obj in objects:
            obj_id = sc.doc.Objects.Add(obj, atts)
            if object_name:
                rs.ObjectName(obj_id, object_name)
            obj_ids.append(obj_id)

        if len(obj_ids) > 0:
            grp = rs.AddGroup()
            rs.AddObjectsToGroup(obj_ids, grp)

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
        if self.Layout:
            self.Layout.Clear()

        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)

        if self.ModeDropDown.SelectedValue == 'Basic':
            if rs.ExeVersion() == 6: self.Height = 540 #487 #406
            self.LayoutBasicForm()
        
        if self.ModeDropDown.SelectedValue == 'Tapered':
            if rs.ExeVersion() == 6: self.Height = 583 #520 #439
            self.LayoutTaperedForm()

        if self.ModeDropDown.SelectedValue == 'List':
            if rs.ExeVersion() == 6: self.Height = 539 #486 #405
            self.LayoutListForm()

        self.Layout.BeginVertical()
        self.Layout.AddSpace()
        self.Layout.AddSpace()
        self.Layout.AddRow(None, self.SetButton, self.FinalizeButton, self.CancelButton)
        self.Layout.EndVertical()

        self.Layout.Create()        
        self.Content = self.Layout

    def LayoutBasicForm(self):        
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.ProngSizeSliderGroup)
        self.Layout.AddRow(self.ProngHeightSliderGroup)
        self.Layout.AddRow(self.ProngDepthSliderGroup)
        self.Layout.AddRow(self.OverlapSliderGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.TiltSliderGroup)
        self.Layout.AddRow(self.RotationSliderGroup)
        self.Layout.AddRow(self.FlareSG)
        # self.Layout.AddRow(self.FlareDDG)
        self.Layout.AddRow(self.FilletDDG)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.LinesDropDownGroup)
        self.Layout.AddRow(self.FlipCheckBoxGroup)
            
        self.Layout.EndVertical()

    def LayoutListForm(self):        
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.ProngSizeListTextBoxGroup)
        self.Layout.AddRow(self.ProngHeightSliderGroup)
        self.Layout.AddRow(self.ProngDepthSliderGroup)
        self.Layout.AddRow(self.OverlapSliderGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.TiltSliderGroup)
        self.Layout.AddRow(self.RotationSliderGroup)
        self.Layout.AddRow(self.FlareSG) 
        # self.Layout.AddRow(self.FlareDDG)
        self.Layout.AddRow(self.FilletDDG)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.LinesDropDownGroup)
        self.Layout.AddRow(self.FlipCheckBoxGroup)       
            
        self.Layout.EndVertical()

    def LayoutTaperedForm(self):        
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.ProngStartSizeSliderGroup)
        self.Layout.AddRow(self.ProngEndSizeSliderGroup)
        self.Layout.AddRow(self.ProngHeightSliderGroup)
        self.Layout.AddRow(self.ProngDepthSliderGroup)
        self.Layout.AddRow(self.OverlapSliderGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.TiltSliderGroup)
        self.Layout.AddRow(self.RotationSliderGroup)
        self.Layout.AddRow(self.FlareSG)
        # self.Layout.AddRow(self.FlareDDG)
        self.Layout.AddRow(self.FilletDDG)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Layout.AddRow(self.LinesDropDownGroup)
        self.Layout.AddRow(self.FlipCheckBoxGroup)
            
        self.Layout.EndVertical()       
        
        
    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        if len(self.GemIDs) > 0 and 'Prongs' in self.LinesDropDown.SelectedValue:
            self.AddObjectsToDocument(self.Prongs, 'prongs', System.Drawing.Color.FromArgb(125, 40, 200), 'wdProng')

        if len(self.GemIDs) > 0 and 'Lines' in self.LinesDropDown.SelectedValue:
            self.AddObjectsToDocument(self.ProngLines, 'prong lines', System.Drawing.Color.FromArgb(200, 0, 0), 'wdProngLine')  

        sc.doc.Views.Redraw()
        self.DisposeObjects(self.GemPlanes)
        self.DisposeObject(self.NorthCurve)
        self.DisposeObject(self.SouthCurve)
        self.DisposeObject(self.CenterCurve)
        self.DisposeObject(self.BaseCurve)
        self.DisposeObject(self.BaseSurface)

        self.DisposeObjects(self.Spheres)
        self.DisposeObjects(self.Prongs)
        self.DisposeObjects(self.ProngMeshes)
        self.DisposeObject(self.ProngCutter)
        self.DisposeObjects(self.ProngLines)
        self.DisposeRenderObjects()
        self.Close()

    def OnFormChanged(self, sender, e):
        global is_free
        if sender == self.ModeDropDown:
            if is_free:
                if self.ModeDropDown.SelectedValue == 'Tapered':
                    self.ModeDropDown.SelectedIndex = 0
                    rs.MessageBox('Tapered mode is only available in the full version.')
                elif self.ModeDropDown.SelectedValue == 'List':
                    self.ModeDropDown.SelectedIndex = 0
                    rs.MessageBox('List mode is only available in the full version.')
                else:
                    self.LayoutForm()
                    self.Solve(sender)
            else:
                self.LayoutForm()
                self.Solve(sender)
        else:
            self.Solve(sender)

    def OnSetButtonClick(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        
    def OnPushPickButton(self, sender, e):
        self.SetGems(sender)

    def SetGems(self, sender):
        shape = None
        gem_ids = []
        selected_obs = rs.GetObjects('Select gems to add prongs to', rs.filter.polysurface, preselect = True, custom_filter = IsGem)
        if selected_obs:
            for ob in selected_obs:
                name = rs.ObjectName(ob)
                if name == 'wdGem':
                    gem_ids.append(ob)
        rs.UnselectAllObjects()

        if len(gem_ids) == 0:
            rs.MessageBox('No gems were selected.')
            shape = None
        else:
            # check that all selected gems are round
            all_round = True
            for i in range(len(gem_ids)):
                shape = rs.GetUserText(gem_ids[i], 'shape')
                if shape != 'Round':
                    all_round = False
                    break  
            if all_round:
                self.GemIDs = gem_ids
                self.ProcessGems(gem_ids)

            else:
                rs.MessageBox('All gems must be round.')

        try:
            self.Solve(sender)
        except Exception as e:
            app.WriteLine(str(e)) 

    def FormatVector(self, vector):
        return [str(vector.X), str(vector.Y), str(vector.Z)]

    def GetApproximateVectorsFromPlane(self, frame):
        vecx = rg.Vector3d(round(frame.XAxis.X,4), round(frame.XAxis.Y,4), round(frame.XAxis.Z,4))
        vecy = rg.Vector3d(round(frame.YAxis.X,4), round(frame.YAxis.Y,4), round(frame.YAxis.Z,4))
        vecz = rg.Vector3d(round(frame.ZAxis.X,4), round(frame.ZAxis.Y,4), round(frame.ZAxis.Z,4))
        return [vecx, vecy, vecz]

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


    def ProcessGems(self, gem_ids):
        self.DisposeObjects(self.GemPlanes)
        self.DisposeObject(self.NorthCurve)
        self.DisposeObject(self.SouthCurve)
        self.DisposeObject(self.CenterCurve)
        self.DisposeObject(self.BaseCurve)
        self.DisposeObject(self.BaseSurface)
        self.DisposeRenderObjects()

        self.CenterPoints = []
        self.NorthPoints = []
        self.SouthPoints = []
        self.GemPlanes = []
        self.GemBoundingBoxes = []
        self.GemRadii = []
        self.CrownHeights = []
        self.PavilionDepths = []
        self.NorthCurve = None
        self.SouthCurve = None
        self.CenterCurve = None
        self.Delta = 0
        self.AvgGap = 0
        self.BaseCurve = None
        self.BaseSurface = None
        self.BaseCenterPoints = []
        self.Corner1 = None
        self.Corner2 = None

        # get the gems' centers, planes, bounding boxes,
        #radii, crown heights and pavilion depths
        for i in range(len(gem_ids)):
            gem_id = gem_ids[i]

            # get gem's plane
            x_axis, y_axis, z_axis = SpatialData.GetAxisLinesFromData(gem_id)
            gem_pln = SpatialData.GetPlane(gem_id)
            self.GemPlanes.append(gem_pln)

            # # get gem's bounding box
            # gem = rs.coercebrep(gem_id)
            # gem_bbox = gem.GetBoundingBox(gem_pln)
            # self.GemBoundingBoxes.append(gem_bbox)

            # get gem's center point
            pnt = gem_pln.Origin
            self.CenterPoints.append(pnt)

            # get gem's data
            self.GemRadii.append(pnt.DistanceTo(x_axis.To))
            self.CrownHeights.append(pnt.DistanceTo(z_axis.From))
            self.PavilionDepths.append(pnt.DistanceTo(z_axis.To))
            
        # determine if gems are basic, tapered, or list
        is_basic = True
        is_tapered = False
        if abs(self.GemRadii[0] - self.GemRadii[len(self.GemRadii)-1]) <= 0.001:
            # could be basic or list
            for i in range(len(gem_ids)):
                if abs(self.GemRadii[0] - self.GemRadii[i]) > 0.001:
                    # treat it as a list
                    is_basic = False
        else:
            # could be tapered or list
            is_basic = False
            is_tapered = True
            self.Delta = (self.GemRadii[0] - self.GemRadii[len(self.GemRadii)-1]) / (len(self.GemRadii)-1)
            for i in range(len(gem_ids)-1):
                diff = self.GemRadii[i] - self.GemRadii[i+1]
                if abs(diff - self.Delta) > 0.01:
                    is_tapered = False

        # calculate radii of dummy gems
        iol = len(self.GemRadii)-1
        if is_basic:
            self.DummyRadius1 = self.GemRadii[0]
            self.DummyRadius2 = self.GemRadii[0]
        elif is_tapered:
            if self.GemRadii[0] > self.GemRadii[1]:
                self.DummyRadius1 = self.GemRadii[0] + self.Delta
            else:
                self.DummyRadius1 = self.GemRadii[0] - self.Delta

            if self.GemRadii[iol] < self.GemRadii[iol-1]:
                self.DummyRadius2 = self.GemRadii[iol] - self.Delta
            else:
                self.DummyRadius2 = self.GemRadii[iol] + self.Delta
        else:
            # it's a list of gems...
            # so the dummy gems will be the size of 2nd and next-to-last gems
            self.DummyRadius1 = self.GemRadii[1]
            self.DummyRadius2 = self.GemRadii[iol-1]

        self.DummyRadius1 = round(self.DummyRadius1, 3)
        self.DummyRadius2 = round(self.DummyRadius2, 3)

        # determine largest gem
        self.LargestY = 0
        for i in range(len(self.GemRadii)):
            if self.GemRadii[i] > self.LargestY: self.LargestY = self.GemRadii[i]
        self.LargestY += 1

        # get north and south points
        for pln in self.GemPlanes:
            # get gem's north point
            pnt = rg.Point3d(0, self.LargestY, 0)
            xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, pln)
            pnt.Transform(xform)
            self.NorthPoints.append(pnt) 
 

            # get gem's south point
            pnt = rg.Point3d(0, -self.LargestY, 0)
            xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, pln)
            pnt.Transform(xform)
            self.SouthPoints.append(pnt)
            
        # create the center curve, north curve, and south curve
        self.CenterCurve = rg.Curve.CreateInterpolatedCurve(self.CenterPoints, 3)
        self.TempObs.append(self.CenterCurve)
        self.NorthCurve = rg.Curve.CreateInterpolatedCurve(self.NorthPoints, 3)
        self.SouthCurve = rg.Curve.CreateInterpolatedCurve(self.SouthPoints, 3)

        # determine the gap size
        curve_length = self.CenterCurve.GetLength()
        total_gem_length = 0
        for i in range(len(self.GemRadii)):
            if i == 0 or i == len(self.GemRadii)-1:
                total_gem_length += self.GemRadii[i]
            else:
                total_gem_length += 2 * self.GemRadii[i]

        total_gap_length = curve_length - total_gem_length        
        gap_count = len(self.GemRadii)-1
        self.AvgGap = round(total_gap_length / gap_count, 2)

        # add dummy radii to gem radii list
        self.GemRadii.insert(0, self.DummyRadius1)
        self.GemRadii.append(self.DummyRadius2)

        # extend center curve to include dummy gems
        gem_count = len(self.GemRadii)
        length1 = self.GemRadii[1] + self.AvgGap + self.GemRadii[0]
        length2 = self.GemRadii[gem_count - 2] + self.AvgGap + self.GemRadii[gem_count - 1]
        # ext_style = rg.CurveExtensionStyle.Arc

        self.CenterCurve = self.GetExtendedCurve(self.CenterCurve, length1, length2)
        self.TempObs.append(self.CenterCurve)

        self.NorthCurve = self.GetExtendedCurve(self.NorthCurve, length1, length2)
        self.TempObs.append(self.NorthCurve)

        self.SouthCurve = self.GetExtendedCurve(self.SouthCurve, length1, length2)
        self.TempObs.append(self.SouthCurve)

        # self.CenterCurve = self.CenterCurve.Extend(rg.CurveEnd.Start, length1, ext_style)
        # self.CenterCurve = self.CenterCurve.Extend(rg.CurveEnd.End, length2, ext_style)

        # # extend the north and south curves
        # self.NorthCurve = self.NorthCurve.Extend(rg.CurveEnd.Start, length1, ext_style)
        # self.NorthCurve = self.NorthCurve.Extend(rg.CurveEnd.End, length2, ext_style)

        # self.SouthCurve = self.SouthCurve.Extend(rg.CurveEnd.Start, length1, ext_style)
        # self.SouthCurve = self.SouthCurve.Extend(rg.CurveEnd.End, length2, ext_style)
        
        # unitize the curves' domain
        # self.CenterCurve.Domain = rg.Interval(0,1)
        # self.NorthCurve.Domain = rg.Interval(0,1)
        # self.SouthCurve.Domain = rg.Interval(0,1)

        # reverse the north and south curves
        self.NorthCurve.Reverse()
        self.SouthCurve.Reverse()

        # refit the curves
        self.NorthCurve = self.NorthCurve.Fit(3, 0.001, 0.001)
        self.SouthCurve = self.SouthCurve.Fit(3, 0.001, 0.001)
        
        # create end line
        end_line = rg.Line(self.SouthCurve.PointAtStart, self.NorthCurve.PointAtStart).ToNurbsCurve()

        # create sweep two rails surface (brep)
        sweep_results = rg.Brep.CreateFromSweep(self.NorthCurve, self.SouthCurve, end_line, False, 0.001)
        if sweep_results and len(sweep_results) > 0:
            self.Surface = sweep_results[0]

        # get the u,v of first gem's center point
        gem_pln = self.GemPlanes[0]
        pnt = self.CenterPoints[0]
        success, u, v = self.Surface.Faces[0].ClosestPoint(pnt)        
        success, frame = self.Surface.Faces[0].FrameAt(u,v)

        # flip if necessary
        angle = rg.Vector3d.VectorAngle(gem_pln.ZAxis, frame.ZAxis)
        if angle == Rhino.RhinoMath.UnsetValue:
            angle = 0
        angle = math.degrees(angle)
        if angle > 178 and angle < 182:
            self.Surface.Flip()
            # print('flipped')

        # reverse U if necessary
        angle = rg.Vector3d.VectorAngle(frame.XAxis, gem_pln.XAxis)
        if angle == Rhino.RhinoMath.UnsetValue:
            angle = 0
        angle = math.degrees(angle)
        if angle > 178 and angle < 182:
            self.Surface.Faces[0].Reverse(0, True)
            # print('U reversed')

        # reverse V if necessary
        angle = rg.Vector3d.VectorAngle(frame.YAxis, gem_pln.YAxis)
        if angle == Rhino.RhinoMath.UnsetValue:
            angle = 0
        angle = math.degrees(angle)
        if angle > 178 and angle < 182:
            self.Surface.Faces[0].Reverse(1, True)        
            # print('V reversed')

        # get corner 2D point on original surface
        u_domain = self.Surface.Faces[0].Domain(0)
        v_domain = self.Surface.Faces[0].Domain(1)
        self.Corner1 = rg.Point2d(u_domain.Min, v_domain.Min)

        # unroll the surface 
        # (consider using Rhino's Unroller in future versions?)        
        srf_width = self.NorthCurve.PointAtEnd.DistanceTo(self.SouthCurve.PointAtEnd)
        srf_length = self.CenterCurve.GetLength()
        self.BaseSurface = rg.PlaneSurface(rg.Plane.WorldXY, rg.Interval(0, srf_length), rg.Interval(-srf_width/2, srf_width/2)).ToBrep()
        self.BaseSurface.Faces[0].SetDomain(0, rg.Interval(0,1))
        self.BaseSurface.Faces[0].SetDomain(1, rg.Interval(0,1))

        u_domain = self.BaseSurface.Faces[0].Domain(0)
        v_domain = self.BaseSurface.Faces[0].Domain(1)
        self.Corner2 = rg.Point2d(u_domain.Min, v_domain.Min)

        # create base curve
        self.BaseCurve = rg.Line(rg.Point3d.Origin, rg.Point3d(srf_length, 0, 0)).ToNurbsCurve()     
        
        # ends of center curve will be the center points of the dummy gems,
        # which we will add to the list of the center points
        self.CenterPoints.insert(0, rg.Point3d(self.CenterCurve.PointAtStart))
        self.CenterPoints.append(rg.Point3d(self.CenterCurve.PointAtEnd))     

        # make new 'gem planes' based on surface and center points
        self.GemPlanes = []
        for i in range(len(self.CenterPoints)):
            # rename point and surface
            pnt = self.CenterPoints[i]
            srf = self.Surface.Faces[0]
            # get u,v
            b, u, v = srf.ClosestPoint(pnt)

            # get isocurves at u,v
            iso_u = srf.IsoCurve(0, u)
            iso_v = srf.IsoCurve(1, v)

            # get t's at u,v
            b, t_u = iso_u.ClosestPoint(pnt)
            b, t_v = iso_v.ClosestPoint(pnt)

            # get tangents at u,v
            tan_u = iso_u.TangentAt(t_u)
            tan_v = iso_v.TangentAt(t_v)

            # get normal at u,v
            normal = srf.NormalAt(u, v)

            # get plane and add it to the list
            # pln = rg.Plane.CreateFromNormalYup(pnt, normal, tan_u)
            pln = rg.Plane(pnt, tan_u, tan_v)
            self.GemPlanes.append(pln) 
           
        self.Solve(self)

    def DistanceToCurve(self, pnt, curve):
        t = curve.ClosestPoint(pnt)[1]
        pnt2 = curve.PointAt(t)
        return(pnt.DistanceTo(pnt2))

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

    def Solve(self, sender):
        if len(self.GemIDs) > 0:
            # clear variables, disposing as needed
            self.DisposeObjects(self.Spheres)
            self.DisposeObjects(self.Prongs)
            self.DisposeObjects(self.ProngMeshes)
            self.DisposeObject(self.ProngCutter)
            self.DisposeObjects(self.ProngLines)
            self.DisposeObjects(self.TempObs)
            self.DisposeRenderObjects()

            self.ProngStartSize = self.ProngStartSizeSliderGroup.Value
            self.ProngEndSize = self.ProngEndSizeSliderGroup.Value
            self.ProngHeight = self.ProngHeightSliderGroup.Value
            self.ProngDepth = self.ProngDepthSliderGroup.Value
            self.TiltAngle = self.TiltSliderGroup.Value
            self.RotationAngle = self.RotationSliderGroup.Value
            self.Overlap = self.OverlapSliderGroup.Value/100
            self.NorthProngPoints = []
            self.SouthProngPoints = []
            self.ProngPoints1 = []
            self.ProngPoints2 = []
            self.NorthPlanes = []
            self.SouthPlanes = []
            self.NorthNormals = []
            self.SouthNormals = [] 
            self.EdgeCurves = []
            self.TempObs = []

            self.Spheres = []
            self.Prongs = []
            self.ProngMeshes = []
            self.ProngCutter = None
            self.ProngLines = []
            self.ProngSizes = []
            self.RenderObjects = []

            error_message = ''

            # calculate prong sizes        
            number_of_prong_pairs = len(self.GemIDs) + 1
            if self.ModeDropDown.SelectedValue == 'Basic':
                for i in range(number_of_prong_pairs):
                    self.ProngSizes.append(self.ProngSizeSliderGroup.Value)
            elif self.ModeDropDown.SelectedValue == 'Tapered':
                delta = 0
                if len(self.GemIDs) > 0: delta = (self.ProngStartSize - self.ProngEndSize) / (number_of_prong_pairs - 1)
                for i in range(number_of_prong_pairs):
                    prong_size = self.ProngStartSize - (i * delta)
                    self.ProngSizes.append(prong_size)
            elif self.ModeDropDown.SelectedValue == 'List':
                # convert entered text to list of sizes
                entered_sizes = self.ProngSizeListTextBox.Text
                entered_sizes = entered_sizes.replace(' ', '')
                if entered_sizes != '':                    
                    entered_sizes = entered_sizes.split(',')
                    for i in range(len(entered_sizes)):
                        try:
                            sz = float(entered_sizes[i])
                            if sz >= 0.4:
                                self.ProngSizes.append(sz)
                            else:
                                error_message = 'Prongs must be at least 0.4mm in diameter. You entered one or more sizes less than 0.4mm and those have been replaced with 0.4mm prongs'
                                app.WriteLine(error_message)
                                self.ProngSizes.append(0.4)                                    
                        except Exception as e:
                            error_message = 'The prong size list field contains one or more non-numbers. These have been replaced with 0.8mm prongs'
                            app.WriteLine(error_message)
                            self.ProngSizes.append(0.8)

                    # repeat last entered size, if needed
                    number_of_entered_sizes = len(self.ProngSizes)
                    last_entered_size = self.ProngSizes[number_of_entered_sizes-1]
                    if number_of_entered_sizes < number_of_prong_pairs:
                        diff = number_of_prong_pairs - len(self.ProngSizes)
                        for i in range(diff):
                            self.ProngSizes.append(last_entered_size)

                else:
                    app.WriteLine('No prong sizes have been entered. Therefore, all prong sizes are set to 0.8mm')
                    for i in range(number_of_prong_pairs):
                        self.ProngSizes.append(0.8)

            # get the prong points
            for i in range(number_of_prong_pairs):
                prong_radius = self.ProngSizes[i]/2
                center1 = self.CenterPoints[i]
                radius1 = self.GemRadii[i] - (prong_radius * (2 * self.Overlap)) + prong_radius
                sphere1 = rg.Sphere(center1, radius1)

                center2 = self.CenterPoints[i+1]
                radius2 = self.GemRadii[i+1] - (prong_radius * (2 * self.Overlap)) + prong_radius
                sphere2 = rg.Sphere(center2, radius2)

                intersection_type, circle = rg.Intersect.Intersection.SphereSphere(sphere1, sphere2)
                circle = circle.ToNurbsCurve()
                if circle:
                    b2, crvs2, pnts2 = rg.Intersect.Intersection.CurveBrep(circle, self.Surface, 0.001)

                    self.ProngPoints1.append(pnts2[0])
                    self.ProngPoints2.append(pnts2[1])

                    self.Spheres.append(sphere1)
                    
                    if i == number_of_prong_pairs-1:
                        self.Spheres.append(sphere2)
                else:
                    rs.MessageBox('Unable to create the prongs. Reordering the gems may correct this issue.')
                    break

            # make the prong planes
            flow_morph1 = rg.Morphs.SporphSpaceMorph(self.Surface.Faces[0], self.BaseSurface.Faces[0], self.Corner1, self.Corner2)
            flow_morph2 = rg.Morphs.SporphSpaceMorph(self.BaseSurface.Faces[0], self.Surface.Faces[0], self.Corner2, self.Corner1)
            for i in range(number_of_prong_pairs):
                # flow the prong points to the base surface
                pnt1 = flow_morph1.MorphPoint(self.ProngPoints1[i])
                pnt2 = flow_morph1.MorphPoint(self.ProngPoints2[i])

                north_point = None
                south_point = None
                if pnt1.Y > 0:
                    north_point = pnt1
                    south_point = pnt2
                else:
                    north_point = pnt2
                    south_point = pnt1

                north_plane = rg.Plane(rg.Plane.WorldXY)
                north_plane.Origin = north_point
                if self.TiltAngle != 0:
                    north_plane.Rotate(math.radians(-self.TiltAngle), north_plane.XAxis)
                if self.RotationAngle != 0:
                    north_plane.Rotate(math.radians(-self.RotationAngle), north_plane.YAxis)                
                if self.FlipCheckBox.Checked:
                    north_plane.Flip()
                    north_plane.Rotate(math.radians(90), north_plane.ZAxis)
                b, pln = flow_morph2.Morph(north_plane) 
                self.NorthPlanes.append(pln)               

                south_plane = rg.Plane(rg.Plane.WorldXY)
                south_plane.Origin = south_point
                if self.TiltAngle != 0:
                    south_plane.Rotate(math.radians(self.TiltAngle), south_plane.XAxis)
                if self.RotationAngle != 0:
                    south_plane.Rotate(math.radians(self.RotationAngle), south_plane.YAxis)
                if self.FlipCheckBox.Checked:
                    south_plane.Flip()
                    south_plane.Rotate(math.radians(90), south_plane.ZAxis)
                b, pln = flow_morph2.Morph(south_plane)
                self.SouthPlanes.append(pln)
             
            # create the prong lines and prongs
            for i in range(number_of_prong_pairs):
                prong_radius = self.ProngSizes[i]/2
                # find the taller gem for this prong pair
                # and give the prong that crown height as a base height
                prong_height = 0
                if i == 0:
                    prong_height = self.CrownHeights[i]
                elif i == number_of_prong_pairs - 1:
                    prong_height = self.CrownHeights[i-1]
                else:
                    height1 = self.CrownHeights[i]
                    height2 = self.CrownHeights[i-1]
                    prong_height = height1 if height1 > height2 else height2

                # add the user prong height input and prong radius to it
                prong_height += self.ProngHeight # + prong_radius

                # set the top points of the prongs
                north_top = rg.Point3d(0, 0, prong_height)
                south_top = rg.Point3d(0, 0, prong_height)

                # set the bottom points of the prongs
                north_btm = rg.Point3d(0, 0, -self.ProngDepth)
                south_btm = rg.Point3d(0, 0, -self.ProngDepth)

                # make a north line and a south line
                north_line = rg.Line(north_btm, north_top).ToNurbsCurve()
                north_line = north_line.Extend(rg.CurveEnd.Start, 1, rg.CurveExtensionStyle.Smooth)

                south_line = rg.Line(south_btm, south_top).ToNurbsCurve()
                south_line = south_line.Extend(rg.CurveEnd.Start, 1, rg.CurveExtensionStyle.Smooth)

                # make bottom circle of cone
                # flare_value = float(self.FlareDD.SelectedValue)
                flare_value = self.FlareSG.Value
                flare_amt = prong_radius * (flare_value/100) if flare_value > 0 else 0
                btm_radius = prong_radius + flare_amt
                circle_btm = rg.Circle(rg.Point3d(0,0,-self.ProngDepth), btm_radius).ToNurbsCurve()

                # make top circle of cone
                circle_top = rg.Circle(rg.Point3d(0,0,prong_height+prong_radius), prong_radius).ToNurbsCurve()

                # loft the circles
                cone = rg.Brep.CreateFromLoft([circle_top, circle_btm], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)[0]
                cone = cone.CapPlanarHoles(0.001)

                # fillet top edge
                fillet_amt = self.FilletDD.SelectedValue / 100
                if fillet_amt == 1: fillet_amt = 0.95
                if fillet_amt > 0:
                    cone = rg.Brep.CreateFilletEdges(cone, [2], [prong_radius * fillet_amt], [prong_radius * fillet_amt], rg.BlendType.Fillet, rg.RailType.DistanceFromEdge, 0.001)[0]

                north_prong = cone
                south_prong = cone.DuplicateBrep() 
                self.TempObs.append(cone) 


                # move prongs to their planes
                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, self.NorthPlanes[i])
                north_line.Transform(xform)
                north_prong.Transform(xform)

                xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, self.SouthPlanes[i])
                south_line.Transform(xform)
                south_prong.Transform(xform)                

                # add prongs and lines to array variables
                if "Lines" in self.LinesDropDown.SelectedValue:
                    self.ProngLines.append(north_line)            
                    self.ProngLines.append(south_line)

                if "Prongs" in self.LinesDropDown.SelectedValue:
                    self.Prongs.append(north_prong)
                    self.Prongs.append(south_prong)


        # for sphere in self.Spheres:
        #     self.RenderObjects.append([sphere, cam.CurveColor])

        for line in self.ProngLines:
            self.RenderObjects.append([line, cam.CurveColor])

        for prong in self.Prongs:
            prong_mesh = self.MeshFromBrep(prong)
            self.RenderObjects.append([prong_mesh, cam.ProngMaterial])
            self.AddEdgeCurves(prong)

        # for pnt in self.BaseCenterPoints:
        #     self.RenderObjects.append([pnt, cam.PointColor])

        # self.RenderObjects.append([self.BaseSurface, cam.VeryTransparentMaterial])

        # self.RenderObjects.append([self.Surface, cam.VeryTransparentMaterial])



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