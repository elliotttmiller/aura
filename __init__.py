bl_info = {
    "name": "AI Design Assistant",
    "author": "Your Company",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Design",
    "description": "An AI co-pilot for advanced 3D design",
    "category": "3D View",
}

from .setup import install, uninstall

def register():
    install()

def unregister():
    uninstall()
