#! python 2
import Rhino
import Rhino.Geometry as rg
import Rhino.RhinoApp as app
import rhinoscriptsyntax as rs
import scriptcontext as sc

def print2(*args):
    txt = ""
    for i in range(len(args)):
        txt += str(args[i])
        if i < len(args)-1: txt += ', '
    app.WriteLine(txt)

def DisposeObjects(obs):
    for ob in obs:
        DisposeObject(ob)

def DisposeObject(ob):
    if hasattr(ob, 'Dispose'): ob.Dispose()

def DisposeRenderObjects(dialog):
    if hasattr(dialog, 'RenderObjects'):
        for ob in dialog.RenderObjects:
            DisposeObject(ob)

    if hasattr(dialog, 'EdgeCurves'):
        for ob in dialog.EdgeCurves:
            DisposeObject(ob)
