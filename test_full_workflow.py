"""
Complete AI → Blender Workflow Test
====================================

This script tests the FULL pipeline:
1. User prompt → AI analysis
2. AI → Construction plan
3. Construction plan → Blender execution
4. Blender → Real 3D model (.blend + .glb)

This verifies that we go from text to actual geometry!
"""

import requests
import json
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def test_full_pipeline(prompt: str, complexity: str = "moderate"):
    """Test the complete AI → Blender pipeline"""
    print("=" * 80)
    print("🚀 COMPLETE AI → BLENDER PIPELINE TEST")
    print("=" * 80)
    print(f"\n📝 Prompt: {prompt}")
    print(f"⚙️  Complexity: {complexity}\n")
    
    # Step 1: Send to AI
    print("Step 1: Sending to Enhanced AI Orchestrator...")
    
    payload = {
        "prompt": prompt,
        "complexity": complexity,
        "session_id": f"test-full-{int(time.time())}"
    }
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/ai/generate-3d-model",
            json=payload,
            timeout=300  # 5 minutes for full workflow
        )
        
        total_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Request failed: HTTP {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        print(f"✅ Request completed in {total_time:.2f}s\n")
        
        # Step 2: Check AI Analysis
        print("=" * 80)
        print("Step 2: AI DESIGN ANALYSIS")
        print("=" * 80)
        
        analysis = result.get('design_analysis', {})
        if analysis:
            print(f"✓ Design Type: {analysis.get('design_type', 'N/A')}")
            print(f"✓ Complexity: {analysis.get('complexity', 'N/A')}")
            print(f"✓ Estimated Operations: {analysis.get('estimated_operations', 'N/A')}")
        else:
            print("⚠ No design analysis available")
        
        # Step 3: Check Construction Plan
        print("\n" + "=" * 80)
        print("Step 3: CONSTRUCTION PLAN")
        print("=" * 80)
        
        plan = result.get('construction_plan', [])
        print(f"✓ Total steps: {len(plan)}")
        for i, step in enumerate(plan, 1):
            print(f"   {i}. {step.get('operation', 'Unknown')}")
        
        # Step 4: Check Blender Execution
        print("\n" + "=" * 80)
        print("Step 4: BLENDER EXECUTION")
        print("=" * 80)
        
        blender_exec = result.get('blender_execution')
        
        if not blender_exec:
            print("❌ NO BLENDER EXECUTION FOUND")
            print("   Construction plan was created but NOT executed!")
            print("   This means the AI generates the plan, but Blender doesn't build it.")
            return False
        
        if blender_exec.get('success'):
            print("✅ BLENDER EXECUTION SUCCESSFUL!")
            print(f"   Execution time: {blender_exec.get('execution_time', 0):.2f}s")
            print(f"   Steps executed: {blender_exec.get('steps_executed', 0)}")
            
            # Check output files
            print("\n📦 OUTPUT FILES:")
            
            blend_file = blender_exec.get('blend_file')
            glb_file = blender_exec.get('glb_file')
            render_file = blender_exec.get('render_file')
            
            if blend_file and Path(blend_file).exists():
                size = Path(blend_file).stat().st_size / 1024
                print(f"   ✓ .blend file: {blend_file} ({size:.1f} KB)")
            else:
                print(f"   ✗ .blend file: NOT FOUND")
            
            if glb_file and Path(glb_file).exists():
                size = Path(glb_file).stat().st_size / 1024
                print(f"   ✓ .glb file: {glb_file} ({size:.1f} KB)")
                print(f"   🌐 Model URL: {result.get('model_url', 'N/A')}")
            else:
                print(f"   ✗ .glb file: NOT FOUND")
            
            if render_file and Path(render_file).exists():
                size = Path(render_file).stat().st_size / 1024
                print(f"   ✓ Render: {render_file} ({size:.1f} KB)")
            else:
                print(f"   ⚠ Render: Not generated (optional)")
            
            # Step 5: Verify in Session
            print("\n" + "=" * 80)
            print("Step 5: SESSION INTEGRATION")
            print("=" * 80)
            
            if result.get('object_id'):
                print(f"✓ Object ID: {result['object_id']}")
                print(f"✓ Session ID: {result['session_id']}")
                print(f"✓ Object added to scene!")
            else:
                print("⚠ No object ID (session not provided)")
            
            # Final Summary
            print("\n" + "=" * 80)
            print("✅ COMPLETE WORKFLOW SUCCESS!")
            print("=" * 80)
            print(f"Total time: {total_time:.2f}s")
            print(f"AI planning: {result.get('processing_time', 0):.2f}s")
            print(f"Blender execution: {blender_exec.get('execution_time', 0):.2f}s")
            print("\n🎉 Text → AI → Construction Plan → Blender → Real 3D Model!")
            
            # Save full results
            output_file = f"full_workflow_test_{int(time.time())}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Full results saved to: {output_file}")
            
            return True
            
        else:
            print("❌ BLENDER EXECUTION FAILED")
            print(f"   Error: {blender_exec.get('error', 'Unknown error')}")
            print("\n⚠️ AI created the plan, but Blender couldn't execute it.")
            print("   Check Blender installation and script generation.")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure backend is running: uvicorn backend.main:app --reload --port 8001")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>300s)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_full_workflow.py \"your prompt\" [complexity]")
        print("\nQuick test with default prompt:")
        test_full_pipeline("simple gold ring", "simple")
    else:
        prompt = sys.argv[1]
        complexity = sys.argv[2] if len(sys.argv) > 2 else "moderate"
        test_full_pipeline(prompt, complexity)
