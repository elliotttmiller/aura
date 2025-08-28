import bpy

from .settings import install_settings, uninstall_settings
from .preferences import AddonPreferences, install_preferences, uninstall_preferences

from .frontend.workflow_panel import WorkflowPanel
from .frontend.ai_panel import AIPanel
from .frontend.analysis_panel import AnalysisPanel
from .frontend.library_panel import LibraryPanel

from .actions.generate_action import GenerateFromScratchOperator, AddDetailOperator
from .actions.analyze_action import AnalyzeOperator
from .actions.add_asset_action import AddAssetOperator
from .actions.interop_action import ImportOperator, ExportOperator

ALL_CLASSES = [
    AddonPreferences,
    WorkflowPanel,
    AIPanel,
    AnalysisPanel,
    LibraryPanel,
    GenerateFromScratchOperator,
    AddDetailOperator,
    AnalyzeOperator,
    AddAssetOperator,
    ImportOperator,
    ExportOperator,
]

def install():
    print("Installing Professional Workflow Add-on...")
    install_settings()
    install_preferences()
    for cls in ALL_CLASSES:
        bpy.utils.register_class(cls)

def uninstall():
    print("Uninstalling Professional Workflow Add-on...")
    for cls in reversed(ALL_CLASSES):
        bpy.utils.unregister_class(cls)
    uninstall_preferences()
    uninstall_settings()
