import sys
from pathlib import Path

ADDON_ROOT = Path(__file__).parent.parent

def get_addon_root():
    return ADDON_ROOT

def get_models_path():
    return ADDON_ROOT / "models"

def get_assets_path():
    return ADDON_ROOT / "assets"

def add_vendor_to_path():
    vendor_path = str(ADDON_ROOT / "vendor")
    if vendor_path not in sys.path:
        sys.path.append(vendor_path)
add_vendor_to_path()
