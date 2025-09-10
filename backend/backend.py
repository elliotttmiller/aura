"""
Backend Compatibility Layer
===========================

Minimal backend functions for V14.0 compatibility with existing setup.
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)


def check_dependencies(report_error=True):
    """
    Check if critical dependencies are available.
    
    Args:
        report_error: Whether to report errors (for backward compatibility)
        
    Returns:
        bool: True if dependencies are available
    """
    try:
        # Check for basic Python packages that should be available
        import json
        import threading
        import queue
        
        # Check if Blender bpy is available (we're running inside Blender)
        import bpy
        
        return True
    except ImportError as e:
        if report_error:
            logger.error(f"Dependency check failed: {e}")
        return False


# Stub functions for backward compatibility
def ProcessingEngine():
    """Stub for backward compatibility."""
    pass


def create_object_in_scene(*args, **kwargs):
    """Stub for backward compatibility."""
    pass


def prepare_and_join(*args, **kwargs):
    """Stub for backward compatibility."""
    pass


def run_analysis(*args, **kwargs):
    """Stub for backward compatibility."""
    pass


def import_model(filepath):
    """Basic model import functionality."""
    try:
        if filepath.lower().endswith('.obj'):
            import bpy
            bpy.ops.import_scene.obj(filepath=filepath)
        elif filepath.lower().endswith('.stl'):
            import bpy
            bpy.ops.import_mesh.stl(filepath=filepath)
        logger.info(f"Imported model: {filepath}")
    except Exception as e:
        logger.error(f"Failed to import model {filepath}: {e}")


def export_model(filepath, context, export_format='STL'):
    """Basic model export functionality."""
    try:
        import bpy
        
        if export_format.upper() == 'STL':
            bpy.ops.export_mesh.stl(filepath=filepath, use_selection=True)
        elif export_format.upper() == 'OBJ':
            bpy.ops.export_scene.obj(filepath=filepath, use_selection=True)
            
        logger.info(f"Exported model: {filepath}")
    except Exception as e:
        logger.error(f"Failed to export model {filepath}: {e}")