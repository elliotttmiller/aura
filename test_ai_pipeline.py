"""
AI 3D Generation Pipeline - Interactive Test Script
====================================================

This script tests the complete AI-driven 3D model generation workflow:
1. Sends a user prompt to the Enhanced AI Orchestrator
2. Shows the AI's design analysis and reasoning
3. Displays the construction plan step-by-step
4. Shows material specifications
5. Tests the frontend integration

Usage:
    python test_ai_pipeline.py
"""

import requests
import json
import time
from typing import Dict, Any
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a styled header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_section(text: str):
    """Print a styled section"""
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{Colors.BOLD}{'─'*80}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")

def print_json(data: Dict[Any, Any], indent: int = 2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))

def test_backend_health() -> bool:
    """Test if backend is running"""
    print_section("🔍 Testing Backend Health")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend is running at {BACKEND_URL}")
            return True
        else:
            print_error(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Cannot connect to backend: {e}")
        print_info("Make sure to start the backend first:")
        print_info("  cd backend && uvicorn main:app --reload --port 8001")
        return False

def test_ai_generation(prompt: str, complexity: str = "moderate") -> Dict[Any, Any]:
    """Test AI 3D model generation"""
    print_section(f"🎨 Testing AI Generation: '{prompt}'")
    
    payload = {
        "prompt": prompt,
        "complexity": complexity,
        "session_id": f"test-{int(time.time())}",
        "context": {
            "existing_objects": [],
            "scene_style": "professional"
        }
    }
    
    print_info(f"Sending request to: {API_BASE}/ai/generate-3d-model")
    print_info(f"Complexity: {complexity}")
    print_info(f"Prompt: {prompt}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/ai/generate-3d-model",
            json=payload,
            timeout=120  # AI generation can take time
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Generation completed in {elapsed_time:.2f}s")
            return result
        else:
            print_error(f"Request failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.Timeout:
        print_error("Request timed out (>120s)")
        return {"success": False, "error": "timeout"}
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return {"success": False, "error": str(e)}

def display_results(result: Dict[Any, Any]):
    """Display the AI generation results in a readable format"""
    if not result.get('success', False):
        print_error("Generation failed!")
        if 'error' in result:
            print_error(f"Error: {result['error']}")
        return
    
    # Design Analysis
    if 'design_analysis' in result:
        print_section("🧠 AI Design Analysis")
        analysis = result['design_analysis']
        
        if 'interpretation' in analysis:
            print(f"{Colors.BOLD}Interpretation:{Colors.ENDC}")
            print(f"  {analysis['interpretation']}\n")
        
        if 'complexity_assessment' in analysis:
            print(f"{Colors.BOLD}Complexity Assessment:{Colors.ENDC}")
            print(f"  {analysis['complexity_assessment']}\n")
        
        if 'recommended_approach' in analysis:
            print(f"{Colors.BOLD}Recommended Approach:{Colors.ENDC}")
            print(f"  {analysis['recommended_approach']}\n")
        
        if 'style_characteristics' in analysis:
            print(f"{Colors.BOLD}Style Characteristics:{Colors.ENDC}")
            for char in analysis['style_characteristics']:
                print(f"  • {char}")
    
    # Construction Plan
    if 'construction_plan' in result:
        print_section("🔨 Construction Plan")
        plan = result['construction_plan']
        
        for i, step in enumerate(plan, 1):
            print(f"{Colors.BOLD}Step {i}: {step.get('operation', 'Unknown')}{Colors.ENDC}")
            print(f"  Description: {step.get('description', 'N/A')}")
            
            if 'parameters' in step:
                print(f"  Parameters:")
                for key, value in step['parameters'].items():
                    print(f"    • {key}: {value}")
            
            if 'reasoning' in step:
                print(f"  Reasoning: {step['reasoning']}")
            print()
    
    # Material Specifications
    if 'material_specifications' in result:
        print_section("💎 Material Specifications")
        materials = result['material_specifications']
        
        if 'primary_material' in materials:
            print(f"{Colors.BOLD}Primary Material:{Colors.ENDC}")
            pm = materials['primary_material']
            print(f"  Name: {pm.get('name', 'N/A')}")
            print(f"  Type: {pm.get('type', 'N/A')}")
            print(f"  Base Color: {pm.get('base_color', 'N/A')}")
            print(f"  Metallic: {pm.get('metallic', 'N/A')}")
            print(f"  Roughness: {pm.get('roughness', 'N/A')}")
            if 'ior' in pm:
                print(f"  IOR: {pm['ior']}")
            print()
        
        if 'accent_materials' in materials and materials['accent_materials']:
            print(f"{Colors.BOLD}Accent Materials:{Colors.ENDC}")
            for accent in materials['accent_materials']:
                print(f"  • {accent.get('name', 'N/A')}: {accent.get('description', 'N/A')}")
    
    # Presentation Plan
    if 'presentation_plan' in result:
        print_section("📸 Presentation Plan")
        presentation = result['presentation_plan']
        
        if 'lighting' in presentation:
            print(f"{Colors.BOLD}Lighting:{Colors.ENDC}")
            print(f"  Setup: {presentation['lighting'].get('setup', 'N/A')}")
            print(f"  Intensity: {presentation['lighting'].get('intensity', 'N/A')}")
        
        if 'camera_angle' in presentation:
            print(f"\n{Colors.BOLD}Camera:{Colors.ENDC}")
            print(f"  Angle: {presentation['camera_angle'].get('angle', 'N/A')}")
            print(f"  Distance: {presentation['camera_angle'].get('distance', 'N/A')}")
        
        if 'background' in presentation:
            print(f"\n{Colors.BOLD}Background:{Colors.ENDC}")
            print(f"  Type: {presentation['background'].get('type', 'N/A')}")
            print(f"  Color: {presentation['background'].get('color', 'N/A')}")
    
    # Metadata
    if 'metadata' in result:
        print_section("📊 Generation Metadata")
        metadata = result['metadata']
        print(f"AI Provider: {metadata.get('ai_provider', 'N/A')}")
        print(f"Processing Time: {result.get('processing_time', 'N/A')}s")
        if 'model' in metadata:
            print(f"Model Used: {metadata['model']}")
        if 'total_tokens' in metadata:
            print(f"Total Tokens: {metadata['total_tokens']}")

def run_interactive_test():
    """Run interactive test with user input"""
    print_header("🚀 Aura AI 3D Generation Pipeline - Interactive Test")
    
    # Test backend health
    if not test_backend_health():
        return
    
    print("\n" + "="*80)
    print("Choose a test option:")
    print("="*80)
    print("\n1. Quick Test - Diamond Engagement Ring")
    print("2. Complex Test - Art Deco Necklace")
    print("3. Hyper-Realistic Test - Vintage Bracelet")
    print("4. Custom Prompt")
    print("5. Run All Tests")
    print("\n0. Exit")
    
    choice = input("\nEnter your choice (0-5): ").strip()
    
    test_cases = {
        '1': ("diamond engagement ring with flower pattern", "moderate"),
        '2': ("art deco emerald necklace with geometric patterns", "complex"),
        '3': ("vintage gold bracelet with intricate filigree work", "hyper_realistic"),
    }
    
    if choice == '0':
        print("\nExiting...")
        return
    elif choice == '4':
        prompt = input("\nEnter your custom prompt: ").strip()
        complexity = input("Enter complexity (simple/moderate/complex/hyper_realistic) [moderate]: ").strip() or "moderate"
        result = test_ai_generation(prompt, complexity)
        display_results(result)
    elif choice == '5':
        for name, (prompt, complexity) in test_cases.items():
            result = test_ai_generation(prompt, complexity)
            display_results(result)
            input("\nPress Enter to continue to next test...")
    elif choice in test_cases:
        prompt, complexity = test_cases[choice]
        result = test_ai_generation(prompt, complexity)
        display_results(result)
    else:
        print_error("Invalid choice!")
        return
    
    # Save results
    print_section("💾 Save Results")
    save = input("Save detailed results to JSON file? (y/n): ").strip().lower()
    if save == 'y':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_generation_test_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print_success(f"Results saved to: {filename}")

if __name__ == "__main__":
    try:
        run_interactive_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
