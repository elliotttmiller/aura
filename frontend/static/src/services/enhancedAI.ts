/**
 * Enhanced AI 3D Model Generation Service
 * ========================================
 * 
 * Advanced frontend service for interacting with the Enhanced AI Orchestrator.
 * Provides sophisticated 3D model generation, refinement, and variation capabilities.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

export interface AI3DGenerationRequest {
  prompt: string
  complexity?: 'simple' | 'moderate' | 'complex' | 'hyper_realistic'
  session_id?: string
  context?: any
}

export interface AI3DGenerationResult {
  success: boolean
  user_prompt?: string
  complexity?: string
  design_analysis?: any
  construction_plan?: any[]
  presentation_plan?: any
  material_specifications?: any
  processing_time?: number
  ai_provider?: string
  metadata?: any
  object_id?: string
  session_id?: string
  error?: string
  fallback_plan?: any
}

export interface AIRefinementRequest {
  session_id: string
  object_id: string
  refinement_request: string
}

export interface AIRefinementResult {
  success: boolean
  refined_design?: any
  refinement_reasoning?: string
  processing_time?: number
  object_id?: string
  session_id?: string
  error?: string
}

export interface AIVariationRequest {
  base_prompt: string
  variation_count?: number
  session_id?: string
}

export interface AIVariationResult {
  success: boolean
  variations?: AI3DGenerationResult[]
  variation_count?: number
  session_id?: string
  object_ids?: string[]
  error?: string
}

export interface AIStatus {
  enhanced_ai_available: boolean
  openai_configured: boolean
  multi_provider_available?: boolean
  openai_model?: string
  capabilities: {
    advanced_3d_generation: boolean
    design_refinement: boolean
    variation_generation: boolean
    material_generation: boolean
  }
}

/**
 * Generate a 3D model using advanced AI orchestration
 */
export async function generate3DModel(
  request: AI3DGenerationRequest,
  onProgress?: (message: string, percentage: number) => void
): Promise<AI3DGenerationResult> {
  try {
    onProgress?.('Connecting to AI...', 5)

    const response = await fetch(`${API_BASE}/ai/generate-3d-model`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: request.prompt,
        complexity: request.complexity || 'moderate',
        session_id: request.session_id,
        context: request.context,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    const result: AI3DGenerationResult = await response.json()

    if (result.success) {
      onProgress?.('3D model generated successfully!', 100)
    } else {
      onProgress?.('Generation completed with errors', 100)
    }

    return result
  } catch (error) {
    console.error('3D model generation failed:', error)
    onProgress?.('Generation failed', 100)
    
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    }
  }
}

/**
 * Refine an existing 3D design
 */
export async function refineDesign(
  request: AIRefinementRequest,
  onProgress?: (message: string, percentage: number) => void
): Promise<AIRefinementResult> {
  try {
    onProgress?.('Analyzing refinement request...', 20)

    const response = await fetch(`${API_BASE}/ai/refine-design`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    const result: AIRefinementResult = await response.json()

    if (result.success) {
      onProgress?.('Refinement complete!', 100)
    }

    return result
  } catch (error) {
    console.error('Design refinement failed:', error)
    onProgress?.('Refinement failed', 100)
    
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    }
  }
}

/**
 * Generate multiple design variations
 */
export async function generateVariations(
  request: AIVariationRequest,
  onProgress?: (message: string, percentage: number) => void
): Promise<AIVariationResult> {
  try {
    onProgress?.('Generating design variations...', 10)

    const response = await fetch(`${API_BASE}/ai/generate-variations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        base_prompt: request.base_prompt,
        variation_count: request.variation_count || 3,
        session_id: request.session_id,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    const result: AIVariationResult = await response.json()

    if (result.success) {
      onProgress?.(`Generated ${result.variation_count} variations!`, 100)
    }

    return result
  } catch (error) {
    console.error('Variation generation failed:', error)
    onProgress?.('Variation generation failed', 100)
    
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    }
  }
}

/**
 * Get AI status and capabilities
 */
export async function getAIStatus(): Promise<AIStatus> {
  try {
    const response = await fetch(`${API_BASE}/ai/status`)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Failed to get AI status:', error)
    
    return {
      enhanced_ai_available: false,
      openai_configured: false,
      capabilities: {
        advanced_3d_generation: false,
        design_refinement: false,
        variation_generation: false,
        material_generation: false,
      },
    }
  }
}

/**
 * Check if enhanced AI features are available
 */
export async function isEnhancedAIAvailable(): Promise<boolean> {
  const status = await getAIStatus()
  return status.enhanced_ai_available && status.openai_configured
}

/**
 * Get suggested complexity for a prompt
 */
export function suggestComplexity(prompt: string): 'simple' | 'moderate' | 'complex' | 'hyper_realistic' {
  const lowerPrompt = prompt.toLowerCase()
  
  // Hyper-realistic indicators
  if (
    lowerPrompt.includes('hyper') ||
    lowerPrompt.includes('photo') ||
    lowerPrompt.includes('realistic') ||
    lowerPrompt.includes('detailed')
  ) {
    return 'hyper_realistic'
  }
  
  // Complex indicators
  if (
    lowerPrompt.includes('complex') ||
    lowerPrompt.includes('intricate') ||
    lowerPrompt.includes('ornate') ||
    lowerPrompt.includes('elaborate')
  ) {
    return 'complex'
  }
  
  // Simple indicators
  if (
    lowerPrompt.includes('simple') ||
    lowerPrompt.includes('basic') ||
    lowerPrompt.includes('minimal')
  ) {
    return 'simple'
  }
  
  // Default to moderate
  return 'moderate'
}

/**
 * Extract design keywords from prompt
 */
export function extractDesignKeywords(prompt: string): string[] {
  const keywords: string[] = []
  const lowerPrompt = prompt.toLowerCase()
  
  // Materials
  const materials = ['gold', 'silver', 'platinum', 'diamond', 'ruby', 'sapphire', 'emerald']
  materials.forEach(material => {
    if (lowerPrompt.includes(material)) {
      keywords.push(material)
    }
  })
  
  // Styles
  const styles = ['vintage', 'modern', 'classic', 'ornate', 'minimal', 'elegant', 'bold']
  styles.forEach(style => {
    if (lowerPrompt.includes(style)) {
      keywords.push(style)
    }
  })
  
  // Object types
  const types = ['ring', 'necklace', 'earring', 'bracelet', 'pendant', 'brooch']
  types.forEach(type => {
    if (lowerPrompt.includes(type)) {
      keywords.push(type)
    }
  })
  
  return keywords
}

export default {
  generate3DModel,
  refineDesign,
  generateVariations,
  getAIStatus,
  isEnhancedAIAvailable,
  suggestComplexity,
  extractDesignKeywords,
}
