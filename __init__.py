bl_info = {
    "name": "Aura V17.0 Sentient Symbiote Environment",
    "author": "Aura Development Team",
    "version": (17, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Design",
    "description": "V17.0 Sentient Symbiote Environment - State-of-the-art implicit function-based AI co-pilot with real-time cognitive streaming and Marching Cubes surface extraction",
    "category": "3D View",
}


from .setup import install, uninstall

def register():
    install()

def unregister():
    uninstall()
