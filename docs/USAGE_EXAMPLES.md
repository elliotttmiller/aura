# Professional Sample Integration - Usage Examples

## Quick Start

### 1. Analyze Professional Samples

```python
from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer

# Initialize analyzer
analyzer = ProfessionalSampleAnalyzer()

# Scan all professional samples
samples = analyzer.scan_professional_samples()
print(f"Found {len(samples)} professional samples")

# Generate training dataset from professional samples
dataset_path = analyzer.create_professional_training_dataset()
print(f"Dataset created: {dataset_path}")
```

**Output:**
```
Found 227 professional samples
Dataset created: output/training_data/professional_samples_dataset.jsonl
Generated 681 professional training examples
```

### 2. Create Unified Training Dataset

```python
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline

# Initialize pipeline
pipeline = EnhancedTrainingPipeline()

# Configure dataset size and composition
pipeline.config['target_dataset_size'] = 2000
pipeline.config['professional_samples_weight'] = 0.4  # 40% professional
pipeline.config['synthetic_variations_weight'] = 0.6  # 60% synthetic

# Create unified dataset
dataset_path = pipeline.create_unified_training_dataset()
print(f"Unified dataset: {dataset_path}")
```

**Output:**
```
================================================================================
🚀 ENHANCED TRAINING PIPELINE - Creating Unified Dataset
================================================================================

📊 Phase 1: Professional Sample Analysis
   Found 227 professional samples
   Generated 681 professional training examples

🎨 Phase 2: Synthetic Data Generation
   Loaded 2 seed entries
   Generated 30 mutations from seed data
   Generated 1170 novel designs
   Total synthetic examples: 1200

⚖️ Phase 3: Data Combination and Balancing
   Combined dataset size: 1881
   Professional: 681 (36.2%)
   Synthetic: 1200 (63.8%)

✅ Phase 4: Quality Validation
   Validated 1227 examples (removed 654)

💾 Phase 5: Saving Unified Dataset
   Saved 1227 examples

✅ ENHANCED TRAINING PIPELINE COMPLETE
Dataset: output/training_data/unified_training_dataset.jsonl
================================================================================
```

### 3. Use with Existing AI Training Pipeline

```python
from backend.data_preprocessor import ModelDataPreprocessor
from backend.synthetic_data_generator import SyntheticDataGenerator
from backend.fine_tune import FineTuningEngine

# Step 1: Use enhanced pipeline to create base dataset
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline
pipeline = EnhancedTrainingPipeline()
unified_dataset = pipeline.create_unified_training_dataset()

# Step 2: Optionally add more manual preprocessing
preprocessor = ModelDataPreprocessor()
# ... additional preprocessing if needed

# Step 3: Fine-tune AI model
fine_tuner = FineTuningEngine(training_data_path=unified_dataset)
fine_tuner.train_model()
```

## Advanced Usage

### Custom Professional Sample Analysis

```python
from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer

analyzer = ProfessionalSampleAnalyzer()

# Scan specific samples
samples = analyzer.scan_professional_samples()

# Filter by category
ring_samples = [s for s in samples if s['category'] == 'ring']
gemstone_samples = [s for s in samples if s['category'] == 'gemstone']

# Generate targeted training examples
ring_examples = analyzer.generate_enhanced_training_examples(
    ring_samples,
    examples_per_sample=5  # Generate 5 variations per ring
)

print(f"Generated {len(ring_examples)} ring training examples")
```

### Custom Dataset Composition

```python
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline

pipeline = EnhancedTrainingPipeline()

# Customize for specific needs
pipeline.config.update({
    'target_dataset_size': 5000,  # Larger dataset
    'professional_samples_weight': 0.6,  # More professional samples
    'synthetic_variations_weight': 0.4,  # Fewer synthetic
    'quality_threshold': 0.8,  # Higher quality threshold
})

dataset_path = pipeline.create_unified_training_dataset(
    output_filename='custom_high_quality_dataset.jsonl'
)
```

### Analyzing Design Patterns

```python
from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer
import json

analyzer = ProfessionalSampleAnalyzer()

# Access built-in design patterns
ring_patterns = analyzer.design_patterns['ring_designs']
print("Ring design patterns:")
for pattern_name, pattern_info in ring_patterns.items():
    print(f"  - {pattern_name}: {pattern_info['description']}")

# Access material finishes
finishes = analyzer.design_patterns['material_finishes']
print("\nMaterial finishes:")
for finish_name, finish_info in finishes.items():
    print(f"  - {finish_name}: {finish_info['description']}")
```

### Quality Analysis

```python
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline
import json

# Load a generated dataset
dataset_path = 'output/training_data/unified_training_dataset.jsonl'

with open(dataset_path, 'r') as f:
    examples = [json.loads(line) for line in f]

# Analyze quality distribution
quality_scores = [
    ex.get('metadata', {}).get('quality_score', 0)
    for ex in examples
]

high_quality = sum(1 for s in quality_scores if s > 0.9)
medium_quality = sum(1 for s in quality_scores if 0.7 <= s <= 0.9)
acceptable = sum(1 for s in quality_scores if 0.6 <= s < 0.7)

print(f"Quality Distribution:")
print(f"  High (>0.9): {high_quality}")
print(f"  Medium (0.7-0.9): {medium_quality}")
print(f"  Acceptable (0.6-0.7): {acceptable}")
print(f"  Average: {sum(quality_scores)/len(quality_scores):.2f}")
```

### Integrating with AI Orchestrator

```python
from backend.ai_orchestrator import AiOrchestrator
from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer

# Initialize AI orchestrator
orchestrator = AiOrchestrator()

# Load professional design patterns for context
analyzer = ProfessionalSampleAnalyzer()
design_patterns = analyzer.design_patterns

# Use patterns to enhance AI prompts
user_prompt = "Create an elegant engagement ring"

# Extract relevant patterns
ring_patterns = design_patterns['ring_designs']
solitaire_pattern = ring_patterns['solitaire']

# Enhance prompt with professional context
enhanced_prompt = f"{user_prompt} following professional {solitaire_pattern['description']} standards"

# Generate jewelry with professional knowledge
result = orchestrator.generate_jewelry(enhanced_prompt)
```

## Command Line Usage

### Generate Professional Sample Dataset

```bash
cd /path/to/aura
python backend/professional_sample_analyzer.py
```

### Generate Unified Training Dataset

```bash
cd /path/to/aura
python backend/enhanced_training_pipeline.py
```

### Run Validation Tests

```bash
cd /path/to/aura
python tests/validate_integration.py
```

## Integration with Existing Workflow

### Method 1: Replace Synthetic Generator

```python
# Instead of using synthetic_data_generator.py alone:
from backend.synthetic_data_generator import SyntheticDataGenerator
generator = SyntheticDataGenerator()
dataset = generator.create_augmented_dataset()

# Use enhanced pipeline for better results:
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline
pipeline = EnhancedTrainingPipeline()
dataset = pipeline.create_unified_training_dataset()
```

### Method 2: Augment Existing Pipeline

```python
from backend.data_preprocessor import ModelDataPreprocessor
from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer
from backend.synthetic_data_generator import SyntheticDataGenerator

# Step 1: Create seed dataset from manual models
preprocessor = ModelDataPreprocessor()
seed_dataset = preprocessor.create_seed_dataset()

# Step 2: Add professional sample knowledge
analyzer = ProfessionalSampleAnalyzer()
professional_dataset = analyzer.create_professional_training_dataset()

# Step 3: Generate synthetic variations
generator = SyntheticDataGenerator()
synthetic_dataset = generator.create_augmented_dataset()

# Step 4: Combine all datasets
combined_examples = []
# Load from seed_dataset.jsonl
# Load from professional_samples_dataset.jsonl
# Load from augmented_dataset.jsonl
# Merge and save

with open('output/training_data/final_dataset.jsonl', 'w') as f:
    for example in combined_examples:
        f.write(json.dumps(example) + '\n')
```

## Best Practices

### 1. Start with Professional Samples

Always begin your training data generation with professional samples:

```python
from backend.professional_sample_analyzer import ProfessionalSampleAnalyzer

analyzer = ProfessionalSampleAnalyzer()
professional_dataset = analyzer.create_professional_training_dataset()

# This ensures your AI learns from real professional designs first
```

### 2. Balance Professional and Synthetic Data

Maintain a good balance (recommended 40-60%):

```python
from backend.enhanced_training_pipeline import EnhancedTrainingPipeline

pipeline = EnhancedTrainingPipeline()
pipeline.config['professional_samples_weight'] = 0.4
pipeline.config['synthetic_variations_weight'] = 0.6
```

### 3. Validate Quality

Always validate your training data quality:

```python
pipeline = EnhancedTrainingPipeline()
pipeline.config['quality_threshold'] = 0.7  # Minimum acceptable quality

# The pipeline automatically filters low-quality examples
dataset = pipeline.create_unified_training_dataset()
```

### 4. Monitor Statistics

Review the generated statistics:

```python
import json

stats_path = 'output/training_data/unified_training_dataset_statistics.json'
with open(stats_path, 'r') as f:
    stats = json.load(f)

print(f"Total examples: {stats['total_examples']}")
print(f"Categories: {stats['categories']}")
print(f"Quality distribution: {stats['quality_distribution']}")
```

### 5. Iterate and Improve

Use validation results to improve:

```bash
# Run validation
python tests/validate_integration.py

# Review results and adjust config
# Regenerate dataset with improved settings
```

## Troubleshooting

### Issue: No Professional Samples Found

```python
# Check if samples directory exists
import os
samples_dir = '/path/to/aura/3d_models/professional_samples'
if not os.path.exists(samples_dir):
    print(f"Directory not found: {samples_dir}")
    # Create directory and add samples

# Verify samples are in correct format
supported_formats = ['.3dm', '.glb', '.obj', '.fbx']
# Ensure files have correct extensions
```

### Issue: Low Quality Dataset

```python
# Adjust quality threshold
pipeline = EnhancedTrainingPipeline()
pipeline.config['quality_threshold'] = 0.6  # Lower threshold

# Or increase professional sample weight
pipeline.config['professional_samples_weight'] = 0.6  # More professional samples
```

### Issue: Dataset Too Small

```python
# Increase target size
pipeline = EnhancedTrainingPipeline()
pipeline.config['target_dataset_size'] = 5000  # Larger dataset

# Or increase examples per sample
analyzer = ProfessionalSampleAnalyzer()
examples = analyzer.generate_enhanced_training_examples(
    samples,
    examples_per_sample=5  # More variations
)
```

## Output Files

### Generated Files

- `professional_samples_dataset.jsonl` - Training examples from professional samples
- `professional_samples_dataset_statistics.json` - Analysis statistics
- `unified_training_dataset.jsonl` - Complete unified training dataset
- `unified_training_dataset_statistics.json` - Unified dataset statistics

### File Locations

All output files are saved to:
```
output/training_data/
├── professional_samples_dataset.jsonl
├── professional_samples_dataset_statistics.json
├── unified_training_dataset.jsonl
└── unified_training_dataset_statistics.json
```

## Next Steps

1. **Generate Training Data**:
   ```bash
   python backend/enhanced_training_pipeline.py
   ```

2. **Train AI Model**:
   ```bash
   python backend/fine_tune.py
   ```

3. **Test AI Generation**:
   ```python
   from backend.ai_orchestrator import AiOrchestrator
   orchestrator = AiOrchestrator()
   result = orchestrator.generate_jewelry("elegant solitaire ring")
   ```

4. **Deploy and Use**:
   - Integrate with frontend
   - Use in production workflows
   - Continuously improve training data

## Resources

- **Documentation**: `docs/PROFESSIONAL_SAMPLE_INTEGRATION_GUIDE.md`
- **Source Code**: 
  - `backend/professional_sample_analyzer.py`
  - `backend/enhanced_training_pipeline.py`
- **Tests**: `tests/validate_integration.py`
- **BytePlus Reference**: Article on ChatGPT 3D model integration methods
