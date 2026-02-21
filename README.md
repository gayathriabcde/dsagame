# Error Mining & ErrorTree Construction (Member 3)

## Overview
This module implements error extraction, classification, and diagnostic mapping for DSA problem-solving, providing conceptual gap analysis to support adaptive sequencing.

## Responsibilities

### Theory & Implementation
- Classify error patterns
- Build ErrorTree decision framework
- Map errors → conceptual gaps

### Backend (Submission Processing Layer)
- Submission storage
- Error detection service
- Error mapping APIs
- Database tables: `submissions`, `error_logs`, `error_mappings`

### Code Editor (Execution Feedback)
- Interpret runtime/wrong answer errors
- Produce readable mistake explanations
- Generate actionable hints

## Components

### Core Analysis

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

### Backend Layer

### 5. `database_schema.py`
- SQL schema for submissions, error_logs, error_mappings tables

### 6. `submission_service.py`
- SubmissionService: Processes and stores submissions
- Stores errors and mappings in database
- Retrieves submission history and error analysis

### 7. `execution_feedback.py`
- ExecutionFeedback: Generates user-friendly error explanations
- Provides hints and recommendations
- Formats feedback for code editor display

### 8. `api_endpoints.py`
- Flask REST API for submission processing
- Endpoints: `/api/submit`, `/api/submissions/<id>`, `/api/errors/<id>`

## Integration Points

### For Member 2 (Learner State)
```python
from error_mining_interface import analyze_learner_submission
from error_taxonomy import DSASubskill

# Specify which skills the problem tests
problem_skills = [DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL]

analysis = analyze_learner_submission(code, test_results, problem_skills)

# Skills the learner got CORRECT
correct_skills = analysis['skills_correct']  # List[DSASubskill]

# Skills the learner got INCORRECT (need improvement)
incorrect_skills = analysis['skills_incorrect']  # List[DSASubskill]

# Overall severity for confidence adjustment
severity = analysis['overall_severity']  # float (0.0-1.0)
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

analysis = analyze_learner_submission(code, test_results, problem_skills)
# Returns: detected_errors, by_category, by_subskill, overall_severity, 
#          conceptual_gaps, priority_skills, skills_correct, skills_incorrect
```

## Key Features
- **18 error patterns** covering common DSA mistakes
- **Regex-based detection** + test result analysis
- **Decision tree diagnosis** for conceptual gap inference
- **Severity scoring** (0.0-1.0) for prioritization
- **Focus area recommendations** for targeted micro-quests
- **Database storage** for submissions and error logs
- **REST API** for submission processing
- **User-friendly feedback** with hints and explanations
- **Skills tracking** (correct vs incorrect) for Member 2

## Database Schema

### Tables
1. **submissions**: Stores all code submissions
2. **error_logs**: Detected errors with confidence scores
3. **error_mappings**: Maps errors to affected subskills

## API Endpoints

### POST /api/submit
Process code submission and return analysis + feedback

### GET /api/submissions/<student_id>
Retrieve submission history for a student

### GET /api/errors/<submission_id>
Get detailed error analysis for a submission
