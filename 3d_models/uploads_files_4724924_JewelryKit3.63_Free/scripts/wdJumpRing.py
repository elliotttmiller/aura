#! python 2

import System
from System.Collections.Generic import List
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import Rhino.Geometry as rg
import Rhino.RhinoApp as rapp
import os
import Eto
import Eto.Drawing as drawing
import Eto.Forms as forms
import math
from sliders import SliderGroup
from pipeline import DrawConduit
from pipeline import ColorsAndMaterials as cam
from components import ComponentGenerator as cg

macro = rs.AliasMacro('wdGem')
wd1gem_script = macro.replace('!_-RunPythonScript ', '')
wd1gem_script = wd1gem_script.replace('"', '')
script_folder = os.path.dirname(wd1gem_script)
data_folder = os.path.join(script_folder, "data")

is_free = False
if "Free" in script_folder:
    is_free = True

round_gauges = ["0.40 mm (26 ga)", "0.50 mm (24 ga)", "0.65 mm (22 ga)", "0.80 mm (20 ga)", "1.00 mm (18 ga)", "1.30 mm (16 ga)"]
round_sizes = [
    ['0.8 mm', '1.0 mm', '1.1 mm', '1.3 mm', '1.6 mm', '2.0 mm'],
    ['1.0 mm', '1.1 mm', '1.3 mm', '1.6 mm', '2.0 mm', '2.5 mm', '2.8 mm', '3.0 mm'],
    ['1.0 mm', '1.1 mm', '1.3 mm', '1.6 mm', '2.0 mm', '2.5 mm', '2.8 mm', '3.0 mm', '3.5 mm', '4.0 mm', '4.5 mm', '5.0 mm', '5.5 mm', '6.0 mm'],
    ['1.6 mm', '2.0 mm', '2.5 mm', '2.8 mm', '3.0 mm', '3.5 mm', '4.0 mm', '4.5 mm', '5.0 mm', '5.5 mm', '6.0 mm', '6.5 mm', '7.0 mm', '7.5 mm', '8.0 mm', '8.5 mm', '9.0 mm', '10.0 mm'],
    ['1.6 mm', '2.0 mm', '2.5 mm', '2.8 mm', '3.0 mm', '3.5 mm', '4.0 mm', '4.5 mm', '5.0 mm', '5.5 mm', '6.0 mm', '6.5 mm', '7.0 mm', '7.5 mm', '8.0 mm', '8.5 mm', '9.0 mm'],
    ['5.0 mm', '5.5 mm', '6.0 mm', '6.5 mm', '7.0 mm', '7.5 mm', '8.0 mm', '8.5 mm', '9.0 mm']
]

oval_gauges = ["0.40 mm (26 ga)", "0.50 mm (24 ga)", "0.65 mm (22 ga)", "0.80 mm (20 ga)", "1.00 mm (18 ga)"]
oval_sizes = [
    ["2.4 mm x 1.7 mm"],
    ["2.5 mm x 1.5 mm", "3.0 mm x 2.0 mm", "4.0 mm x 2.0 mm", "5.0 mm x 3.0 mm", "6.0 mm x 4.0 mm"],
    ["2.0 mm x 1.4 mm ", "2.0 mm x 1.7 mm", "2.5 mm x 1.5 mm", "3.0 mm x 2.0 mm", "4.0 mm x 2.0 mm", "5.0 mm x 3.0 mm", "5.5 mm x 3.8 mm", "6.0 mm x 4.0 mm"],
    ["2.2 mm x 1.6 mm", "2.5 mm x 1.5 mm", "3.0 mm x 2.0 mm", "4.0 mm x 2.0 mm", "5.0 mm x 3.0 mm", "5.0 mm x 3.2 mm", "6.0 mm x 4.0 mm"],
    ["4.2 mm x 2.2 mm", "5.5 mm x 3.3 mm", "6.3 mm x 4.0 mm"]
]           

               
class wdDialog(forms.Dialog):
    def __init__(self):
        super(wdDialog, self).__init__()
        # form stuff        
        self.Title = 'Jump Ring Builder'
        self.Padding = drawing.Padding(15)
        self.AutoSize = False if rs.ExeVersion() < 7 else True
        self.Layout = None
        self.Closing += self.OnDialogClosing
        if rs.ExeVersion() >= 8:
            Rhino.UI.EtoExtensions.UseRhinoStyle(self)

        # overlay visualization stuff
        self.Conduit = DrawConduit(self)
        self.Conduit.Enabled = True
        self.RenderObjects = []
        self.EdgeCurves = []
        self.Conduit.EdgeColor = cam.PointColor2

        # inputs
        self.Mode = 'Common'
        self.SelectedLocation = None
        self.JumpRingShape = 'Round'
        self.WireStyle = 'Round'
        self.WireSize = 0.8
        self.InnerWidth = 2.0
        self.InnerLength = 4.0
        self.FilletFactor = 0.25

        # outputs
        # NOTE: Profile2 and Rail2 are scaled up a tad to prevent z-fighting
        self.JumpRing = None
        self.JumpRingMesh = None
        self.Profile = None
        self.Profile2 = None
        self.Plane = None
        self.Rail = None
        self.Rail2 = None 

        # constants
        self.TextBoxWidth = 170
        self.LabelWidth = 70      
        
        # input controls
        self.ModeDropDownGroup, self.ModeDropDown =  self.CreateDropDownGroup('Mode: ', ['Common', 'Basic', 'Sliders']) 
        self.JumpRingShapeDropDownGroup, self.JumpRingShapeDropDown = self.CreateDropDownGroup('Shape: ', ['Round', 'Ellipse'])
        self.WireStyleDropDownGroup, self.WireStyleDropDown =  self.CreateDropDownGroup('Wire Style: ', ['Round', 'Square']) 

        self.WireSizeDropDownGroup, self.WireSizeDropDown = self.CreateDropDownGroup('Wire Size: ', round_gauges) 
        self.InnerSizeDropDownGroup, self.InnerSizeDropDown = self.CreateDropDownGroup('Inner Size: ', round_sizes[0])

        self.WireSizeTextBoxGroup, self.WireSizeTextBox = self.CreateTextBoxGroup('Wire Size: ', '0.8', self.TextBoxWidth)
        self.InnerWidthTextBoxGroup, self.InnerWidthTextBox = self.CreateTextBoxGroup('Inner Width: ', '1.6', self.TextBoxWidth)
        self.InnerLengthTextBoxGroup, self.InnerLengthTextBox = self.CreateTextBoxGroup('Inner Length: ', '2.2', self.TextBoxWidth)

        self.WireSizeSliderGroup = self.CreateSliderGroup('Wire Size: ', 0.4, 2.0, 2, self.WireSize)
        self.InnerWidthSliderGroup = self.CreateSliderGroup('Inner Width: ', 0.5, 15, 2, self.InnerWidth)
        self.InnerLengthSliderGroup = self.CreateSliderGroup('Inner Length: ', 0.5, 15, 2, self.InnerLength)
        self.FilletFactorSliderGroup = self.CreateSliderGroup('Fillet Factor: ', 0.0, 0.49, 2, self.FilletFactor)
        
        # bottom buttons
        self.SetButton = self.CreateButton('Set Location', self.OnSet)  
        self.FinalizeButton = self.CreateButton('Finalize', self.OnFinalizeButtonClick)
        self.CancelButton = self.CreateButton('Cancel', self.OnCancelButtonClick)

        # the default button must be set for Macs (might as well set the abort button, too.)
        self.DefaultButton = self.SetButton
        self.AbortButton = self.CancelButton
        
        # lay it out and run the solver
        self.LayoutForm()
        self.Solve(self)
        
    def CreateButton(self, text, handler):
        btn = forms.Button()
        btn.Text = text
        btn.Click += handler
        return btn
        
    def CreateDropDown(self, data):
        dd = forms.DropDown()
        dd.DataStore = data
        dd.SelectedIndex = 0
        dd.SelectedValueChanged += self.OnFormChanged
        return dd
        
    def CreateDropDownGroup(self, text, choices):
        pnl = forms.Panel()
        pnl.Padding = drawing.Padding(5)
        lbl = self.CreateLabel(text, self.LabelWidth)
        dd = self.CreateDropDown(choices)
        
        pnl_layout = forms.DynamicLayout()
        pnl_layout.DefaultSpacing = drawing.Size(5,5)
        pnl_layout.BeginHorizontal()
        pnl_layout.AddAutoSized(lbl)
        pnl_layout.AddAutoSized(dd)
        pnl_layout.EndHorizontal()
        pnl.Content = pnl_layout
        
        return pnl, dd
        
    def CreateLabel(self, text, width=None):
        lbl = forms.Label()
        lbl.Text = text
        if width: lbl.Width = width
        lbl.TextAlignment = forms.TextAlignment.Right
        return lbl
        
    def CreateSliderGroup(self, text, min, max, decimals, value):
        sg = SliderGroup()
        sg.Label.Text = text
        sg.Label.Width = self.LabelWidth
        sg.SetMinMax(min, max)
        sg.SetDecimalPlaces(decimals)
        sg.SetValue(value)
        sg.Slider.TickFrequency = 0
        sg.Subscribe(self.Solve)
        return sg

    def CreateTextBoxGroup(self, label_text, values, width):
        pnl = forms.Panel()
        pnl.Padding = drawing.Padding(5)
        lbl = self.CreateLabel(label_text, self.LabelWidth)
        tb = forms.TextBox()
        tb.Width = width
        tb.Text = values
        tb.TextChanged += self.OnFormChanged

        pnl_layout = forms.DynamicLayout()
        pnl_layout.DefaultSpacing = drawing.Size(5,5)
        pnl_layout.BeginHorizontal()
        pnl_layout.AddAutoSized(lbl)
        pnl_layout.AddAutoSized(tb)
        pnl_layout.EndHorizontal()
        pnl.Content = pnl_layout

        return pnl, tb
        
    def CreateVerticalSpacer(self, width):
        pnl = forms.Panel()
        pnl.Width = width
        return pnl

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
    
    def GetValue(self, txt):
        value = 0.0
        try:
            value = float(txt)
        except:
            value = 0.0
        return value
        
    def LayoutForm(self):
        if self.Layout:
            self.Layout.Clear()
        
        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)
        
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)
        self.Layout.AddRow(self.JumpRingShapeDropDownGroup)
        self.Layout.AddRow(self.WireStyleDropDownGroup)
        self.Layout.AddRow(None)

        if self.Mode == 'Common':
            if rs.ExeVersion() < 7:
                self.Height = 299
                self.Width = 298
            self.Layout.AddRow(self.WireSizeDropDownGroup)
            self.Layout.AddRow(self.InnerSizeDropDownGroup)
        elif self.Mode == 'Basic':
            if rs.ExeVersion() < 7:
                self.Height = 303
                self.Width = 303
            self.Layout.AddRow(self.WireSizeTextBoxGroup)
            self.Layout.AddRow(self.InnerWidthTextBoxGroup)
            if self.JumpRingShape == 'Ellipse':
                self.Layout.AddRow(self.InnerLengthTextBoxGroup)
                if rs.ExeVersion() < 7: self.Height += 38
        elif self.Mode == 'Sliders':
            if rs.ExeVersion() < 7:
                self.Height = 293
                self.Width = 380
            self.Layout.AddRow(self.WireSizeSliderGroup)
            self.Layout.AddRow(self.InnerWidthSliderGroup)
            if self.JumpRingShape == 'Ellipse':
                self.Layout.AddRow(self.InnerLengthSliderGroup)
                if rs.ExeVersion() < 7: self.Height += 33
        
        if self.WireStyle == 'Square':
            self.Layout.AddRow(self.FilletFactorSliderGroup) 
            if rs.ExeVersion() < 7:
                self.Height += 33
                self.Width = 380

        self.Layout.EndVertical()
        
        self.Layout.BeginVertical()
        self.Layout.AddRow(cg.CreateVerticalSpacer(15))
        self.Layout.AddSpace()
        self.Layout.AddRow(None, self.SetButton, self.FinalizeButton, self.CancelButton)
        self.Layout.EndVertical()
        
        self.Layout.Create()
        
        self.Content = self.Layout
        
    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        if self.SelectedLocation:
            sc.doc.Objects.AddPoint(self.SelectedLocation)
            if self.JumpRing:
                sc.doc.Objects.AddBrep(self.JumpRing)
            sc.doc.Views.Redraw()

        self.DisposeObject(self.JumpRing)
        self.DisposeObject(self.JumpRingMesh)
        self.DisposeObject(self.Profile)
        self.DisposeObject(self.Profile2)
        self.DisposeObject(self.Plane)
        self.DisposeObject(self.Rail)
        self.DisposeObject(self.Rail2)
        self.DisposeRenderObjects()
        self.Close()

    def OnFormChanged(self, sender, e):
        self.Mode = self.ModeDropDown.SelectedValue
        self.JumpRingShape = self.JumpRingShapeDropDown.SelectedValue
        self.WireStyle = self.WireStyleDropDown.SelectedValue

        if sender == self.JumpRingShapeDropDown:
            if self.JumpRingShape == 'Round':
                self.WireSizeDropDown.DataStore = round_gauges
                self.InnerSizeDropDown.DataStore = round_sizes[0]
                self.InnerSizeDropDown.SelectedIndex = 1
            elif self.JumpRingShape == 'Ellipse':
                self.WireSizeDropDown.DataStore = oval_gauges
                self.InnerSizeDropDown.DataStore = oval_sizes[0]
                self.InnerSizeDropDown.SelectedIndex = 0

        if self.Mode == 'Common' and sender == self.WireSizeDropDown:
            if self.JumpRingShape == 'Round':
                self.InnerSizeDropDown.DataStore = round_sizes[self.WireSizeDropDown.SelectedIndex]
                self.InnerSizeDropDown.SelectedIndex = 0
            elif self.JumpRingShape == 'Ellipse':
                self.InnerSizeDropDown.DataStore = oval_sizes[self.WireSizeDropDown.SelectedIndex]
                self.InnerSizeDropDown.SelectedIndex = 0

        if sender == self.ModeDropDown or sender == self.JumpRingShapeDropDown or sender == self.WireStyleDropDown:
            self.LayoutForm()

        try:
            self.Solve(sender)
        except Exception as e:
            Rhino.RhinoApp.WriteLine(str(e))
        
    def OnSet(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        
    def OnPushPickButton(self, sender, e):
        self.SetLocation(sender)
        
    def SetLocation(self, sender):
        self.SelectedLocation = rs.GetPoint('Select a location')
        self.Plane = sc.doc.Views.ActiveView.ActiveViewport.GetConstructionPlane().Plane
        self.Plane.Origin = self.SelectedLocation
        self.AxisLine = rg.Line(self.Plane.Origin, self.Plane.ZAxis, 1.0)
        try:
            self.Solve(sender)
        except Exception as e:
            Rhino.RhinoApp.WriteLine(str(e))

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
        self.DisposeObject(self.JumpRing)
        self.DisposeObject(self.JumpRingMesh)
        self.DisposeObject(self.Profile)
        self.DisposeObject(self.Profile2)
        self.DisposeObject(self.Plane)
        self.DisposeObject(self.Rail)
        self.DisposeObject(self.Rail2)
        self.DisposeRenderObjects()

        self.Rail = None
        self.Rail2 = None
        self.Profile = None
        self.Profile2 = None
        self.JumpRing = None
        self.JumpRingMesh = None
        self.RenderObjects = []
        self.EdgeCurves = []

        # update inputs
        self.JumpRingShape =  self.JumpRingShapeDropDown.SelectedValue
        self.WireStyle = self.WireStyleDropDown.SelectedValue

        if self.Mode == 'Common':
            sz = self.WireSizeDropDown.SelectedValue
            sz = sz.split(' ')[0]
            self.WireSize = float(sz)

            if self.JumpRingShape == 'Round':
                sz = self.InnerSizeDropDown.SelectedValue
                if sz:
                    sz = sz.split(' ')[0]
                    self.InnerWidth = float(sz)
            elif self.JumpRingShape == 'Ellipse':
                sz = self.InnerSizeDropDown.SelectedValue
                if sz:
                    sz = sz.split(' ')
                    self.InnerWidth = float(sz[3])
                    self.InnerLength = float(sz[0])

        elif self.Mode == 'Basic':
            self.WireSize = self.GetValue(self.WireSizeTextBox.Text)
            self.InnerWidth = self.GetValue(self.InnerWidthTextBox.Text)
            self.InnerLength = self.GetValue(self.InnerLengthTextBox.Text)
        elif self.Mode == 'Sliders':
            self.WireSize = self.WireSizeSliderGroup.Value
            self.InnerWidth = self.InnerWidthSliderGroup.Value        
            self.InnerLength = self.InnerLengthSliderGroup.Value  

        self.FilletFactor = self.FilletFactorSliderGroup.Value

        if self.WireSize > 0:

            # update calculated values
            self.WireRadius = self.WireSize / 2
            self.RadiusX = self.InnerWidth / 2
            self.RadiusY = self.InnerLength / 2
            
            # if a location has been selected, let's do some solving...
            if self.SelectedLocation:
                # the profile plane  
                self.ProfilePlane = self.Plane.Clone()
                xform = rg.Transform.Rotation(math.radians(90), self.Plane.XAxis, self.Plane.Origin)
                self.ProfilePlane.Transform(xform)
                vec = rg.Vector3d.Multiply(self.RadiusX + self.WireRadius, self.Plane.XAxis)
                xform = rg.Transform.Translation(vec)
                self.ProfilePlane.Transform(xform)

                # the profile shape
                if self.WireStyle == 'Round':
                    self.Profile = rg.Circle(rg.Plane.WorldXY, self.WireRadius).ToNurbsCurve()
                    xform = rg.Transform.Rotation(math.radians(180), rg.Point3d.Origin)
                    self.Profile.Transform(xform)
                    xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, self.ProfilePlane)
                    self.Profile.Transform(xform)
                else:
                    interval1 = rg.Interval(-self.WireRadius, self.WireRadius)
                    interval2 = rg.Interval(-self.WireRadius, self.WireRadius)
                    self.Profile = rg.Rectangle3d(rg.Plane.WorldXY, interval1, interval2).ToNurbsCurve()
                    p = rg.Point3d(-self.WireRadius, 0, 0)
                    rs, t = self.Profile.ClosestPoint(p)
                    self.Profile.ChangeClosedCurveSeam(t)
                    if self.FilletFactor > 0:
                        self.Profile = rg.Curve.CreateFilletCornersCurve(self.Profile, self.WireSize * self.FilletFactor, 0.001, 0.001)
                    xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, self.ProfilePlane)
                    self.Profile.Transform(xform)

                # the jump ring             
                if self.JumpRingShape == 'Round': 
                    self.Rail = rg.Circle(self.Plane, self.RadiusX).ToNurbsCurve()             
                    self.JumpRing = rg.NurbsSurface.CreateRailRevolvedSurface(self.Profile, self.Rail, self.AxisLine, False).ToBrep()
                else:
                    self.Rail = rg.Ellipse(self.Plane, self.RadiusX, self.RadiusY).ToNurbsCurve() 
                    self.JumpRing = rg.Brep.CreateFromSweep(self.Rail, self.Profile, True, 0.001)[0]

                # the jumpring mesh, rail and profile for visualizing  
                self.JumpRingMesh = self.MeshFromBrep(self.JumpRing)

                # render objects
                self.RenderObjects.append([self.JumpRingMesh, cam.GeneralMaterial])
                self.AddEdgeCurves(self.JumpRing)

                # self.JumpRingMesh = rg.Mesh.CreateFromBrep(self.JumpRing, rg.MeshingParameters.Smooth)[0]

                # self.Rail2 = self.Rail.DuplicateCurve()
                # xform = rg.Transform.Scale(self.Plane.Origin, 0.99)
                # self.Rail2.Transform(xform)

                # self.Profile2 = self.Profile.DuplicateCurve()
                # xform = rg.Transform.Scale(self.ProfilePlane.Origin,1.01)
                # self.Profile2.Transform(xform)

                # render objects
                # if self.Rail: self.RenderObjects.append([self.Rail, cam.PointColor])
                # if self.Rail2: self.RenderObjects.append([self.Rail2, cam.PointColor])
                # if self.Profile: self.RenderObjects.append([self.Profile, cam.PointColor])
                # if self.Profile2: self.RenderObjects.append([self.Profile2, cam.PointColor])
                # # if self.JumpRing: self.RenderObjects.append([self.JumpRing, cam.GeneralMaterial])
                # if self.JumpRingMesh: self.RenderObjects.append([self.JumpRingMesh, cam.GeneralMaterial])
        else:
            self.Rail = None
            self.Rail2 = None
            self.Profile = None
            self.Profile2 = None
            self.JumpRing = None
            self.JumpRingMesh = None


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