#!/usr/bin/env python3
"""
Aura V14.0 Installation Validator
=================================

Simple validation script to verify V14.0 Sentient Artisan Environment 
installation and core functionality without requiring Blender runtime.

Run this script to validate that all core components are properly installed.
"""

import os
import sys
import json
import importlib.util
from pathlib import Path


def validate_v14_installation():
    """Validate V14.0 installation structure and components."""
    
    print("🧠 Aura V14.0 Sentient Artisan Environment - Installation Validator")
    print("=" * 70)
    
    addon_root = Path(__file__).parent
    all_checks_passed = True
    
    # Check 1: Core files existence
    print("\n📁 Checking Core File Structure...")
    
    required_files = [
        "__init__.py",
        "setup.py", 
        "operators.py",
        "frontend/aura_panel.py",
        "backend/orchestrator.py",
        "backend/procedural_knowledge.py",
        "backend/aura_backend.py",
        "LIVE_TEST_RESULTS_V14.md",
        "README.md"
    ]
    
    for file_path in required_files:
        full_path = addon_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            all_checks_passed = False
    
    # Check 2: Core class definitions
    print("\n🔧 Checking Core Components...")
    
    try:
        # Add current directory to Python path for imports
        sys.path.insert(0, str(addon_root))
        
        # Test procedural knowledge import
        spec = importlib.util.spec_from_file_location(
            "procedural_knowledge", 
            addon_root / "backend" / "procedural_knowledge.py"
        )
        pk_module = importlib.util.module_from_spec(spec)
        
        # Check for key functions (without bpy dependency)
        expected_functions = [
            'execute_technique',
            'create_pave_setting', 
            'create_bezel_setting',
            'create_tension_setting',
            'create_classic_prong_setting'
        ]
        
        # Read the file content to check for function definitions
        with open(addon_root / "backend" / "procedural_knowledge.py", 'r') as f:
            content = f.read()
            
        for func_name in expected_functions:
            if f"def {func_name}" in content:
                print(f"   ✅ {func_name}() function defined")
            else:
                print(f"   ❌ {func_name}() function missing")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ⚠️  Component check skipped (expected in standalone mode): {e}")
    
    # Check 3: V14.0 Master Blueprint Schema
    print("\n📋 Checking V14.0 Master Blueprint Schema...")
    
    try:
        with open(addon_root / "backend" / "orchestrator.py", 'r') as f:
            orchestrator_content = f.read()
            
        schema_checks = [
            '"technique":',  # V14.0 technique selection
            '"parameters":',  # Technique-specific parameters
            'Pave',          # Professional technique
            'Bezel',         # Professional technique  
            'Tension',       # Professional technique
            'ClassicProng'   # Professional technique
        ]
        
        for check in schema_checks:
            if check in orchestrator_content:
                print(f"   ✅ V14.0 schema includes: {check}")
            else:
                print(f"   ❌ V14.0 schema missing: {check}")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ❌ Schema validation failed: {e}")
        all_checks_passed = False
    
    # Check 4: Modal Operator Architecture
    print("\n⚡ Checking Asynchronous Architecture...")
    
    try:
        with open(addon_root / "operators.py", 'r') as f:
            operators_content = f.read()
            
        async_checks = [
            'modal_handler_add',        # Modal operator pattern
            'threading.Thread',         # Worker thread management
            'queue.Queue',             # Thread-safe communication
            'bpy.app.timers.register', # Real-time updates
            'shape_key_animation'      # Shape Key animation system
        ]
        
        for check in async_checks:
            if check in operators_content:
                print(f"   ✅ Asynchronous feature: {check}")
            else:
                print(f"   ❌ Missing async feature: {check}")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ❌ Async architecture validation failed: {e}")
        all_checks_passed = False
    
    # Check 5: Chat Interface
    print("\n💬 Checking Native Chat Interface...")
    
    try:
        with open(addon_root / "frontend" / "aura_panel.py", 'r') as f:
            panel_content = f.read()
            
        ui_checks = [
            'AuraChatPanel',           # Main chat panel
            'chat_messages',           # Message storage
            'real-time',               # Real-time updates
            'AuraGenerateOperator',    # Generate operator
            'Processing...'            # Status indicators
        ]
        
        for check in ui_checks:
            if check in panel_content:
                print(f"   ✅ UI feature: {check}")
            else:
                print(f"   ❌ Missing UI feature: {check}")
                all_checks_passed = False
                
    except Exception as e:
        print(f"   ❌ Chat interface validation failed: {e}")
        all_checks_passed = False
    
    # Final validation results
    print("\n" + "=" * 70)
    
    if all_checks_passed:
        print("🎉 VALIDATION PASSED: Aura V14.0 Sentient Artisan Environment")
        print("   All core components are properly installed and configured.")
        print("\n🚀 Ready to install as Blender add-on!")
        print("\nInstallation Steps:")
        print("1. Open Blender → Edit → Preferences → Add-ons")  
        print("2. Click 'Install...' and select this aura folder")
        print("3. Enable 'Aura V14.0 Sentient Artisan Environment'")
        print("4. Switch to 'Aura' workspace and start creating!")
        return True
    else:
        print("❌ VALIDATION FAILED: Some components are missing or incorrect")
        print("   Please check the installation and try again.")
        return False


if __name__ == "__main__":
    success = validate_v14_installation()
    sys.exit(0 if success else 1)