# 🚀 Quick Start Guide - Enhanced AI 3D Model Generation

Get up and running with Aura's AI-driven 3D model generation in **5 minutes**!

## Prerequisites

- **Python 3.8+** (check: `python --version`)
- **Node.js 16+** (check: `node --version`)
- **OpenAI API Key** (recommended) - [Get one here](https://platform.openai.com/api-keys)
  - OR use **LM Studio** (free local alternative) - [Download here](https://lmstudio.ai/)

## Step 1: Clone and Setup Environment (2 minutes)

```bash
# Clone the repository (if not already done)
git clone https://github.com/elliotttmiller/aura.git
cd aura

# Create environment configuration
cp .env.example .env

# Edit .env and add your OpenAI API key
# Set: OPENAI_API_KEY=sk-your-actual-key-here
nano .env  # or use your favorite text editor
```

## Step 2: Install Backend Dependencies (1 minute)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import openai; print('✓ OpenAI SDK installed')"
```

## Step 3: Install Frontend Dependencies (1 minute)

```bash
cd frontend/static
npm install
cd ../..
```

## Step 4: Start the Backend (30 seconds)

```bash
# From the root directory
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
✓ Enhanced AI Orchestrator initialized
✓ OpenAI GPT-4 3D Generator: ENABLED
```

## Step 5: Start the Frontend (30 seconds)

In a **new terminal**:

```bash
cd frontend/static
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

## Step 6: Test the System! 🎉

### Option A: Via Web Interface

1. Open your browser to http://localhost:5173
2. Click on **AI Design Collaborator** panel
3. Type a prompt like: `"elegant gold ring with diamond"`
4. Click **Send** and watch the AI create your design!

### Option B: Via API

```bash
# Check AI status
curl http://localhost:8001/api/ai/status

# Generate a 3D model
curl -X POST http://localhost:8001/api/ai/generate-3d-model \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "simple gold ring",
    "complexity": "moderate"
  }'
```

### Option C: Via Python

```python
import requests

# Generate a 3D model
response = requests.post('http://localhost:8001/api/ai/generate-3d-model', json={
    'prompt': 'elegant silver necklace with pendant',
    'complexity': 'moderate'
})

result = response.json()
print(f"Success: {result['success']}")
print(f"Operations: {len(result.get('construction_plan', []))}")
```

## 🎓 Example Prompts to Try

### Jewelry (Primary Use Case)
```
- "elegant engagement ring with vintage filigree details in platinum"
- "modern minimalist silver band with brushed finish"
- "ornate gold necklace with intricate chain work"
- "delicate diamond stud earrings"
- "bold statement ring with gemstone accents"
```

### Complexity Levels
```
simple: "basic gold ring"
moderate: "elegant ring with gemstone setting"
complex: "intricate ring with multiple stones and detailed band"
hyper_realistic: "photorealistic engagement ring with detailed filigree"
```

### Refinement Workflow
```
1. Initial: "simple gold ring"
2. Refine: "make it thicker and add texture"
3. Refine: "add a small diamond on top"
4. Refine: "change to platinum finish"
```

## 🔧 Troubleshooting

### "Enhanced AI orchestration not available"

**Problem:** OpenAI API key not configured

**Solution:**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# If empty, edit .env file and add:
# OPENAI_API_KEY=sk-your-actual-key-here

# Restart backend
```

### "Module 'openai' not found"

**Problem:** OpenAI SDK not installed

**Solution:**
```bash
pip install openai>=1.42.0
```

### "Connection refused to localhost:8001"

**Problem:** Backend not running

**Solution:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Slow Generation Times

**Problem:** Using complex prompts or high token limits

**Solutions:**
- Use simpler prompts
- Reduce complexity level
- Use `gpt-3.5-turbo` instead of `gpt-4` in .env
- Reduce `OPENAI_MAX_TOKENS` in .env

## 🆓 Using Free Alternatives

### Option 1: LM Studio (Local AI)

1. **Download LM Studio:** https://lmstudio.ai/
2. **Download a model:** Llama 3.1 8B Instruct (recommended)
3. **Start the server:** Click "Local Server" tab, then "Start Server"
4. **Update .env:**
   ```bash
   # Comment out OpenAI
   # OPENAI_API_KEY=...
   
   # Enable LM Studio
   LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
   LM_STUDIO_MODEL=llama-3.1-8b-instruct
   ```
5. **Restart backend**

### Option 2: Ollama (Local AI)

1. **Download Ollama:** https://ollama.ai/
2. **Install a model:**
   ```bash
   ollama pull llama3.1
   ```
3. **Update .env:**
   ```bash
   OLLAMA_URL=http://localhost:11434/api/generate
   OLLAMA_MODEL=llama3.1
   ```
4. **Restart backend**

## 📊 Running Tests

```bash
# Run the test suite
python tests/test_enhanced_ai.py

# Expected output:
# ✅ PASS - AI 3D Model Generator
# ✅ PASS - Enhanced AI Orchestrator
# ✅ PASS - Backend Integration
# ✅ PASS - OpenAI API Integration
```

## 📚 Next Steps

1. **Read the Full Documentation:** `docs/ENHANCED_AI_SYSTEM.md`
2. **Explore API Endpoints:** See API Reference section
3. **Try Refinement Workflow:** Iteratively improve designs
4. **Generate Variations:** Create multiple design options
5. **Integrate with Your App:** Use the TypeScript service

## 💡 Pro Tips

1. **Be Specific:** More detailed prompts = better results
   - ❌ "ring"
   - ✅ "elegant 2mm wide platinum wedding band with brushed finish"

2. **Use Complexity Wisely:**
   - Simple = Basic shapes, fast generation
   - Moderate = Standard designs, balanced quality/speed
   - Complex = Intricate details, slower but more detailed
   - Hyper-realistic = Photorealistic, slowest but best quality

3. **Iterate Incrementally:**
   - Start with base design
   - Add details through refinements
   - Test variations before committing

4. **Monitor Usage:**
   - OpenAI charges per token
   - Check usage at: https://platform.openai.com/usage
   - Set spending limits in OpenAI dashboard

## 🆘 Getting Help

- **Documentation:** `docs/ENHANCED_AI_SYSTEM.md`
- **Test Output:** Run `python tests/test_enhanced_ai.py` for diagnostics
- **API Status:** Check `http://localhost:8001/api/ai/status`
- **Backend Logs:** Watch terminal running uvicorn
- **Frontend Logs:** Check browser console (F12)

## ✅ Success Checklist

- [ ] `.env` file created with OPENAI_API_KEY
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend running (http://localhost:8001)
- [ ] Frontend running (http://localhost:5173)
- [ ] Test successful (API returns generation result)
- [ ] Web interface shows 3D model

---

**🎉 Congratulations!** You're now ready to create AI-driven 3D models!

**Next:** Open http://localhost:5173 and start designing! 🚀
