"""
Enhanced AI 3D Model Generation - Live Demonstration
=====================================================

This script demonstrates the complete AI-driven 3D model generation workflow
with visual output and comprehensive logging.
"""

import sys
import os
import json
import time
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def print_banner(text: str):
    """Print a styled banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text: str):
    """Print a styled section header."""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)

def print_progress(message: str, percentage: int):
    """Print a progress bar."""
    bar_length = 50
    filled = int(bar_length * percentage / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r  [{bar}] {percentage}% - {message}", end='', flush=True)
    if percentage >= 100:
        print()  # New line when complete

def demo_design_analysis():
    """Demonstrate AI design intent analysis."""
    print_section("🧠 DEMONSTRATION 1: AI Design Intent Analysis")
    
    from backend.enhanced_ai_orchestrator import EnhancedAIOrchestrator
    
    orchestrator = EnhancedAIOrchestrator()
    
    test_prompts = [
        "simple gold ring",
        "elegant engagement ring with vintage filigree details in platinum",
        "modern minimalist silver band with brushed finish",
        "ornate diamond necklace with intricate chain work"
    ]
    
    for prompt in test_prompts:
        print(f"\n📝 Analyzing: \"{prompt}\"")
        
        result = orchestrator._analyze_design_intent(prompt, None)
        
        if result.get('success', False):
            analysis = result.get('analysis', {})
            print(f"   ✓ Design Type: {analysis.get('design_type', 'N/A')}")
            print(f"   ✓ Complexity: {analysis.get('complexity', 'N/A')}")
            print(f"   ✓ Key Features: {', '.join(analysis.get('key_features', []))[:60]}")
            print(f"   ✓ Aesthetic Goals: {', '.join(analysis.get('aesthetic_goals', []))}")
        else:
            print(f"   ⚠️  Using fallback analysis")

def demo_construction_planning():
    """Demonstrate AI construction plan generation."""
    print_section("🏗️  DEMONSTRATION 2: Construction Plan Generation")
    
    from backend.enhanced_ai_orchestrator import EnhancedAIOrchestrator
    
    orchestrator = EnhancedAIOrchestrator()
    
    prompts = [
        ("Simple Design", "basic gold ring", "simple"),
        ("Moderate Design", "elegant ring with diamond setting", "moderate"),
        ("Complex Design", "intricate vintage ring with filigree", "complex"),
    ]
    
    for name, prompt, complexity in prompts:
        print(f"\n🎨 {name}: \"{prompt}\" (complexity: {complexity})")
        
        result = orchestrator.generate_3d_model(
            user_prompt=prompt,
            complexity=complexity,
            context=None,
            progress_callback=None  # Silent mode for demo
        )
        
        if result.get('success', False):
            plan = result.get('construction_plan', [])
            print(f"   ✓ Operations: {len(plan)}")
            
            for i, op in enumerate(plan[:3], 1):
                op_name = op.get('operation', 'unknown')
                op_desc = op.get('description', 'No description')[:50]
                print(f"      {i}. {op_name}: {op_desc}")
            
            if len(plan) > 3:
                print(f"      ... and {len(plan) - 3} more operations")
            
            # Show material specs
            materials = result.get('material_specifications', {})
            primary = materials.get('primary_material', {})
            if primary:
                print(f"   ✓ Material: {primary.get('name', 'N/A')}")
                print(f"      Color: {primary.get('base_color', 'N/A')}")
                print(f"      Metallic: {primary.get('metallic', 'N/A')}")
                print(f"      Roughness: {primary.get('roughness', 'N/A')}")
        else:
            print(f"   ⚠️  Generation failed: {result.get('error', 'Unknown error')}")

def demo_full_workflow():
    """Demonstrate complete end-to-end workflow."""
    print_section("⚡ DEMONSTRATION 3: Complete End-to-End Workflow")
    
    from backend.enhanced_ai_orchestrator import EnhancedAIOrchestrator
    
    orchestrator = EnhancedAIOrchestrator()
    
    print("\n🎯 Creating a sophisticated jewelry piece...")
    print("   User Request: 'elegant 1 carat solitaire engagement ring in 18k gold'")
    
    start_time = time.time()
    
    result = orchestrator.generate_3d_model(
        user_prompt="elegant 1 carat solitaire engagement ring in 18k gold",
        complexity="moderate",
        context=None,
        progress_callback=print_progress
    )
    
    processing_time = time.time() - start_time
    
    print(f"\n\n📊 Generation Results:")
    print(f"   ✓ Status: {'SUCCESS' if result.get('success') else 'FAILED'}")
    print(f"   ✓ Processing Time: {processing_time:.2f}s")
    print(f"   ✓ AI Provider: {result.get('ai_provider', 'Unknown')}")
    
    if result.get('success', False):
        # Show construction plan
        plan = result.get('construction_plan', [])
        print(f"\n   📐 Construction Plan ({len(plan)} operations):")
        for i, op in enumerate(plan, 1):
            print(f"      {i}. {op.get('operation', 'unknown')}")
            params = op.get('parameters', {})
            for key, value in list(params.items())[:3]:
                print(f"         - {key}: {value}")
        
        # Show materials
        materials = result.get('material_specifications', {})
        if materials:
            print(f"\n   🎨 Material Specifications:")
            primary = materials.get('primary_material', {})
            if primary:
                print(f"      Primary: {primary.get('name', 'N/A')}")
                print(f"      - Color: {primary.get('base_color', 'N/A')}")
                print(f"      - Metallic: {primary.get('metallic', 0.0):.2f}")
                print(f"      - Roughness: {primary.get('roughness', 0.0):.2f}")
        
        # Show metadata
        metadata = result.get('metadata', {})
        if metadata:
            print(f"\n   📝 Design Metadata:")
            print(f"      Design Type: {metadata.get('design_type', 'N/A')}")
            print(f"      Complexity: {metadata.get('complexity', 'N/A')}")
            print(f"      Estimated Operations: {metadata.get('estimated_operations', 0)}")
            
            reasoning = metadata.get('ai_reasoning', '')
            if reasoning:
                print(f"      AI Reasoning: {reasoning[:100]}...")

def demo_system_capabilities():
    """Demonstrate system capabilities and status."""
    print_section("🔍 DEMONSTRATION 4: System Capabilities")
    
    from backend.enhanced_ai_orchestrator import EnhancedAIOrchestrator
    
    orchestrator = EnhancedAIOrchestrator()
    
    print("\n💡 System Status:")
    print(f"   Enhanced AI Available: {orchestrator.openai_enabled or orchestrator.multi_provider_enabled}")
    print(f"   OpenAI GPT-4 Enabled: {orchestrator.openai_enabled}")
    print(f"   Multi-Provider Enabled: {orchestrator.multi_provider_enabled}")
    
    if orchestrator.openai_enabled:
        print(f"   OpenAI Model: {orchestrator.ai_3d_generator.model}")
        print(f"   Temperature: {orchestrator.ai_3d_generator.temperature}")
        print(f"   Max Tokens: {orchestrator.ai_3d_generator.max_tokens}")
    
    print("\n✨ Available Features:")
    features = [
        ("Advanced 3D Generation", orchestrator.openai_enabled),
        ("Design Refinement", orchestrator.openai_enabled),
        ("Variation Generation", orchestrator.openai_enabled),
        ("Material Specifications", orchestrator.openai_enabled),
        ("Fallback Mode", True),
        ("Multi-Provider Support", orchestrator.multi_provider_enabled),
    ]
    
    for feature, available in features:
        status = "✅" if available else "⚠️ "
        print(f"   {status} {feature}")
    
    print("\n🎯 Complexity Levels Supported:")
    complexities = ["Simple", "Moderate", "Complex", "Hyper-Realistic"]
    for complexity in complexities:
        print(f"   ✓ {complexity}")

def run_demonstration():
    """Run the complete demonstration."""
    print_banner("🚀 ENHANCED AI 3D MODEL GENERATION - LIVE DEMONSTRATION")
    
    print("\n📌 This demonstration showcases:")
    print("   1. AI Design Intent Analysis")
    print("   2. Construction Plan Generation")
    print("   3. Complete End-to-End Workflow")
    print("   4. System Capabilities and Status")
    
    input("\n🎬 Press ENTER to start the demonstration...")
    
    try:
        # Demo 1: Design Analysis
        demo_design_analysis()
        input("\n📌 Press ENTER to continue to next demonstration...")
        
        # Demo 2: Construction Planning
        demo_construction_planning()
        input("\n📌 Press ENTER to continue to next demonstration...")
        
        # Demo 3: Full Workflow
        demo_full_workflow()
        input("\n📌 Press ENTER to continue to system capabilities...")
        
        # Demo 4: System Capabilities
        demo_system_capabilities()
        
        print_banner("✅ DEMONSTRATION COMPLETE")
        
        print("\n🎉 Key Takeaways:")
        print("   ✓ AI can analyze and understand design intent from natural language")
        print("   ✓ Sophisticated construction plans are generated automatically")
        print("   ✓ Material specifications use professional PBR parameters")
        print("   ✓ System supports multiple complexity levels")
        print("   ✓ Fallback mode ensures functionality without OpenAI")
        
        print("\n💡 Next Steps:")
        print("   1. Configure your OpenAI API key in .env")
        print("   2. Start the backend: uvicorn backend.main:app --reload")
        print("   3. Start the frontend: cd frontend/static && npm run dev")
        print("   4. Try the web interface at http://localhost:5173")
        
        print("\n📚 Documentation:")
        print("   - Quick Start: QUICKSTART.md")
        print("   - Full Documentation: docs/ENHANCED_AI_SYSTEM.md")
        print("   - Test Suite: python tests/test_enhanced_ai.py")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_demonstration())
