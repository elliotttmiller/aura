"""
Blender Bridge - Subprocess Execution Layer
============================================

This module provides the critical bridge between the FastAPI web server and Blender.
It spawns Blender in headless mode to execute 3D generation scripts that require
the Blender Python API (bpy).

Key Responsibilities:
- Spawn Blender subprocess with construction blueprints
- Execute generation scripts in Blender's Python environment
- Extract GLB files from output packages
- Manage file serving to frontend
- Handle timeouts and error recovery

Part of the V36 Universal Artisan production implementation.
"""

import os
import sys
import json
import subprocess
import tempfile
import zipfile
import shutil
import logging
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class BlenderBridge:
    """
    Bridge between FastAPI backend and Blender subprocess execution.
    
    This class handles the complete lifecycle of 3D model generation:
    1. Prepare Blender execution environment
    2. Spawn Blender in headless mode
    3. Execute generation scripts
    4. Extract and serve generated files
    """
    
    def __init__(self, blender_path: Optional[str] = None, timeout: int = 300):
        """
        Initialize the Blender bridge.
        
        Args:
            blender_path: Path to Blender executable (auto-detected if None)
            timeout: Maximum execution time in seconds
        """
        self.blender_path = blender_path or self._find_blender()
        self.timeout = timeout
        self.backend_dir = Path(__file__).parent
        self.output_dir = self.backend_dir.parent / "output"
        self.models_dir = self.backend_dir.parent / "3d_models"
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"BlenderBridge initialized with Blender: {self.blender_path}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Models directory: {self.models_dir}")
    
    def _find_blender(self) -> str:
        """
        Auto-detect Blender executable path.
        
        Returns:
            Path to Blender executable
            
        Raises:
            FileNotFoundError: If Blender cannot be found
        """
        # Try environment variable first
        from ..config import get_blender_path
        env_path = get_blender_path()
        if env_path and Path(env_path).exists():
            return env_path
        
        # Common Blender installation paths
        common_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "C:\\Program Files\\Blender Foundation\\Blender 4.5\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "/Applications/Blender.app/Contents/MacOS/Blender",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                logger.info(f"Auto-detected Blender at: {path}")
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(['which', 'blender'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                logger.info(f"Found Blender in PATH: {path}")
                return path
        except Exception:
            pass
        
        raise FileNotFoundError(
            "Blender executable not found. Please install Blender or set BLENDER_PATH environment variable."
        )
    
    def generate_3d_model(
        self,
        blueprint: Dict[str, Any],
        session_id: str,
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate a 3D model using Blender subprocess.
        
        Args:
            blueprint: AI-generated construction blueprint
            session_id: Unique session identifier
            user_prompt: Original user prompt
            
        Returns:
            Dictionary with generation results and file paths
        """
        logger.info(f"Starting 3D generation for session {session_id}")
        logger.info(f"User prompt: {user_prompt}")
        
        start_time = time.time()
        
        try:
            # Create temporary workspace
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Prepare Blender script
                script_path = self._create_blender_script(
                    temp_path, blueprint, session_id, user_prompt
                )
                
                # Execute Blender subprocess
                result = self._execute_blender(script_path, temp_path)
                
                # Process results
                if result['success']:
                    # Extract and serve generated files
                    output_files = self._process_output_files(
                        temp_path, session_id
                    )
                    
                    execution_time = time.time() - start_time
                    
                    logger.info(f"✅ 3D generation completed in {execution_time:.2f}s")
                    
                    return {
                        'success': True,
                        'execution_time': execution_time,
                        'model_url': output_files.get('glb_url'),
                        'model_path': output_files.get('glb_path'),
                        'renders': output_files.get('renders', {}),
                        'package_path': output_files.get('package_path'),
                        'blender_output': result.get('output', '')
                    }
                else:
                    execution_time = time.time() - start_time
                    logger.error(f"❌ 3D generation failed: {result.get('error')}")
                    
                    return {
                        'success': False,
                        'execution_time': execution_time,
                        'error': result.get('error', 'Unknown Blender execution error'),
                        'blender_output': result.get('output', ''),
                        'blender_error': result.get('stderr', '')
                    }
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.exception(f"Exception during 3D generation: {e}")
            
            return {
                'success': False,
                'execution_time': execution_time,
                'error': f"Blender bridge exception: {str(e)}"
            }
    
    def _create_blender_script(
        self,
        temp_path: Path,
        blueprint: Dict[str, Any],
        session_id: str,
        user_prompt: str
    ) -> Path:
        """
        Create a Blender Python script for execution.
        
        Args:
            temp_path: Temporary directory path
            blueprint: Construction blueprint
            session_id: Session identifier
            user_prompt: User prompt
            
        Returns:
            Path to created script file
        """
        script_path = temp_path / "generate_model.py"
        
        # Save blueprint to file
        blueprint_path = temp_path / "blueprint.json"
        with open(blueprint_path, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        # Create the Blender script
        script_content = f'''#!/usr/bin/env python3
"""
Blender Generation Script - Auto-generated
==========================================
Session: {session_id}
Prompt: {user_prompt}
"""

import bpy
import sys
import json
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path("{self.backend_dir}")
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))

print("=" * 80)
print("BLENDER 3D GENERATION STARTED")
print("=" * 80)
print(f"Session ID: {session_id}")
print(f"Blender version: {{bpy.app.version_string}}")
print(f"Python version: {{sys.version}}")
print(f"Working directory: {{os.getcwd()}}")
print("=" * 80)

try:
    # Import execution engine
    print("Importing execution engine...")
    from backend.execution_engine import UnifiedExecutionEngine
    print("✓ Execution engine imported")
    
    # Load blueprint
    print("Loading blueprint...")
    blueprint_path = Path("{blueprint_path}")
    with open(blueprint_path, 'r') as f:
        blueprint = json.load(f)
    print(f"✓ Blueprint loaded: {{len(blueprint.get('construction_plan', []))}} operations")
    
    # Initialize execution engine
    print("Initializing execution engine...")
    engine = UnifiedExecutionEngine()
    print("✓ Execution engine initialized")
    
    # Prepare output paths
    output_dir = Path("{temp_path}")
    glb_path = output_dir / "{session_id}.glb"
    package_path = output_dir / "{session_id}_package.zip"
    
    print(f"Output GLB: {{glb_path}}")
    print(f"Output package: {{package_path}}")
    
    # Execute generation
    print("=" * 80)
    print("EXECUTING CONSTRUCTION PLAN")
    print("=" * 80)
    
    result = engine.generate_jewelry(
        construction_plan=blueprint.get('construction_plan', []),
        presentation_plan=blueprint.get('presentation_plan', {{}}),
        output_path=str(glb_path)
    )
    
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"Success: {{result.get('success', False)}}")
    print(f"Execution time: {{result.get('execution_time', 0):.2f}}s")
    
    # Save result metadata
    result_path = output_dir / "result.json"
    with open(result_path, 'w') as f:
        # Convert result to JSON-serializable format
        json_result = {{
            'success': result.get('success', False),
            'execution_time': result.get('execution_time', 0),
            'primary_asset': str(result.get('primary_asset', '')),
            'package_path': str(result.get('package_path', '')),
            'error': str(result.get('error', '')) if 'error' in result else None
        }}
        json.dump(json_result, f, indent=2)
    
    print(f"✓ Result saved to: {{result_path}}")
    
    # Export GLB if not already done by engine
    if result.get('success') and not glb_path.exists():
        print("Exporting GLB manually...")
        bpy.ops.export_scene.gltf(
            filepath=str(glb_path),
            export_format='GLB',
            use_selection=False,
            export_apply=True
        )
        print(f"✓ GLB exported to: {{glb_path}}")
    
    print("=" * 80)
    print("BLENDER SCRIPT COMPLETED SUCCESSFULLY")
    print("=" * 80)
    sys.exit(0)
    
except Exception as e:
    print("=" * 80)
    print("BLENDER SCRIPT FAILED")
    print("=" * 80)
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
    print("=" * 80)
    sys.exit(1)
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        logger.info(f"Created Blender script: {script_path}")
        return script_path
    
    def _execute_blender(self, script_path: Path, temp_path: Path) -> Dict[str, Any]:
        """
        Execute Blender in headless mode with the generation script.
        
        Args:
            script_path: Path to Blender Python script
            temp_path: Temporary directory path
            
        Returns:
            Execution result dictionary
        """
        logger.info("Executing Blender subprocess...")
        
        cmd = [
            self.blender_path,
            '--background',  # Headless mode
            '--python', str(script_path),  # Execute our script
        ]
        
        logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(temp_path)
            )
            
            logger.info(f"Blender process completed with return code: {result.returncode}")
            
            # Log output for debugging
            if result.stdout:
                logger.debug(f"Blender stdout:\n{result.stdout}")
            if result.stderr:
                logger.debug(f"Blender stderr:\n{result.stderr}")
            
            # Check result file
            result_file = temp_path / "result.json"
            if result_file.exists():
                with open(result_file, 'r') as f:
                    blender_result = json.load(f)
                
                return {
                    'success': blender_result.get('success', False) and result.returncode == 0,
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'blender_result': blender_result
                }
            else:
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'error': 'No result file generated by Blender script'
                }
        
        except subprocess.TimeoutExpired:
            logger.error(f"Blender execution timed out after {self.timeout}s")
            return {
                'success': False,
                'error': f'Blender execution timeout ({self.timeout}s)',
                'output': '',
                'stderr': ''
            }
        
        except Exception as e:
            logger.exception(f"Blender execution exception: {e}")
            return {
                'success': False,
                'error': f'Blender execution exception: {str(e)}',
                'output': '',
                'stderr': ''
            }
    
    def _process_output_files(
        self,
        temp_path: Path,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Process and serve generated output files.
        
        Args:
            temp_path: Temporary directory with generated files
            session_id: Session identifier
            
        Returns:
            Dictionary with file paths and URLs
        """
        logger.info("Processing output files...")
        
        output_files = {}
        
        # Look for GLB file
        glb_file = temp_path / f"{session_id}.glb"
        if glb_file.exists():
            # Copy to models directory for serving
            dest_glb = self.models_dir / f"ai_generated_{session_id}.glb"
            shutil.copy(glb_file, dest_glb)
            
            output_files['glb_path'] = str(dest_glb)
            output_files['glb_url'] = f"/3d_models/ai_generated_{session_id}.glb"
            
            logger.info(f"✓ GLB file copied to: {dest_glb}")
        else:
            logger.warning(f"GLB file not found: {glb_file}")
        
        # Look for package ZIP
        package_file = temp_path / f"{session_id}_package.zip"
        if package_file.exists():
            # Copy to output directory
            dest_package = self.output_dir / f"ai_generated_{session_id}_package.zip"
            shutil.copy(package_file, dest_package)
            
            output_files['package_path'] = str(dest_package)
            
            # Try to extract GLB from package if not found above
            if 'glb_path' not in output_files:
                glb_from_package = self._extract_glb_from_package(package_file, session_id)
                if glb_from_package:
                    output_files.update(glb_from_package)
            
            logger.info(f"✓ Package copied to: {dest_package}")
        
        # Look for render images
        renders = {}
        for render_file in temp_path.glob("*.png"):
            render_name = render_file.stem
            dest_render = self.output_dir / f"ai_generated_{session_id}_{render_name}.png"
            shutil.copy(render_file, dest_render)
            renders[render_name] = str(dest_render)
            logger.info(f"✓ Render copied: {render_name}")
        
        if renders:
            output_files['renders'] = renders
        
        return output_files
    
    def _extract_glb_from_package(
        self,
        package_path: Path,
        session_id: str
    ) -> Optional[Dict[str, str]]:
        """
        Extract GLB file from output package.
        
        Args:
            package_path: Path to ZIP package
            session_id: Session identifier
            
        Returns:
            Dictionary with GLB path and URL, or None if not found
        """
        logger.info(f"Extracting GLB from package: {package_path}")
        
        try:
            with zipfile.ZipFile(package_path, 'r') as zip_ref:
                # Look for GLB files in the package
                glb_files = [f for f in zip_ref.namelist() if f.endswith('.glb')]
                
                if glb_files:
                    # Extract the first GLB file found
                    glb_name = glb_files[0]
                    
                    # Extract to models directory
                    dest_glb = self.models_dir / f"ai_generated_{session_id}.glb"
                    with zip_ref.open(glb_name) as source:
                        with open(dest_glb, 'wb') as target:
                            target.write(source.read())
                    
                    logger.info(f"✓ Extracted GLB from package: {dest_glb}")
                    
                    return {
                        'glb_path': str(dest_glb),
                        'glb_url': f"/3d_models/ai_generated_{session_id}.glb"
                    }
                else:
                    logger.warning("No GLB files found in package")
                    return None
        
        except Exception as e:
            logger.error(f"Failed to extract GLB from package: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old generated files.
        
        Args:
            max_age_hours: Maximum age of files to keep
        """
        logger.info(f"Cleaning up files older than {max_age_hours} hours...")
        
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        # Clean models directory
        for file_path in self.models_dir.glob("ai_generated_*.glb"):
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                file_path.unlink()
                logger.info(f"Deleted old model: {file_path}")
        
        # Clean output directory
        for file_path in self.output_dir.glob("ai_generated_*"):
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                file_path.unlink()
                logger.info(f"Deleted old output: {file_path}")


# Global bridge instance (initialized on first use)
_bridge_instance: Optional[BlenderBridge] = None


def get_blender_bridge() -> BlenderBridge:
    """
    Get or create the global Blender bridge instance.
    
    Returns:
        BlenderBridge instance
    """
    global _bridge_instance
    
    if _bridge_instance is None:
        try:
            _bridge_instance = BlenderBridge()
            logger.info("Blender bridge initialized successfully")
        except FileNotFoundError as e:
            logger.warning(f"Blender not found: {e}")
            logger.warning("3D generation will use fallback mode")
            _bridge_instance = None
    
    return _bridge_instance


def check_blender_available() -> bool:
    """
    Check if Blender is available for execution.
    
    Returns:
        True if Blender bridge is available
    """
    try:
        bridge = get_blender_bridge()
        return bridge is not None
    except Exception:
        return False
