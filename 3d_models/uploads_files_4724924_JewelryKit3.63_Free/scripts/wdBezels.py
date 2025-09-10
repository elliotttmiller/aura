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
from sliders import SliderGroup as sg
from components import ComponentGenerator as cg
import SpatialData as sd
from Rhino import RhinoApp as app
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
        self.LabelWidth = 105
        self.Title = 'Bezel Builder'
        self.Padding = drawing.Padding(15)
        self.AutoSize = True
        self.Layout = None
        self.Tab1Layout = None
        self.Tab2Layout = None
        self.Closing += self.OnDialogClosing
        if rs.ExeVersion() >= 8:
            Rhino.UI.EtoExtensions.UseRhinoStyle(self)

        # pipeline stuff
        self.Conduit = DrawConduit(self)
        self.Conduit.Enabled = True
        self.RenderObjects = []
        self.EdgeCurves = []
        self.TempObs = []
        self.SetObs = []
        self.Conduit.EdgeColor = cam.ProngColor

        # some handy variables
        self.CornerStyles = [rg.CurveOffsetCornerStyle.Sharp, rg.CurveOffsetCornerStyle.Round, rg.CurveOffsetCornerStyle.Smooth]

        # output variables
        self.GemIDs = []
        self.Bezels = []

        # tabs
        # general tab page
        self.Tab1 = forms.TabPage()
        self.Tab1.Padding = drawing.Padding(10,20,10,10)
        self.Tab1.Text = 'General'
        
        # prong tab page
        self.Tab2 = forms.TabPage()
        self.Tab2.Padding = drawing.Padding(10,15,10,10)
        self.Tab2.Text = 'Taper / Bulge / Chamfer'

        # tab control
        self.Tabs = forms.TabControl()
        self.Tabs.Pages.Add(self.Tab1)
        self.Tabs.Pages.Add(self.Tab2)   
        self.Tabs.Height = 450
       
        # input controls
        # self.CornerStyleDropDownGroup, self.CornerStyleDropDown = cg.CreateDropDownGroup('Corner Style: ', self.LabelWidth, self.CornerStyles, self.OnFormChanged, default_index = 2) 
        self.HeightSG = cg.CreateSliderGroup('Bezel Height: ', self.LabelWidth, 0.5, 1.5, 2, 1.0, self.Solve) 
        self.DepthSG = cg.CreateSliderGroup('Bezel Depth: ', self.LabelWidth, 1.0, 10.0, 2, 1.0, self.Solve)
        self.TopThicknessSG = cg.CreateSliderGroup('Top Thickness: ', self.LabelWidth, 0.5, 2.0, 2, 0.8, self.Solve)   
        self.BottomThicknessSG = cg.CreateSliderGroup('Bottom Thickness: ', self.LabelWidth, 0.5, 2.0, 2, 0.8, self.Solve)
        self.LedgeThicknessSG = cg.CreateSliderGroup('Ledge Width: ', self.LabelWidth, 0.1, 1.0, 2, 0.3, self.Solve)
        self.LedgeDepthSG = cg.CreateSliderGroup('Ledge Depth: ', self.LabelWidth, 0.0, 1.0, 2, 0.0, self.Solve)

        self.TaperXSG = cg.CreateSliderGroup('Taper X: ', self.LabelWidth, 0.0, 0.5, 2, 0.0, self.Solve)
        self.TaperYSG = cg.CreateSliderGroup('Taper Y: ', self.LabelWidth, 0.0, 0.5, 2, 0.0, self.Solve)
        self.LockTaperCheckBoxGroup, self.LockTaperCheckBox = cg.CreateCheckBoxGroup('Lock: ', self.LabelWidth, True, self.OnFormChanged)

        self.BulgeLocSG = cg.CreateSliderGroup('Bulge Location: ', self.LabelWidth, 0.3, 0.6, 2, 0.5, self.Solve)
        self.BulgeXSG = cg.CreateSliderGroup('Bulge X: ', self.LabelWidth, 0.0, 0.5, 2, 0.0, self.Solve)  
        self.BulgeYSG = cg.CreateSliderGroup('Bulge Y: ', self.LabelWidth, 0.0, 0.5, 2, 0.0, self.Solve)  
        self.LockBulgeCheckBoxGroup, self.LockBulgeCheckBox = cg.CreateCheckBoxGroup('Lock: ', self.LabelWidth, True, self.OnFormChanged) 

        self.UseChamferCheckBoxGroup, self.UseChamferCheckBox = cg.CreateCheckBoxGroup('Chamfer Bezel? ', self.LabelWidth, False, self.OnFormChanged)
        self.ChamferThicknessSG = cg.CreateSliderGroup('Chamfer Thickness: ', self.LabelWidth, 0.1, 1.0, 2, 0.4, self.Solve)
        self.ChamferDepthSG = cg.CreateSliderGroup('Chamfer Depth: ', self.LabelWidth, 0.1, 1.2, 2, 0.8, self.Solve)


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

    def AddToRenderObjects(self, objects, mtl):
        for obj in objects:
            self.RenderObjects.append([obj, mtl])

    def DisposeOb(self, ob):
        if ob and hasattr(ob, 'Dispose'): ob.Dispose()

    def DisposeObs(self, obs):
        for ob in obs:
            self.DisposeOb(ob)

    def DisposeTempObs(self):
        for ob in self.TempObs:
            if isinstance(ob, list):
                for x in ob:
                    self.DisposeOb(x)
            else:
                self.DisposeOb(ob)
        # self.DisposeObs(self.TempObs)
        self.TempObs = []

    def DisposeSetObs(self):
        self.DisposeObs(self.SetObs)

    def DisposeRenderObjects(self):
        self.DisposeObs(self.RenderObjects)

    def DisposeAll(self):
        self.DisposeTempObs()
        self.DisposeSetObs()
        
    def LayoutForm(self):
        if self.Layout:
            self.Layout.Clear()

        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)

        self.LayoutTab1()
        self.LayoutTab2()

        self.Layout.BeginVertical()
        self.Layout.AddRow(self.Tabs)
        self.Layout.EndVertical()

        self.Layout.BeginVertical()
        self.Layout.AddRow(forms.Label())
        self.Layout.AddRow(None, self.SetButton, self.FinalizeButton, self.CancelButton)
        self.Layout.EndVertical()

        self.Layout.Create()        
        self.Content = self.Layout

    def LayoutTab1(self):
        if self.Tab1Layout:
            self.Tab1Layout.Clear()

        self.Tab1Layout = forms.DynamicLayout()
        self.Tab1Layout.DefaultSpacing = drawing.Size(5,5)

        self.Tab1Layout.BeginVertical()
        # add input controls here
        # self.Tab1Layout.AddRow(self.CornerStyleDropDownGroup)
        # self.Tab1Layout.AddRow(cg.CreateVerticalSpacer(10))
        self.Tab1Layout.AddRow(self.HeightSG)
        self.Tab1Layout.AddRow(self.DepthSG)
        self.Tab1Layout.AddRow(cg.CreateVerticalSpacer(20))
        self.Tab1Layout.AddRow(self.TopThicknessSG)
        self.Tab1Layout.AddRow(self.BottomThicknessSG)
        self.Tab1Layout.AddRow(cg.CreateVerticalSpacer(20))
        self.Tab1Layout.AddRow(self.LedgeThicknessSG)
        self.Tab1Layout.AddRow(self.LedgeDepthSG)
        self.Tab1Layout.EndVertical()

        self.Tab1Layout.Create()
        self.Tab1.Content = self.Tab1Layout

    def LayoutTab2(self):
        if self.Tab2Layout:
            self.Tab2Layout.Clear()

        self.Tab2Layout = forms.DynamicLayout()
        self.Tab2Layout.DefaultSpacing = drawing.Size(5,5)

        self.Tab2Layout.BeginVertical()
        self.Tab2Layout.AddRow(self.TaperXSG)
        self.Tab2Layout.AddRow(self.TaperYSG)
        self.Tab2Layout.AddRow(self.LockTaperCheckBoxGroup)
        self.Tab2Layout.EndVertical()

        self.Tab2Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Tab2Layout.AddRow(cg.CreateHR())
        self.Tab2Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Tab2Layout.BeginVertical()
        self.Tab2Layout.AddRow(self.BulgeLocSG)
        self.Tab2Layout.AddRow(self.BulgeXSG)
        self.Tab2Layout.AddRow(self.BulgeYSG)
        self.Tab2Layout.AddRow(self.LockBulgeCheckBoxGroup)
        self.Tab2Layout.EndVertical()

        self.Tab2Layout.AddRow(cg.CreateVerticalSpacer(5))
        self.Tab2Layout.AddRow(cg.CreateHR())
        self.Tab2Layout.AddRow(cg.CreateVerticalSpacer(5))

        self.Tab2Layout.BeginVertical()
        self.Tab2Layout.AddRow(self.UseChamferCheckBoxGroup)
        self.Tab2Layout.AddRow(self.ChamferThicknessSG)
        self.Tab2Layout.AddRow(self.ChamferDepthSG)
        self.Tab2Layout.EndVertical()

        self.Tab2Layout.Create()
        self.Tab2.Content = self.Tab2Layout

    def LoadBaseOutline(self, shape):
        filename = shape + ".3dm"
        gem_folder = script_folder.replace("scripts", "gems")
        outline_folder = os.path.join(gem_folder, '5Outlines')
        fullpath = os.path.join(outline_folder, filename)
        outline_file = Rhino.FileIO.File3dm.Read(fullpath)
        base_outline = outline_file.Objects.FindByLayer('gem profiles')[0].Geometry
        self.BaseOutline = base_outline.ToNurbsCurve()
        base_outline.Dispose()
        self.SetObs.append(self.BaseOutline)

    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        if len(self.Bezels) > 0:
            layer_name = 'bezels'
            if not rs.IsLayer(layer_name):
                rs.AddLayer(layer_name, cam.ProngColor)
            
            layer = sc.doc.Layers.FindName(layer_name)
            atts = Rhino.DocObjects.ObjectAttributes()
            atts.LayerIndex = layer.Index
                
            guids = []
            for ob in self.Bezels:            
                guid = sc.doc.Objects.AddBrep(ob, atts)
                rs.ObjectName(guid, 'wdBezel')
                guids.append(guid)

            # make group
            if len(guids) > 1:
                grp = rs.AddGroup()
                rs.AddObjectsToGroup(guids, grp)

            sc.doc.Views.Redraw()

        self.DisposeAll()            
        self.Close()

    def OnFormChanged(self, sender, e):
        # self.UseHeartBase = self.UseHeartBaseCheckBox.Checked

        # if sender == self.UseHeartBaseCheckBox:
        #     if self.UseHeartBase:
        #         self.Shape = 'Heart Base'
        #     else:
        #         self.Shape = 'Heart'
        #     self.LoadBaseOutline(self.Shape)

        self.LayoutForm()
        self.Solve(sender)

    def OnSetButtonClick(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        
    def OnPushPickButton(self, sender, e):
        try:
            self.SetGems(sender)
        except Exception as e:
            app.WriteLine(str(e))
            app.WriteLine("line 167")
        
    def SetGems(self, sender):
        self.DisposeSetObs()
        shape = None
        gem_ids = []

        selected_guids = rs.GetObjects('Select one or more gems to add cutters to', rs.filter.polysurface, preselect = True, select = False, custom_filter = IsGem)
        if selected_guids:
            for guid in selected_guids:
                name = rs.ObjectName(guid)
                if name == 'wdGem':
                    gem_ids.append(guid)
            rs.UnselectAllObjects()

        if len(gem_ids) == 0:
            rs.MessageBox('No gems were selected.')
            shape = None
        else:
            # check that all selected gems have same shape
            for i in range(len(gem_ids)):
                if i == 0:
                    shape = rs.GetUserText(gem_ids[i], 'shape')
                else:
                    if rs.GetUserText(gem_ids[i], 'shape') != shape:
                        shape = None
                        rs.MessageBox('All selected gems must have the same shape.')
                        break

            if shape:
                self.Shape = shape
                try:
                    self.LoadBaseOutline(self.Shape)
                    self.LayoutForm()
                except Exception as e:
                    Rhino.RhinoApp.WriteLine('line 199: ' + str(e))
                
                self.GemIDs = gem_ids

        self.Solve(sender)

    def ClearAll(self):
        self.DisposeObs(self.Bezels)
        self.DisposeObs(self.RenderObjects)
        self.DisposeObs(self.EdgeCurves)
        self.DisposeObs(self.TempObs)

        self.Bezels = []
        self.RenderObjects = [] 
        self.EdgeCurves = []
        self.TempObs = [] 

    def MeshFromBrep(self, brep):
        meshing_params = Rhino.Geometry.MeshingParameters.QualityRenderMesh
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

    def SetSeam(self, curve):
        bbox = curve.GetBoundingBox(True)
        pnt = rg.Point3d(bbox.Min.X, 0, 0)
        success, t = curve.ClosestPoint(pnt)
        if success:
            curve.ChangeClosedCurveSeam(t)
        else:
            app.WriteLine('Could not set seam on a curve')


    def Solve(self, sender):
        self.ClearAll() 

        # handle taper lock        
        if self.LockTaperCheckBox.Checked:
            self.TaperYSG.Unsubscribe(self.Solve)
            self.TaperYSG.SetEnabled(False)
            self.TaperYSG.SetValue(self.TaperXSG.Value)
        else:
            self.TaperYSG.Subscribe(self.Solve)
            self.TaperYSG.SetEnabled(True) 

        # handle bulge lock
        if self.LockBulgeCheckBox.Checked:
            self.BulgeYSG.Unsubscribe(self.Solve)
            self.BulgeYSG.SetEnabled(False)
            self.BulgeYSG.SetValue(self.BulgeXSG.Value)
        else:
            self.BulgeYSG.Subscribe(self.Solve)
            self.BulgeYSG.SetEnabled(True)  

        offset_corner_style = rg.CurveOffsetCornerStyle.Smooth

        for gem_id in self.GemIDs:
            # get gem's plane
            gem_pln = sd.GetPlane(gem_id)

            # get gem brep
            gem_brep = rs.coercebrep(gem_id)
            self.TempObs.append(gem_brep)

            # get gem's length and width
            gem_bbox = gem_brep.GetBoundingBox(gem_pln)
            gem_width = gem_bbox.Max.X - gem_bbox.Min.X
            gem_length = gem_bbox.Max.Y - gem_bbox.Min.Y
            gem_depth = gem_bbox.Max.Z - gem_bbox.Min.Z
            gem_pavilion_depth = -gem_bbox.Min.Z
            gem_crown_height = gem_bbox.Max.Z

            # get the girdle outline and scale it to gem
            girdle_outline = self.BaseOutline.DuplicateCurve()
            girdle_outline_bbox = girdle_outline.GetBoundingBox(True)
            girdle_outline_width = girdle_outline_bbox.Max.X - girdle_outline_bbox.Min.X
            girdle_outline_length = girdle_outline_bbox.Max.Y - girdle_outline_bbox.Min.Y
            xform = rg.Transform.Scale(rg.Plane.WorldXY, gem_width/girdle_outline_width, gem_length/girdle_outline_length, 1)
            girdle_outline.Transform(xform)

            # set outline's seam
            self.SetSeam(girdle_outline)  

            girdle_outline = girdle_outline.Fit(3, 0.001, 0.001)
            fc_attempt = rg.Curve.CreateFilletCornersCurve(girdle_outline, 0.03, 0.001, 0.001)
            if fc_attempt:
                girdle_outline = fc_attempt
            self.TempObs.append(girdle_outline)
            self.TempObs.append(fc_attempt)

            # create the inner top outline, move it to top of appropriate
            # height based height slider (a percentage of crown height)
            inner_top_outline = girdle_outline.DuplicateCurve()
            bezel_height = self.HeightSG.Value * gem_crown_height
            xform = rg.Transform.Translation(0,0,bezel_height)
            inner_top_outline.Transform(xform)  
            self.TempObs.append(inner_top_outline)

            # create the outer top outline 
            outer_top_outline = None           
            results = inner_top_outline.Offset(rg.Point3d.Origin, rg.Plane.WorldXY.ZAxis, -self.TopThicknessSG.Value, 0.001, offset_corner_style)
            if results and len(results) == 1:
                outer_top_outline = results[0]
            elif results and len(results) > 1:
                outer_top_outline = rg.Curve.JoinCurves(results, 0.001)
            else:
                app.WriteLine('Error: Unable to create outer top outline!')

            fc_attempt = rg.Curve.CreateFilletCornersCurve(outer_top_outline, 0.05, 0.001, 0.001)
            if fc_attempt:
                outer_top_outline = fc_attempt
            self.TempObs.append(outer_top_outline)
            self.TempObs.append(fc_attempt)
            self.TempObs.extend(results)

            # create the outer bottom outline
            btm_depth = bezel_height + self.DepthSG.Value
            outer_btm_outline = outer_top_outline.DuplicateCurve()
            outer_btm_outline.Translate(0,0,-btm_depth) 

            # scale outer bottom outline (tapers bezel)
            taperSFX = 1-self.TaperXSG.Value
            taperSFY = 1-self.TaperYSG.Value
            xform = rg.Transform.Scale(rg.Plane.WorldXY, taperSFX, taperSFY, 1)
            outer_btm_outline.Transform(xform)
            self.TempObs.append(outer_btm_outline)

            # create the outer middle outline
            outer_mid_outline = outer_top_outline.DuplicateCurve()

            # move the outer middle outline
            middle_depth = self.BulgeLocSG.Value * btm_depth
            outer_mid_outline.Translate(0,0,-middle_depth)

            # scale the outer middle outline to match taper
            middleSFX = 1 - (self.BulgeLocSG.Value * (1-taperSFX))
            middleSFY = 1 - (self.BulgeLocSG.Value * (1-taperSFY))
            xform = rg.Transform.Scale(rg.Plane.WorldXY, middleSFX, middleSFY, 1)
            outer_mid_outline.Transform(xform)

            # scale the outer middle outline for bulge
            middleSFX2 = 1 + self.BulgeXSG.Value
            middleSFY2 = 1 + self.BulgeYSG.Value
            xform = rg.Transform.Scale(rg.Plane.WorldXY, middleSFX2, middleSFY2, 1)
            outer_mid_outline.Transform(xform)
            self.TempObs.append(outer_mid_outline)

            # create the inner bottom outline
            inner_btm_outline = None
            results = outer_btm_outline.Offset(rg.Point3d.Origin, rg.Plane.WorldXY.ZAxis, self.BottomThicknessSG.Value, 0.001, offset_corner_style)
            self.TempObs.append(results)
            if results and len(results) == 1:
                inner_btm_outline = results[0]
            elif results and len(results) > 1:
                inner_btm_outline = rg.Curve.JoinCurves(results, 0.001)[0]
            else:
                app.WriteLine('Error: Unable to create inner bottom outline!') 

            inner_btm_outline = inner_btm_outline.Fit(3, 0.001, 0.001)           
            fc_attempt = rg.Curve.CreateFilletCornersCurve(inner_btm_outline, 0.03, 0.001, 0.001)
            if fc_attempt:
                inner_btm_outline = fc_attempt

            self.TempObs.append(inner_btm_outline)
            self.TempObs.append(fc_attempt)
            self.TempObs.extend(results)

            # create the ledge outline
            ledge_outline = None
            results = girdle_outline.Offset(rg.Point3d.Origin, rg.Plane.WorldXY.ZAxis, self.LedgeThicknessSG.Value, 0.001, offset_corner_style)
            self.TempObs.append(results)
            if results and len(results) == 1:
                ledge_outline = results[0]
            else:
                app.WriteLine('Error: Unable to create ledge outline!') 

            ledge_outline = ledge_outline.Fit(3, 0.001, 0.001)
            fc_attempt = rg.Curve.CreateFilletCornersCurve(ledge_outline, 0.03, 0.001, 0.001)
            if fc_attempt:
                ledge_outline = fc_attempt

            # move ledge outline down
            ledge_outline.Translate(0,0,-self.LedgeDepthSG.Value)

            self.TempObs.append(ledge_outline)
            self.TempObs.append(fc_attempt)
            self.TempObs.extend(results)

            # create bezel
            outer_bezel = None
            bezel_outer_surface = None
            results = None
            if self.BulgeXSG.Value == 0 and self.BulgeYSG.Value == 0:
                results = rg.Brep.CreateFromLoft([outer_top_outline, outer_btm_outline], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)
            else:
                results = rg.Brep.CreateFromLoft([outer_top_outline, outer_mid_outline, outer_btm_outline], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
            if results and len(results) == 1:
                bezel_outer_surface = results[0]
            else:
                app.WriteLine('Could not loft outer bezel curves')
            self.TempObs.append(bezel_outer_surface)
            self.TempObs.extend(results)

            outer_bezel = bezel_outer_surface.CapPlanarHoles(0.001)
            if outer_bezel.SolidOrientation == rg.BrepSolidOrientation.Inward:
                outer_bezel.Flip()
            self.TempObs.append(outer_bezel)

            # create bezel cutter
            inner_top_outline.Translate(0,0,0.02)
            inner_btm_outline.Translate(0,0,-0.02)
            bezel_cutter_outer_surface = None
            result = rg.Brep.CreateFromLoft([inner_top_outline, girdle_outline, ledge_outline, inner_btm_outline], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)
            self.TempObs.append(result)
            
            if result and len(result) == 1:
                bezel_cutter_outer_surface = result[0]
            else:
                app.WriteLine('Could not loft inner bezel curves')
                sc.doc.Objects.AddCurve(inner_top_outline)
                sc.doc.Objects.AddCurve(girdle_outline)
                sc.doc.Objects.AddCurve(ledge_outline)
                sc.doc.Objects.AddCurve(inner_btm_outline)
                sc.doc.Objects.AddCurve(outer_btm_outline)

            self.TempObs.append(bezel_cutter_outer_surface)

            bezel_cutter = bezel_cutter_outer_surface.CapPlanarHoles(0.001)
            if bezel_cutter.SolidOrientation == rg.BrepSolidOrientation.Inward:
                bezel_cutter.Flip()
            self.TempObs.append(bezel_cutter)

            # boolean difference the cutter from the bezel
            bezel = None
            results = rg.Brep.CreateBooleanDifference(outer_bezel, bezel_cutter, 0.001)
            self.TempObs.append(results)
            if results and len(results) == 1:
                bezel = results[0]
            else:
                app.WriteLine('Could not hollow the bezel')
            self.TempObs.append(bezel)

            # chamfer bezel if neededed
            inner_lower_chamfer_outline = None
            inner_upper_chamfer_outline = None
            outer_lower_chamfer_outline = None
            outer_upper_chamfer_outline = None
            chamfer_cutter = None
            use_chamfer = self.UseChamferCheckBox.Checked
            chamfer_thickness = self.ChamferThicknessSG.Value if self.ChamferThicknessSG.Value < self.TopThicknessSG.Value - 0.3 else self.TopThicknessSG.Value - 0.3
            chamfer_depth = self.ChamferDepthSG.Value * bezel_height
            if use_chamfer:
                # create inner lower chamfer outline
                results = inner_top_outline.Offset(rg.Point3d.Origin, rg.Plane.WorldXY.ZAxis, -chamfer_thickness, 0.001, offset_corner_style)
                self.TempObs.append(results)
                if results and len(results) == 1:
                    inner_lower_chamfer_outline = results[0]
                    inner_lower_chamfer_outline.Translate(0,0,0.01)
                else:
                    app.WriteLine('Error: Unable to create chamfer outline!')

                fc_attempt = rg.Curve.CreateFilletCornersCurve(inner_lower_chamfer_outline, 0.03, 0.001, 0.001)
                self.TempObs.append(fc_attempt)
                if fc_attempt:
                    inner_lower_chamfer_outline = fc_attempt

                # create outer lower chamfer outline
                outer_lower_chamfer_outline = None
                pln = rg.PlaneSurface(rg.Plane.WorldXY, rg.Interval(-100, 100), rg.Interval(-100,100))
                self.TempObs.append(pln)

                pln_brep = pln.ToBrep()
                self.TempObs.append(pln_brep)

                pln_brep.Translate(0, 0, bezel_height - chamfer_depth)

                success, crvs, pnts = rg.Intersect.Intersection.BrepBrep(bezel, pln_brep, 0.001)
                if success and crvs and len(crvs) > 0:
                    joined = rg.Curve.JoinCurves(crvs, 0.001)
                    bbox1 = joined[0].GetBoundingBox(True)
                    bbox2 = joined[1].GetBoundingBox(True)
                    
                    crv1_width = bbox1.Max.X - bbox1.Min.X
                    crv2_width = bbox2.Max.X - bbox2.Min.X

                    outer_lower_chamfer_outline = joined[0] if crv1_width > crv2_width else joined[1]
                else:
                    app.WriteLine('Could not create outer lower chamfer outline.')

                # scale it up a bit
                outer_lower_chamfer_outline.Scale(1.003)


                # create inner upper chamfer outline
                inner_upper_chamfer_outline = inner_lower_chamfer_outline.DuplicateCurve()
                inner_upper_chamfer_outline.Translate(0,0,chamfer_depth + 1)

                # create outer upper chamfer outline
                outer_upper_chamfer_outline = outer_lower_chamfer_outline.DuplicateCurve()
                outer_upper_chamfer_outline.Translate(0,0,chamfer_depth + 1)

                # make chamfer cutter
                results = rg.Brep.CreateFromLoft([inner_lower_chamfer_outline, outer_lower_chamfer_outline, outer_upper_chamfer_outline, inner_upper_chamfer_outline], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, True)
                self.TempObs.append(results)
                if results and len(results) == 1:
                    chamfer_cutter = results[0]
                else:
                    app.WriteLine('Could not create chamfer cutter')
                
                # boolean difference the chamfer cutter from the bezel
                results = rg.Brep.CreateBooleanDifference(bezel, chamfer_cutter, 0.001)
                self.TempObs.append(results)
                if result and len(results) == 1:
                    bezel = results[0]
                else:
                    app.WriteLine('Could not hollow the bezel')
                self.TempObs.append(bezel)                

            # move objects to gem's plane
            xform = rg.Transform.PlaneToPlane(rg.Plane.WorldXY, gem_pln)
            outer_mid_outline.Transform(xform)
            bezel.Transform(xform)

            # record brep for finalizing
            self.Bezels.append(bezel)

            # get mesh for rendering
            bezel_mesh = self.MeshFromBrep(bezel)

            # record temp objects for disposal
            self.TempObs.append(girdle_outline)
            self.TempObs.append(inner_top_outline)
            self.TempObs.append(outer_top_outline)  
            self.TempObs.append(outer_btm_outline)
            self.TempObs.append(outer_mid_outline)
            self.TempObs.append(inner_btm_outline)    
            self.TempObs.append(ledge_outline) 

            # record render objects for rending in the pipeline
            if self.BulgeXSG.Value > 0 or self.BulgeYSG.Value > 0:
                self.AddToRenderObjects([outer_mid_outline], cam.CurveColor)
            self.AddToRenderObjects([bezel_mesh], cam.ProngMaterial)
            self.AddEdgeCurves(bezel)
        
        # redraw                
        sc.doc.Views.Redraw()

        
if __name__ == '__main__':        
    dialog = wdDialog()
    if rs.ExeVersion() > 6:
        parent = Rhino.UI.RhinoEtoApp.MainWindowForDocument(sc.doc)
    else:
        parent = Rhino.UI.RhinoEtoApp.MainWindow
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, sc.doc, parent)