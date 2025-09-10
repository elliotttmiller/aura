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

               
class wdDialog(forms.Dialog):
    def __init__(self):
        super(wdDialog, self).__init__()
        # form stuff        
        self.LabelWidth = 100
        self.Title = 'Ring Shape Tool'
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
        self.TempObs = []

        # handy variables
        self.SizingCircle = None
        self.FingerRadius = 0
        self.LeftPoint = None
        self.RightPoint = None
        self.BottomPoint = None
        self.TopPoint = None
        self.TopPoint2 = None
        self.BlendLine = None
        self.RingShape = None
       
        # input controls 
        self.ModeDropDownGroup, self.ModeDropDown = cg.CreateDropDownGroup('Mode: ', self.LabelWidth, ['Offset', 'Bottom Only', 'Full (Basic)', 'Full (Advanced)'], self.OnFormChanged, default_index = 2)
        self.BottomStyleDropDownGroup, self.BottomStyleDropDown = cg.CreateDropDownGroup('Bottom Style: ', self.LabelWidth, ['Arc', 'Ellipse'], self.OnFormChanged)
        # self.TopStyleDropDownGroup, self.TopStyleDropDown = cg.CreateDropDownGroup('Top Style: ', self.LabelWidth, ['Sharp', 'Smooth'], self.OnFormChanged)
        self.OffsetSliderGroup = cg.CreateSliderGroup('Offset Amount: ', self.LabelWidth, 0.8, 3.0, 2, 1.8, self.Solve)
        self.SideThicknessSliderGroup = cg.CreateSliderGroup('Side Thickness: ', self.LabelWidth, 0.8, 3.0, 2, 1.8, self.Solve)       
        self.BottomThicknessSliderGroup = cg.CreateSliderGroup('Bottom Thickness: ', self.LabelWidth, 0.8, 3.0, 2, 1.6, self.Solve)   
        self.TopThicknessSliderGroup = cg.CreateSliderGroup('Top Height: ', self.LabelWidth, 0.8, 10.0, 2, 3.0, self.Solve)   
        self.TopWidthSliderGroup = cg.CreateSliderGroup('Top Width: ', self.LabelWidth, 0.0, 20.0, 2, 0.0, self.Solve)
        self.AngleSliderGroup =  cg.CreateSliderGroup('Top Angle: ', self.LabelWidth, 0, 135, 2, 0, self.Solve) 
        self.SideInfluenceSliderGroup = cg.CreateSliderGroup('Side Influence: ', self.LabelWidth, 0.0, 1.0, 2, 0.4, self.Solve) 
        self.TopInfluenceSliderGroup = cg.CreateSliderGroup('Top Influence: ', self.LabelWidth, 0.0, 1.0, 2, 0.4, self.Solve) 
        self.ConnectCheckBoxGroup, self.ConnectCheckBox = cg.CreateCheckBoxGroup('Connect: ', self.LabelWidth, False, self.OnFormChanged) 
        self.SmoothCheckBoxGroup, self.SmoothCheckBox = cg.CreateCheckBoxGroup('Smooth: ', self.LabelWidth, True, self.OnFormChanged)   

        # bottom buttons
        self.SetButton = cg.CreateButton('Set Sizing Circle', self.OnSetButtonClick)
        self.SetButton.Width = 128
        self.FinalizeButton = cg.CreateButton('Finalize', self.OnFinalizeButtonClick)
        self.FinalizeButton.Enabled = False
        self.CancelButton = cg.CreateButton('Cancel', self.OnCancelButtonClick)

        # the default button must be set for Macs (might as well set the abort button, too.)
        self.DefaultButton = self.SetButton
        self.AbortButton = self.CancelButton
        
        # lay it out and run the solver
        self.LayoutForm()
        self.Solve(self)
        
    def LayoutForm(self):  
        if rs.ExeVersion <= 6:
            if self.ModeDropDown.SelectedValue == 'Offset':
                self.Height = 202
            elif self.ModeDropDown.SelectedValue == 'Bottom Only':
                self.Height = 266
            elif self.ModeDropDown.SelectedValue == 'Full (Basic)':
                self.Height = 396
            elif self.ModeDropDown.SelectedValue == 'Full (Advanced)':
                self.Height = 464           
                
    
        if self.Layout:
            self.Layout.Clear()

        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)

        self.Layout.BeginVertical()
        self.Layout.AddRow(self.ModeDropDownGroup)

        if self.ModeDropDown.SelectedValue != 'Offset':
            self.Layout.AddRow(self.BottomStyleDropDownGroup)

        self.Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Layout.AddRow(cg.CreateHR())
        self.Layout.AddRow(cg.CreateVerticalSpacer(5))

        if self.ModeDropDown.SelectedValue == 'Offset':
            self.Layout.AddRow(self.OffsetSliderGroup)
        elif self.ModeDropDown.SelectedValue == 'Bottom Only':
            self.Layout.AddRow(self.SideThicknessSliderGroup)
            self.Layout.AddRow(self.BottomThicknessSliderGroup)
        elif 'Basic' in self.ModeDropDown.SelectedValue:
            self.Layout.AddRow(self.SideThicknessSliderGroup)
            self.Layout.AddRow(self.BottomThicknessSliderGroup)
            self.Layout.AddRow(self.TopThicknessSliderGroup)
            self.Layout.AddRow(self.TopWidthSliderGroup)
            self.Layout.AddRow(self.SmoothCheckBoxGroup)
            self.Layout.AddRow(self.ConnectCheckBoxGroup)
        elif 'Advanced' in self.ModeDropDown.SelectedValue:
            self.Layout.AddRow(self.SideThicknessSliderGroup)
            self.Layout.AddRow(self.BottomThicknessSliderGroup)
            self.Layout.AddRow(self.TopThicknessSliderGroup)
            self.Layout.AddRow(self.TopWidthSliderGroup)
            self.Layout.AddRow(self.AngleSliderGroup)
            self.Layout.AddRow(self.TopInfluenceSliderGroup)
            self.Layout.AddRow(self.SideInfluenceSliderGroup)
            self.Layout.AddRow(self.ConnectCheckBoxGroup)        
        self.Layout.EndVertical()
        
        self.Layout.BeginVertical()
        self.Layout.AddSpace()
        self.Layout.AddRow(None, self.SetButton, self.FinalizeButton, self.CancelButton)
        self.Layout.EndVertical()

        self.Layout.Create()        
        self.Content = self.Layout

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

    def DisposeTempObs(self):
        for ob in self.TempObs:
            if isinstance(ob, list):
                for x in ob:
                    self.DisposeObject(x)
            else:
                self.DisposeObject(ob)

        self.TempObs = []

    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        if self.RingShape:
            if not rs.IsLayer('ring shape'):
                rs.AddLayer('ring shape', System.Drawing.Color.FromArgb(100, 12, 12))

            # get layer (create it if it doesn't exist)
            layer = sc.doc.Layers.FindName('ring shape')
            atts = Rhino.DocObjects.ObjectAttributes()
            atts.LayerIndex = layer.Index

            # add objects to document   
            ob_id = sc.doc.Objects.Add(self.RingShape, atts)
            rs.ObjectName(ob_id, 'Ring Shape')

        sc.doc.Views.Redraw()

        self.DisposeObject(self.SizingCircle)
        self.DisposeObject(self.BlendLine)
        self.DisposeObject(self.RingShape)
        self.DisposeRenderObjects()
        self.Close()

    def OnFormChanged(self, sender, e):       
        self.LayoutForm()
        self.Solve(sender)

    def OnSetButtonClick(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        
    def OnPushPickButton(self, sender, e):
        try:
            self.Set(sender)
        except Exception as e:
            app.WriteLine("wdRingShape:OnPushPickButton: " + str(e))
        
    def Set(self, sender):
        self.DisposeObject(self.SizingCircle)
        self.SizingCircle = None

        selected_ob = rs.GetObject('Select the sizing circle', rs.filter.curve, preselect = True, select = False)
        if selected_ob:
            name = rs.ObjectName(selected_ob)
            if rs.ObjectType(selected_ob) == 4 and 'Size' in name:
                self.SizingCircle = selected_ob
                curve = rs.coercecurve(self.SizingCircle)
                self.FingerRadius = abs(curve.PointAtStart.Z)

        if not self.SizingCircle:
            rs.MessageBox('No sizing circle was selected.')
        else:
            self.FinalizeButton.Enabled = True
            self.TopWidthSliderGroup.SetMinMax(0.0, round(2*self.FingerRadius, 0))
            self.LayoutForm()
            self.Solve(sender)


    def Solve(self, sender): 
        self.ConnectCheckBox.Enabled = False if self.TopWidthSliderGroup.Value == 0 else True 
        if self.SizingCircle:
            self.DisposeObject(self.BlendLine)
            self.DisposeObject(self.RingShape)
            self.DisposeRenderObjects()
            self.DisposeTempObs()

            self.LeftPoint = None
            self.RightPoint = None
            self.BottomPoint = None
            self.TopPoint = None
            self.TopPoint2 = None
            self.BlendLine = None
            self.RingShape = None
            self.RenderObjects = []
    
            offset_amt = self.OffsetSliderGroup.Value
            side = self.SideThicknessSliderGroup.Value
            btm = self.BottomThicknessSliderGroup.Value
            top = self.TopThicknessSliderGroup.Value
            top_width = self.TopWidthSliderGroup.Value / 2
            connected = self.ConnectCheckBox.Checked
            radius = self.FingerRadius
            btm_style = self.BottomStyleDropDown.SelectedValue
            angle = math.radians(-self.AngleSliderGroup.Value)
            sizing_circle = rs.coercecurve(self.SizingCircle) if self.SizingCircle else None
            sizing_circle_seam = sizing_circle.PointAtStart if sizing_circle else None
    
            # if top_width == 0: self.SmoothCheckBoxGroup.Enabled = True
            # else: self.SmoothCheckBoxGroup.Enabled = False
    
            # points
            left_pnt = rg.Point3d(-radius-side, 0, 0)
            right_pnt = rg.Point3d(radius+side, 0, 0)
            btm_pnt = rg.Point3d(0, 0, -radius-btm)
            top_pnt = rg.Point3d(-top_width, 0, radius+top)
            top_pnt2 = rg.Point3d(-top_pnt.X, top_pnt.Y, top_pnt.Z)
            top_pnt3 = rg.Point3d(top_pnt.X + 3, top_pnt.Y, top_pnt.Z)
    
            # bottom curve
            btm_arc = rg.Arc(left_pnt, btm_pnt, right_pnt).ToNurbsCurve()
            btm_ellipse = rg.Ellipse(rg.Point3d.Origin, left_pnt, btm_pnt).ToNurbsCurve()
            btm_curve = btm_arc if btm_style == 'Arc' else btm_ellipse            
    
            # bottom parameters
            t_left = btm_curve.ClosestPoint(left_pnt, 0.001)[1]
            t_right = btm_curve.ClosestPoint(right_pnt, 0.001)[1]
            t_bottom = btm_curve.ClosestPoint(btm_pnt, 0.001)[1]
    
            ring_btm = btm_curve.Split([t_left, t_right])[0]
            ring_btm_left = btm_curve.Split([t_left, t_right, t_bottom])[0]
            ring_btm_left.Reverse()
    
            # top line
            top_line = rg.Line(top_pnt, top_pnt2).ToNurbsCurve() if connected else None

            # track disposable objects
            self.TempObs.append(btm_arc)
            self.TempObs.append(btm_ellipse)
            self.TempObs.append(btm_curve)
            self.TempObs.append(ring_btm)
            self.TempObs.append(ring_btm_left)
            self.TempObs.append(top_line)
    
            if self.ModeDropDown.SelectedValue == 'Offset':
                # create offset curve
                # offset_radius = radius + offset_amt
                # offset_curve = rg.Circle(rg.Plane.WorldZX, offset_radius).ToNurbsCurve()
                offset_curve = None
                if sizing_circle:
                    offset_curve = sizing_circle.Offset(rg.Plane.WorldZX, offset_amt, 0.001, rg.CurveOffsetCornerStyle.None)[0]
    
                # update variables (so display pipeline can see them)
                self.RingShape = offset_curve

                self.TempObs.append(offset_curve)
                self.TempObs.append(sizing_circle)
    
            elif 'Bottom' in self.ModeDropDown.SelectedValue:
                # update variables (so display pipeline can see them)
                self.LeftPoint = left_pnt
                self.RightPoint = right_pnt
                self.BottomPoint = btm_pnt
                self.RingShape = ring_btm   
    
            elif 'Basic' in self.ModeDropDown.SelectedValue:
                # left side
                if self.SmoothCheckBox.Checked:
                    bulgea = 0.4
                    bulgeb = 0.4
                    blend_line = rg.Line(top_pnt, top_pnt3).ToNurbsCurve()
                    left_side = rg.Curve.CreateBlendCurve(ring_btm_left, blend_line, rg.BlendContinuity.Tangency, bulgea, bulgeb)

                    self.TempObs.append(blend_line)
                else:
                    left_side = ring_btm_left.Extend(rg.CurveEnd.End, rg.CurveExtensionStyle.Arc, top_pnt)
    
                # right side
                right_side = left_side.DuplicateCurve()
                xform = rg.Transform.Mirror(rg.Plane.WorldYZ)
                right_side.Transform(xform)

                self.TempObs.append(left_side)
                self.TempObs.append(right_side)
    
                # the ring shape
                ring_shape = None
                if connected: 
                    ring_shape = rg.Curve.JoinCurves([left_side, ring_btm, right_side, top_line])[0]
                else:
                    ring_shape = rg.Curve.JoinCurves([left_side, ring_btm, right_side])[0]
    
                # set seam position to match sizing circle's seam position
                if ring_shape.IsClosed:
                    b, t = ring_shape.ClosestPoint(sizing_circle_seam)
                    ring_shape.ChangeClosedCurveSeam(t)
    
                # update variables (so display pipeline can see them)
                self.LeftPoint = left_pnt
                self.RightPoint = right_pnt
                self.BottomPoint = btm_pnt
                self.TopPoint = top_pnt
                if top_width > 0: self.TopPoint2 = top_pnt2
                self.RingShape = ring_shape

                self.TempObs.append(ring_shape)
    
            elif 'Advanced' in self.ModeDropDown.SelectedValue:
                # side and top influence
                bulgea = self.SideInfluenceSliderGroup.Value
                bulgeb = self.TopInfluenceSliderGroup.Value

                # enable / disable angle slider as needed
                if bulgeb == 0:
                    if self.AngleSliderGroup.IsEnabled():
                        self.AngleSliderGroup.SetEnabled(False)
                        self.LayoutForm()
                else:
                    if not self.AngleSliderGroup.IsEnabled():
                        self.AngleSliderGroup.SetEnabled(True)
                        self.LayoutForm()

                # blend line
                blend_line = rg.Line(top_pnt, top_pnt3).ToNurbsCurve()
                blend_pln = rg.Plane.WorldZX
                blend_pln.Origin = top_pnt
                xform = rg.Transform.Rotation(angle, blend_pln.ZAxis, top_pnt)
                blend_line.Transform(xform)
    
                # left side
                left_side = rg.Curve.CreateBlendCurve(ring_btm_left, blend_line, rg.BlendContinuity.Tangency, bulgea, bulgeb)
                
                # right side
                right_side = left_side.DuplicateCurve()
                xform = rg.Transform.Mirror(rg.Plane.WorldYZ)
                right_side.Transform(xform)

                self.TempObs.append(blend_line)
                self.TempObs.append(blend_pln)
                self.TempObs.append(left_side)
                self.TempObs.append(right_side)
    
                # the ring shape
                ring_shape = None
                if connected: 
                    ring_shape = rg.Curve.JoinCurves([left_side, ring_btm, right_side, top_line])[0]
                else:
                    ring_shape = rg.Curve.JoinCurves([left_side, ring_btm, right_side])[0]
    
                # set seam position to match sizing circle's seam position
                if ring_shape.IsClosed:
                    b, t = ring_shape.ClosestPoint(sizing_circle_seam)
                    ring_shape.ChangeClosedCurveSeam(t)
    
                self.LeftPoint = left_pnt
                self.RightPoint = right_pnt
                self.BottomPoint = btm_pnt
                self.TopPoint = top_pnt
                if top_width > 0: self.TopPoint2 = top_pnt2
                if 'Advanced' in self.ModeDropDown.SelectedValue and bulgeb > 0:
                    self.BlendLine = blend_line
                else:
                    self.BlendLine = None
                self.RingShape = ring_shape

                self.TempObs.append(ring_shape)

        # render objects
        if self.LeftPoint: self.RenderObjects.append([self.LeftPoint, cam.PointColor])
        if self.RightPoint: self.RenderObjects.append([self.RightPoint, cam.PointColor])
        if self.BottomPoint: self.RenderObjects.append([self.BottomPoint, cam.PointColor])
        if self.TopPoint: self.RenderObjects.append([self.TopPoint, cam.PointColor])
        if self.TopPoint2: self.RenderObjects.append([self.TopPoint2, cam.PointColor])
        if self.BlendLine: self.RenderObjects.append([self.BlendLine, cam.PointColor])
        if self.RingShape: self.RenderObjects.append([self.RingShape, cam.CurveColor])
        
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