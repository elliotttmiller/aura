# Quick Reference: Upload Integration

## For Developers

### Loading Models

#### AI-Generated Models (Existing Code - No Changes Needed)
```typescript
// Existing AI pipeline calls work unchanged
actions.loadGLBModel(modelUrl, 'AI Generated Ring')
// Source automatically inferred as 'ai'
```

#### Uploaded Models (New)
```typescript
// Explicitly mark as uploaded
actions.loadGLBModel(modelUrl, 'Custom Ring', 'uploaded')
// Source explicitly set to 'uploaded'
```

#### Flexible Loading
```typescript
// With all parameters
actions.loadGLBModel(url, name, 'uploaded')

// With optional parameters
actions.loadGLBModel(url, name)  // Source inferred from URL

// Minimal call (backward compatible)
actions.loadGLBModel()  // Uses defaults
```

### Feature Flags

Located in: `frontend/static/src/config/featureFlags.ts`

```typescript
export const featureFlags = {
  // Apply jewelry-specific material enhancements to uploaded models
  enableJewelryMaterialEnhancements: false,  // Default: off
  
  // Use high-fidelity lighting (future)
  enableHighFidelityViewportLighting: false  // Default: off
} as const
```

**To enable jewelry enhancements**:
1. Change `enableJewelryMaterialEnhancements` to `true`
2. Restart dev server
3. Only uploaded models get enhanced materials

### Material Enhancements

When `enableJewelryMaterialEnhancements: true` and model source is `'uploaded'`:

```typescript
// Applied enhancements:
material.envMapIntensity = 2.0        // vs 1.5 default
material.metalness = 0.8              // if undefined
material.roughness = 0.2              // if undefined
material.clearcoat = 0.35             // jewelry shine
material.clearcoatRoughness = 0.1     // smooth clearcoat
```

### Upload Flow (User Experience)

1. **Initial State**: Chat interface visible
2. **Click "📁 Upload Model"**: Shows uploader, hides chat
3. **Select File**: Drag/drop or click to browse
4. **Upload Progress**: Spinner shows upload in progress
5. **Success**: Model appears in viewport, uploader closes, chat returns
6. **Chat Confirmation**: Success message appears in chat history

### Scene Outliner Display

Models display with source badges:
- 🤖 + "AI" badge → AI-generated models
- 📁 + "Uploaded" badge → User-uploaded models

Badge colors:
- AI: Purple gradient
- Uploaded: Blue accent

### Backward Compatibility

All existing code continues to work:
- Models without `source` property render correctly
- Source inferred from URL if not explicit
- No console errors for missing metadata
- Graceful fallbacks throughout

### Testing Checklist

Run this after making changes:

```bash
# Run integration tests
python test_safe_integration.py

# Check TypeScript errors
npm run type-check  # or tsc --noEmit

# Start dev server
npm run dev
```

Test in browser:
1. ✅ AI generation works
2. ✅ Upload button appears
3. ✅ Upload succeeds
4. ✅ Model renders in viewport
5. ✅ Source badge shows correctly
6. ✅ Layer selection works

### Common Issues

**Issue**: Upload models look too shiny
**Solution**: Check feature flags. Set `enableJewelryMaterialEnhancements: false`

**Issue**: Source badge missing
**Solution**: Pass third parameter to `loadGLBModel`: `actions.loadGLBModel(url, name, 'uploaded')`

**Issue**: Upload doesn't work
**Solution**: Check backend `/api/upload/model` endpoint is running

**Issue**: Model doesn't render
**Solution**: Check browser console for WebGL errors, verify model format

### File Structure

```
frontend/static/src/
├── components/
│   ├── AIChatSidebar/
│   │   ├── AIChatSidebar.tsx      # Upload toggle + integration
│   │   └── AIChatSidebar.css      # Upload button styles
│   ├── ModelUploader/
│   │   ├── ModelUploader.tsx      # Upload UI component
│   │   └── ModelUploader.css      # Upload styles
│   ├── GLBModel/
│   │   └── GLBModel.tsx           # Material enhancements (guarded)
│   ├── SceneOutliner/
│   │   ├── SceneOutliner.tsx      # Source badge display
│   │   └── SceneOutliner.css      # Badge styles
│   └── Viewport/
│       └── Viewport.tsx           # NO CHANGES (working baseline)
├── store/
│   └── designStore.ts             # loadGLBModel (backward compatible)
└── config/
    └── featureFlags.ts            # Feature toggles
```

### API Endpoints

**Upload Model**:
```
POST /api/upload/model
Content-Type: multipart/form-data

Body:
- file: (binary)

Response:
{
  "success": true,
  "model_url": "/api/models/uploaded/filename.glb",
  "model_name": "filename.glb",
  "status": "ready"
}
```

### Debugging

Enable debug logs in GLBModel:
```typescript
// Already present in development mode
if (process.env.NODE_ENV === 'development') {
  console.log(`📏 Auto-framed GLB model: ...`)
  console.log(`📋 GLBModel detected ${meshes.length} layers...`)
}
```

Check feature flags in console:
```javascript
import { featureFlags } from './config/featureFlags'
console.log(featureFlags)
```

### Rollback

If issues arise, revert changes to:
1. `frontend/static/src/store/designStore.ts` (loadGLBModel)
2. `frontend/static/src/components/AIChatSidebar/AIChatSidebar.tsx` (remove upload section)
3. `frontend/static/src/components/GLBModel/GLBModel.tsx` (remove feature checks)
4. `frontend/static/src/components/SceneOutliner/SceneOutliner.tsx` (remove badges)

Original working commit: `020b12541b95f46cc9eebf6188f9270b2bdf8a3a`
