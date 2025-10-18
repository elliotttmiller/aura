"""
Frontend-Equivalent AI Workflow Test
=====================================

This script mimics EXACTLY what the frontend does:
1. Check backend health
2. Create a new session
3. Send AI prompt to /api/ai/generate-3d-model
4. Display results just like the frontend console.log statements

Usage:
    python test_frontend_workflow.py
    
Or with custom prompt:
    python test_frontend_workflow.py "Generate a silver engagement ring with sapphires"
"""

import requests
import json
import time
import sys
from pathlib import Path
from typing import Optional

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# ANSI color codes for pretty output
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
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def check_backend_health() -> bool:
    """Step 1: Check if backend is running (like frontend health check)"""
    print_info("Checking backend health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print_success(f"Backend is {health.get('status', 'unknown')}")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Backend not reachable: {e}")
        print_warning("Make sure backend is running: cd backend && python main.py")
        return False

def create_session() -> Optional[str]:
    """Step 2: Create a new session (like frontend initializeSession)"""
    print_info("Creating new session...")
    try:
        response = requests.post(
            f"{API_BASE}/session/new",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print_success(f"Session created: {session_id}")
            return session_id
        else:
            print_error(f"Session creation failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print_error(f"Session creation error: {e}")
        return None

def execute_ai_prompt(session_id: str, prompt: str) -> dict:
    """Step 3: Execute AI prompt (EXACTLY like frontend executeAIPrompt)"""
    print_info(f"Sending prompt to AI: '{prompt}'")
    print_info("This is the SAME endpoint the frontend calls...")
    
    # Construct payload EXACTLY like frontend
    payload = {
        "prompt": prompt,
        "complexity": "moderate",
        "session_id": session_id,
        "context": {
            "existing_objects": [],  # Empty for new session
            "selected_object_id": None
        }
    }
    
    print_info(f"Endpoint: POST {API_BASE}/ai/generate-3d-model")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/ai/generate-3d-model",
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=300  # 5 minutes for AI + Blender
        )
        
        execution_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            data['_execution_time'] = execution_time
            return data
        else:
            error_data = response.json() if response.content else {"error": "Unknown error"}
            print_error(f"AI request failed ({response.status_code}): {error_data.get('error', 'Unknown')}")
            return {"success": False, "error": error_data.get("error", "Unknown error")}
            
    except requests.exceptions.Timeout:
        print_error("Request timed out (>5 minutes)")
        return {"success": False, "error": "Timeout"}
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return {"success": False, "error": str(e)}

def display_results(data: dict, prompt: str):
    """Step 4: Display results (like frontend console.log statements)"""
    print_header("AI GENERATION RESULTS")
    
    if not data.get('success'):
        print_error(f"Generation failed: {data.get('error', 'Unknown error')}")
        return
    
    # Mimic frontend console.log outputs
    print_success("AI-generated object created")
    print(f"\n{Colors.BOLD}📝 User prompt:{Colors.ENDC} {prompt}")
    
    # Construction Plan
    if 'construction_plan' in data:
        plan = data['construction_plan']
        print(f"\n{Colors.BOLD}📦 Construction plan:{Colors.ENDC}")
        if isinstance(plan, dict):
            steps = plan.get('construction_steps', plan.get('steps', []))
            print(f"   Type: {plan.get('type', 'unknown')}")
            print(f"   Steps: {len(steps)} operations")
            for i, step in enumerate(steps[:3], 1):  # Show first 3 steps
                op = step.get('operation', 'unknown')
                params = step.get('parameters', {})
                print(f"   {i}. {op} - {params}")
            if len(steps) > 3:
                print(f"   ... and {len(steps) - 3} more steps")
        else:
            print(f"   {plan}")
    
    # Materials
    if 'material_specifications' in data:
        materials = data['material_specifications']
        print(f"\n{Colors.BOLD}💎 Materials:{Colors.ENDC}")
        if isinstance(materials, dict):
            for mat_name, mat_props in materials.items():
                print(f"   {mat_name}:")
                if isinstance(mat_props, dict):
                    for key, value in mat_props.items():
                        print(f"      {key}: {value}")
        else:
            print(f"   {materials}")
    
    # Blender Execution
    if 'blender_execution' in data:
        blender = data['blender_execution']
        if blender.get('success'):
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🔨 Blender execution successful!{Colors.ENDC}")
            if 'glb_file' in data:
                glb_path = Path(data['glb_file'])
                print(f"   📁 GLB file: {glb_path}")
                if glb_path.exists():
                    size_mb = glb_path.stat().st_size / (1024 * 1024)
                    print_success(f"File exists! Size: {size_mb:.2f} MB")
                else:
                    print_warning(f"File not found at {glb_path}")
            
            if 'blend_file' in blender:
                print(f"   📁 Blend file: {blender['blend_file']}")
            
            if 'render_file' in blender:
                print(f"   📁 Render: {blender['render_file']}")
            
            if 'execution_time' in blender:
                print(f"   ⏱️  Execution time: {blender['execution_time']:.2f} s")
        else:
            print_warning(f"Blender execution failed: {blender.get('error', 'Unknown error')}")
    
    # Total execution time
    if '_execution_time' in data:
        print(f"\n{Colors.BOLD}⏱️  Total API call time:{Colors.ENDC} {data['_execution_time']:.2f} seconds")
    
    # Object data (what would be added to scene)
    if 'object_id' in data:
        print(f"\n{Colors.BOLD}🎨 Scene Object:{Colors.ENDC}")
        print(f"   ID: {data['object_id']}")
        print(f"   Name: AI: {prompt[:30]}...")
        print(f"   Type: ai_generated")
        
        # Material from AI specs
        if 'material_specifications' in data:
            mats = data['material_specifications']
            if 'primary_material' in mats:
                pm = mats['primary_material']
                print(f"   Material:")
                print(f"      Color: {pm.get('base_color', '#FFD700')}")
                print(f"      Roughness: {pm.get('roughness', 0.2)}")
                print(f"      Metallic: {pm.get('metallic', 0.8)}")

def main():
    """Main test flow - mimics frontend user interaction"""
    print_header("FRONTEND WORKFLOW TEST - AI → BLENDER PIPELINE")
    
    # Get prompt from command line or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Generate a simple gold ring with diamond"
    
    print_info(f"Testing with prompt: '{prompt}'")
    print_info("This test mimics exactly what happens when you click 'Generate' in the UI\n")
    
    # Step 1: Health check
    if not check_backend_health():
        print_error("\nTest aborted: Backend not available")
        print_info("Start backend with: cd backend && python main.py")
        return 1
    
    # Step 2: Create session
    session_id = create_session()
    if not session_id:
        print_error("\nTest aborted: Could not create session")
        return 1
    
    # Step 3: Execute AI prompt
    print_header("EXECUTING AI PROMPT")
    print_info("⏳ This may take 30-60 seconds (AI analysis + Blender execution)...")
    print_info("Watch for real-time progress in the backend console...\n")
    
    result = execute_ai_prompt(session_id, prompt)
    
    # Step 4: Display results
    display_results(result, prompt)
    
    # Summary
    print_header("TEST COMPLETE")
    if result.get('success'):
        print_success("✅ Full workflow completed successfully!")
        print_info("The frontend would now:")
        print_info("  1. Add the object to the scene outliner (left sidebar)")
        print_info("  2. Load the GLB file into the 3D viewport")
        print_info("  3. Apply the AI-generated PBR materials")
        print_info("  4. Select the new object")
        return 0
    else:
        print_error("❌ Workflow failed")
        print_info("Check backend logs for detailed error information")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
