"""
Test Suite for Member 3 - Error Mining & ErrorTree Construction
Verifies all required tasks are implemented correctly
"""

from error_taxonomy import ErrorCategory, DSASubskill, ERROR_PATTERNS
from error_extractor import ErrorExtractor, ErrorClassifier, DetectedError
from error_tree import ErrorTree, ErrorMiningPipeline, ConceptualGap
from error_mining_interface import analyze_learner_submission

def test_task_1_error_taxonomy():
    """Task 1: Error taxonomy with 7 categories, 20 subskills, 18 patterns"""
    print("\n=== TASK 1: Error Taxonomy ===")
    
    # Check 7 error categories
    categories = list(ErrorCategory)
    print(f"[OK] Error Categories: {len(categories)} (expected 7)")
    assert len(categories) == 7, "Should have 7 error categories"
    
    # Check 20 DSA subskills
    subskills = list(DSASubskill)
    print(f"[OK] DSA Subskills: {len(subskills)} (expected 20)")
    assert len(subskills) == 20, "Should have 20 DSA subskills"
    
    # Check 18 error patterns
    print(f"[OK] Error Patterns: {len(ERROR_PATTERNS)} (expected 18)")
    assert len(ERROR_PATTERNS) == 18, "Should have 18 error patterns"
    
    # Verify severity scores
    for pattern in ERROR_PATTERNS.values():
        assert 0.0 <= pattern.severity <= 1.0, "Severity must be 0.0-1.0"
    print("[OK] All severity scores valid (0.0-1.0)")
    
    print("[PASS] TASK 1 PASSED\n")

def test_task_2_error_extraction():
    """Task 2: Error extraction from code and test results"""
    print("=== TASK 2: Error Extraction ===")
    
    extractor = ErrorExtractor()
    
    # Test code with multiple errors
    buggy_code = """
def binary_search(arr, target):
    left, right = 0, len(arr)  # E018: wrong bound
    while left <= right:
        mid = (left + right) / 2
        if arr[mid] == target:
            return mid
    return -1

def factorial(n):
    return n * factorial(n-1)  # E002: missing base case
"""
    
    test_results = {
        'passed': False,
        'failures': [
            {'message': 'IndexError: list index out of range', 'test_case': 'boundary_test'}
        ]
    }
    
    errors = extractor.extract_from_code(buggy_code, test_results)
    print(f"[OK] Detected {len(errors)} errors from code + test results")
    assert len(errors) > 0, "Should detect errors"
    
    # Verify error structure
    for error in errors:
        assert hasattr(error, 'error_id'), "Error should have error_id"
        assert hasattr(error, 'pattern'), "Error should have pattern"
        assert hasattr(error, 'confidence'), "Error should have confidence"
        assert 0.0 <= error.confidence <= 1.0, "Confidence must be 0.0-1.0"
    print("[OK] Error structure valid (error_id, pattern, confidence)")
    
    print("[PASS] TASK 2 PASSED\n")

def test_task_3_error_classification():
    """Task 3: Error classification by category and subskill"""
    print("=== TASK 3: Error Classification ===")
    
    classifier = ErrorClassifier()
    
    # Create sample errors
    errors = [
        DetectedError("E001", ERROR_PATTERNS["E001"], 0.8, "loop error"),
        DetectedError("E005", ERROR_PATTERNS["E005"], 0.9, "index error"),
        DetectedError("E002", ERROR_PATTERNS["E002"], 0.85, "recursion error"),
    ]
    
    # Test classification by category
    by_category = classifier.classify_by_category(errors)
    print(f"[OK] Classified into {len([v for v in by_category.values() if v])} categories")
    assert ErrorCategory.BOUNDARY in by_category, "Should classify boundary errors"
    assert ErrorCategory.LOGIC in by_category, "Should classify logic errors"
    
    # Test classification by subskill
    by_subskill = classifier.classify_by_subskill(errors)
    print(f"[OK] Mapped to {len([v for v in by_subskill.values() if v])} subskills")
    assert DSASubskill.ARRAY_TRAVERSAL in by_subskill, "Should map to array traversal"
    assert DSASubskill.RECURSION in by_subskill, "Should map to recursion"
    
    # Test severity scoring
    severity = classifier.get_severity_score(errors)
    print(f"[OK] Overall severity: {severity:.2f}")
    assert 0.0 <= severity <= 1.0, "Severity must be 0.0-1.0"
    
    print("[PASS] TASK 3 PASSED\n")

def test_task_4_error_tree():
    """Task 4: ErrorTree decision tree for conceptual gap diagnosis"""
    print("=== TASK 4: ErrorTree Decision Framework ===")
    
    tree = ErrorTree()
    
    # Verify tree structure
    assert tree.root is not None, "Tree should have root node"
    print("[OK] ErrorTree constructed with root node")
    
    # Test diagnosis with sample errors
    errors = [
        DetectedError("E002", ERROR_PATTERNS["E002"], 0.9, "recursion base case"),
        DetectedError("E002", ERROR_PATTERNS["E002"], 0.85, "recursion call"),
    ]
    
    gaps = tree.diagnose(errors)
    print(f"[OK] Diagnosed {len(gaps)} conceptual gaps")
    assert len(gaps) > 0, "Should diagnose conceptual gaps"
    
    # Verify ConceptualGap structure
    for gap in gaps:
        assert isinstance(gap.subskill, DSASubskill), "Gap should have DSA subskill"
        assert 0.0 <= gap.severity <= 1.0, "Severity must be 0.0-1.0"
        assert gap.error_count >= 0, "Error count must be non-negative"
        assert len(gap.recommended_focus) > 0, "Should have focus recommendations"
    print("[OK] ConceptualGap structure valid (subskill, severity, focus areas)")
    
    print("[PASS] TASK 4 PASSED\n")

def test_task_5_end_to_end_pipeline():
    """Task 5: Complete error mining pipeline"""
    print("=== TASK 5: End-to-End Pipeline ===")
    
    pipeline = ErrorMiningPipeline()
    
    code = """
def search(arr, target):
    for i in range(len(arr) + 1):  # Off-by-one
        if arr[i] == target:
            return i
    return -1
"""
    
    test_results = {
        'passed': False,
        'failures': [{'message': 'IndexError: list index out of range'}]
    }
    
    analysis = pipeline.analyze(code, test_results)
    
    # Verify all required outputs
    assert 'detected_errors' in analysis, "Should return detected_errors"
    assert 'by_category' in analysis, "Should return by_category"
    assert 'by_subskill' in analysis, "Should return by_subskill"
    assert 'overall_severity' in analysis, "Should return overall_severity"
    assert 'conceptual_gaps' in analysis, "Should return conceptual_gaps"
    assert 'priority_skills' in analysis, "Should return priority_skills"
    print("[OK] Pipeline returns all required fields")
    
    print(f"  - Detected errors: {len(analysis['detected_errors'])}")
    print(f"  - Overall severity: {analysis['overall_severity']:.2f}")
    print(f"  - Conceptual gaps: {len(analysis['conceptual_gaps'])}")
    print(f"  - Priority skills: {len(analysis['priority_skills'])}")
    
    print("[PASS] TASK 5 PASSED\n")

def test_task_6_integration_interface():
    """Task 6: Integration interface for other members"""
    print("=== TASK 6: Integration Interface ===")
    
    code = """
def factorial(n):
    return n * factorial(n-1)  # Missing base case
"""
    
    test_results = {'passed': False, 'failures': [{'message': 'RecursionError: maximum recursion depth'}]}
    
    # Test main interface function
    analysis = analyze_learner_submission(code, test_results)
    
    # Verify Member 2 integration (Learner State)
    assert 'priority_skills' in analysis, "Member 2 needs priority_skills"
    assert 'overall_severity' in analysis, "Member 2 needs overall_severity"
    print("[OK] Member 2 integration: priority_skills, overall_severity")
    
    # Verify Member 4 integration (Adaptive Sequencing)
    assert 'conceptual_gaps' in analysis, "Member 4 needs conceptual_gaps"
    if analysis['conceptual_gaps']:
        gap = analysis['conceptual_gaps'][0]
        assert hasattr(gap, 'subskill'), "Member 4 needs subskill"
        assert hasattr(gap, 'recommended_focus'), "Member 4 needs focus areas"
    print("[OK] Member 4 integration: conceptual_gaps with subskill & focus")
    
    # Verify Member 6 integration (Evaluation)
    assert 'detected_errors' in analysis, "Member 6 needs detected_errors"
    assert 'by_category' in analysis, "Member 6 needs by_category"
    print("[OK] Member 6 integration: detected_errors, by_category")
    
    print("[PASS] TASK 6 PASSED\n")

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("MEMBER 3 - ERROR MINING & ERRORTREE VERIFICATION")
    print("="*60)
    
    try:
        test_task_1_error_taxonomy()
        test_task_2_error_extraction()
        test_task_3_error_classification()
        test_task_4_error_tree()
        test_task_5_end_to_end_pipeline()
        test_task_6_integration_interface()
        
        print("="*60)
        print("*** ALL TESTS PASSED - MEMBER 3 IMPLEMENTATION COMPLETE ***")
        print("="*60)
        print("\nYour implementation includes:")
        print("[OK] 7 error categories")
        print("[OK] 20 DSA subskills")
        print("[OK] 18 error patterns with severity scores")
        print("[OK] Regex-based error extraction")
        print("[OK] Test result analysis")
        print("[OK] Error classification by category & subskill")
        print("[OK] ErrorTree decision framework")
        print("[OK] Conceptual gap diagnosis")
        print("[OK] Complete end-to-end pipeline")
        print("[OK] Integration interfaces for Members 2, 4, 6")
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] ERROR: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
