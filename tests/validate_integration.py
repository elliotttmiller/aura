"""
Simple validation script for professional sample integration.
Tests core functionality without pytest dependencies.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline


def test_professional_sample_analyzer():
    """Test professional sample analyzer functionality."""
    print("\n" + "=" * 80)
    print("TEST 1: Professional Sample Analyzer")
    print("=" * 80)
    
    try:
        # Initialize analyzer
        print("  [1/5] Initializing analyzer...")
        analyzer = ProfessionalSampleAnalyzer()
        print("      ✓ Analyzer initialized")
        
        # Scan samples
        print("  [2/5] Scanning professional samples...")
        samples = analyzer.scan_professional_samples()
        print(f"      ✓ Found {len(samples)} professional samples")
        
        # Test categorization
        print("  [3/5] Testing categorization...")
        ring_cat = analyzer._categorize_sample("test_ring.glb", "rings/test_ring.glb")
        assert ring_cat == 'ring', f"Expected 'ring', got '{ring_cat}'"
        print("      ✓ Categorization working correctly")
        
        # Generate training examples
        print("  [4/5] Generating training examples...")
        if samples:
            test_samples = samples[:5]
            examples = analyzer.generate_enhanced_training_examples(
                test_samples,
                examples_per_sample=2
            )
            print(f"      ✓ Generated {len(examples)} training examples")
            
            # Verify structure
            if examples:
                ex = examples[0]
                assert 'id' in ex
                assert 'master_blueprint' in ex
                assert ex.get('professional_sample') == True
                print("      ✓ Example structure validated")
        
        # Create dataset
        print("  [5/5] Creating professional dataset...")
        dataset_path = analyzer.create_professional_training_dataset(
            output_filename='validation_test_dataset.jsonl'
        )
        assert os.path.exists(dataset_path)
        
        # Check content
        with open(dataset_path, 'r') as f:
            line_count = len(f.readlines())
        print(f"      ✓ Dataset created with {line_count} examples")
        
        # Cleanup
        os.remove(dataset_path)
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        if os.path.exists(stats_path):
            os.remove(stats_path)
        
        print("\n✅ TEST 1 PASSED: Professional Sample Analyzer")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_training_pipeline():
    """Test enhanced training pipeline functionality."""
    print("\n" + "=" * 80)
    print("TEST 2: Enhanced Training Pipeline")
    print("=" * 80)
    
    try:
        # Initialize pipeline
        print("  [1/5] Initializing pipeline...")
        pipeline = EnhancedTrainingPipeline()
        assert pipeline.sample_analyzer is not None
        assert pipeline.synthetic_generator is not None
        print("      ✓ Pipeline initialized")
        
        # Test quality scoring
        print("  [2/5] Testing quality score calculation...")
        high_quality_example = {
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
                'presentation_plan': {'render_environment': 'Studio'}
            }
        }
        score = pipeline._calculate_quality_score(high_quality_example)
        assert score > 0.8, f"Expected score > 0.8, got {score}"
        print(f"      ✓ Quality scoring working (score: {score:.2f})")
        
        # Test validation
        print("  [3/5] Testing validation and filtering...")
        test_dataset = [
            high_quality_example,
            {'master_blueprint': {'construction_plan': []}},  # Invalid
            {'description': 'Invalid'}  # Invalid
        ]
        validated = pipeline._validate_and_filter(test_dataset)
        assert len(validated) == 1
        print(f"      ✓ Filtered {len(test_dataset)} to {len(validated)} valid examples")
        
        # Test dataset creation (small size)
        print("  [4/5] Creating test unified dataset...")
        pipeline.config['target_dataset_size'] = 50
        dataset_path = pipeline.create_unified_training_dataset(
            output_filename='validation_unified_test.jsonl'
        )
        assert os.path.exists(dataset_path)
        print("      ✓ Unified dataset created")
        
        # Verify content
        print("  [5/5] Validating dataset content...")
        with open(dataset_path, 'r') as f:
            examples = [json.loads(line) for line in f]
        
        professional_count = sum(1 for ex in examples if ex.get('professional_sample', False))
        synthetic_count = len(examples) - professional_count
        
        print(f"      ✓ Dataset has {len(examples)} examples")
        print(f"        - Professional: {professional_count}")
        print(f"        - Synthetic: {synthetic_count}")
        
        # Cleanup
        os.remove(dataset_path)
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        if os.path.exists(stats_path):
            os.remove(stats_path)
        
        print("\n✅ TEST 2 PASSED: Enhanced Training Pipeline")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_scenario():
    """Test complete integration scenario."""
    print("\n" + "=" * 80)
    print("TEST 3: End-to-End Integration")
    print("=" * 80)
    
    try:
        print("  [1/3] Analyzing professional samples...")
        analyzer = ProfessionalSampleAnalyzer()
        samples = analyzer.scan_professional_samples()
        print(f"      ✓ Analyzed {len(samples)} samples")
        
        print("  [2/3] Creating unified training pipeline...")
        pipeline = EnhancedTrainingPipeline()
        pipeline.config['target_dataset_size'] = 100
        print("      ✓ Pipeline configured")
        
        print("  [3/3] Generating complete dataset...")
        dataset_path = pipeline.create_unified_training_dataset(
            output_filename='validation_e2e_test.jsonl'
        )
        
        # Verify
        with open(dataset_path, 'r') as f:
            examples = [json.loads(line) for line in f]
        
        print(f"      ✓ Complete dataset with {len(examples)} examples")
        
        # Check quality scores
        quality_scores = [
            ex.get('metadata', {}).get('quality_score', 0)
            for ex in examples
        ]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        print(f"      ✓ Average quality score: {avg_quality:.2f}")
        
        # Cleanup
        os.remove(dataset_path)
        stats_path = dataset_path.replace('.jsonl', '_statistics.json')
        if os.path.exists(stats_path):
            os.remove(stats_path)
        
        print("\n✅ TEST 3 PASSED: End-to-End Integration")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("🧪 PROFESSIONAL SAMPLE INTEGRATION VALIDATION")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(test_professional_sample_analyzer())
    results.append(test_enhanced_training_pipeline())
    results.append(test_integration_scenario())
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL VALIDATION TESTS PASSED")
        print("=" * 80)
        return 0
    else:
        print("\n❌ SOME VALIDATION TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
