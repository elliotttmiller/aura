# Complete Testing Guide - AI → Blender Pipeline

## What You Have Now

✅ **Frontend-Equivalent Test Script** (`test_frontend_workflow.py`)
   - Calls the EXACT same API endpoint as the UI
   - Sends identical request payload
   - Shows same console.log output
   - Verifies complete workflow

✅ **Quick Start Scripts**
   - `start_backend.py` - Easy backend startup
   - `test_frontend_workflow.py` - Full workflow test
   - `test_full_workflow.py` - Alternative test (existing)

## Testing Flow Chart

```
User Action (UI)          Test Script               Backend
─────────────────        ──────────────            ─────────
                                                        
1. Click Generate    →   execute_ai_prompt()   →   POST /api/ai/generate-3d-model
                                                        ↓
                                                   Enhanced AI Orchestrator
                                                        ↓
                                                   Construction Plan
                                                        ↓
                                                   Blender Executor
                                                        ↓
2. View in Console   ←   display_results()     ←   Returns GLB + Materials
                                                        
3. See in Viewport       (Not tested - UI only)   
```

## Testing Methods

### Method 1: Quick CLI Test (Recommended)

**Terminal 1:**
```powershell
cd backend
python main.py
```

**Terminal 2:**
```powershell
python test_frontend_workflow.py "Generate a simple gold ring"
```

**Advantages:**
✅ Fast feedback
✅ No browser needed
✅ Colored output
✅ Easy to test multiple prompts
✅ Shows exact API responses

### Method 2: Browser UI Test

**Terminal 1:**
```powershell
cd backend
python main.py
```

**Browser:**
1. Navigate to http://localhost:8001
2. Refresh (F5) to load updated frontend
3. Open AI Chat sidebar (right toggle button)
4. Enter prompt: "Generate a simple gold ring"
5. Click Generate
6. Open DevTools Console (F12)
7. Watch for console.log statements

**Advantages:**
✅ Tests actual UI
✅ Verifies frontend integration
✅ Shows visual feedback
✅ Complete user experience

### Method 3: Alternative Test Script

```powershell
python test_full_workflow.py
```

Simpler output, less frontend-specific.

## What Each Test Verifies

| Component | CLI Test | Browser Test |
|-----------|----------|--------------|
| Backend Health | ✅ | ✅ |
| Session Creation | ✅ | ✅ |
| AI Orchestrator | ✅ | ✅ |
| Construction Plan | ✅ | ✅ |
| Blender Execution | ✅ | ✅ |
| GLB File Creation | ✅ | ✅ |
| Frontend Integration | ❌ | ✅ |
| UI Responsiveness | ❌ | ✅ |
| Viewport Display | ❌ | ⚠️ (Partial) |

## Sample Test Session

### 1. Start Backend
```powershell
PS C:\Users\AMD\aura> cd backend
PS C:\Users\AMD\aura\backend> python main.py
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```

### 2. Run Test (New Terminal)
```powershell
PS C:\Users\AMD\aura> python test_frontend_workflow.py "Generate a gold ring"
```

**Expected Output:**
```
================================================================================
                 FRONTEND WORKFLOW TEST - AI → BLENDER PIPELINE
================================================================================

ℹ️  Testing with prompt: 'Generate a gold ring'
ℹ️  This test mimics exactly what happens when you click 'Generate' in the UI

ℹ️  Checking backend health...
✅ Backend is healthy

ℹ️  Creating new session...
✅ Session created: session_1729180234

================================================================================
                            EXECUTING AI PROMPT
================================================================================

ℹ️  Sending prompt to AI: 'Generate a gold ring'
ℹ️  This is the SAME endpoint the frontend calls...
ℹ️  Endpoint: POST http://localhost:8001/api/ai/generate-3d-model
ℹ️  ⏳ This may take 30-60 seconds (AI analysis + Blender execution)...

[... wait 30-60 seconds ...]

================================================================================
                            AI GENERATION RESULTS
================================================================================

✅ AI-generated object created

📝 User prompt: Generate a gold ring

📦 Construction plan:
   Type: jewelry_ring
   Steps: 5 operations
   1. create_shank - {'profile': 'round', 'width': 2.0}
   2. create_head - {'type': 'prong_setting'}
   3. apply_material - {'name': 'Gold'}
   ... and 2 more steps

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
   Name: AI: Generate a gold ring...
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

### 3. Verify Output Files
```powershell
PS C:\Users\AMD\aura> ls output/ai_generated/
```

**Expected:**
```
ai_ring_1729180234.glb
ai_ring_1729180234.blend
ai_ring_1729180234.png
```

## Test Prompts to Try

### Simple Tests
```powershell
python test_frontend_workflow.py "Generate a gold ring"
python test_frontend_workflow.py "Generate a silver pendant"
python test_frontend_workflow.py "Generate diamond earrings"
```

### Complex Tests
```powershell
python test_frontend_workflow.py "Generate a platinum engagement ring with round diamond in prong setting"
python test_frontend_workflow.py "Generate a gold bracelet with emerald stones"
python test_frontend_workflow.py "Generate a wedding band with engraved pattern"
```

### Edge Cases
```powershell
python test_frontend_workflow.py "Generate a ring"  # Minimal prompt
python test_frontend_workflow.py "Generate a very elaborate Victorian-style engagement ring with intricate filigree work, halo setting, and multiple accent diamonds"  # Complex prompt
```

## Troubleshooting

### Error: Backend Not Reachable
```
❌ Backend not reachable: Connection refused
```

**Solution:** Start backend server
```powershell
cd backend
python main.py
```

### Error: OpenAI API Error
```
❌ Generation failed: OpenAI API error
```

**Solution:** Check `.env` file has valid API key
```powershell
# In project root, check .env file
OPENAI_API_KEY=sk-...your-key...
```

### Error: Blender Execution Failed
```
⚠️  Blender execution failed: Blender executable not found
```

**Solutions:**
1. Install Blender 4.5+: https://www.blender.org/download/
2. Or set BLENDER_PATH in `.env`:
   ```
   BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe
   ```

### Error: Timeout (>5 minutes)
```
❌ Request timed out (>5 minutes)
```

**Causes:**
- OpenAI API slow/rate limited
- Blender taking too long
- Complex prompt requiring more processing

**Solution:** Try simpler prompt or check OpenAI API status

## Backend Console Monitoring

While test runs, watch **Terminal 1 (backend)** for:

```
INFO:     127.0.0.1:xxxx - "POST /api/session/new HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxx - "POST /api/ai/generate-3d-model HTTP/1.1" 200 OK
🧠 Enhanced AI Orchestrator: Analyzing prompt: 'Generate a gold ring'
📝 Construction plan generated: jewelry_ring with 5 steps
🔨 Blender Construction Executor: Starting execution...
✅ Blender execution complete: ai_ring_1729180234.glb
```

Both terminals should show success! ✅

## Success Criteria

Your test **PASSES** if:

✅ Health check returns "healthy"
✅ Session ID created (e.g., `session_1729180234`)
✅ AI prompt executes without timeout
✅ Construction plan has 3+ steps
✅ Material specifications returned
✅ Blender execution succeeds
✅ GLB file created and exists
✅ File size > 0 KB
✅ Total time < 2 minutes

## After Test Passes

1. **Verify 3D Model**
   - Open GLB viewer: https://gltf-viewer.donmccurdy.com/
   - Drag `output/ai_generated/ai_ring_*.glb` into browser
   - Model should display correctly

2. **Test in UI**
   - Keep backend running
   - Open http://localhost:8001
   - Refresh browser (F5)
   - Click Generate in AI Chat
   - Should see same results!

3. **Check Console Logs**
   - Browser DevTools (F12)
   - Should see same console.log statements as CLI test
   - Proves frontend integration working

## Related Files

- `test_frontend_workflow.py` - Main test script
- `TESTING_FRONTEND_WORKFLOW.md` - Detailed documentation
- `QUICK_TEST_GUIDE.md` - Quick reference
- `FRONTEND_FIX.md` - Frontend endpoint fix details
- `AI_BLENDER_WORKFLOW.md` - Architecture documentation

## Need More Help?

Check these resources:
1. `DEPLOYMENT_GUIDE.md` - Full setup instructions
2. `TESTING_GUIDE.md` - General testing guide
3. Backend logs in Terminal 1
4. OpenAI API dashboard for quota/errors

---

**🎯 Goal:** CLI test should match browser UI behavior **exactly**!

When CLI test passes, your frontend will work! ✅
