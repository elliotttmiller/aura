bl_info = {
    "name": "Aura V14.0 Sentient Artisan Environment",
    "author": "Aura Development Team",
    "version": (14, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Design",
    "description": "V14.0 Sentient Artisan Environment - AI co-pilot for master-level jewelry design with real-time cognitive streaming",
    "category": "3D View",
}


from .setup import install, uninstall

def register():
    install()

def unregister():
    uninstall()
