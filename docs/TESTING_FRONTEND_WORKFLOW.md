# Testing Frontend → Backend AI Workflow

This guide shows you how to test the **exact same workflow** that happens when a user clicks "Generate" in the UI.

## Quick Start

### 1. Start the Backend Server

In Terminal 1:
```powershell
cd backend
python main.py
```

Wait for:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### 2. Run the Frontend Workflow Test

In Terminal 2:
```powershell
python test_frontend_workflow.py
```

Or with a custom prompt:
```powershell
python test_frontend_workflow.py "Generate a silver engagement ring with sapphires"
```

## What This Test Does

The `test_frontend_workflow.py` script **mimics exactly** what happens in the UI:

### Step 1: Health Check
```typescript
// Frontend: checkSystemHealth()
const health = await fetch('/api/health')
```
```python
# Test: check_backend_health()
requests.get(f"{API_BASE}/health")
```

### Step 2: Create Session
```typescript
// Frontend: initializeSession()
const response = await fetch('/api/session/new', { method: 'POST' })
```
```python
# Test: create_session()
requests.post(f"{API_BASE}/session/new")
```

### Step 3: Execute AI Prompt
```typescript
// Frontend: executeAIPrompt()
fetch('/api/ai/generate-3d-model', {
  method: 'POST',
  body: JSON.stringify({
    prompt,
    complexity: 'moderate',
    session_id,
    context: { existing_objects, selected_object_id }
  })
})
```
```python
# Test: execute_ai_prompt()
requests.post(
  f"{API_BASE}/ai/generate-3d-model",
  json={
    "prompt": prompt,
    "complexity": "moderate",
    "session_id": session_id,
    "context": {
      "existing_objects": [],
      "selected_object_id": None
    }
  }
)
```

### Step 4: Display Results
```typescript
// Frontend console.log statements:
console.log('✅ AI-generated object added:', newObject)
console.log('📝 User prompt:', prompt)
console.log('📦 Construction plan:', data.construction_plan)
console.log('💎 Materials:', data.material_specifications)
console.log('🔨 Blender execution successful!')
console.log('📁 GLB file:', data.glb_file)
```
```python
# Test: display_results()
# Shows exactly the same information with colored output
```

## Expected Output

```
================================================================================
                  FRONTEND WORKFLOW TEST - AI → BLENDER PIPELINE
================================================================================

ℹ️  Testing with prompt: 'Generate a simple gold ring with diamond'
ℹ️  This test mimics exactly what happens when you click 'Generate' in the UI

ℹ️  Checking backend health...
✅ Backend is healthy

ℹ️  Creating new session...
✅ Session created: session_abc123

================================================================================
                            EXECUTING AI PROMPT
================================================================================

ℹ️  Sending prompt to AI: 'Generate a simple gold ring with diamond'
ℹ️  This is the SAME endpoint the frontend calls...
ℹ️  Endpoint: POST http://localhost:8001/api/ai/generate-3d-model
ℹ️  ⏳ This may take 30-60 seconds (AI analysis + Blender execution)...

================================================================================
                            AI GENERATION RESULTS
================================================================================

✅ AI-generated object created

📝 User prompt: Generate a simple gold ring with diamond

📦 Construction plan:
   Type: jewelry_ring
   Steps: 6 operations
   1. create_shank - {'profile': 'round', 'width': 2.0, ...}
   2. create_head - {'type': 'prong_setting', ...}
   3. create_diamond - {'shape': 'round', 'size': 1.0}
   ... and 3 more steps

💎 Materials:
   primary_material:
      name: Gold
      base_color: #FFD700
      roughness: 0.2
      metallic: 0.9

🔨 Blender execution successful!
   📁 GLB file: C:/Users/AMD/aura/output/ai_generated/ai_ring_1729180234.glb
   ✅ File exists! Size: 0.52 MB
   📁 Blend file: C:/Users/AMD/aura/output/ai_generated/ai_ring_1729180234.blend
   📁 Render: C:/Users/AMD/aura/output/ai_generated/ai_ring_1729180234.png
   ⏱️  Execution time: 12.34 s

⏱️  Total API call time: 45.67 seconds

🎨 Scene Object:
   ID: ai_ring_1729180234
   Name: AI: Generate a simple gold ring w...
   Type: ai_generated
   Material:
      Color: #FFD700
      Roughness: 0.2
      Metallic: 0.9

================================================================================
                              TEST COMPLETE
================================================================================

✅ Full workflow completed successfully!
ℹ️  The frontend would now:
ℹ️    1. Add the object to the scene outliner (left sidebar)
ℹ️    2. Load the GLB file into the 3D viewport
ℹ️    3. Apply the AI-generated PBR materials
ℹ️    4. Select the new object
```

## Test Different Prompts

```powershell
# Simple ring
python test_frontend_workflow.py "Generate a simple gold ring"

# Complex jewelry
python test_frontend_workflow.py "Generate a platinum engagement ring with emerald center stone and diamond accents"

# Earrings
python test_frontend_workflow.py "Generate diamond stud earrings"

# Pendant
python test_frontend_workflow.py "Generate a heart-shaped pendant with ruby"
```

## Troubleshooting

### Backend Not Running
```
❌ Backend not reachable: Connection refused
⚠️  Make sure backend is running: cd backend && python main.py
```

**Solution:** Start the backend server first

### Timeout (>5 minutes)
```
❌ Request timed out (>5 minutes)
```

**Possible Causes:**
1. Blender not found
2. AI provider (OpenAI) slow/unresponsive
3. Complex prompt requiring more time

**Solution:** Check backend logs for specific error

### Blender Execution Failed
```
⚠️  Blender execution failed: Blender executable not found
```

**Solution:** Install Blender 4.5+ or update BLENDER_PATH in backend

### AI Generation Failed
```
❌ Generation failed: OpenAI API error
```

**Solution:** Check `.env` file has valid `OPENAI_API_KEY`

## Comparing Backend Logs

When running the test, you'll see activity in **both terminals**:

### Terminal 1 (Backend):
```
INFO:     127.0.0.1 - "POST /api/session/new HTTP/1.1" 200 OK
INFO:     127.0.0.1 - "POST /api/ai/generate-3d-model HTTP/1.1" 200 OK
🧠 Enhanced AI Orchestrator: Analyzing prompt...
📝 Generating construction plan...
🔨 Executing Blender construction...
✅ Blender execution complete: ai_ring_1729180234.glb
```

### Terminal 2 (Test Script):
```
ℹ️  Sending prompt to AI...
⏳ This may take 30-60 seconds...
✅ AI-generated object created
🔨 Blender execution successful!
```

Both should show success! ✅

## Next Steps After Test Passes

1. **Verify Output Files**
   ```powershell
   ls output/ai_generated/
   ```
   You should see:
   - `ai_ring_*.glb` (3D model)
   - `ai_ring_*.blend` (Blender source)
   - `ai_ring_*.png` (Render preview)

2. **Test in Frontend UI**
   - Refresh browser (F5)
   - Open AI Chat sidebar
   - Enter same prompt
   - Click Generate
   - Check DevTools Console (F12) for same logs

3. **View GLB in Viewer**
   - Open https://gltf-viewer.donmccurdy.com/
   - Drag `output/ai_generated/ai_ring_*.glb` into viewer
   - Verify 3D model looks correct

## Related Documentation

- `FRONTEND_FIX.md` - Frontend endpoint integration details
- `AI_BLENDER_WORKFLOW.md` - Complete architecture documentation
- `TESTING_AI_PIPELINE.md` - Additional AI testing guides
- `test_full_workflow.py` - Alternative test script (simpler)

## Success Criteria

✅ **Test passes if:**
1. Health check returns "healthy"
2. Session created successfully
3. AI prompt executes without timeout
4. Construction plan generated with multiple steps
5. Material specifications returned
6. Blender execution succeeds
7. GLB file created and exists on disk
8. Total execution time < 2 minutes

This confirms your **entire AI → Blender pipeline is working** and the frontend should work identically! 🎯
