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
import SpatialData as sd
import Rhino.RhinoApp as app
from components import ComponentGenerator as cg
# from pipeline import DrawConduit
# from pipeline import ColorsAndMaterials as cam


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
        self.LabelWidth = 90
        self.Title = 'Reorder Gems'
        self.Padding = drawing.Padding(15)
        self.AutoSize = True
        self.Layout = None
        self.Closing += self.OnDialogClosing
        if rs.ExeVersion() >= 8:
            Rhino.UI.EtoExtensions.UseRhinoStyle(self)

        # overlay visualization stuff
        # self.Conduit = DrawConduit(self)
        # self.Conduit.Enabled = True
        # self.RenderObjects = []

        # handy variables
        self.GemIDs = []
        self.Gems = []
        self.GemPlanes = []
        self.Centers = []
        self.Curve = None
       
        # input controls 
        self.Label = forms.Label()
        self.Label.Text = 'Select the gems in order.'       
        

        # bottom buttons
        self.SetButton = cg.CreateButton('Select Gems', self.OnSetButtonClick)
        # self.FinalizeButton = cg.CreateButton('Finalize', self.OnFinalizeButtonClick)
        self.CancelButton = cg.CreateButton('Cancel', self.OnCancelButtonClick)

        # the default button must be set for Macs (might as well set the abort button, too.)
        self.DefaultButton = self.SetButton
        self.AbortButton = self.CancelButton
        
        # lay it out and run the solver
        self.LayoutForm()
        
    def LayoutForm(self):
        if self.Layout:
            self.Layout.Clear()

        self.Layout = forms.DynamicLayout()
        self.Layout.DefaultSpacing = drawing.Size(5,5)

        # self.Layout.BeginVertical()
        # # add input controls here
        # self.Layout.EndVertical()
        
        self.Layout.BeginVertical()
        self.Layout.AddRow(self.Label, None)
        self.Layout.AddRow(forms.Label())
        # self.Layout.AddRow(None, self.SetButton, self.FinalizeButton, self.CancelButton)
        self.Layout.AddRow(self.SetButton, self.CancelButton)
        self.Layout.EndVertical()

        self.Layout.Create()        
        self.Content = self.Layout

    def OnCancelButtonClick(self, sender, e):
        self.Close()
       
    def OnDialogClosing(self, sender, e):
        pass
        # self.Conduit.Enabled = False

    def OnFinalizeButtonClick(self, sender, e):
        # get layer (create it if it doesn't exist)
        layer = sc.doc.Layers.FindName('layer_name')
        if not layer:
            layer = sc.doc.Layers.Add('layer_name', System.Drawing.Color.FromArgb(125, 40, 200))
        else: layer = layer.Index
        atts = Rhino.DocObjects.ObjectAttributes()
        atts.LayerIndex = layer

        # add objects to document            
        ob_ids = []
        print (self.ObjectIDs)
        for ob_id in self.ObjectIDs:            
            ob_id = sc.doc.Objects.AddBrep(ob_id, atts)
            rs.ObjectName(ubid, 'object name')
            ob_ids.append(ubid)

        # make group, if needed
        if len(ob_ids) > 1:
            grp = rs.AddGroup()
            rs.AddObjectsToGroup(ob_ids, grp)

        sc.doc.Views.Redraw()
        self.Clear(self.Gems)
        self.Clear(self.GemPlanes)
        self.Clear(self.Centers)
        self.Clear(self.Curve)
        self.Close()

    def OnFormChanged(self, sender, e):
        self.UseHeartBase = self.UseHeartBaseCheckBox.Checked

        if sender == self.UseHeartBaseCheckBox:
            if self.UseHeartBase:
                self.Shape = 'Heart Base'
            else:
                self.Shape = 'Heart'
            self.LoadBaseOutline(self.Shape)

        self.LayoutForm()
        self.Solve(sender)

    def OnSetButtonClick(self, sender, e):
        Rhino.UI.EtoExtensions.PushPickButton(self, self.OnPushPickButton)
        self.Close()
        
    def OnPushPickButton(self, sender, e):
        try:
            self.SetGems(sender)
        except Exception as e:
            app.WriteLine("line 221")
        
    def SetGems(self, sender):
        gem_ids = []
        selected_obs = rs.GetObjects('Select the gems in order', group = False, filter = rs.filter.polysurface, preselect = False, custom_filter = IsGem)
        if selected_obs:
            for ob in selected_obs:
                name = rs.ObjectName(ob)
                if name == 'wdGem':
                    gem_ids.append(ob)

        if len(gem_ids) == 0:
            rs.MessageBox('No gems were selected.')
            shape = None
        else:
            self.GemIDs = gem_ids
            print(len(self.GemIDs))
            self.ReorderGems()

    def Clear(self, obj):
        if isinstance(obj, list):
            if len(obj) > 0:
                for item in obj:
                    if hasattr(item, 'Dispose'): item.Dispose()
                obj = []
        else:
            if obj and hasattr(obj, 'Dispose'):
                obj.Dispose()
                obj = None

    def ReorderGems(self):
        self.Clear(self.Gems)
        self.Clear(self.GemPlanes)
        self.Clear(self.Centers)
        self.Clear(self.Curve)

        # collect breps and planes from old gems
        for i in range(len(self.GemIDs)):
            # get id and brep
            gem_id = self.GemIDs[i]
            gem = rs.coercebrep(gem_id)
            self.Gems.append(gem)

            # get old gem's plane
            gem_pln = sd.GetPlane(gem_id)
            self.GemPlanes.append(gem_pln)

            # get center point
            self.Centers.append(gem_pln.Origin)

        # create a center curve
        self.Curve = rg.Curve.CreateInterpolatedCurve(self.Centers, 3)

        # get frames on curve at each gem's center
        for i in range(len(self.Gems)):
            success, t = self.Curve.ClosestPoint(self.Centers[i])
            success, frame = self.Curve.FrameAt(t)

            # rotate frame so frame's normal and gem plane's normal match
            angle = rg.Vector3d.VectorAngle(frame.ZAxis, self.GemPlanes[i].ZAxis)
            if angle == Rhino.RhinoMath.UnsetValue:
                angle = 0
            frame.Rotate(angle, frame.XAxis)
            # frames.append(frame)

            # rotate gem if needed
            angle = rg.Vector3d.VectorAngle(frame.XAxis, self.GemPlanes[i].XAxis, self.GemPlanes[i])
            if angle == Rhino.RhinoMath.UnsetValue:
                angle = 0
            self.Gems[i].Rotate(angle, self.GemPlanes[i].ZAxis, self.GemPlanes[i].Origin)

        # make a new group of new breps
        new_grp = rs.AddGroup()
        for i in range(len(self.GemIDs)):
            old_gem_id = self.GemIDs[i]
            new_gem_id = rs.CopyObject(old_gem_id)
            rs.DeleteObject(old_gem_id)
            rs.RemoveObjectFromAllGroups(new_gem_id)
            rs.AddObjectToGroup(new_gem_id, new_grp)

        rs.MessageBox('Gems have been re-ordered!')


        
if __name__ == '__main__':        
    dialog = wdDialog()
    if rs.ExeVersion() > 6:
        parent = Rhino.UI.RhinoEtoApp.MainWindowForDocument(sc.doc)
    else:
        parent = Rhino.UI.RhinoEtoApp.MainWindow
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, sc.doc, parent)