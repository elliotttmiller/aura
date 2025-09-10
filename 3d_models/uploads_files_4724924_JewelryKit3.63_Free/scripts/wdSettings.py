#! python 2
import rhinoscriptsyntax as rs
import Rhino
import os
import platform
import subprocess
import zipfile
import shutil

macro = rs.AliasMacro('wdGem')
wd1gem_script = macro.replace('!_-RunPythonScript ', '')
wd1gem_script = wd1gem_script.replace('"', '')
script_folder = os.path.dirname(wd1gem_script)
kit_folder = os.path.dirname(script_folder)
kit_toolbar_folder = os.path.abspath(os.path.join(script_folder, "data", "toolbar"))
ui_folder = os.path.join(os.getenv("APPDATA"),"McNeel", "Rhinoceros", str(rs.ExeVersion()) + ".0", "UI")
old_commands = ["wdGem", "wdJumpRing", "wdMaterials", "wdRingSize", "wdXtras"]
preload_cmd = "wdPreLoad"

# this is McNeel's ShowToolbar script. It doesn't work when
# accessed via rhinoscriptsyntax, but it does if used here
# for some reason
def ShowToolbar(name, toolbar_group):
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        group = tbfile.GetGroup(toolbar_group)
        if group:
            group.Visible = True
            return True
    return False

# this is McNeel's IsToolbarVisible script. It doesn't work when
# accessed via rhinoscriptsyntax, but it does if used here
# for some reason   
def IsToolbarVisible(name, toolbar_group):
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        group = tbfile.GetGroup(toolbar_group)
        if group: return group.Visible

# this is McNeel's ToolbarNames script. It doesn't work when
# accessed via rhinoscriptsyntax, but it does if used here
# for some reason 
def ToolbarNames(name, groups=False):
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        rc = []
        if groups:
            for i in range(tbfile.GroupCount): rc.append(tbfile.GetGroup(i).Name)
        else:
            for i in range(tbfile.ToolbarCount): rc.append(tbfile.GetToolbar(i).Name)
        return rc;

def RemoveKitCommands():
    # remove any old commands that might exist
    for cmd in old_commands:
        if rs.IsAlias(cmd):
            rs.DeleteAlias(cmd)

    # remove all current commands
    potential_names = os.listdir(script_folder)
    for name in potential_names:
        if "wd" in name:
            cmd = name.split(".")[0]
            if rs.IsAlias(cmd):
                rs.DeleteAlias(cmd)

    print("The kit's commands were removed.")


def WipeKitCommands():
    result = rs.MessageBox(
        "You will not be able to use the kit's toolbar after wiping the commands. Continue?",
        4 | 32,
    )
    if result == 6:
        RemoveKitCommands()


def RestoreKitCommands():
    RemoveKitCommands()
    potential_names = os.listdir(script_folder)
    for name in potential_names:
        if "wd" in name:
            cmd = name.split(".")[0]
            macro = ""
            if "wd2" in cmd:
                macro = (
                    "!_-Grasshopper _Document _Open "
                    + os.path.join(script_folder, name)
                    + " _Enter"
                )
            else:
                macro = "!_-RunPythonScript " + os.path.join(script_folder, name)

            rs.AddAlias(cmd, macro)
    print("The kit's commands were restored.")
    rs.MessageBox("The kit's commands were restored.")


# only meant for text files, xml files, etc
def OpenPath(path):
    if os.path.exists(path):
        if platform.system() == "Windows":
            os.startfile(path)
        else:
            subprocess.call(["open", path])
    else:
        rs.MessageBox("Path does not exist.")


def CopyKitPath():
    rs.ClipboardText(kit_folder)
    rs.MessageBox("The kit folder's path was copied to clipboard")


def CopyToolbarFilePath():
    toolbarPath = os.path.join(script_folder, "data", "toolbar")
    toolbarPath = os.path.join(toolbarPath, os.listdir(toolbarPath)[0])
    rs.ClipboardText(toolbarPath)
    rs.MessageBox("The kit's toolbar path was copied to clipboard.")


def CopyToolbarFolderPath():
    toolbarFolderPath = os.path.join(script_folder, "data", "toolbar")
    rs.ClipboardText(toolbarFolderPath)
    rs.MessageBox("The kit's toolbar folder path was copied to clipboard.")

def CopyPreLoadCommand():
    rs.ClipboardText(preload_cmd)
    rs.MessageBox('The command ' + preload_cmd + ' has been copied to the clipboard.')

def RunPreLoadCommand():
    rs.Command(preload_cmd)

def OpenUIFolder():
    if os.path.exists(ui_folder):
        if platform.system() == "Windows":
            os.startfile(ui_folder)
        else:
            subprocess.call(["open", ui_folder])
    else:
        rs.MessageBox("The UI folder was not found.")


def CopyUIFolderPath():
    if os.path.exists(ui_folder):
        rs.ClipboardText(ui_folder)
        rs.MessageBox("Rhino's UI folder's location was copied to clipboard")
    else:
        rs.MessageBox("Thue UI folder was not found.")

def ShowKitInfo():
    kit_name = os.path.basename(kit_folder)
    parts = kit_name.split("_")
    kit_version = parts[0].replace("JewelryKit", "")
    free_or_paid = "Paid"
    rhino_version = parts[1].replace("Rhino", "")
    if "Free" in kit_name: free_or_paid = "Free"
    info = "Kit Version: " + kit_version + "\n"
    info += "Free or Paid: " + free_or_paid + "\n"
    info += "Rhino Version: " + rhino_version
    rs.MessageBox(info)

def ShowToolbar():
    kit_name = os.path.basename(kit_folder)
    parts = kit_name.split("_")
    kit_version = parts[0].replace("JewelryKit", "")
    rhino_version = '' if rs.ExeVersion() < 8 else '.8'    
    free = 'Free' if 'Free' in kit_name else ''
    if "Free" in kit_name: free = "Free"
    
    toolbar_filename = "JewelryKit" + free + kit_version + rhino_version + ".rui"
    toolbar_name = "JewelryKit" + free + kit_version + rhino_version + ".JewelryKit"
    
    if IsToolbarOpen():
        rs.Command('_-ShowToolbar "' + toolbar_name + '"')
    else:
        OpenToolbar()

def IsToolbarOpen():
    is_open = False
    tb_names = rs.ToolbarCollectionNames()
    if tb_names:
        for name in tb_names:
            if "JewelryKit" in name:
                is_open = True
    return is_open

def IsFree():
    is_free = False
    macro = rs.AliasMacro("wd1Gem")
    if "Free" in macro:
        is_free = True

    return is_free

def OpenToolbar():
    kit_name = os.path.basename(kit_folder)
    parts = kit_name.split("_")
    kit_version = parts[0].replace("JewelryKit", "")
    rhino_version = '' if rs.ExeVersion() < 8 else '.8'    
    free = 'Free' if 'Free' in kit_name else ''
    if "Free" in kit_name: free = "Free"
    
    toolbar_filename = "JewelryKit" + free + kit_version + rhino_version + ".rui"
    toolbar_name = "JewelryKit" + free + kit_version + rhino_version + ".JewelryKit"
    
    toolbar_folder = os.path.join(kit_folder, "scripts", "data", "toolbar")
    toolbar_path = os.path.join(toolbar_folder, toolbar_filename)                
    rs.OpenToolbarCollection(toolbar_path)
    
    rs.Command('_-ShowToolbar "' + toolbar_name + '"')

choices = [
    "Copy Kit Folder's Path",
    # "Copy PreLoad Command",
    "Open Kit Toolbar",
    "Open Kit Folder",
    # "Run PreLoad Command",
    "Restore Commands",
    "Show Kit Info"
]

choice = rs.ListBox(choices, "Choose an option", "Kit Settings", None)

if choice == "Open Kit Toolbar":
    ShowToolbar()
elif choice == "Open Kit Folder":
    OpenPath(kit_folder)
elif choice == "Copy Kit Folder's Path":
    CopyKitPath()
elif choice == "Copy PreLoad Command":
    CopyPreLoadCommand()
elif choice == "Run PreLoad Command":
    RunPreLoadCommand()
elif choice == "Restore Commands":
    RestoreKitCommands()
elif choice == "Show Kit Info":
    ShowKitInfo()
