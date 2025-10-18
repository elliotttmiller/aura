# 🚀 AI Generation Pipeline - Complete Testing Guide

## Overview

This guide walks you through testing the **complete AI-driven 3D model generation workflow** from prompt → AI analysis → construction plan → execution.

---

## 🎯 What Gets Tested

1. **Backend API** - Enhanced AI Orchestrator endpoints
2. **OpenAI Integration** - GPT-4 design analysis and planning
3. **Design Analysis** - AI interpretation of user prompts
4. **Construction Planning** - Step-by-step build instructions
5. **Material Specifications** - PBR material generation
6. **Frontend Integration** - Complete workflow through UI

---

## 📋 Prerequisites

### 1. Backend Must Be Running
```powershell
# Start the backend server
cd backend
uvicorn main:app --reload --port 8001
```

### 2. Environment Variables Configured
Check your `.env` file has:
```env
OPENAI_API_KEY=sk-proj-...your-key...
OPENAI_MODEL=gpt-4o
BACKEND_PORT=8001
```

### 3. Python Dependencies Installed
```powershell
pip install -r requirements.txt
```

---

## 🧪 Testing Methods

### **Method 1: Interactive Test Script (Recommended)**

Full-featured test with beautiful output formatting:

```powershell
python test_ai_pipeline.py
```

**Features:**
- ✅ Backend health check
- ✅ Pre-configured test cases
- ✅ Custom prompt support
- ✅ Detailed formatted results
- ✅ Saves JSON output
- ✅ Multiple complexity levels

**Menu Options:**
1. Quick Test - Diamond Engagement Ring (moderate)
2. Complex Test - Art Deco Necklace (complex)
3. Hyper-Realistic Test - Vintage Bracelet (hyper_realistic)
4. Custom Prompt (your own)
5. Run All Tests (sequential)

**Output Shows:**
- 🧠 AI Design Analysis
- 🔨 Construction Plan (step-by-step)
- 💎 Material Specifications
- 📸 Presentation Plan
- 📊 Generation Metadata

---

### **Method 2: Quick Command-Line Test**

Fast single-prompt test:

```powershell
# Basic test
python quick_test.py "diamond engagement ring"

# With complexity
python quick_test.py "art deco necklace" complex

# Hyper-realistic
python quick_test.py "vintage gold bracelet with filigree" hyper_realistic
```

**Complexity Levels:**
- `simple` - Basic shapes, minimal detail (fastest, ~10s)
- `moderate` - Standard jewelry, good detail (default, ~20s)
- `complex` - Intricate patterns, multiple components (~30s)
- `hyper_realistic` - Maximum detail, realistic rendering (~40-60s)

---

### **Method 3: Direct API Call (curl/PowerShell)**

Test raw API endpoint:

```powershell
# Using Invoke-RestMethod (PowerShell)
$body = @{
    prompt = "diamond engagement ring with flower pattern"
    complexity = "moderate"
    session_id = "test-session-001"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8001/api/ai/generate-3d-model" -Method POST -Body $body -ContentType "application/json"

# View results
$response | ConvertTo-Json -Depth 10
```

```bash
# Using curl (if available)
curl -X POST http://localhost:8001/api/ai/generate-3d-model \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "diamond engagement ring with flower pattern",
    "complexity": "moderate",
    "session_id": "test-001"
  }' | python -m json.tool
```

---

### **Method 4: Frontend UI Test (End-to-End)**

Test through the actual application interface:

1. **Start Backend:**
   ```powershell
   cd backend
   uvicorn main:app --reload --port 8001
   ```

2. **Start Frontend:**
   ```powershell
   cd frontend/static
   npm run dev
   ```

3. **Open Browser:**
   - Navigate to `http://localhost:5173`
   - Open the **AI Chat** sidebar (right side)

4. **Send Test Prompt:**
   ```
   Generate a diamond engagement ring with intricate flower patterns
   ```

5. **Observe:**
   - AI chat response with analysis
   - Construction plan displayed
   - 3D object appears in Scene Outliner (left sidebar)
   - Model visible in viewport (center)

---

## 📊 Expected Results

### **Successful Response Structure:**

```json
{
  "success": true,
  "user_prompt": "diamond engagement ring with flower pattern",
  "complexity": "moderate",
  
  "design_analysis": {
    "interpretation": "User wants a romantic engagement ring...",
    "complexity_assessment": "Moderate complexity due to...",
    "recommended_approach": "Use NURBS curves for...",
    "style_characteristics": [
      "Romantic and elegant",
      "Feminine with organic patterns",
      "Traditional engagement ring proportions"
    ]
  },
  
  "construction_plan": [
    {
      "step": 1,
      "operation": "create_ring_band",
      "description": "Create the base ring band with proper sizing",
      "parameters": {
        "inner_diameter": 16.5,
        "outer_diameter": 18.5,
        "height": 2.0,
        "profile": "comfort_fit"
      },
      "reasoning": "Standard comfort-fit band provides...",
      "expected_outcome": "Smooth, wearable ring base"
    },
    // ... more steps
  ],
  
  "material_specifications": {
    "primary_material": {
      "name": "18K White Gold",
      "type": "metal",
      "base_color": "#F5F5F5",
      "metallic": 0.95,
      "roughness": 0.15,
      "ior": 1.47
    },
    "accent_materials": [
      {
        "name": "Diamond (1.0ct center)",
        "type": "gemstone",
        "description": "Round brilliant cut, VS1 clarity"
      }
    ]
  },
  
  "presentation_plan": {
    "lighting": {
      "setup": "three_point_studio",
      "intensity": 1.2,
      "temperature": 6500
    },
    "camera_angle": {
      "angle": "45_degree_perspective",
      "distance": "close_detail"
    },
    "background": {
      "type": "gradient",
      "color": "#2A2B4A to #1A1B2F"
    }
  },
  
  "metadata": {
    "ai_provider": "openai",
    "model": "gpt-4o",
    "processing_time": 18.34,
    "total_tokens": 2847,
    "timestamp": "2025-10-17T20:45:32"
  },
  
  "object_id": "obj_abc123",
  "session_id": "test-session-001"
}
```

---

## 🎨 Example Test Prompts

### **Simple Complexity:**
- "simple gold ring"
- "basic silver pendant"
- "plain wedding band"

### **Moderate Complexity:**
- "diamond engagement ring with flower pattern"
- "pearl necklace with gold chain"
- "emerald stud earrings with halo setting"

### **Complex Complexity:**
- "art deco sapphire necklace with geometric patterns"
- "vintage filigree bracelet with gemstone accents"
- "multi-stone cocktail ring with intricate metalwork"

### **Hyper-Realistic Complexity:**
- "hyper-realistic diamond tiara with Victorian styling"
- "antique brooch with detailed enamel work and micro-pavé diamonds"
- "custom wedding ring set with nature-inspired organic patterns"

---

## 🔍 Troubleshooting

### **"Cannot connect to backend"**
```powershell
# Check if backend is running
# Should see: "INFO:     Uvicorn running on http://0.0.0.0:8001"
netstat -ano | findstr :8001

# Restart backend
cd backend
uvicorn main:app --reload --port 8001
```

### **"Enhanced AI orchestration not available"**
Check `.env` file:
```env
OPENAI_API_KEY=sk-proj-...  # Must be valid
```

### **"Request timed out"**
- Hyper-realistic complexity can take 40-60s
- Increase timeout in test script
- Check OpenAI API status

### **"HTTP 503" or "Service Unavailable"**
Check backend logs for:
```
✓ Enhanced AI Orchestrator available
✓ Enhanced AI Orchestrator initialized
```

If missing:
1. Verify OpenAI API key is valid
2. Check `backend/enhanced_ai_orchestrator.py` exists
3. Restart backend

---

## 📈 Performance Benchmarks

| Complexity | Avg. Time | Tokens Used | API Cost (GPT-4o) |
|------------|-----------|-------------|-------------------|
| Simple | 8-12s | 500-1000 | ~$0.01-0.02 |
| Moderate | 15-25s | 1500-2500 | ~$0.03-0.05 |
| Complex | 25-40s | 2500-4000 | ~$0.05-0.08 |
| Hyper-Realistic | 40-60s | 4000-6000 | ~$0.08-0.12 |

*Note: Costs based on GPT-4o pricing as of Oct 2025*

---

## 💾 Saving Results

All test scripts automatically save results to JSON files:

```
ai_generation_test_20251017_204532.json  # Interactive test
ai_test_1729203945.json                  # Quick test
```

**Use results for:**
- Debugging construction plans
- Training data analysis
- Performance monitoring
- API documentation
- Frontend integration testing

---

## 🚀 Next Steps

After successful testing:

1. **Integrate with Frontend:**
   - Connect AI Chat to `/api/ai/generate-3d-model`
   - Display construction plan in UI
   - Show material specs in Properties Inspector

2. **Add Progress Feedback:**
   - Implement Server-Sent Events (SSE)
   - Show real-time AI thinking progress
   - Display construction step execution

3. **Enable Variations:**
   - Test `/api/ai/generate-variations` endpoint
   - Generate multiple design options
   - Allow user to select preferred variation

4. **Add Refinement:**
   - Test `/api/ai/refine` endpoint
   - Enable iterative improvements
   - "Make it bigger/smaller/more detailed"

---

## 📞 Support

If you encounter issues:

1. Check backend logs for errors
2. Verify `.env` configuration
3. Test with simple prompts first
4. Review API response in browser DevTools
5. Check OpenAI API usage dashboard

**Happy Testing! 🎉**
