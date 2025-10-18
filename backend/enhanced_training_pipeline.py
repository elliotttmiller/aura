"""
Enhanced Training Pipeline - Unified Professional & Synthetic Data Generation
============================================================================

This module implements a unified training pipeline that combines:
1. Professional sample analysis and knowledge extraction
2. Synthetic data generation with creative mutations
3. Intelligent data augmentation and enrichment

Implements BytePlus ChatGPT 3D methodology:
- Workflow automation through pattern-based generation
- Conceptual assistance via professional knowledge
- Enhanced creativity through intelligent variations
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer
from backend.synthetic_data_generator import SyntheticDataGenerator

# Setup professional logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] PIPELINE %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedTrainingPipeline:
    """
    Unified training pipeline combining professional samples and synthetic generation.
    
    This pipeline orchestrates the complete training data creation process:
    1. Extract knowledge from 227+ professional jewelry samples
    2. Generate synthetic variations using intelligent mutation
    3. Combine and enrich data for optimal AI training
    4. Create comprehensive training datasets with quality validation
    """
    
    def __init__(self, models_dir: str = None, output_dir: str = None):
        """
        Initialize the enhanced training pipeline.
        
        Args:
            models_dir: Directory containing professional samples
            output_dir: Directory for training data output
        """
        self.addon_root = self._get_addon_root()
        
        # Initialize components
        self.sample_analyzer = ProfessionalSampleAnalyzer(models_dir)
        self.synthetic_generator = SyntheticDataGenerator()
        
        # Output configuration
        self.output_dir = output_dir or os.path.join(
            self.addon_root, "output", "training_data"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Pipeline configuration
        self.config = {
            'professional_samples_weight': 0.4,  # 40% professional samples
            'synthetic_variations_weight': 0.6,  # 60% synthetic variations
            'target_dataset_size': 2000,  # Target total examples
            'quality_threshold': 0.7,  # Minimum quality score
        }
        
        logger.info("🚀 Enhanced Training Pipeline initialized")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"⚖️ Professional samples weight: {self.config['professional_samples_weight']:.0%}")
        logger.info(f"⚖️ Synthetic variations weight: {self.config['synthetic_variations_weight']:.0%}")
        
    def _get_addon_root(self) -> str:
        """Get the root directory of the addon."""
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(current_file)
        return os.path.dirname(backend_dir)
    
    def create_unified_training_dataset(
        self,
        output_filename: str = 'unified_training_dataset.jsonl'
    ) -> str:
        """
        Create a unified training dataset combining professional and synthetic data.
        
        This method orchestrates the complete pipeline:
        1. Analyze professional samples
        2. Generate synthetic variations
        3. Combine and balance datasets
        4. Validate and filter quality
        5. Create final unified dataset
        
        Args:
            output_filename: Name of output JSONL file
            
        Returns:
            Path to created dataset file
        """
        logger.info("=" * 80)
        logger.info("🚀 ENHANCED TRAINING PIPELINE - Creating Unified Dataset")
        logger.info("=" * 80)
        
        # Phase 1: Professional Sample Analysis
        logger.info("\n📊 Phase 1: Professional Sample Analysis")
        logger.info("-" * 80)
        professional_examples = self._generate_professional_examples()
        
        # Phase 2: Synthetic Data Generation
        logger.info("\n🎨 Phase 2: Synthetic Data Generation")
        logger.info("-" * 80)
        synthetic_examples = self._generate_synthetic_examples()
        
        # Phase 3: Data Combination and Balancing
        logger.info("\n⚖️ Phase 3: Data Combination and Balancing")
        logger.info("-" * 80)
        unified_dataset = self._combine_and_balance(
            professional_examples,
            synthetic_examples
        )
        
        # Phase 4: Quality Validation
        logger.info("\n✅ Phase 4: Quality Validation")
        logger.info("-" * 80)
        validated_dataset = self._validate_and_filter(unified_dataset)
        
        # Phase 5: Save Unified Dataset
        logger.info("\n💾 Phase 5: Saving Unified Dataset")
        logger.info("-" * 80)
        dataset_path = self._save_unified_dataset(
            validated_dataset,
            output_filename
        )
        
        # Generate comprehensive statistics
        self._generate_pipeline_statistics(validated_dataset, dataset_path)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ENHANCED TRAINING PIPELINE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"📁 Dataset path: {dataset_path}")
        logger.info(f"📊 Total examples: {len(validated_dataset)}")
        logger.info(f"🎯 Quality validated: ✓")
        logger.info("=" * 80)
        
        return dataset_path
    
    def _generate_professional_examples(self) -> List[Dict[str, Any]]:
        """Generate training examples from professional samples."""
        logger.info("🔬 Analyzing professional jewelry samples...")
        
        # Scan professional samples
        samples = self.sample_analyzer.scan_professional_samples()
        logger.info(f"   Found {len(samples)} professional samples")
        
        # Generate training examples (3 variations per sample)
        examples = self.sample_analyzer.generate_enhanced_training_examples(
            samples,
            examples_per_sample=3
        )
        
        logger.info(f"✅ Generated {len(examples)} professional training examples")
        return examples
    
    def _generate_synthetic_examples(self) -> List[Dict[str, Any]]:
        """Generate synthetic training examples with creative mutations."""
        logger.info("🎭 Generating synthetic design variations...")
        
        # Load seed data (use professional examples as seed)
        seed_data = self.synthetic_generator.load_seed_dataset()
        
        # If no seed data, use demonstration data
        if not seed_data:
            logger.info("   Using demonstration seed dataset")
            seed_data = self.synthetic_generator._create_demonstration_seed_dataset()
        
        logger.info(f"   Loaded {len(seed_data)} seed entries")
        
        # Generate mutations
        all_mutations = []
        for seed_entry in seed_data:
            mutations = self.synthetic_generator.generate_creative_mutations(
                seed_entry,
                num_mutations=15
            )
            all_mutations.extend(mutations)
        
        logger.info(f"   Generated {len(all_mutations)} mutations from seed data")
        
        # Generate novel designs
        remaining_needed = max(
            0,
            int(self.config['target_dataset_size'] * self.config['synthetic_variations_weight']) - len(all_mutations)
        )
        
        if remaining_needed > 0:
            novel_designs = self.synthetic_generator.generate_novel_designs(
                remaining_needed
            )
            all_mutations.extend(novel_designs)
            logger.info(f"   Generated {len(novel_designs)} novel designs")
        
        logger.info(f"✅ Total synthetic examples: {len(all_mutations)}")
        return all_mutations
    
    def _combine_and_balance(
        self,
        professional_examples: List[Dict[str, Any]],
        synthetic_examples: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine and balance professional and synthetic examples.
        
        Args:
            professional_examples: Examples from professional samples
            synthetic_examples: Synthetically generated examples
            
        Returns:
            Balanced combined dataset
        """
        target_size = self.config['target_dataset_size']
        prof_weight = self.config['professional_samples_weight']
        synth_weight = self.config['synthetic_variations_weight']
        
        # Calculate target counts
        target_prof = int(target_size * prof_weight)
        target_synth = int(target_size * synth_weight)
        
        logger.info(f"   Target professional examples: {target_prof}")
        logger.info(f"   Target synthetic examples: {target_synth}")
        
        # Balance professional examples
        if len(professional_examples) > target_prof:
            # Randomly sample if we have too many
            import random
            professional_balanced = random.sample(professional_examples, target_prof)
            logger.info(f"   Sampled {target_prof} from {len(professional_examples)} professional examples")
        else:
            professional_balanced = professional_examples
            logger.info(f"   Using all {len(professional_examples)} professional examples")
        
        # Balance synthetic examples
        if len(synthetic_examples) > target_synth:
            import random
            synthetic_balanced = random.sample(synthetic_examples, target_synth)
            logger.info(f"   Sampled {target_synth} from {len(synthetic_examples)} synthetic examples")
        else:
            synthetic_balanced = synthetic_examples
            logger.info(f"   Using all {len(synthetic_examples)} synthetic examples")
        
        # Combine datasets
        combined = professional_balanced + synthetic_balanced
        
        # Shuffle for better training distribution
        import random
        random.shuffle(combined)
        
        logger.info(f"✅ Combined dataset size: {len(combined)}")
        logger.info(f"   Professional: {len(professional_balanced)} ({len(professional_balanced)/len(combined)*100:.1f}%)")
        logger.info(f"   Synthetic: {len(synthetic_balanced)} ({len(synthetic_balanced)/len(combined)*100:.1f}%)")
        
        return combined
    
    def _validate_and_filter(
        self,
        dataset: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Validate and filter dataset based on quality criteria.
        
        Args:
            dataset: Dataset to validate
            
        Returns:
            Validated and filtered dataset
        """
        logger.info(f"   Validating {len(dataset)} examples...")
        
        validated = []
        validation_issues = {
            'missing_blueprint': 0,
            'missing_construction_plan': 0,
            'invalid_parameters': 0,
            'low_quality': 0
        }
        
        for example in dataset:
            # Check for master blueprint
            if 'master_blueprint' not in example:
                validation_issues['missing_blueprint'] += 1
                continue
            
            blueprint = example['master_blueprint']
            
            # Check for construction plan
            if 'construction_plan' not in blueprint:
                validation_issues['missing_construction_plan'] += 1
                continue
            
            # Check construction plan has operations
            construction_plan = blueprint['construction_plan']
            if not construction_plan or len(construction_plan) == 0:
                validation_issues['invalid_parameters'] += 1
                continue
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(example)
            
            if quality_score < self.config['quality_threshold']:
                validation_issues['low_quality'] += 1
                continue
            
            # Add quality score to metadata
            if 'metadata' not in example:
                example['metadata'] = {}
            example['metadata']['quality_score'] = quality_score
            
            validated.append(example)
        
        # Report validation results
        removed = len(dataset) - len(validated)
        logger.info(f"✅ Validated {len(validated)} examples (removed {removed})")
        
        if removed > 0:
            logger.info(f"   Validation issues:")
            for issue, count in validation_issues.items():
                if count > 0:
                    logger.info(f"     • {issue}: {count}")
        
        return validated
    
    def _calculate_quality_score(self, example: Dict[str, Any]) -> float:
        """
        Calculate quality score for a training example.
        
        Args:
            example: Training example to score
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        max_score = 0.0
        
        # Check for description
        max_score += 0.2
        if 'description' in example and example['description']:
            score += 0.2
        
        # Check for construction plan
        max_score += 0.3
        blueprint = example.get('master_blueprint', {})
        construction_plan = blueprint.get('construction_plan', [])
        if construction_plan:
            # More operations = higher quality
            operation_score = min(len(construction_plan) / 3.0, 1.0) * 0.3
            score += operation_score
        
        # Check for material specifications
        max_score += 0.2
        material_specs = blueprint.get('material_specifications', {})
        if material_specs:
            required_keys = ['primary_material', 'finish']
            present_keys = sum(1 for key in required_keys if key in material_specs)
            score += (present_keys / len(required_keys)) * 0.2
        
        # Check for presentation plan
        max_score += 0.15
        presentation_plan = blueprint.get('presentation_plan', {})
        if presentation_plan:
            score += 0.15
        
        # Check for reasoning
        max_score += 0.15
        if 'reasoning' in blueprint and blueprint['reasoning']:
            score += 0.15
        
        return score / max_score if max_score > 0 else 0.0
    
    def _save_unified_dataset(
        self,
        dataset: List[Dict[str, Any]],
        filename: str
    ) -> str:
        """
        Save the unified dataset to JSONL file.
        
        Args:
            dataset: Dataset to save
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        dataset_path = os.path.join(self.output_dir, filename)
        
        logger.info(f"   Saving to: {dataset_path}")
        
        with open(dataset_path, 'w') as f:
            for example in dataset:
                json.dump(example, f)
                f.write('\n')
        
        logger.info(f"✅ Saved {len(dataset)} examples")
        
        return dataset_path
    
    def _generate_pipeline_statistics(
        self,
        dataset: List[Dict[str, Any]],
        dataset_path: str
    ) -> None:
        """
        Generate comprehensive statistics about the unified dataset.
        
        Args:
            dataset: Dataset to analyze
            dataset_path: Path to dataset file
        """
        from collections import defaultdict
        import datetime
        
        stats = {
            'pipeline_version': '1.0_enhanced',
            'creation_timestamp': datetime.datetime.now().isoformat(),
            'total_examples': len(dataset),
            'dataset_path': dataset_path,
            'configuration': self.config,
            'data_sources': {
                'professional_samples': len([d for d in dataset if d.get('professional_sample', False)]),
                'synthetic_variations': len([d for d in dataset if not d.get('professional_sample', False)])
            },
            'categories': defaultdict(int),
            'materials': defaultdict(int),
            'styles': defaultdict(int),
            'complexities': defaultdict(int),
            'quality_distribution': {
                'high': 0,  # > 0.9
                'medium': 0,  # 0.7 - 0.9
                'acceptable': 0  # 0.6 - 0.7
            }
        }
        
        # Analyze dataset
        for example in dataset:
            # Category
            category = example.get('source_category', 'unknown')
            stats['categories'][category] += 1
            
            # Material
            blueprint = example.get('master_blueprint', {})
            material_specs = blueprint.get('material_specifications', {})
            material = material_specs.get('primary_material', 'unknown')
            stats['materials'][material] += 1
            
            # Style and complexity (from metadata if available)
            metadata = example.get('metadata', {})
            if 'design_insights' in metadata:
                insights = metadata['design_insights']
                style = insights.get('style', 'unknown')
                complexity = insights.get('complexity', 'unknown')
                stats['styles'][style] += 1
                stats['complexities'][complexity] += 1
            
            # Quality score
            quality_score = metadata.get('quality_score', 0.0)
            if quality_score > 0.9:
                stats['quality_distribution']['high'] += 1
            elif quality_score >= 0.7:
                stats['quality_distribution']['medium'] += 1
            else:
                stats['quality_distribution']['acceptable'] += 1
        
        # Convert defaultdicts to regular dicts
        stats['categories'] = dict(stats['categories'])
        stats['materials'] = dict(stats['materials'])
        stats['styles'] = dict(stats['styles'])
        stats['complexities'] = dict(stats['complexities'])
        
        # Save statistics
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"📈 Statistics saved: {stats_path}")
        logger.info(f"\n📊 Dataset Statistics:")
        logger.info(f"   Total examples: {stats['total_examples']}")
        logger.info(f"   Professional samples: {stats['data_sources']['professional_samples']}")
        logger.info(f"   Synthetic variations: {stats['data_sources']['synthetic_variations']}")
        logger.info(f"   Categories: {stats['categories']}")
        logger.info(f"   Materials: {stats['materials']}")
        logger.info(f"   Quality: High={stats['quality_distribution']['high']}, "
                   f"Medium={stats['quality_distribution']['medium']}, "
                   f"Acceptable={stats['quality_distribution']['acceptable']}")


def main():
    """Main execution function for enhanced training pipeline."""
    print("\n" + "=" * 80)
    print("🚀 ENHANCED TRAINING PIPELINE")
    print("Professional Samples + Synthetic Generation + Quality Validation")
    print("=" * 80 + "\n")
    
    # Initialize pipeline
    pipeline = EnhancedTrainingPipeline()
    
    # Create unified training dataset
    dataset_path = pipeline.create_unified_training_dataset()
    
    print("\n" + "=" * 80)
    print("✅ PIPELINE COMPLETE")
    print("=" * 80)
    print(f"📁 Dataset: {dataset_path}")
    print(f"🎯 Ready for fine-tuning with backend/fine_tune.py")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
