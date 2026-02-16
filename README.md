# Error Mining & ErrorTree Construction (Member 3)

## Overview
This module implements error extraction, classification, and diagnostic mapping for DSA problem-solving, providing conceptual gap analysis to support adaptive sequencing.

## Components

### 1. `error_taxonomy.py`
- **ErrorCategory**: 7 error types (Logic, Boundary, Complexity, Data Structure, Algorithm, Syntax, Memory)
- **DSASubskill**: 20 DSA subskills (Array, LinkedList, Tree, Graph, DP, etc.)
- **ErrorPattern**: 18 predefined error patterns with severity scores

### 2. `error_extractor.py`
- **ErrorExtractor**: Detects errors from code and test results using regex + heuristics
- **ErrorClassifier**: Groups errors by category and subskill, computes severity scores

### 3. `error_tree.py`
- **ErrorTree**: Decision tree that maps error patterns to conceptual gaps
- **ConceptualGap**: Diagnosed skill deficiency with severity and focus areas
- **ErrorMiningPipeline**: End-to-end analysis pipeline

### 4. `error_mining_interface.py`
- Main interface function `analyze_learner_submission()` for integration with other members

## Integration Points

### For Member 2 (Learner State)
```python
from error_mining_interface import analyze_learner_submission

analysis = analyze_learner_submission(code, test_results)
affected_skills = analysis['priority_skills']  # Update learner mastery for these skills
severity = analysis['overall_severity']  # Adjust skill confidence
```

### For Member 4 (Adaptive Sequencing)
```python
gaps = analysis['conceptual_gaps']
next_skill = gaps[0].subskill  # Highest priority skill
focus_areas = gaps[0].recommended_focus  # Specific concepts to target
```

### For Member 6 (Evaluation)
```python
error_labels = [e.error_id for e in analysis['detected_errors']]
by_category = analysis['by_category']  # For error distribution analysis
```

## Usage Example
```python
from error_mining_interface import analyze_learner_submission

code = "..."  # Learner's code
test_results = {'passed': False, 'failures': [...]}

analysis = analyze_learner_submission(code, test_results)
# Returns: detected_errors, by_category, by_subskill, overall_severity, conceptual_gaps, priority_skills
```

## Key Features
- **18 error patterns** covering common DSA mistakes
- **Regex-based detection** + test result analysis
- **Decision tree diagnosis** for conceptual gap inference
- **Severity scoring** (0.0-1.0) for prioritization
- **Focus area recommendations** for targeted micro-quests
