#! python 2

import System
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import Rhino.Geometry as rg
import os
import Eto
import Eto.Drawing as drawing
import Eto.Forms as forms
import math
import webbrowser
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

    
us_size_dict = {
    0 : 11.63,
    1 : 12.44,
    2 : 13.26,
    3 : 14.07,
    4 : 14.88,
    5 : 15.69,
    6 : 16.51,
    7 : 17.32,
    8 : 18.13,
    9 : 18.95,
    10 : 19.76,
    11 : 20.57,
    12 : 21.38,
    13 : 22.20,
    14 : 23.01,
    15 : 23.82,
    16 : 24.63
    }

# provided by Gemini
# uk_ring_sizes = {
#     "A": 12.0,  #
#     "B": 12.4,  #
#     "C": 12.8,  #
#     "D": 13.2,  #
#     "E": 13.6,  #
#     "F": 14.1,  #
#     "G": 14.4,  #
#     "H": 14.8,  #
#     "I": 15.2,  #
#     "J": 15.4,  #
#     "K": 15.9,  #
#     "L": 16.3,  #
#     "M": 16.7,  #
#     "N": 17.1,  #
#     "O": 17.5,  #
#     "P": 17.9,  #
#     "Q": 18.3,  #
#     "R": 18.7,  #
#     "S": 19.1,  #
#     "T": 19.5,  #
#     "U": 19.9,  #
#     "V": 20.3,  #
#     "W": 20.7,  #
#     "X": 21.1,  #
#     "Y": 21.5,  #
#     "Z": 21.7,  #
#     "Z+2": 22.9,  #
#     "Z+3": 23.2,  #
#     "Z+4": 23.6,  #
# }

# if we assume C is 40mm in diameter
uk_size_dict = {
    'A' : 11.94,
    'B' : 12.33,
    'C' : 12.73,
    'D' : 13.13,
    'E' : 13.53,
    'F' : 13.93,
    'G' : 14.32,
    'H' : 14.72,
    'I' : 15.12,
    'J' : 15.52,
    'K' : 15.92,
    'L' : 16.31,
    'M' : 16.71,
    'N' : 17.11,
    'O' : 17.51,
    'P' : 17.91,
    'Q' : 18.3,
    'R' : 18.7,
    'S' : 19.1,
    'T' : 19.5,
    'U' : 19.89,
    'V' : 20.29,
    'W' : 20.69,
    'X' : 21.09,
    'Y' : 21.49,
    'Z' : 21.88,
    'Z+1' : 22.28,
    'Z+2' : 22.68,
    'Z+3' : 23.08,
    'Z+4' : 23.48
    }

# if we assume C = 40.4mm in diameter
# uk_size_dict = {
#     A : 12.06,
#     B : 12.46,
#     C : 12.86,
#     D : 13.26,
#     E : 13.66,
#     F : 14.05,
#     G : 14.45,
#     H : 14.85,
#     I : 15.25,
#     J : 15.64,
#     K : 16.04,
#     L : 16.44,
#     M : 16.84,
#     N : 17.24,
#     O : 17.63,
#     P : 18.03,
#     Q : 18.43,
#     R : 18.83,
#     S : 19.23,
#     T : 19.62,
#     U : 20.02,
#     V : 20.42,
#     W : 20.82,
#     X : 21.22,
#     Y : 21.61,
#     Z : 22.01,
#     Z1 : 22.41,
#     Z2 : 22.81,
#     Z3 : 23.2,
#     Z4 : 23.6
# }

india_size_dict = {
    1 : 13.1,
    2 : 13.3,
    3 : 13.7,
    4 : 13.9,
    5 : 14.3,
    6 : 14.7,
    7 : 15.1,
    8 : 15.3,
    9 : 15.5,
    10 : 15.9,
    11 : 16.3,
    12 : 16.5,
    13 : 16.9,
    14 : 17.3,
    15 : 17.5,
    16 : 17.9,
    17 : 18.1,
    18 : 18.5,
    19 : 18.8,
    20 : 19.2,
    21 : 19.4,
    22 : 19.8,
    23 : 20.0,
    24 : 20.4,
    25 : 20.6,
    26 : 21.0,
    27 : 21.4,
    28 : 21.6,
    29 : 22.0,
    30 : 22.3 
    }

asia_size_dict = {
    1 : 12.5,
    2 : 13.3,
    3 : 13.7,
    4 : 14.1,
    5 : 14.3,
    6 : 14.7,
    7 : 14.9,
    8 : 15.3,
    9 : 15.7,
    10 : 16.1,
    11 : 16.5,
    12 : 16.7,
    13 : 16.9,
    14 : 17.3,
    15 : 17.7,
    16 : 18.1,
    17 : 18.5,
    18 : 19.0,
    19 : 19.4,
    20 : 19.8,
    21 : 20.0,
    22 : 20.2,
    23 : 20.6,
    24 : 21.0,
    25 : 21.4,
    26 : 21.8,
    27 : 22.2  
    }

german_size_dict = {
    14 : 14,
    14.5 : 14.5,
    15 : 15,
    15.5 : 15.5,
    16 : 16,
    16.5 : 16.5,
    17 : 17,
    17.5 : 17.5,
    18 : 18,
    18.5 : 18.5,
    19 : 19,
    19.5 : 19.5,
    20 : 20,
    20.5 : 20.5,
    21 : 21,
    21.5 : 21.5,
    22 : 22,
    22.5 : 22.5,
    23 : 23,
    23.5 : 23.5,
    24 : 24
}

eu_size_dict = {
    44 : 14.0,
    45 : 14.3,
    46 : 14.6,
    47 : 15.0,
    48 : 15.3,
    49 : 15.6,
    50 : 15.9,
    51 : 16.2,
    52 : 16.6,
    53 : 16.9,
    54 : 17.2,
    55 : 17.5,
    56 : 17.8,
    57 : 18.1,
    58 : 18.5,
    59 : 18.8,
    60 : 19.1,
    61 : 19.4,
    62 : 19.7,
    63 : 20.1,
    64 : 20.4,
    65 : 20.7,
    66 : 21.0,
    67 : 21.3,
    68 : 21.6,
    69 : 22.0,
    70 : 22.3,
    71 : 22.6,
    72 : 22.9,
    73 : 23.2,
    74 : 23.6,
    75 : 23.9,
    76 : 24.2
}

swiss_size_dict = {
    4 : 14.0,
    5 : 14.3,
    6 : 14.6,
    7 : 15.0,
    8 : 15.3,
    9 : 15.6,
    10 : 15.9,
    11 : 16.2,
    12 : 16.6,
    13 : 16.9,
    14 : 17.2,
    15 : 17.5,
    16 : 17.8,
    17 : 18.1,
    18 : 18.5,
    19 : 18.8,
    20 : 19.1,
    21 : 19.4,
    22 : 19.7,
    23 : 20.1,
    24 : 20.4,
    25 : 20.7,
    26 : 21.0,
    27 : 21.3,
    28 : 21.6,
    29 : 22.0,
    30 : 22.3,
    31 : 22.6,
    32 : 22.9,
    33 : 23.2,
    34 : 23.6,
    35 : 23.9,
    36 : 24.2
}




region_abbs = ['US', 'UK', 'IND', 'ASIA', 'GER', 'EUR', 'SWISS']


list_of_size_dicts = [us_size_dict, uk_size_dict, india_size_dict, asia_size_dict, german_size_dict, eu_size_dict, swiss_size_dict]

# some general constants we'll need
regions = ['US', 'UK', 'Indian', 'Asian', 'German', 'European', 'Swiss']
us_sizes = sorted(us_size_dict.keys())
uk_sizes = sorted(uk_size_dict.keys())
india_sizes = sorted(india_size_dict.keys())
asia_sizes = sorted(asia_size_dict.keys())
german_sizes = sorted(german_size_dict.keys())
eu_sizes = sorted(eu_size_dict.keys())
swiss_sizes = sorted(swiss_size_dict.keys())

list_of_size_lists = [us_sizes, uk_sizes, india_sizes, asia_sizes, german_sizes, eu_sizes]
us_fractions = ["--", "1/8", "1/4", "3/8", "1/2", "5/8", "3/4", "7/8"]
uk_fractions = ["--", "1/2"]

# formatting constants
FORM_PADDING = 15
PANEL_PADDING = 5
GROUPBOX_PADDING = 10
TABCONTROL_PADDING = 20
TABPAGE_PADDING = 20
LAYOUT_SPACING = 10


class wdDialog(forms.Dialog):
    
    diameter = 0
    seam_point = rg.Point3d.Unset
    seam_parameter = 0
    size_dropdowns = []
    size_layouts = []
    sizing_circle = None
    seam_point = None
    canceled = True
    conduit = None
    
    def __init__(self):
        super(wdDialog, self).__init__()
        
        if rs.ExeVersion() >= 8:
            Rhino.UI.EtoExtensions.UseRhinoStyle(self)
            
        # form style properties
        self.Title = "Ring Size Tool"
        self.Padding = drawing.Padding(FORM_PADDING)
        self.Resizable = False
        self.Closing += self.OnDialogClosing
        
        self.conduit = DrawConduit(self)
        self.conduit.Enabled = True
        self.RenderObjects = []
        
        # controls
        
        # sizing system
        self.lbl_region = forms.Label()
        self.lbl_region.Text = "Sizing System: "
        self.lbl_region.TextAlignment = forms.TextAlignment.Right
        self.dd_region = forms.DropDown()
        self.dd_region.DataStore = regions
        self.dd_region.SelectedIndex = 0
        self.dd_region.SelectedIndexChanged += self.OnSizingCircleChanged
        
        # ring size
        self.lbl_size = forms.Label()
        self.lbl_size.Text = "Ring Size: "
        self.lbl_size.TextAlignment = forms.TextAlignment.Right
        
        # us sizes
        self.dd_us_sizes = forms.DropDown()
        self.dd_us_sizes.DataStore = us_sizes
        self.dd_us_sizes.SelectedIndex = 0
        self.dd_us_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_us_sizes)
        
        self.dd_uk_sizes = forms.DropDown()
        self.dd_uk_sizes.DataStore = uk_sizes
        self.dd_uk_sizes.SelectedIndex = 0
        self.dd_uk_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_uk_sizes)
        
        self.dd_india_sizes = forms.DropDown()
        self.dd_india_sizes.DataStore = india_sizes
        self.dd_india_sizes.SelectedIndex = 0
        self.dd_india_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_india_sizes)
        
        self.dd_asia_sizes = forms.DropDown()
        self.dd_asia_sizes.DataStore = asia_sizes
        self.dd_asia_sizes.SelectedIndex = 0
        self.dd_asia_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_asia_sizes)

        self.dd_german_sizes = forms.DropDown()
        self.dd_german_sizes.DataStore = german_sizes
        self.dd_german_sizes.SelectedIndex = 0
        self.dd_german_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_german_sizes)

        self.dd_eu_sizes = forms.DropDown()
        self.dd_eu_sizes.DataStore = eu_sizes
        self.dd_eu_sizes.SelectedIndex = 0
        self.dd_eu_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_eu_sizes)

        self.dd_swiss_sizes = forms.DropDown()
        self.dd_swiss_sizes.DataStore = swiss_sizes
        self.dd_swiss_sizes.SelectedIndex = 0
        self.dd_swiss_sizes.SelectedIndexChanged += self.OnSizingCircleChanged
        self.size_dropdowns.append(self.dd_swiss_sizes)
        
        self.dd_us_fra = forms.DropDown()
        self.dd_us_fra.DataStore = us_fractions
        self.dd_us_fra.SelectedIndex = 0
        self.dd_us_fra.SelectedIndexChanged += self.OnSizingCircleChanged
        
        self.dd_uk_fra = forms.DropDown()
        self.dd_uk_fra.DataStore = uk_fractions
        self.dd_uk_fra.SelectedIndex = 0
        self.dd_uk_fra.SelectedIndexChanged += self.OnSizingCircleChanged
     
        layout_us_size = forms.DynamicLayout()
        layout_us_size.Spacing = drawing.Size(5, 5)
        layout_us_size.AddRow(self.dd_us_sizes, self.dd_us_fra, None)
        self.size_layouts.append(layout_us_size)
        
        layout_uk_size = forms.DynamicLayout()
        layout_uk_size.Spacing = drawing.Size(5, 5)
        layout_uk_size.AddRow(self.dd_uk_sizes, self.dd_uk_fra, None)
        self.size_layouts.append(layout_uk_size)
        
        layout_india_size = forms.DynamicLayout()
        layout_india_size.Spacing = drawing.Size(5, 5)
        layout_india_size.AddRow(self.dd_india_sizes, None)
        self.size_layouts.append(layout_india_size)
        
        layout_asia_size = forms.DynamicLayout()
        layout_asia_size.Spacing = drawing.Size(5, 5)
        layout_asia_size.AddRow(self.dd_asia_sizes, None)
        self.size_layouts.append(layout_asia_size)

        layout_german_size = forms.DynamicLayout()
        layout_german_size.Spacing = drawing.Size(5, 5)
        layout_german_size.AddRow(self.dd_german_sizes, None)
        self.size_layouts.append(layout_german_size)

        layout_eu_size = forms.DynamicLayout()
        layout_eu_size.Spacing = drawing.Size(5, 5)
        layout_eu_size.AddRow(self.dd_eu_sizes, None)
        self.size_layouts.append(layout_eu_size)

        layout_swiss_size = forms.DynamicLayout()
        layout_swiss_size.Spacing = drawing.Size(5, 5)
        layout_swiss_size.AddRow(self.dd_swiss_sizes, None)
        self.size_layouts.append(layout_swiss_size)
        
        self.pnl_size = forms.Panel()
        
        # curve seam postion
        self.lbl_seam = forms.Label()
        self.lbl_seam.Text = "Seam Position: "
        self.lbl_seam.TextAlignment = forms.TextAlignment.Right
        self.rbl_seam = forms.RadioButtonList()
        self.rbl_seam.Spacing = drawing.Size(10,10)
        self.rbl_seam.Padding = drawing.Padding(0, 5, 0, 5)
        self.rbl_seam.DataStore = ["Top", "Bottom"]
        self.rbl_seam.Orientation = forms.Orientation.Horizontal
        self.rbl_seam.SelectedIndex = 1
        self.rbl_seam.SelectedIndexChanged += self.OnSizingCircleChanged
        
        # diameter display
        self.lbl_diameter = forms.Label()
        self.lbl_diameter.Text = "Diameter: "
        self.lbl_diameter.TextAlignment = forms.TextAlignment.Right
        self.lbl_diameter_data = forms.Label()
        self.lbl_diameter_data.Text = "17.5mm"
        
        # buttons
        self.btn_ok = forms.Button()
        self.btn_ok.Text = 'Finalize'
        self.btn_ok.Click += self.OnOKButtonClick

        self.btn_cancel = forms.Button()
        self.btn_cancel.Text = 'Cancel'
        self.btn_cancel.Click += self.OnCloseButtonClick 
        
        self.AbortButton = self.btn_cancel
        self.DefaultButton = self.btn_ok
        
        # dialog layout
        layout_dlg = forms.DynamicLayout()
        layout_dlg.DefaultSpacing = drawing.Size(5, 5)
        
        layout_dlg.BeginVertical()
        layout_dlg.AddRow(self.lbl_region, self.dd_region)
        layout_dlg.AddRow(self.lbl_size, self.pnl_size)
        layout_dlg.AddRow(self.lbl_seam, self.rbl_seam)
        layout_dlg.AddRow(self.lbl_diameter, self.lbl_diameter_data)
        layout_dlg.EndVertical()
        
        layout_dlg.BeginVertical()
        layout_dlg.AddRow(None)
        layout_dlg.AddRow(None)
        layout_dlg.AddRow(None)
        layout_dlg.AddRow(self.btn_ok)
        layout_dlg.AddRow(self.btn_cancel)
        layout_dlg.EndVertical()
        
        self.Content = layout_dlg
        self.Update()

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
        
    def GetDiameter(self):
        if 'Ger' not in self.dd_region.SelectedValue:
            # get region
            region_index = self.dd_region.SelectedIndex
            region = self.dd_region.SelectedValue
            region_size_dict = list_of_size_dicts[region_index]
            
            # get size
            size = 0
            for i in range(len(self.size_dropdowns)):
                if i == region_index:
                    size = self.size_dropdowns[i].SelectedValue
            
            # get diameter from size
            d = region_size_dict[size]
            
            # get fractional diameter from fraction
            fraction = 0
            if self.dd_us_fra.Visible == True:
                if self.dd_us_fra.SelectedIndex > 0:
                    size_increment = 0.8128
                    bits = self.dd_us_fra.SelectedValue.split("/")
                    numerator = int(bits[0])
                    denominator = int(bits[1])
                    fraction = round((numerator / denominator) * size_increment,2)
                    
            if self.dd_uk_fra.Visible == True:
                if self.dd_uk_fra.SelectedIndex > 0:
                    fraction = 0.2
            
            # add diameter and fractional diameter
            d = d + fraction
        else:
            d = float(self.dd_german_sizes.SelectedValue)

        return d
        
    def GetSize(self):
        # get region
        region_index = self.dd_region.SelectedIndex
        region = self.dd_region.SelectedValue
        region_size_dict = list_of_size_dicts[region_index]
        
        # get size
        size = 0
        for i in range(len(self.size_dropdowns)):
            if i == region_index:
                size = self.size_dropdowns[i].SelectedValue
                
        # get fractional diameter from fraction
        fraction = 0
        if self.dd_us_fra.Visible == True:
            if self.dd_us_fra.SelectedIndex > 0:
                size_increment = 0.8128
                bits = self.dd_us_fra.SelectedValue.split("/")
                numerator = int(bits[0])
                denominator = int(bits[1])
                fraction = round(numerator / denominator,4)
                
        if self.dd_uk_fra.Visible == True:
            if self.dd_uk_fra.SelectedIndex > 0:
                fraction = " 1/2"
            else:
                fraction = ""
        
        # add diameter and fractional diameter
        size = size + fraction
        return size
        
    def Update(self):
        # get region
        region_index = self.dd_region.SelectedIndex
        region = regions[region_index]
        
        # make correct size dropdown visible
        self.pnl_size.Content = self.size_layouts[region_index]
        
        # display fractional drop down if needed
        if region_index == 0:
            self.dd_us_fra.Visible = True
            self.dd_us_fra.Width = -1
        else:
            self.dd_us_fra.Visible = False
            
        if region_index == 1:
            self.dd_uk_fra.Visible = True
            self.dd_uk_fra.Width = -1
        else:
            self.dd_uk_fra.Visible = False
            self.dd_uk_fra.Width = 0

        # get diameter and display it
        d = self.GetDiameter()
        self.lbl_diameter_data.Text = str(d) + "mm"
        
        # create circle
        self.DisposeObject(self.sizing_circle)
        self.sizing_circle = rg.Circle(rg.Plane.WorldZX, d/2).ToNurbsCurve()
            
        # create seam point (for visualization only)
        if self.rbl_seam.SelectedIndex == 0:
            self.seam_point = rg.Point3d(0,0,d/2)
        else:
            self.seam_point = rg.Point3d(0,0,-d/2)
            
        # change seam as needed
        rc, self.seam_parameter = self.sizing_circle.ClosestPoint(self.seam_point)
        rg.Curve.ChangeClosedCurveSeam(self.sizing_circle, self.seam_parameter)

        self.DisposeRenderObjects()
        self.RenderObjects = []
        self.RenderObjects.append([self.seam_point, cam.PointColor])
        self.RenderObjects.append([self.sizing_circle, cam.CurveColor])

        sc.doc.Views.Redraw()
        
    def OnSizingCircleChanged(self, sender, e):
        self.Update()
        
    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.Close()
 
    # OK button click handler
    def OnOKButtonClick(self, sender, e):
        layer_name = 'sizing circle'
        if not rs.IsLayer(layer_name):
            rs.AddLayer(layer_name, System.Drawing.Color.FromArgb(255, 100, 12, 12))

        layer = sc.doc.Layers.FindName(layer_name)
        atts = Rhino.DocObjects.ObjectAttributes()
        atts.LayerIndex = layer.Index

        guid = sc.doc.Objects.AddCurve(self.sizing_circle, atts)
        obj_name = region_abbs[self.dd_region.SelectedIndex] + " Size: " + str(self.GetSize())
        rs.ObjectName(guid, obj_name)
        self.DisposeObject(self.sizing_circle)
        self.Close()
        
    def OnDialogClosing(self, sender, e):
        self.conduit.Enabled = False
        
    ## END DIALOG CLASS ##



# the main code
if __name__ == "__main__":        
    dialog = wdDialog()
    if rs.ExeVersion() > 6:
        parent = Rhino.UI.RhinoEtoApp.MainWindowForDocument(sc.doc)
    else:
        parent = Rhino.UI.RhinoEtoApp.MainWindow
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, sc.doc, parent)