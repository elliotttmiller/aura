# How to Test the AI → Blender Pipeline

## Quick Test (2 steps)

### Step 1: Start Backend (Terminal 1)
```powershell
cd backend
python main.py
```

**Wait for this message:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### Step 2: Run Test (Terminal 2 - New Window)
```powershell
python test_frontend_workflow.py "Generate a simple gold ring"
```

## Expected Test Output

If backend is running correctly, you'll see:

```
✅ Backend is healthy
✅ Session created: session_abc123
ℹ️  ⏳ This may take 30-60 seconds (AI analysis + Blender execution)...
✅ AI-generated object created
🔨 Blender execution successful!
📁 GLB file: C:/Users/AMD/aura/output/ai_generated/ai_ring_*.glb
✅ File exists! Size: 0.52 MB
⏱️  Total API call time: 45.67 seconds
✅ Full workflow completed successfully!
```

## What This Proves

✅ Backend server is running
✅ OpenAI API is working
✅ Enhanced AI Orchestrator is analyzing prompts
✅ Construction plans are being generated
✅ Blender Construction Executor is working
✅ 3D models (.glb files) are being created
✅ **The frontend will work identically!**

## Current Status

Based on your test run, backend is **NOT running**.

To start it:

### Option 1: Manual Start
```powershell
# Terminal 1
cd C:\Users\AMD\aura\backend
python main.py
```

### Option 2: VS Code Task
1. Press `Ctrl+Shift+P`
2. Type "Run Task"
3. Select "Start Backend Server"

## After Backend Starts

Once you see:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
```

Then run the test:
```powershell
python test_frontend_workflow.py "Generate a simple gold ring"
```

## Test Different Prompts

```powershell
# Basic ring
python test_frontend_workflow.py "Generate a gold wedding band"

# With gemstones
python test_frontend_workflow.py "Generate a platinum ring with sapphire"

# Complex design
python test_frontend_workflow.py "Generate an engagement ring with halo setting"
```

## Verify Generated Files

After successful test:
```powershell
ls output/ai_generated/
```

You should see:
- `ai_ring_*.glb` - 3D model (web format)
- `ai_ring_*.blend` - Blender source file
- `ai_ring_*.png` - Render preview

## Next: Test in Browser

After CLI test passes:
1. Keep backend running
2. Open http://localhost:8001 in browser
3. Refresh page (F5) to load new frontend
4. Open AI Chat sidebar (right toggle)
5. Enter same prompt
6. Click Generate
7. Open DevTools Console (F12)
8. Should see identical success logs!

---

**Need Help?**
See `TESTING_FRONTEND_WORKFLOW.md` for detailed troubleshooting guide.
