#! python 2
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import os

xtras_dict = {
    "Bail":"bail.3dm",
    "Braid Pattern":"braid_pattern.3dm",
    "Chain (Single)":"chain1.3dm",
    "Chains (Left & Right)":"chain2.3dm",
    "Heart Outline":"heart_outline.3dm"
    }

jumpring_dict = {
    "0.50mm x 1.00mm":"jr050x100.3dm",
    "0.65mm x 1.30mm":"jr065x130.3dm",
    "0.80mm x 1.60mm":"jr080x160.3dm",
    "0.80mm x 2.00mm":"jr080x200.3dm",
    "1.00mm x 2.50mm":"jr100x250.3dm",
    "1.00mm x 3.00mm":"jr100x300.3dm"
    }

xtras_items = [
    "Bail",
    "Braid Pattern",
    "Chain (Single)",
    "Chains (Left & Right)",
    "Heart Outline",
    "Jump Rings",
    "Miscellaneous Gems"
    ]

jumpring_items = [
    "0.50mm x 1.00mm",
    "0.65mm x 1.30mm",
    "0.80mm x 1.60mm",
    "0.80mm x 2.00mm",
    "1.00mm x 2.50mm",
    "1.00mm x 3.00mm",
    "Back"    
    ]

gem_items = [
    'Checker-Cut Cabochon',
    'Checker-Cut Gem',
    'Rose-Cut Hexagon',
    'Back'
]

macro = rs.AliasMacro('wdGem')
wdgem_script = macro.replace('!_-RunPythonScript ', '')
wdgem_script = wdgem_script.replace('"', '')
script_folder = os.path.dirname(wdgem_script)
kit_folder = os.path.dirname(script_folder)
xtras_folder = os.path.join(kit_folder, "xtras")

def LoadObject(folder, filename):
    path = os.path.join(folder, filename)
    options = Rhino.FileIO.FileReadOptions()
    options.ImportMode = True
    options.UseScaleGeometry = True
    sc.doc.ReadFile(path, options)
    options.Dispose()

def ChooseItem():
    xtras_item = rs.ListBox(xtras_items, "Select an item.", "Xtras Objects")
    if xtras_item:
        if xtras_item == "Jump Rings":
            jumpring_item = rs.ListBox(jumpring_items, "Select a jump ring size.", "Jump Ring Sizes")
            if jumpring_item:
                if jumpring_item == "Back":
                    ChooseItem()
                else:
                    filename = jumpring_dict[jumpring_item]
                    LoadObject(xtras_folder, filename)
        elif xtras_item == "Miscellaneous Gems":
            gem_item = rs.ListBox(gem_items, "Select a gem.", "Miscellaneous Gems")
            if gem_item:
                if gem_item == "Back":
                    ChooseItem()
                else:
                    filename = gem_item + '.3dm'
                    LoadObject(xtras_folder, filename)
        else:
            filename = xtras_dict[xtras_item]
            LoadObject(xtras_folder, filename)

ChooseItem()

# selected_filename = rs.ListBox(xtras_filenames, "Select an object", "Xtra Objects", None)
# if selected_filename:
#     LoadObject(xtras_folder, selected_filename)