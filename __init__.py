bl_info = {
    "name": "Universal Design Engine V20.0",
    "author": "Universal Design Engine Development Team",
    "version": (20, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Design",
    "description": "V20.0 Universal Design Engine - State-of-the-art implicit function-based AI co-pilot with real-time cognitive streaming and Marching Cubes surface extraction for procedural asset generation",
    "category": "3D View",
}


from .setup import install, uninstall

def register():
    install()

def unregister():
    uninstall()
