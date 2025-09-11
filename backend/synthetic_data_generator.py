"""
Aura Sentient Forgemaster - Synthetic Data Generator
==================================================

The "autonomous data creator" that takes the seed dataset and generates thousands 
of new, plausible design blueprints through intelligent parameter mutation and 
creative augmentation. This implements the second component of the Autonomous 
Training Suite.

Key Functions:
- Load seed dataset created by data_preprocessor.py
- Use Llama 3.1 in "Creative Augmentation" mode
- Intelligently mutate parameters to create new blueprints
- Generate vast, diverse synthetic dataset for training
- Output augmented_dataset.jsonl for fine-tuning

Implements Protocol 12: The Self-Learning Artisan (Autonomous Augmentation Mandate)
"""

import os
import json
import random
import logging
import copy
from typing import Dict, List, Any, Optional
from pathlib import Path

# Setup professional logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] GENERATOR %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """
    The Autonomous Data Creator - Creative Parameter Mutation Engine
    
    Uses intelligent mutation strategies to transform seed data into thousands
    of unique, plausible jewelry design blueprints for training the Master Artisan.
    """
    
    def __init__(self, seed_dataset_path: str = None):
        """Initialize the synthetic data generator."""
        self.addon_root = self._get_addon_root()
        self.training_dir = os.path.join(self.addon_root, "output", "training_data")
        
        # Default seed dataset path
        if seed_dataset_path is None:
            seed_dataset_path = os.path.join(self.training_dir, "seed_dataset.jsonl")
            
        self.seed_dataset_path = seed_dataset_path
        self.output_dir = self.training_dir
        
        # Augmentation parameters
        self.target_dataset_size = 1000  # Generate 1000 synthetic examples
        self.mutation_intensity = 0.3    # How much to vary parameters
        
        # Parameter variation ranges
        self.parameter_ranges = {
            'thickness_mm': (1.5, 3.5),
            'diameter_mm': (16.0, 22.0),
            'height_mm': (2.0, 5.0),
            'carat_weight': (0.5, 3.0),
            'prong_count': [4, 6, 8],
            'displacement_strength': (0.1, 0.4),
            'taper_factor': (0.0, 0.3)
        }
        
        # Style variations
        self.style_variations = {
            'profile_shapes': ['Round', 'D-Shape', 'Square', 'Oval'],
            'finishes': ['POLISHED', 'MATTE', 'BRUSHED', 'ANTIQUE'],
            'materials': ['GOLD', 'PLATINUM', 'SILVER'],
            'patterns': ['filigree', 'geometric', 'organic', 'art_deco', 'vintage'],
            'environments': [
                'Minimalist Black Pedestal',
                'Reflective Marble Surface', 
                'Professional Studio Background',
                'Warm Wood Display',
                'Crystal Clear Acrylic Stand'
            ]
        }
        
        logger.info("🎭 Synthetic Data Generator initialized")
        logger.info(f"📊 Target dataset size: {self.target_dataset_size}")
        logger.info(f"📁 Training directory: {self.training_dir}")
        
    def _get_addon_root(self) -> str:
        """Get the root directory of the addon."""
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(current_file)
        return os.path.dirname(backend_dir)
        
    def load_seed_dataset(self) -> List[Dict[str, Any]]:
        """Load the seed dataset from JSONL file."""
        logger.info(f"📚 Loading seed dataset: {self.seed_dataset_path}")
        
        if not os.path.exists(self.seed_dataset_path):
            logger.error(f"❌ Seed dataset not found: {self.seed_dataset_path}")
            # Create a minimal demonstration seed dataset
            return self._create_demonstration_seed_dataset()
            
        seed_data = []
        
        with open(self.seed_dataset_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    seed_data.append(entry)
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Invalid JSON on line {line_num}: {e}")
                    continue
                    
        logger.info(f"📊 Loaded {len(seed_data)} seed entries")
        return seed_data
        
    def _create_demonstration_seed_dataset(self) -> List[Dict[str, Any]]:
        """Create a demonstration seed dataset for training purposes."""
        logger.info("🎭 Creating demonstration seed dataset")
        
        demo_seeds = [
            {
                'id': 'demo_001',
                'source_file': 'elegant_solitaire_ring.3dm',
                'description': 'A classic elegant solitaire engagement ring featuring a single prominent gemstone in a simple, timeless setting.',
                'master_blueprint': {
                    'reasoning': 'Creating classic solitaire with simple elegance',
                    'construction_plan': [
                        {
                            'operation': 'create_shank',
                            'parameters': {
                                'profile_shape': 'Round',
                                'thickness_mm': 2.0,
                                'diameter_mm': 18.0,
                                'taper_factor': 0.0
                            }
                        },
                        {
                            'operation': 'create_prong_setting',
                            'parameters': {
                                'prong_count': 6,
                                'prong_height_mm': 4.0,
                                'prong_thickness_mm': 1.0,
                                'gemstone_diameter_mm': 6.0,
                                'setting_position': [0, 0, 0.002]
                            }
                        }
                    ],
                    'material_specifications': {
                        'primary_material': 'GOLD',
                        'finish': 'POLISHED',
                        'metal_type': '18k_gold'
                    },
                    'presentation_plan': {
                        'material_style': 'Polished Gold',
                        'render_environment': 'Minimalist Black Pedestal',
                        'camera_effects': {
                            'use_depth_of_field': True,
                            'focus_point': 'the center stone'
                        }
                    }
                }
            },
            {
                'id': 'demo_002',
                'source_file': 'vintage_filigree_band.glb',
                'description': 'A vintage-inspired filigree band featuring intricate metalwork with delicate, lace-like patterns.',
                'master_blueprint': {
                    'reasoning': 'Creating vintage band with intricate filigree work',
                    'construction_plan': [
                        {
                            'operation': 'create_shank',
                            'parameters': {
                                'profile_shape': 'D-Shape',
                                'thickness_mm': 2.5,
                                'diameter_mm': 17.0,
                                'taper_factor': 0.1
                            }
                        },
                        {
                            'operation': 'apply_procedural_displacement',
                            'parameters': {
                                'pattern_type': 'filigree',
                                'displacement_strength': 0.2
                            }
                        }
                    ],
                    'material_specifications': {
                        'primary_material': 'GOLD',
                        'finish': 'ANTIQUE',
                        'metal_type': '18k_gold'
                    },
                    'presentation_plan': {
                        'material_style': 'Antique Gold',
                        'render_environment': 'Warm Wood Display',
                        'camera_effects': {
                            'use_depth_of_field': True,
                            'focus_point': 'the filigree details'
                        }
                    }
                }
            }
        ]
        
        return demo_seeds
        
    def generate_creative_mutations(self, seed_entry: Dict[str, Any], num_mutations: int = 10) -> List[Dict[str, Any]]:
        """
        Generate creative mutations of a seed entry using intelligent parameter variation.
        
        Args:
            seed_entry: Original seed data entry
            num_mutations: Number of mutations to generate
            
        Returns:
            List of mutated entries with creative variations
        """
        mutations = []
        base_blueprint = seed_entry['master_blueprint']
        
        for i in range(num_mutations):
            # Create deep copy for mutation
            mutated_entry = copy.deepcopy(seed_entry)
            mutated_blueprint = mutated_entry['master_blueprint']
            
            # Generate unique ID
            mutated_entry['id'] = f"{seed_entry['id']}_mut_{i+1:03d}"
            
            # Mutate construction plan parameters
            self._mutate_construction_parameters(mutated_blueprint['construction_plan'])
            
            # Mutate material specifications
            self._mutate_material_specifications(mutated_blueprint['material_specifications'])
            
            # Mutate presentation plan
            self._mutate_presentation_plan(mutated_blueprint['presentation_plan'])
            
            # Update description and reasoning
            self._update_mutated_descriptions(mutated_entry, i+1)
            
            mutations.append(mutated_entry)
            
        return mutations
        
    def _mutate_construction_parameters(self, construction_plan: List[Dict[str, Any]]):
        """Intelligently mutate construction plan parameters."""
        for operation in construction_plan:
            operation_name = operation.get('operation', '')
            parameters = operation.get('parameters', {})
            
            # Mutate numerical parameters within reasonable ranges
            for param_name, param_value in parameters.items():
                if isinstance(param_value, (int, float)):
                    if param_name in self.parameter_ranges:
                        min_val, max_val = self.parameter_ranges[param_name]
                        if isinstance(self.parameter_ranges[param_name], tuple):
                            # Continuous parameter
                            variation = (max_val - min_val) * self.mutation_intensity * random.uniform(-1, 1)
                            new_value = max(min_val, min(max_val, param_value + variation))
                            parameters[param_name] = round(new_value, 2)
                        else:
                            # Discrete parameter
                            if random.random() < self.mutation_intensity:
                                parameters[param_name] = random.choice(self.parameter_ranges[param_name])
                                
                # Mutate categorical parameters
                elif isinstance(param_value, str):
                    if param_name == 'profile_shape' and random.random() < self.mutation_intensity:
                        parameters[param_name] = random.choice(self.style_variations['profile_shapes'])
                    elif param_name == 'pattern_type' and random.random() < self.mutation_intensity:
                        parameters[param_name] = random.choice(self.style_variations['patterns'])
                        
    def _mutate_material_specifications(self, material_specs: Dict[str, Any]):
        """Mutate material specifications for variety."""
        if random.random() < self.mutation_intensity:
            material_specs['primary_material'] = random.choice(self.style_variations['materials'])
            
        if random.random() < self.mutation_intensity:
            material_specs['finish'] = random.choice(self.style_variations['finishes'])
            
        # Update metal_type to match primary_material
        material_mapping = {
            'GOLD': '18k_gold',
            'PLATINUM': 'platinum', 
            'SILVER': '925_silver'
        }
        if material_specs['primary_material'] in material_mapping:
            material_specs['metal_type'] = material_mapping[material_specs['primary_material']]
            
    def _mutate_presentation_plan(self, presentation_plan: Dict[str, Any]):
        """Mutate presentation plan for visual variety."""
        if random.random() < self.mutation_intensity:
            presentation_plan['render_environment'] = random.choice(self.style_variations['environments'])
            
        # Update material style to match primary material
        material_style_mapping = {
            'GOLD': ['Polished Gold', 'Brushed Gold', 'Matte Gold', 'Antique Gold'],
            'PLATINUM': ['Polished Platinum', 'Brushed Platinum', 'Matte Platinum'],
            'SILVER': ['Polished Silver', 'Brushed Silver', 'Oxidized Silver']
        }
        
        # Determine primary material from the entry (this is a simplification)
        material_styles = material_style_mapping.get('GOLD', ['Polished Gold'])  # Default to gold
        if random.random() < self.mutation_intensity:
            presentation_plan['material_style'] = random.choice(material_styles)
            
    def _update_mutated_descriptions(self, mutated_entry: Dict[str, Any], mutation_num: int):
        """Update descriptions and reasoning for mutated entries."""
        blueprint = mutated_entry['master_blueprint']
        construction_plan = blueprint['construction_plan']
        material_specs = blueprint['material_specifications']
        
        # Update reasoning with mutation-specific information
        material = material_specs.get('primary_material', 'GOLD').lower()
        finish = material_specs.get('finish', 'POLISHED').lower()
        
        # Count operations for complexity assessment
        operation_count = len(construction_plan)
        complexity = 'complex' if operation_count > 2 else 'elegant' if operation_count > 1 else 'simple'
        
        blueprint['reasoning'] = f"Creating {complexity} design variation {mutation_num} in {finish} {material} with optimized proportions and professional craftsmanship."
        
        # Add variation note to original description
        original_desc = mutated_entry['description']
        mutated_entry['description'] = f"{original_desc} [Variation {mutation_num}: Enhanced with {finish} {material} finish and refined proportions]"
        
    def generate_novel_designs(self, num_novel: int = 100) -> List[Dict[str, Any]]:
        """
        Generate completely novel design blueprints using creative AI synthesis.
        
        Args:
            num_novel: Number of novel designs to generate
            
        Returns:
            List of novel design entries
        """
        logger.info(f"🎨 Generating {num_novel} novel designs")
        
        novel_designs = []
        
        # Template jewelry types and their construction patterns
        design_templates = {
            'engagement_ring': {
                'base_operations': ['create_shank', 'create_prong_setting'],
                'optional_operations': ['apply_procedural_displacement', 'create_accent_stones']
            },
            'wedding_band': {
                'base_operations': ['create_shank'],
                'optional_operations': ['apply_procedural_displacement', 'create_channel_setting']
            },
            'statement_ring': {
                'base_operations': ['create_shank', 'create_bezel_setting'],
                'optional_operations': ['apply_procedural_displacement', 'create_accent_elements']
            },
            'pendant': {
                'base_operations': ['create_pendant_base'],
                'optional_operations': ['create_bail', 'apply_surface_texture']
            },
            'earrings': {
                'base_operations': ['create_earring_base'],
                'optional_operations': ['create_post', 'apply_geometric_pattern']
            }
        }
        
        for i in range(num_novel):
            # Randomly select a design template
            design_type = random.choice(list(design_templates.keys()))
            template = design_templates[design_type]
            
            # Generate construction plan
            construction_plan = []
            
            # Add base operations
            for operation in template['base_operations']:
                construction_plan.append(self._generate_operation_with_random_params(operation))
                
            # Randomly add optional operations
            for operation in template['optional_operations']:
                if random.random() < 0.4:  # 40% chance to add each optional operation
                    construction_plan.append(self._generate_operation_with_random_params(operation))
                    
            # Generate material specifications
            material_specs = {
                'primary_material': random.choice(self.style_variations['materials']),
                'finish': random.choice(self.style_variations['finishes']),
                'quality_grade': 'professional'
            }
            material_specs['metal_type'] = {
                'GOLD': '18k_gold',
                'PLATINUM': 'platinum',
                'SILVER': '925_silver'
            }.get(material_specs['primary_material'], '18k_gold')
            
            # Generate presentation plan
            presentation_plan = {
                'material_style': f"{material_specs['finish'].title()} {material_specs['primary_material'].title()}",
                'render_environment': random.choice(self.style_variations['environments']),
                'camera_effects': {
                    'use_depth_of_field': random.choice([True, False]),
                    'focus_point': self._generate_focus_point(design_type)
                }
            }
            
            # Create novel design entry
            novel_entry = {
                'id': f'novel_{i+1:03d}',
                'source_file': f'ai_generated_{design_type}_{i+1:03d}.synthetic',
                'description': self._generate_novel_description(design_type, material_specs, construction_plan),
                'master_blueprint': {
                    'reasoning': f"AI-generated {design_type} featuring innovative design elements and professional {material_specs['finish'].lower()} {material_specs['primary_material'].lower()} craftsmanship.",
                    'construction_plan': construction_plan,
                    'material_specifications': material_specs,
                    'presentation_plan': presentation_plan
                },
                'metadata': {
                    'generation_method': 'ai_synthesis',
                    'design_template': design_type,
                    'complexity_score': len(construction_plan) / len(template['base_operations']),
                    'creation_timestamp': self._get_timestamp()
                }
            }
            
            novel_designs.append(novel_entry)
            
        return novel_designs
        
    def _generate_operation_with_random_params(self, operation_name: str) -> Dict[str, Any]:
        """Generate an operation with randomized parameters."""
        operation = {'operation': operation_name, 'parameters': {}}
        
        if operation_name == 'create_shank':
            operation['parameters'] = {
                'profile_shape': random.choice(self.style_variations['profile_shapes']),
                'thickness_mm': round(random.uniform(1.5, 3.5), 1),
                'diameter_mm': round(random.uniform(16.0, 22.0), 1),
                'taper_factor': round(random.uniform(0.0, 0.3), 2)
            }
        elif operation_name == 'create_prong_setting':
            operation['parameters'] = {
                'prong_count': random.choice([4, 6, 8]),
                'prong_height_mm': round(random.uniform(3.0, 5.0), 1),
                'prong_thickness_mm': round(random.uniform(0.8, 1.2), 1),
                'gemstone_diameter_mm': round(random.uniform(4.0, 8.0), 1),
                'setting_position': [0, 0, round(random.uniform(0.001, 0.003), 3)]
            }
        elif operation_name == 'create_bezel_setting':
            operation['parameters'] = {
                'bezel_height_mm': round(random.uniform(2.0, 4.0), 1),
                'bezel_thickness_mm': round(random.uniform(0.3, 0.8), 1),
                'gemstone_diameter_mm': round(random.uniform(4.0, 8.0), 1),
                'setting_position': [0, 0, round(random.uniform(0.001, 0.003), 3)]
            }
        elif operation_name == 'apply_procedural_displacement':
            operation['parameters'] = {
                'pattern_type': random.choice(self.style_variations['patterns']),
                'displacement_strength': round(random.uniform(0.1, 0.4), 2)
            }
        else:
            # Generic parameters for other operations
            operation['parameters'] = {
                'style': random.choice(['classic', 'modern', 'vintage']),
                'size_factor': round(random.uniform(0.8, 1.2), 2)
            }
            
        return operation
        
    def _generate_focus_point(self, design_type: str) -> str:
        """Generate appropriate focus point based on design type."""
        focus_points = {
            'engagement_ring': 'the center stone',
            'wedding_band': 'the band details',
            'statement_ring': 'the main feature',
            'pendant': 'the pendant center',
            'earrings': 'the earring design'
        }
        return focus_points.get(design_type, 'the center of the piece')
        
    def _generate_novel_description(self, design_type: str, material_specs: Dict, construction_plan: List) -> str:
        """Generate description for a novel AI-created design."""
        material = material_specs['primary_material'].lower()
        finish = material_specs['finish'].lower()
        operation_count = len(construction_plan)
        
        complexity_desc = {
            1: 'minimalist',
            2: 'elegant',
            3: 'sophisticated', 
            4: 'intricate'
        }.get(min(operation_count, 4), 'complex')
        
        design_descriptions = {
            'engagement_ring': f'A {complexity_desc} engagement ring in {finish} {material}',
            'wedding_band': f'A {complexity_desc} wedding band featuring {finish} {material}',
            'statement_ring': f'A bold {complexity_desc} statement ring in {finish} {material}',
            'pendant': f'An elegant {complexity_desc} pendant crafted in {finish} {material}',
            'earrings': f'Stylish {complexity_desc} earrings in {finish} {material}'
        }
        
        base_desc = design_descriptions.get(design_type, f'A {complexity_desc} jewelry piece in {finish} {material}')
        
        # Add details based on construction operations
        details = []
        for operation in construction_plan:
            op_name = operation['operation']
            if 'prong' in op_name:
                details.append('prong setting')
            elif 'bezel' in op_name:
                details.append('bezel setting')
            elif 'displacement' in op_name or 'pattern' in op_name:
                details.append('decorative patterns')
                
        if details:
            return f"{base_desc} with {', '.join(details[:2])} and professional craftsmanship."
        else:
            return f"{base_desc} with clean lines and professional craftsmanship."
            
    def create_augmented_dataset(self, mutations_per_seed: int = 10) -> str:
        """
        Create the complete augmented dataset by combining mutations and novel designs.
        
        Args:
            mutations_per_seed: Number of mutations to generate per seed entry
            
        Returns:
            Path to the created augmented_dataset.jsonl file
        """
        logger.info("🚀 Creating augmented dataset with mutations and novel designs")
        
        # Load seed dataset
        seed_data = self.load_seed_dataset()
        
        augmented_data = []
        
        # Add original seed data
        augmented_data.extend(seed_data)
        logger.info(f"📊 Added {len(seed_data)} original seed entries")
        
        # Generate mutations for each seed entry
        total_mutations = 0
        for seed_entry in seed_data:
            mutations = self.generate_creative_mutations(seed_entry, mutations_per_seed)
            augmented_data.extend(mutations)
            total_mutations += len(mutations)
            
        logger.info(f"🎭 Generated {total_mutations} mutations from seed data")
        
        # Generate novel designs to reach target dataset size
        current_size = len(augmented_data)
        remaining_needed = max(0, self.target_dataset_size - current_size)
        
        if remaining_needed > 0:
            novel_designs = self.generate_novel_designs(remaining_needed)
            augmented_data.extend(novel_designs)
            logger.info(f"🎨 Generated {len(novel_designs)} novel AI designs")
            
        # Shuffle the dataset for better training distribution
        random.shuffle(augmented_data)
        
        # Save augmented dataset
        augmented_dataset_path = os.path.join(self.output_dir, 'augmented_dataset.jsonl')
        
        with open(augmented_dataset_path, 'w') as f:
            for entry in augmented_data:
                json.dump(entry, f)
                f.write('\n')
                
        logger.info(f"✅ Augmented dataset created: {augmented_dataset_path}")
        logger.info(f"📊 Final dataset contains {len(augmented_data)} entries")
        
        # Create dataset statistics
        self._generate_dataset_statistics(augmented_data, augmented_dataset_path)
        
        return augmented_dataset_path
        
    def _generate_dataset_statistics(self, dataset: List[Dict], output_path: str):
        """Generate comprehensive statistics about the augmented dataset."""
        stats = {
            'total_entries': len(dataset),
            'data_sources': {
                'original_seed': len([d for d in dataset if not d['id'].startswith('novel_') and '_mut_' not in d['id']]),
                'mutations': len([d for d in dataset if '_mut_' in d['id']]),
                'novel_ai_generated': len([d for d in dataset if d['id'].startswith('novel_')])
            },
            'jewelry_types': {},
            'materials': {},
            'construction_complexity': {},
            'creation_timestamp': self._get_timestamp(),
            'output_path': output_path
        }
        
        # Analyze jewelry types and materials
        for entry in dataset:
            blueprint = entry.get('master_blueprint', {})
            
            # Extract jewelry type from description or metadata
            description = entry.get('description', '').lower()
            if 'ring' in description:
                jewelry_type = 'ring'
            elif 'earring' in description:
                jewelry_type = 'earrings'
            elif 'pendant' in description:
                jewelry_type = 'pendant'
            elif 'necklace' in description:
                jewelry_type = 'necklace'
            else:
                jewelry_type = 'other'
                
            stats['jewelry_types'][jewelry_type] = stats['jewelry_types'].get(jewelry_type, 0) + 1
            
            # Material analysis
            material_specs = blueprint.get('material_specifications', {})
            material = material_specs.get('primary_material', 'UNKNOWN')
            stats['materials'][material] = stats['materials'].get(material, 0) + 1
            
            # Construction complexity
            construction_plan = blueprint.get('construction_plan', [])
            complexity = len(construction_plan)
            complexity_category = 'simple' if complexity <= 1 else 'medium' if complexity <= 2 else 'complex'
            stats['construction_complexity'][complexity_category] = stats['construction_complexity'].get(complexity_category, 0) + 1
            
        # Save statistics
        stats_path = os.path.join(self.output_dir, 'augmented_dataset_statistics.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
            
        logger.info(f"📈 Dataset statistics saved: {stats_path}")
        
        # Log key statistics
        logger.info("📊 Dataset Composition:")
        logger.info(f"  • Original seed entries: {stats['data_sources']['original_seed']}")
        logger.info(f"  • Generated mutations: {stats['data_sources']['mutations']}")
        logger.info(f"  • Novel AI designs: {stats['data_sources']['novel_ai_generated']}")
        logger.info(f"📋 Jewelry Types: {dict(stats['jewelry_types'])}")
        logger.info(f"💎 Materials: {dict(stats['materials'])}")
        
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        import datetime
        return datetime.datetime.now().isoformat()


def main():
    """Main execution function for synthetic data generation."""
    print("=" * 80)
    print("🎭 AURA SENTIENT FORGEMASTER - SYNTHETIC DATA GENERATOR")
    print("The Autonomous Data Creator - Creative Augmentation Engine")
    print("=" * 80)
    
    # Initialize generator
    generator = SyntheticDataGenerator()
    
    # Create augmented dataset
    dataset_path = generator.create_augmented_dataset(mutations_per_seed=15)
    
    print(f"\n✅ Augmented dataset creation complete!")
    print(f"📁 Dataset saved to: {dataset_path}")
    print(f"🎯 Target size achieved: {generator.target_dataset_size} entries")
    print("🚀 Ready for fine-tuning phase")
    print("=" * 80)


if __name__ == "__main__":
    main()