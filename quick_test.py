"""
Quick AI Generation Test - Single Command
==========================================

Quick test of the AI generation pipeline with a single prompt.

Usage:
    python quick_test.py "diamond engagement ring"
    python quick_test.py "art deco necklace" complex
"""

import sys
import requests
import json
import time

def quick_test(prompt: str, complexity: str = "moderate"):
    """Quick test of AI generation"""
    print(f"\n🚀 Testing AI Generation: '{prompt}'")
    print(f"   Complexity: {complexity}")
    print(f"   This will take 10-30 seconds...\n")
    
    try:
        start = time.time()
        response = requests.post(
            "http://localhost:8001/api/ai/generate-3d-model",
            json={
                "prompt": prompt,
                "complexity": complexity,
                "session_id": f"quick-test-{int(time.time())}"
            },
            timeout=120
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS in {elapsed:.1f}s\n")
            
            # Show key results
            if result.get('success'):
                print("=" * 60)
                print("AI DESIGN ANALYSIS:")
                print("=" * 60)
                analysis = result.get('design_analysis', {})
                print(f"\n{analysis.get('interpretation', 'N/A')}\n")
                
                print("=" * 60)
                print("CONSTRUCTION PLAN:")
                print("=" * 60)
                for i, step in enumerate(result.get('construction_plan', []), 1):
                    print(f"\n{i}. {step.get('operation', 'Unknown')}")
                    print(f"   {step.get('description', 'N/A')}")
                
                print("\n" + "=" * 60)
                print("MATERIALS:")
                print("=" * 60)
                primary = result.get('material_specifications', {}).get('primary_material', {})
                print(f"\nPrimary: {primary.get('name', 'N/A')}")
                print(f"Color: {primary.get('base_color', 'N/A')}")
                print(f"Metallic: {primary.get('metallic', 'N/A')}")
                print(f"Roughness: {primary.get('roughness', 'N/A')}")
                
                print("\n" + "=" * 60)
                print(f"AI Provider: {result.get('metadata', {}).get('ai_provider', 'N/A')}")
                print(f"Processing Time: {result.get('processing_time', 'N/A')}s")
                print("=" * 60 + "\n")
                
                # Save to file
                filename = f"ai_test_{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"💾 Full results saved to: {filename}\n")
                
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend!")
        print("   Make sure backend is running:")
        print("   cd backend && uvicorn main:app --reload --port 8001")
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>120s)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py \"your prompt\" [complexity]")
        print("\nExamples:")
        print("  python quick_test.py \"diamond engagement ring\"")
        print("  python quick_test.py \"art deco necklace\" complex")
        print("  python quick_test.py \"vintage bracelet\" hyper_realistic")
        sys.exit(1)
    
    prompt = sys.argv[1]
    complexity = sys.argv[2] if len(sys.argv) > 2 else "moderate"
    quick_test(prompt, complexity)
