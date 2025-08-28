
import bpy
from backend.aura_backend import check_dependencies

from .settings import install_settings, uninstall_settings
from .preferences import AddonPreferences, install_preferences, uninstall_preferences


from .frontend.aura_panel import WorkflowPanel, AIPanel, AnalysisPanel, LibraryPanel, GenerateFromScratchOperator, AddDetailOperator, AnalyzeOperator, AddAssetOperator, ImportOperator, ExportOperator


ALL_CLASSES = [
    AddonPreferences,
    WorkflowPanel, AIPanel, AnalysisPanel, LibraryPanel,
    GenerateFromScratchOperator, AddDetailOperator, AnalyzeOperator,
    AddAssetOperator, ImportOperator, ExportOperator,
]

def install():
    print("Installing AI Design Assistant...")
    # Perform a check on startup and print a warning to the console if needed
    if not check_dependencies(report_error=False):
        print("Aura Warning: Critical dependencies (like onnxruntime) not found in the 'vendor' folder. The AI features will be disabled.")

    install_settings()
    install_preferences()
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)

def uninstall():
    print("Uninstalling AI Design Assistant...")
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
    uninstall_preferences()
    uninstall_settings()
