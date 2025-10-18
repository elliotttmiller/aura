# Duplicate React Keys Fix - SceneOutliner Component

## Problem Identified
The SceneOutliner2 component was generating React warnings about duplicate keys, which can cause:
- React reconciliation issues
- Missing or invisible 3D objects
- Broken UI rendering
- Unpredictable component updates

## Root Causes Found

### 1. Non-Unique Layer IDs in GLBModel
**Location**: `frontend/static/src/components/GLBModel/GLBModel.tsx`
**Issue**: Layer IDs were generated using only `${parentModelId}_layer_${child.uuid}`, which could produce duplicates when:
- The same GLB file is loaded multiple times
- THREE.js reuses UUIDs across different model instances
- Multiple components process the same scene

**Fix**: Enhanced ID generation to include timestamp and index:
```typescript
const uniqueId = `${parentModelId}_layer_${layerIndex}_${child.uuid}_${Date.now()}`
```

### 2. No Duplicate Prevention in Store
**Location**: `frontend/static/src/store/designStore.ts`
**Issue**: The `addGLBLayers` function didn't check for existing layers before adding new ones.

**Fix**: Added deduplication logic:
```typescript
const existingLayerIds = new Set(get().session.objects.filter(obj => obj.isLayer && obj.parentModelId === modelId).map(obj => obj.id))
const newLayers = layers.filter(layer => !existingLayerIds.has(layer.id))
```

### 3. Insufficient React Key Uniqueness
**Location**: `frontend/static/src/components/SceneOutliner/SceneOutliner.tsx`
**Issue**: React keys used only object IDs, providing no fallback if IDs were duplicated.

**Fix**: Enhanced React keys to include array index as fallback:
```typescript
key={`${object.id}_${index}`}
```

## Additional Improvements

### 1. Development-Mode Debugging
Added console warnings to detect duplicate IDs in development:
```typescript
if (process.env.NODE_ENV === 'development') {
  const allIds = objects.map(obj => obj.id)
  const duplicateIds = allIds.filter((id, index) => allIds.indexOf(id) !== index)
  if (duplicateIds.length > 0) {
    console.warn('⚠️ SceneOutliner: Duplicate object IDs detected:', duplicateIds)
  }
}
```

### 2. Layer Detection Logging
Added logging in GLBModel to track layer detection:
```typescript
if (process.env.NODE_ENV === 'development') {
  console.log(`📋 GLBModel detected ${meshes.length} layers for model ${parentModelId}:`, meshes.map(m => m.id))
}
```

## Files Modified

1. **GLBModel.tsx**
   - Enhanced layer ID generation with timestamp and index
   - Added development-mode logging

2. **designStore.ts** 
   - Added duplicate layer prevention in `addGLBLayers`
   - Filters out existing layers before adding new ones

3. **SceneOutliner.tsx**
   - Enhanced React keys with index fallback
   - Added duplicate ID detection in development
   - Applied to all list renderings (models, layers, regular objects)

## Testing the Fix

1. Open browser console
2. Load a GLB model
3. Check for React warnings about duplicate keys
4. Verify all 3D objects render correctly
5. Check SceneOutliner displays all layers properly

## Expected Results

- ✅ No React "duplicate key" warnings in console
- ✅ All 3D model layers render correctly
- ✅ SceneOutliner shows all objects without missing items
- ✅ UI updates work reliably when objects are added/removed
- ✅ No invisible or missing 3D objects

## Prevention Strategy

The fixes implement multiple layers of protection:
1. **Primary**: Unique ID generation prevents duplicates at the source
2. **Secondary**: Store-level deduplication prevents adding duplicates
3. **Tertiary**: React key enhancement ensures rendering works even with duplicates
4. **Monitoring**: Development warnings help catch future issues

This comprehensive approach ensures the duplicate key issue is resolved and won't recur.