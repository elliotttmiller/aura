bl_info = {
    "name": "Aura V24 Autonomous Design Engine",
    "author": "Aura Development Team",
    "version": (24, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Aura",
    "description": "V24 Autonomous & Holistic Design Engine - State-of-the-art AI-driven 3D creation with sentient transparency, autonomous cognitive authority, and flawless end-to-end integration",
    "category": "3D View",
}


from .setup import install, uninstall

def register():
    install()

def unregister():
    uninstall()
