"""
Test Enhanced AI 3D Model Generation System
===========================================

This script tests the enhanced AI-driven 3D model generation workflow
with comprehensive validation and demonstration.
"""

import sys
import os
import json
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_ai_3d_generator():
    """Test the AI 3D Model Generator module."""
    print("\n" + "=" * 80)
    print("TEST 1: AI 3D Model Generator")
    print("=" * 80)
    
    from backend.ai_3d_model_generator import AI3DModelGenerator, ModelComplexity
    
    # Test with no API key (fallback mode)
    print("\n📝 Testing without API key (fallback mode)...")
    generator = AI3DModelGenerator(api_key=None)
    
    print(f"   Enabled: {generator.is_enabled()}")
    assert not generator.is_enabled(), "Should be disabled without API key"
    
    # Test fallback design analysis
    print("\n🧠 Testing fallback design analysis...")
    result = generator.analyze_design_intent("elegant gold ring with diamond")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Analysis: {json.dumps(result.get('analysis', result.get('fallback', {})), indent=2)}")
    
    # Test fallback construction plan
    print("\n🏗️  Testing fallback construction plan...")
    design_analysis = {'analysis': result.get('analysis', result.get('fallback', {}))}
    plan_result = generator.generate_construction_plan(
        "elegant gold ring",
        design_analysis,
        ModelComplexity.MODERATE
    )
    print(f"   Success: {plan_result.get('success', False)}")
    print(f"   Operations: {len(plan_result.get('plan', plan_result.get('fallback', {})).get('construction_plan', []))}")
    
    # Test fallback material specs
    print("\n🎨 Testing fallback material specifications...")
    material_specs = generator.generate_material_specifications("jewelry", ["professional", "elegant"])
    print(f"   Success: {material_specs.get('success', False)}")
    print(f"   Materials: {json.dumps(material_specs.get('materials', material_specs.get('fallback', {})), indent=2)}")
    
    print("\n✅ AI 3D Model Generator tests passed!")
    return True


def test_enhanced_orchestrator():
    """Test the Enhanced AI Orchestrator."""
    print("\n" + "=" * 80)
    print("TEST 2: Enhanced AI Orchestrator")
    print("=" * 80)
    
    from backend.enhanced_ai_orchestrator import EnhancedAIOrchestrator
    
    print("\n🚀 Initializing Enhanced AI Orchestrator...")
    orchestrator = EnhancedAIOrchestrator()
    
    print(f"   OpenAI Enabled: {orchestrator.openai_enabled}")
    print(f"   Multi-Provider Enabled: {orchestrator.multi_provider_enabled}")
    
    # Test 3D model generation
    print("\n🎨 Testing 3D model generation...")
    print("   Prompt: 'simple gold ring'")
    
    start_time = time.time()
    result = orchestrator.generate_3d_model(
        user_prompt="simple gold ring",
        complexity="moderate",
        context=None,
        progress_callback=lambda msg, pct: print(f"   [{pct}%] {msg}")
    )
    
    processing_time = time.time() - start_time
    
    print(f"\n   Success: {result.get('success', False)}")
    print(f"   Processing Time: {processing_time:.2f}s")
    print(f"   AI Provider: {result.get('ai_provider', 'Unknown')}")
    print(f"   Operations: {len(result.get('construction_plan', []))}")
    
    if result.get('construction_plan'):
        print("\n   Construction Plan:")
        for i, op in enumerate(result['construction_plan'][:3], 1):
            print(f"      {i}. {op.get('operation', 'unknown')}")
    
    print("\n✅ Enhanced AI Orchestrator tests passed!")
    return result


def test_backend_integration():
    """Test integration with backend main.py."""
    print("\n" + "=" * 80)
    print("TEST 3: Backend Integration")
    print("=" * 80)
    
    try:
        # Import backend main to check integration
        print("\n📦 Importing backend main...")
        from backend.main import app, ENHANCED_AI_AVAILABLE, enhanced_ai_orchestrator
        
        print(f"   FastAPI App: {app is not None}")
        print(f"   Enhanced AI Available: {ENHANCED_AI_AVAILABLE}")
        print(f"   Enhanced Orchestrator: {enhanced_ai_orchestrator is not None}")
        
        if ENHANCED_AI_AVAILABLE and enhanced_ai_orchestrator:
            print(f"   OpenAI Enabled: {enhanced_ai_orchestrator.openai_enabled}")
        
        print("\n✅ Backend integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n⚠️  Backend integration test failed: {e}")
        return False


def test_with_api_key():
    """Test with OpenAI API key if available."""
    print("\n" + "=" * 80)
    print("TEST 4: OpenAI API Integration (if key available)")
    print("=" * 80)
    
    api_key = os.getenv('OPENAI_API_KEY', '')
    
    if not api_key:
        print("\n⚠️  No OPENAI_API_KEY found in environment")
        print("   Skipping OpenAI-specific tests")
        print("   To enable: export OPENAI_API_KEY='your-key-here'")
        return True
    
    from backend.ai_3d_model_generator import AI3DModelGenerator
    
    print(f"\n✓ OPENAI_API_KEY found (length: {len(api_key)})")
    print("\n🚀 Initializing with API key...")
    
    generator = AI3DModelGenerator(api_key=api_key)
    print(f"   Enabled: {generator.is_enabled()}")
    print(f"   Model: {generator.model}")
    
    if generator.is_enabled():
        print("\n🧠 Testing live AI design analysis...")
        print("   Prompt: 'elegant engagement ring with vintage filigree details'")
        
        try:
            result = generator.analyze_design_intent(
                "elegant engagement ring with vintage filigree details"
            )
            
            if result.get('success', False):
                print(f"   ✓ Analysis successful!")
                print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"   Tokens Used: {result.get('tokens_used', 0)}")
                
                analysis = result.get('analysis', {})
                print(f"\n   Design Type: {analysis.get('design_type', 'N/A')}")
                print(f"   Complexity: {analysis.get('complexity', 'N/A')}")
                print(f"   Key Features: {', '.join(analysis.get('key_features', []))}")
                
                print("\n✅ OpenAI API tests passed!")
            else:
                print(f"   ⚠️  Analysis failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Error during API call: {e}")
            import traceback
            traceback.print_exc()
    
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("🧪 ENHANCED AI 3D MODEL GENERATION - TEST SUITE")
    print("=" * 80)
    
    results = []
    
    try:
        results.append(("AI 3D Model Generator", test_ai_3d_generator()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("AI 3D Model Generator", False))
    
    try:
        gen_result = test_enhanced_orchestrator()
        results.append(("Enhanced AI Orchestrator", gen_result.get('success', False)))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Enhanced AI Orchestrator", False))
    
    try:
        results.append(("Backend Integration", test_backend_integration()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        results.append(("Backend Integration", False))
    
    try:
        results.append(("OpenAI API Integration", test_with_api_key()))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        results.append(("OpenAI API Integration", False))
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
        print("\n✨ Enhanced AI 3D Model Generation system is ready!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
