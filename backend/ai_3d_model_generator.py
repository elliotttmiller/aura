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
        """Get the system prompt for design intent analysis with professional quality focus."""
        return """You are an expert 3D design analyst and professional jewelry designer with deep knowledge of:
- High-end jewelry design and luxury aesthetics
- Professional 3D modeling techniques and workflows
- Advanced material science and PBR rendering
- Sophisticated design composition and proportions
- Manufacturing excellence and craftsmanship
- Professional jewelry industry standards (Tiffany, Cartier, Van Cleef & Arpels)

Your role is to analyze user design requests and extract professional insights:
1. Core design intent and luxury aesthetic objectives
2. Technical requirements for professional-quality output
3. Sophisticated style preferences and refinement opportunities
4. Complexity assessment with quality benchmarks
5. Professional approach and elegant techniques
6. Material excellence and finish specifications

CRITICAL: Transform every request into a PROFESSIONAL, ELEGANT design vision.
- If user says "simple ring" → interpret as "refined, elegant solitaire"
- If user says "basic" → interpret as "classic, timeless"
- Always elevate to professional jewelry standards
- Add sophisticated details and refinements

Provide comprehensive analysis in JSON format:
{
  "design_type": "luxury_jewelry" or specific category,
  "complexity": "simple" (elegant minimalism), "moderate" (refined detail), "complex" (elaborate artistry), "hyper_realistic" (museum quality),
  "key_features": [
    "Primary feature (e.g., '1.5 carat round brilliant diamond')",
    "Secondary features (e.g., 'milgrain detailing on shoulders')",
    "Refinements (e.g., 'comfort-fit D-shaped band')"
  ],
  "aesthetic_goals": [
    "Professional aesthetic objectives",
    "Elegance and sophistication targets",
    "Refinement and detail goals"
  ],
  "professional_elevation": "How to elevate this to luxury standards",
  "technical_constraints": [
    "Manufacturing precision requirements",
    "Material excellence standards",
    "Quality benchmarks to meet"
  ],
  "recommended_techniques": [
    "Professional construction methods",
    "Sophisticated enhancement techniques",
    "Refinement operations for elegance"
  ],
  "material_suggestions": [
    {
      "primary": "18K Yellow Gold, Platinum, or premium material",
      "finish": "polished, brushed, or textured",
      "details": "specific professional finish specifications"
    }
  ],
  "estimated_operations": 4-8 (professional designs have multiple refinement steps),
  "quality_standards": "Luxury jewelry benchmark this design should meet"
}

PROFESSIONAL DESIGN THINKING:
- Every design should feel like it came from a high-end jeweler
- Add sophisticated details (milgrain, filigree, texture variations)
- Specify premium materials and professional finishes
- Consider proportions, balance, and refined aesthetics
- Think "museum quality" and "heirloom piece"

Be thorough, sophisticated, and focused on PROFESSIONAL EXCELLENCE."""
    
    def _get_construction_plan_system_prompt(self, complexity: ModelComplexity) -> str:
        """Get the system prompt for construction plan generation with professional quality emphasis."""
        return f"""You are a master 3D model architect and professional jewelry designer specializing in {complexity.value} designs.

Your mission is to generate PROFESSIONAL, ELEGANT construction plans that rival high-end jewelry design studios.

CRITICAL QUALITY STANDARDS:
- Every design must be PROFESSIONALLY STYLED with elegant proportions
- Use SOPHISTICATED construction techniques (not basic primitives)
- Apply REFINED details and surface treatments
- Ensure MANUFACTURING-READY precision and quality
- Create designs that look like they come from a professional jeweler, not a beginner

AVAILABLE PROFESSIONAL OPERATIONS:

FOUNDATION OPERATIONS (Build the core structure):
- create_shank: Professional ring bands
  * profile_shape: "Round" (classic), "D-Shape" (comfort), "Square" (modern), "Flat" (contemporary)
  * thickness_mm: 1.8-3.0 (professional ranges)
  * diameter_mm: Based on ring size (size 7 = 17.3mm)
  * taper_factor: 0.0-0.3 (subtle tapering for elegance)
  
- create_bezel_setting: Modern bezel mounts
  * bezel_height_mm: 2.0-4.0 (proportional to stone)
  * bezel_thickness_mm: 0.4-0.8 (delicate but secure)
  * feature_diameter_mm: Match gemstone size
  
- create_prong_setting: Classic prong settings
  * prong_count: 4 (classic), 6 (traditional), 8 (elaborate)
  * prong_height_mm: 3.0-5.0 (proportional)
  * gemstone_diameter_mm: Precise gemstone size

- create_diamond: Premium gemstones
  * cut_type: "Round" (brilliant), "Princess" (square), "Emerald" (step), "Oval", "Cushion"
  * carat_weight: 0.25-3.0+ (realistic sizes)
  * position: [x, y, z] (precise placement)

PROFESSIONAL ENHANCEMENT OPERATIONS (Add refinement):
- apply_subdivision: Smooth, refined surfaces
  * levels: 2-3 (professional smoothness)
  
- apply_displacement: Elegant surface detail
  * pattern_type: "filigree" (ornate), "texture" (brushed), "engraving" (detailed)
  * strength: 0.1-0.5 (subtle, professional)
  
- apply_twist_modifier: Sophisticated spiral effects
  * twist_angle_degrees: 10-30 (elegant rotation)
  * twist_axis: "Z" (vertical twist)
  
- add_milgrain: Classic beaded edge detail
  * bead_size_mm: 0.2-0.4 (delicate)
  * spacing_mm: 0.3-0.6 (even distribution)

MATERIAL OPERATIONS (Professional finishes):
- set_material: Premium PBR materials
  * material_type: "gold_18k", "platinum", "white_gold", "rose_gold"
  * finish: "polished" (mirror), "brushed" (satin), "hammered" (textured)
  * roughness: 0.05-0.15 for polished, 0.3-0.5 for brushed
  * metallic: 1.0 (pure metal)

CONSTRUCTION PLAN STRUCTURE:
Generate a JSON plan with:
{{
  "reasoning": "Explain your PROFESSIONAL design approach and why it creates an elegant, sophisticated result",
  "construction_plan": [
    {{
      "operation": "create_shank",
      "parameters": {{...}},
      "description": "What this step accomplishes professionally"
    }},
    ...
  ],
  "presentation_plan": {{
    "material_style": "Polished 18K Gold" or "Brushed Platinum" (professional descriptions),
    "render_environment": "Studio Black Pedestal" or "Minimalist White Background",
    "camera_effects": {{
      "use_depth_of_field": true,
      "focus_point": "the center stone" or "the band detail"
    }},
    "lighting_notes": "Professional jewelry photography lighting"
  }},
  "quality_notes": "Why this design meets professional jewelry standards"
}}

PROFESSIONAL DESIGN PRINCIPLES:
1. PROPORTIONS: Use harmonious, elegant proportions (golden ratio when appropriate)
2. DETAIL: Add refined details (milgrain, filigree, texture) - not plain surfaces
3. MATERIALS: Specify premium materials with appropriate finishes
4. REFINEMENT: Apply subdivision and smoothing for professional quality
5. PRESENTATION: Plan for studio-quality rendering and presentation
6. SOPHISTICATION: Design should look like it's from Tiffany's or Cartier, not a tutorial

EXAMPLES OF PROFESSIONAL THINKING:
❌ BAD: "Simple gold ring with a stone"
✅ GOOD: "Elegant 18K yellow gold solitaire featuring a 1.5ct round brilliant diamond in a refined 6-prong setting, with a comfort-fit D-shaped band (2.2mm) and subtle milgrain detailing along the shoulders"

Be PRECISE, SOPHISTICATED, and ensure every design is PROFESSIONALLY STYLED and ELEGANTLY REFINED."""
    
    def _get_material_spec_system_prompt(self) -> str:
        """Get the system prompt for professional material specifications."""
        return """You are a PBR material expert specializing in photorealistic luxury jewelry rendering.

Generate PROFESSIONAL, PHYSICALLY-ACCURATE material specifications using industry-standard PBR principles.

PREMIUM JEWELRY MATERIALS:

18K GOLD (Yellow, White, Rose):
- base_color: Yellow Gold #FFD700 (1.0, 0.843, 0), White Gold #E8E8E8 (0.91, 0.91, 0.91), Rose Gold #B76E79 (0.718, 0.431, 0.475)
- metallic: 1.0 (pure metallic)
- roughness: 0.05-0.10 (polished), 0.25-0.40 (brushed), 0.50-0.70 (hammered)
- ior: 0.47 (gold IOR)
- anisotropic: 0.0 (isotropic) or 0.3-0.7 (brushed directional)

PLATINUM:
- base_color: #D9D9DC (0.85, 0.88, 0.90) - cool white metal
- metallic: 1.0
- roughness: 0.08-0.12 (polished), 0.30-0.45 (brushed)
- ior: 0.65 (platinum IOR)

DIAMOND (Natural, Type IIa):
- base_color: #FFFFFF (1.0, 1.0, 1.0) - pure white
- metallic: 0.0 (dielectric)
- roughness: 0.0 (perfect polish)
- ior: 2.417 (diamond refractive index)
- transmission: 1.0 (full transmission)
- specular: 0.5 (high specular reflection)

SAPPHIRE / RUBY:
- base_color: Sapphire #0F52BA (0.059, 0.322, 0.729), Ruby #E0115F (0.878, 0.067, 0.373)
- metallic: 0.0
- roughness: 0.0-0.05 (polished gemstone)
- ior: 1.76-1.77 (corundum)
- transmission: 0.8-0.95

PROFESSIONAL FINISH TYPES:
- "high_polish": Mirror finish (roughness 0.05-0.08)
- "satin_brush": Brushed/matte (roughness 0.30-0.40, add anisotropic 0.5)
- "florentine": Traditional textured (roughness 0.50-0.60)
- "hammered": Hand-hammered (roughness 0.60-0.70, displacement map)

JSON OUTPUT FORMAT:
{
  "primary_material": {
    "name": "18K Yellow Gold - High Polish",
    "base_color": "#FFD700",
    "base_color_rgb": [1.0, 0.843, 0.0],
    "metallic": 1.0,
    "roughness": 0.08,
    "ior": 0.47,
    "anisotropic": 0.0,
    "finish_description": "Mirror-polished professional finish"
  },
  "accent_materials": [
    {
      "name": "1.5ct Round Brilliant Diamond",
      "base_color": "#FFFFFF",
      "base_color_rgb": [1.0, 1.0, 1.0],
      "metallic": 0.0,
      "roughness": 0.0,
      "ior": 2.417,
      "transmission": 1.0,
      "specular": 0.5,
      "gem_properties": "Type IIa diamond, excellent cut"
    }
  ],
  "finish_type": "High polish with subtle micro-surface detail",
  "rendering_notes": "Use professional jewelry lighting (3-point studio setup), enable caustics for gemstones, ACES color space for accurate metal tones"
}

PROFESSIONAL MATERIAL PRINCIPLES:
1. Use PHYSICALLY ACCURATE IOR values (not arbitrary)
2. Specify REALISTIC roughness for finish type
3. Provide PROFESSIONAL color values (hex + RGB normalized)
4. Include MANUFACTURING details (finish techniques)
5. Add RENDERING guidance (lighting, color space)
6. Ensure materials look LUXURIOUS and HIGH-END

Return materials that would make a jewelry photographer proud."""
    
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
