"""
Test Suite for Professional Sample Integration
==============================================

Comprehensive tests for the professional sample analyzer,
enhanced training pipeline, and AI integration.
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline


class TestProfessionalSampleAnalyzer:
    """Test suite for professional sample analyzer."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = ProfessionalSampleAnalyzer()
        
        assert analyzer is not None
        assert os.path.exists(analyzer.samples_dir)
        assert analyzer.design_patterns is not None
        assert 'ring_designs' in analyzer.design_patterns
        
    def test_scan_professional_samples(self):
        """Test scanning of professional samples."""
        analyzer = ProfessionalSampleAnalyzer()
        samples = analyzer.scan_professional_samples()
        
        assert samples is not None
        assert len(samples) > 0
        print(f"✓ Found {len(samples)} professional samples")
        
        # Verify sample structure
        if samples:
            sample = samples[0]
            assert 'filename' in sample
            assert 'filepath' in sample
            assert 'category' in sample
            assert 'design_insights' in sample
            
    def test_categorization(self):
        """Test sample categorization."""
        analyzer = ProfessionalSampleAnalyzer()
        
        # Test ring categorization
        assert analyzer._categorize_sample("test_ring.glb", "rings/test_ring.glb") == 'ring'
        assert analyzer._categorize_sample("diamond_ring.3dm", "samples/diamond_ring.3dm") == 'ring'
        
        # Test necklace categorization
        assert analyzer._categorize_sample("necklace.glb", "necklace.glb") == 'necklace'
        
        # Test gemstone categorization
        assert analyzer._categorize_sample("diamond.glb", "gems/diamond.glb") == 'gemstone'
        
    def test_design_insights_extraction(self):
        """Test extraction of design insights."""
        analyzer = ProfessionalSampleAnalyzer()
        
        # Test complexity detection
        insights = analyzer._extract_design_insights("simple_ring.glb", "ring")
        assert insights['complexity'] == 'simple'
        
        insights = analyzer._extract_design_insights("ornate_filigree_ring.glb", "ring")
        assert insights['complexity'] == 'complex'
        
        # Test style detection
        insights = analyzer._extract_design_insights("vintage_ring.glb", "ring")
        assert insights['style'] == 'vintage'
        
        # Test technique detection
        insights = analyzer._extract_design_insights("filigree_bezel_ring.glb", "ring")
        assert 'filigree_work' in insights['techniques']
        assert 'bezel_setting' in insights['techniques']
        
    def test_training_example_generation(self):
        """Test generation of training examples."""
        analyzer = ProfessionalSampleAnalyzer()
        samples = analyzer.scan_professional_samples()
        
        if samples:
            # Test with first 5 samples
            test_samples = samples[:5]
            examples = analyzer.generate_enhanced_training_examples(
                test_samples,
                examples_per_sample=2
            )
            
            assert len(examples) == len(test_samples) * 2
            
            # Verify example structure
            example = examples[0]
            assert 'id' in example
            assert 'description' in example
            assert 'master_blueprint' in example
            assert 'professional_sample' in example
            assert example['professional_sample'] == True
            
            blueprint = example['master_blueprint']
            assert 'reasoning' in blueprint
            assert 'construction_plan' in blueprint
            assert 'material_specifications' in blueprint
            assert 'presentation_plan' in blueprint
            
    def test_professional_training_dataset_creation(self):
        """Test creation of professional training dataset."""
        analyzer = ProfessionalSampleAnalyzer()
        
        # Create dataset
        dataset_path = analyzer.create_professional_training_dataset(
            output_filename='test_professional_dataset.jsonl'
        )
        
        assert dataset_path != ""
        assert os.path.exists(dataset_path)
        
        # Verify dataset content
        with open(dataset_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            
            # Check first entry
            first_entry = json.loads(lines[0])
            assert 'id' in first_entry
            assert 'master_blueprint' in first_entry
            
        # Verify statistics file exists
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        assert os.path.exists(stats_path)
        
        with open(stats_path, 'r') as f:
            stats = json.load(f)
            assert 'total_examples' in stats
            assert 'categories' in stats
            assert stats['total_examples'] > 0
            
        print(f"✓ Created dataset with {stats['total_examples']} examples")
        
        # Cleanup test file
        os.remove(dataset_path)
        os.remove(stats_path)


class TestEnhancedTrainingPipeline:
    """Test suite for enhanced training pipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly."""
        pipeline = EnhancedTrainingPipeline()
        
        assert pipeline is not None
        assert pipeline.sample_analyzer is not None
        assert pipeline.synthetic_generator is not None
        assert pipeline.config is not None
        assert pipeline.config['target_dataset_size'] > 0
        
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        pipeline = EnhancedTrainingPipeline()
        
        # Test high quality example
        high_quality = {
            'description': 'A beautiful ring',
            'master_blueprint': {
                'reasoning': 'Professional design',
                'construction_plan': [
                    {'operation': 'create_shank', 'parameters': {}},
                    {'operation': 'create_setting', 'parameters': {}}
                ],
                'material_specifications': {
                    'primary_material': 'GOLD',
                    'finish': 'POLISHED'
                },
                'presentation_plan': {
                    'render_environment': 'Studio'
                }
            }
        }
        
        score = pipeline._calculate_quality_score(high_quality)
        assert score > 0.8
        print(f"✓ High quality example score: {score:.2f}")
        
        # Test low quality example
        low_quality = {
            'master_blueprint': {
                'construction_plan': []
            }
        }
        
        score = pipeline._calculate_quality_score(low_quality)
        assert score < 0.5
        print(f"✓ Low quality example score: {score:.2f}")
        
    def test_validation_and_filtering(self):
        """Test validation and filtering of dataset."""
        pipeline = EnhancedTrainingPipeline()
        
        test_dataset = [
            # Valid example
            {
                'id': 'test_1',
                'description': 'Test ring',
                'master_blueprint': {
                    'reasoning': 'Test',
                    'construction_plan': [
                        {'operation': 'create_shank', 'parameters': {}}
                    ],
                    'material_specifications': {'primary_material': 'GOLD'},
                    'presentation_plan': {}
                }
            },
            # Invalid - no blueprint
            {
                'id': 'test_2',
                'description': 'Invalid'
            },
            # Invalid - empty construction plan
            {
                'id': 'test_3',
                'master_blueprint': {
                    'construction_plan': []
                }
            }
        ]
        
        validated = pipeline._validate_and_filter(test_dataset)
        
        assert len(validated) == 1
        assert validated[0]['id'] == 'test_1'
        assert 'quality_score' in validated[0]['metadata']
        
        print(f"✓ Filtered {len(test_dataset)} examples to {len(validated)} valid examples")
        
    def test_unified_dataset_creation(self):
        """Test creation of unified training dataset."""
        pipeline = EnhancedTrainingPipeline()
        
        # Create test dataset with smaller size
        pipeline.config['target_dataset_size'] = 100
        
        dataset_path = pipeline.create_unified_training_dataset(
            output_filename='test_unified_dataset.jsonl'
        )
        
        assert dataset_path != ""
        assert os.path.exists(dataset_path)
        
        # Verify dataset content
        with open(dataset_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            print(f"✓ Created unified dataset with {len(lines)} examples")
            
        # Verify statistics
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        assert os.path.exists(stats_path)
        
        with open(stats_path, 'r') as f:
            stats = json.load(f)
            assert 'total_examples' in stats
            assert 'data_sources' in stats
            assert 'quality_distribution' in stats
            
            # Verify mix of professional and synthetic
            prof_count = stats['data_sources']['professional_samples']
            synth_count = stats['data_sources']['synthetic_variations']
            print(f"✓ Professional: {prof_count}, Synthetic: {synth_count}")
            
        # Cleanup test files
        os.remove(dataset_path)
        os.remove(stats_path)


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""
    
    def test_end_to_end_pipeline(self):
        """Test complete end-to-end training data generation."""
        # Step 1: Analyze professional samples
        analyzer = ProfessionalSampleAnalyzer()
        samples = analyzer.scan_professional_samples()
        assert len(samples) > 0
        
        # Step 2: Generate professional examples
        prof_examples = analyzer.generate_enhanced_training_examples(
            samples[:10],  # Use subset for testing
            examples_per_sample=2
        )
        assert len(prof_examples) > 0
        
        # Step 3: Create unified pipeline
        pipeline = EnhancedTrainingPipeline()
        pipeline.config['target_dataset_size'] = 50  # Small size for testing
        
        # Step 4: Generate unified dataset
        dataset_path = pipeline.create_unified_training_dataset(
            output_filename='test_e2e_dataset.jsonl'
        )
        
        assert os.path.exists(dataset_path)
        
        # Step 5: Verify quality
        with open(dataset_path, 'r') as f:
            examples = [json.loads(line) for line in f]
            
        # Check mix of sources
        professional_count = sum(1 for ex in examples if ex.get('professional_sample', False))
        synthetic_count = len(examples) - professional_count
        
        print(f"✓ E2E Test: {len(examples)} examples")
        print(f"  - Professional: {professional_count}")
        print(f"  - Synthetic: {synthetic_count}")
        
        assert len(examples) > 0
        assert professional_count > 0 or synthetic_count > 0
        
        # Cleanup
        os.remove(dataset_path)
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        if os.path.exists(stats_path):
            os.remove(stats_path)


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 80)
    print("🧪 PROFESSIONAL SAMPLE INTEGRATION TEST SUITE")
    print("=" * 80)
    
    # Run tests using pytest
    pytest_args = [
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    result = pytest.main(pytest_args)
    
    print("\n" + "=" * 80)
    if result == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
