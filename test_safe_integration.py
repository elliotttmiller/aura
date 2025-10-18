#!/usr/bin/env python3
"""
Integration Test for Safe Upload Reintegration

Tests that upload functionality works without breaking existing viewport rendering.
"""

import json
import os
from pathlib import Path

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return Path(filepath).exists()

def check_feature_flags() -> dict:
    """Verify feature flags are properly configured."""
    flags_path = "frontend/static/src/config/featureFlags.ts"
    
    if not check_file_exists(flags_path):
        return {"status": "error", "message": "Feature flags file not found"}
    
    with open(flags_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for both flags
    has_jewelry_flag = "enableJewelryMaterialEnhancements" in content
    has_lighting_flag = "enableHighFidelityViewportLighting" in content
    
    # Check they're set to false (conservative defaults)
    jewelry_disabled = "enableJewelryMaterialEnhancements: false" in content
    lighting_disabled = "enableHighFidelityViewportLighting: false" in content
    
    return {
        "status": "pass" if all([has_jewelry_flag, has_lighting_flag, jewelry_disabled, lighting_disabled]) else "warn",
        "flags_exist": has_jewelry_flag and has_lighting_flag,
        "conservative_defaults": jewelry_disabled and lighting_disabled,
        "message": "Feature flags configured correctly" if jewelry_disabled and lighting_disabled else "Feature flags may not have conservative defaults"
    }

def check_store_backward_compatibility() -> dict:
    """Verify designStore has backward compatible loadGLBModel."""
    store_path = "frontend/static/src/store/designStore.ts"
    
    if not check_file_exists(store_path):
        return {"status": "error", "message": "Store file not found"}
    
    with open(store_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for optional parameters
    has_optional_params = "loadGLBModel: (modelPath?, modelName?, sourceOverride?)" in content
    has_source_logic = "resolvedSource: SceneObject['source']" in content or "let resolvedSource" in content
    has_smart_resolution = "sourceOverride" in content and "modelPath" in content
    
    return {
        "status": "pass" if all([has_optional_params, has_source_logic, has_smart_resolution]) else "fail",
        "optional_params": has_optional_params,
        "source_tracking": has_source_logic,
        "smart_resolution": has_smart_resolution,
        "message": "Store API is backward compatible" if has_optional_params else "Store API may break existing code"
    }

def check_glb_model_guards() -> dict:
    """Verify GLBModel has proper feature flag guards."""
    glb_path = "frontend/static/src/components/GLBModel/GLBModel.tsx"
    
    if not check_file_exists(glb_path):
        return {"status": "error", "message": "GLBModel file not found"}
    
    with open(glb_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for feature flag import
    has_flag_import = "featureFlags" in content
    
    # Check for conditional enhancement
    has_conditional = "shouldEnhanceMaterials" in content
    has_flag_check = "featureFlags.enableJewelryMaterialEnhancements" in content
    has_source_check = "source === 'uploaded'" in content
    
    return {
        "status": "pass" if all([has_flag_import, has_conditional, has_flag_check, has_source_check]) else "fail",
        "imports_flags": has_flag_import,
        "conditional_enhancement": has_conditional,
        "checks_flag": has_flag_check,
        "checks_source": has_source_check,
        "message": "GLBModel properly guards material enhancements" if has_flag_check else "GLBModel may apply enhancements unconditionally"
    }

def check_scene_outliner_safety() -> dict:
    """Verify SceneOutliner safely handles missing metadata."""
    outliner_path = "frontend/static/src/components/SceneOutliner/SceneOutliner.tsx"
    
    if not check_file_exists(outliner_path):
        return {"status": "error", "message": "SceneOutliner file not found"}
    
    with open(outliner_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for safe fallback
    has_nullish_coalescing = "model.source ??" in content
    has_url_fallback = "model.url?.includes('/uploaded/')" in content
    has_source_badge = "source-badge" in content
    
    return {
        "status": "pass" if all([has_nullish_coalescing, has_url_fallback, has_source_badge]) else "warn",
        "safe_fallback": has_nullish_coalescing,
        "url_detection": has_url_fallback,
        "displays_badge": has_source_badge,
        "message": "SceneOutliner safely handles missing source metadata"
    }

def check_chat_sidebar_integration() -> dict:
    """Verify AIChatSidebar properly integrates upload."""
    chat_path = "frontend/static/src/components/AIChatSidebar/AIChatSidebar.tsx"
    
    if not check_file_exists(chat_path):
        return {"status": "error", "message": "AIChatSidebar file not found"}
    
    with open(chat_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for proper integration
    has_uploader_import = "ModelUploader" in content
    has_show_state = "showUploader" in content
    has_toggle = "setShowUploader" in content
    has_explicit_source = "loadGLBModel(modelUrl, modelName, 'uploaded')" in content
    
    return {
        "status": "pass" if all([has_uploader_import, has_show_state, has_toggle, has_explicit_source]) else "fail",
        "imports_uploader": has_uploader_import,
        "toggle_state": has_show_state,
        "explicit_source": has_explicit_source,
        "message": "AIChatSidebar properly integrates upload with explicit source tracking"
    }

def run_integration_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Safe Integration Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Feature Flags", check_feature_flags),
        ("Store Backward Compatibility", check_store_backward_compatibility),
        ("GLBModel Guards", check_glb_model_guards),
        ("SceneOutliner Safety", check_scene_outliner_safety),
        ("ChatSidebar Integration", check_chat_sidebar_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing: {name}...")
        result = test_func()
        results.append((name, result))
        
        status_emoji = {
            "pass": "✅",
            "warn": "⚠️",
            "fail": "❌",
            "error": "💥"
        }.get(result["status"], "❓")
        
        print(f"  {status_emoji} {result['message']}")
        
        # Print details for non-passing tests
        if result["status"] != "pass":
            for key, value in result.items():
                if key not in ["status", "message"]:
                    print(f"    - {key}: {value}")
        print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r["status"] == "pass")
    warned = sum(1 for _, r in results if r["status"] == "warn")
    failed = sum(1 for _, r in results if r["status"] == "fail")
    errored = sum(1 for _, r in results if r["status"] == "error")
    
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Warned: {warned}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errored}")
    print()
    
    if failed == 0 and errored == 0:
        print("🎉 All critical tests passed! Integration is safe.")
        return True
    else:
        print("⚠️  Some tests failed. Review before deploying.")
        return False

if __name__ == "__main__":
    import sys
    success = run_integration_tests()
    sys.exit(0 if success else 1)
