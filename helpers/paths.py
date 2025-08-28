import sys
from pathlib import Path

# __file__ gives the path to this file (paths.py)
# .parent gives the directory (helpers/)
# .parent again gives the root of the add-on package (aura/)
ADDON_ROOT = Path(__file__).parent.parent

def get_addon_root():
    """Returns the root path of the entire add-on."""
    return ADDON_ROOT

def get_models_path():
    """Returns the path to the 'models' folder for AI files."""
    return ADDON_ROOT / "models"

def get_assets_path():
    """Returns the path to the 'assets' folder for library files."""
    return ADDON_ROOT / "assets"

def add_vendor_to_path():
    """Adds the vendor directory to Python's path to find dependencies."""
    vendor_path = str(ADDON_ROOT / "vendor")
    if vendor_path not in sys.path:
        sys.path.append(vendor_path)

# Ensure our dependencies can be found as soon as the add-on is loaded
add_vendor_to_path()
