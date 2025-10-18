"""
AI-Driven 3D Model Generator - Advanced OpenAI Integration
===========================================================

This module implements state-of-the-art AI-driven 3D model design, generation,
and build logic using OpenAI's GPT-4/GPT-4o models. It provides:

- Intelligent 3D model design analysis and planning
- Advanced prompt engineering for optimal 3D geometry generation
- Sophisticated construction plan generation with material specifications
- Real-time AI reasoning and decision-making transparency
- Professional validation and quality assurance
- Seamless integration with the existing Aura workflow

This represents the pinnacle of AI-driven 3D design intelligence.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# Check for OpenAI availability
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not available. Install with: pip install openai>=1.42.0")


class ModelComplexity(Enum):
    """3D Model complexity levels for intelligent processing."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    HYPER_REALISTIC = "hyper_realistic"


class AI3DModelGenerator:
    """
    Advanced AI-Driven 3D Model Generator using OpenAI GPT-4/GPT-4o.
    
    This class orchestrates the complete AI-driven 3D model design workflow,
    from initial concept to detailed construction plans with material specifications.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI 3D Model Generator.
        
        Args:
            api_key: OpenAI API key (if not provided, reads from environment)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. AI 3D generation will be limited.")
            self.client = None
            self.enabled = False
        elif not OPENAI_AVAILABLE:
            logger.error("OpenAI SDK not installed. Please install: pip install openai>=1.42.0")
            self.client = None
            self.enabled = False
        else:
            self.client = OpenAI(api_key=self.api_key)
            self.enabled = True
            logger.info("✓ AI 3D Model Generator initialized with OpenAI GPT-4")
        
        # Model configuration for optimal 3D design generation
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4096'))
        
    def is_enabled(self) -> bool:
        """Check if the AI generator is properly configured."""
        return self.enabled
    
    def analyze_design_intent(self, user_prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze user's design intent using advanced AI reasoning.
        
        This method uses GPT-4 to deeply understand the user's creative vision,
        extracting key design parameters, constraints, and aesthetic preferences.
        
        Args:
            user_prompt: User's natural language design description
            context: Optional context about existing scene or project
            
        Returns:
            Comprehensive design analysis with recommendations
        """
        if not self.enabled:
            return self._fallback_design_analysis(user_prompt)
        
        logger.info("🧠 Analyzing design intent with GPT-4...")
        
        system_prompt = self._get_design_analysis_system_prompt()
        user_message = self._format_design_analysis_prompt(user_prompt, context)
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            analysis_time = time.time() - start_time
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"✓ Design analysis completed in {analysis_time:.2f}s")
            
            return {
                "success": True,
                "analysis": result,
                "processing_time": analysis_time,
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Design analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._fallback_design_analysis(user_prompt)
            }
    
    def generate_construction_plan(
        self,
        user_prompt: str,
        design_analysis: Dict[str, Any],
        complexity: ModelComplexity = ModelComplexity.MODERATE
    ) -> Dict[str, Any]:
        """
        Generate detailed 3D construction plan using AI intelligence.
        
        This is the core function that transforms design intent into actionable
        3D modeling operations with precise parameters and material specifications.
        
        Args:
            user_prompt: Original user design request
            design_analysis: Results from design intent analysis
            complexity: Target complexity level for the model
            
        Returns:
            Detailed construction plan with operations and materials
        """
        if not self.enabled:
            return self._fallback_construction_plan(user_prompt)
        
        logger.info("🏗️ Generating construction plan with GPT-4...")
        
        system_prompt = self._get_construction_plan_system_prompt(complexity)
        user_message = self._format_construction_plan_prompt(
            user_prompt, design_analysis, complexity
        )
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            plan_time = time.time() - start_time
            construction_plan = json.loads(response.choices[0].message.content)
            
            logger.info(f"✓ Construction plan generated in {plan_time:.2f}s")
            logger.info(f"  Operations: {len(construction_plan.get('construction_plan', []))}")
            
            return {
                "success": True,
                "plan": construction_plan,
                "processing_time": plan_time,
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Construction plan generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._fallback_construction_plan(user_prompt)
            }
    
    def generate_material_specifications(
        self,
        design_type: str,
        aesthetic_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Generate advanced material specifications using AI.
        
        Args:
            design_type: Type of design (jewelry, architecture, product, etc.)
            aesthetic_goals: List of aesthetic objectives
            
        Returns:
            Material specifications with PBR parameters
        """
        if not self.enabled:
            return self._fallback_material_specs(design_type)
        
        logger.info("🎨 Generating material specifications...")
        
        system_prompt = self._get_material_spec_system_prompt()
        user_message = f"""
Design Type: {design_type}
Aesthetic Goals: {', '.join(aesthetic_goals)}

Generate professional PBR material specifications that achieve these aesthetic goals.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            materials = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "materials": materials,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Material specification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": self._fallback_material_specs(design_type)
            }
    
    def refine_design(
        self,
        current_design: Dict[str, Any],
        refinement_request: str
    ) -> Dict[str, Any]:
        """
        Refine existing design based on user feedback.
        
        Args:
            current_design: Current design state and construction plan
            refinement_request: User's refinement instructions
            
        Returns:
            Refined construction plan
        """
        if not self.enabled:
            return {"success": False, "error": "AI refinement not available"}
        
        logger.info("✨ Refining design with AI...")
        
        system_prompt = """You are an expert 3D designer specializing in iterative refinement.
Analyze the current design and user's refinement request, then generate an updated
construction plan that incorporates the requested changes while maintaining design integrity.

Return a JSON object with:
- reasoning: Why these changes work
- modified_operations: Updated construction operations
- new_operations: Any new operations to add
- material_updates: Any material changes needed
"""
        
        user_message = f"""
Current Design:
{json.dumps(current_design, indent=2)}

Refinement Request: {refinement_request}

Generate a refined construction plan.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            refinement = json.loads(response.choices[0].message.content)
            
            logger.info("✓ Design refinement completed")
            
            return {
                "success": True,
                "refinement": refinement,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Design refinement failed: {e}")
            return {"success": False, "error": str(e)}
    
    # =========================================================================
    # Advanced Prompt Engineering - System Prompts
    # =========================================================================
    
    def _get_design_analysis_system_prompt(self) -> str:
        """Get the system prompt for design intent analysis."""
        return """You are an expert 3D design analyst with deep knowledge of:
- 3D modeling techniques and workflows
- Material science and PBR rendering
- Design aesthetics and composition
- Manufacturing constraints and feasibility

Your role is to analyze user design requests and extract:
1. Core design intent and objectives
2. Technical requirements and constraints
3. Aesthetic preferences and style
4. Complexity assessment
5. Recommended approach and techniques

Provide comprehensive analysis in JSON format with these keys:
- design_type: Type of object (jewelry, architecture, product, etc.)
- complexity: simple, moderate, complex, or hyper_realistic
- key_features: List of essential features to include
- aesthetic_goals: List of aesthetic objectives
- technical_constraints: Any constraints to consider
- recommended_techniques: Suggested 3D modeling techniques
- material_suggestions: Initial material recommendations
- estimated_operations: Approximate number of construction steps

Be thorough, professional, and actionable in your analysis."""
    
    def _get_construction_plan_system_prompt(self, complexity: ModelComplexity) -> str:
        """Get the system prompt for construction plan generation."""
        return f"""You are a master 3D model architect specializing in {complexity.value} designs.

Your task is to generate precise, actionable construction plans for 3D models.
You have access to these professional operations:

GEOMETRIC OPERATIONS:
- create_shank: Ring bands with parameters (profile_shape, thickness_mm, diameter_mm, taper_factor)
- create_bezel_setting: Bezels with (bezel_height_mm, bezel_thickness_mm, feature_diameter_mm)
- create_prong_setting: Prongs with (prong_count, prong_height_mm, gemstone_diameter_mm)
- create_diamond: Gemstones with (cut_type, carat_weight, position)
- create_primitive: Basic shapes (type, dimensions, position, rotation)
- apply_modifier: Modifiers (type, parameters)
- boolean_operation: CSG operations (operation, target, tool)

ENHANCEMENT OPERATIONS:
- apply_subdivision: Smooth surfaces (levels)
- apply_displacement: Surface detail (pattern_type, strength)
- apply_texture: Surface textures (texture_type, scale, strength)
- add_detail: Fine details (detail_type, density, scale)

MATERIAL OPERATIONS:
- set_material: PBR materials (material_type, color, roughness, metallic, transmission)
- apply_finish: Surface finish (finish_type)

Generate a JSON construction plan with:
- reasoning: Why this approach is optimal
- construction_plan: Array of operations in execution order
- presentation_plan: Rendering and material specifications
- quality_notes: Manufacturing and quality considerations

Each operation must have:
- operation: Operation name
- parameters: Dict of precise parameters
- description: What this step accomplishes

Be precise, professional, and ensure manufacturability."""
    
    def _get_material_spec_system_prompt(self) -> str:
        """Get the system prompt for material specifications."""
        return """You are a PBR material expert specializing in photorealistic 3D rendering.

Generate professional material specifications using physically-based rendering principles.

For each material, specify:
- name: Material name
- base_color: RGB hex color
- metallic: 0.0 to 1.0 (0=dielectric, 1=metal)
- roughness: 0.0 to 1.0 (0=mirror, 1=matte)
- ior: Index of refraction (1.45-2.42)
- transmission: 0.0 to 1.0 (for transparent materials)
- emission: RGB hex color for emissive materials
- emission_strength: Emission intensity

Provide materials in JSON format with these principles:
- Physically accurate IOR values
- Realistic roughness for material types
- Appropriate metallic values
- Professional color selection
- Manufacturing feasibility

Return JSON with:
- primary_material: Main material specification
- accent_materials: List of accent materials
- finish_type: Surface finish description
- rendering_notes: Lighting and rendering suggestions"""
    
    # =========================================================================
    # Prompt Formatting Helpers
    # =========================================================================
    
    def _format_design_analysis_prompt(
        self,
        user_prompt: str,
        context: Optional[Dict] = None
    ) -> str:
        """Format the design analysis prompt."""
        context_str = ""
        if context:
            context_str = f"\n\nExisting Context:\n{json.dumps(context, indent=2)}"
        
        return f"""Design Request: {user_prompt}{context_str}

Analyze this design request comprehensively and provide detailed insights
for optimal 3D model generation."""
    
    def _format_construction_plan_prompt(
        self,
        user_prompt: str,
        design_analysis: Dict[str, Any],
        complexity: ModelComplexity
    ) -> str:
        """Format the construction plan prompt."""
        analysis = design_analysis.get('analysis', {})
        
        return f"""Design Request: {user_prompt}

Design Analysis:
{json.dumps(analysis, indent=2)}

Target Complexity: {complexity.value}

Generate a precise, step-by-step construction plan that:
1. Implements the core design intent
2. Achieves the aesthetic goals
3. Respects technical constraints
4. Uses appropriate complexity level
5. Ensures manufacturability

Provide complete construction and presentation plans."""
    
    # =========================================================================
    # Fallback Methods (when OpenAI not available)
    # =========================================================================
    
    def _fallback_design_analysis(self, user_prompt: str) -> Dict[str, Any]:
        """Fallback design analysis without AI."""
        logger.info("Using fallback design analysis")
        
        # Simple keyword-based analysis
        prompt_lower = user_prompt.lower()
        
        complexity = ModelComplexity.SIMPLE
        if any(word in prompt_lower for word in ['complex', 'intricate', 'detailed', 'ornate']):
            complexity = ModelComplexity.COMPLEX
        elif any(word in prompt_lower for word in ['hyper', 'realistic', 'photorealistic']):
            complexity = ModelComplexity.HYPER_REALISTIC
        elif any(word in prompt_lower for word in ['moderate', 'medium', 'standard']):
            complexity = ModelComplexity.MODERATE
        
        design_type = "jewelry"
        if any(word in prompt_lower for word in ['building', 'house', 'structure']):
            design_type = "architecture"
        elif any(word in prompt_lower for word in ['product', 'device', 'tool']):
            design_type = "product"
        
        return {
            "design_type": design_type,
            "complexity": complexity.value,
            "key_features": ["primary_form", "surface_detail"],
            "aesthetic_goals": ["professional", "clean"],
            "technical_constraints": ["standard_manufacturing"],
            "recommended_techniques": ["geometric_primitives", "modifiers"],
            "material_suggestions": ["metal", "glass"],
            "estimated_operations": 3
        }
    
    def _fallback_construction_plan(self, user_prompt: str) -> Dict[str, Any]:
        """Fallback construction plan without AI."""
        logger.info("Using fallback construction plan")
        
        return {
            "reasoning": "Basic construction plan generated without AI",
            "construction_plan": [
                {
                    "operation": "create_primitive",
                    "parameters": {
                        "type": "torus",
                        "major_radius": 0.018,
                        "minor_radius": 0.002,
                        "position": [0, 0, 0]
                    },
                    "description": "Create base ring form"
                }
            ],
            "presentation_plan": {
                "material_style": "Polished Metal",
                "render_environment": "Studio",
                "camera_effects": {"use_depth_of_field": False}
            }
        }
    
    def _fallback_material_specs(self, design_type: str) -> Dict[str, Any]:
        """Fallback material specifications without AI."""
        logger.info("Using fallback material specifications")
        
        if design_type == "jewelry":
            return {
                "primary_material": {
                    "name": "18K Gold",
                    "base_color": "#FFD700",
                    "metallic": 1.0,
                    "roughness": 0.1,
                    "ior": 0.47
                },
                "finish_type": "Polished"
            }
        else:
            return {
                "primary_material": {
                    "name": "Brushed Metal",
                    "base_color": "#CCCCCC",
                    "metallic": 1.0,
                    "roughness": 0.3,
                    "ior": 1.5
                },
                "finish_type": "Brushed"
            }


# Module-level convenience function
def create_ai_3d_generator(api_key: Optional[str] = None) -> AI3DModelGenerator:
    """
    Create and configure an AI 3D Model Generator instance.
    
    Args:
        api_key: Optional OpenAI API key
        
    Returns:
        Configured AI3DModelGenerator instance
    """
    return AI3DModelGenerator(api_key=api_key)
