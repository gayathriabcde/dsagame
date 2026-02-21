from error_tree import ErrorMiningPipeline
from error_taxonomy import DSASubskill

def analyze_learner_submission(code: str, test_results: dict, problem_skills: list = None) -> dict:
    """
    Main interface for Member 2 (Learner State) and Member 4 (Adaptive Sequencing)
    
    Args:
        code: Learner's submitted code
        test_results: Test execution results with pass/fail info
        problem_skills: List of DSASubskills required for the problem
    
    Returns:
        Analysis containing detected errors, conceptual gaps, priority skills,
        skills_correct (passed), and skills_incorrect (failed)
    """
    pipeline = ErrorMiningPipeline()
    analysis = pipeline.analyze(code, test_results)
    
    # Determine correct vs incorrect skills
    if problem_skills:
        # Get all skills affected by detected errors
        affected_skills = set()
        for error in analysis['detected_errors']:
            affected_skills.update(error.pattern.affected_subskills)
        
        # Skills with errors are INCORRECT
        analysis['skills_incorrect'] = [s for s in problem_skills if s in affected_skills]
        # Skills without errors are CORRECT
        analysis['skills_correct'] = [s for s in problem_skills if s not in affected_skills]
    else:
        # If no problem_skills provided, all affected skills are incorrect
        affected_skills = set()
        for error in analysis['detected_errors']:
            affected_skills.update(error.pattern.affected_subskills)
        analysis['skills_incorrect'] = list(affected_skills)
        analysis['skills_correct'] = []
    
    return analysis

# Example usage
if __name__ == "__main__":
    sample_code = """
def binary_search(arr, target):
    left, right = 0, len(arr)
    while left <= right:
        mid = (left + right) / 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
    
    sample_test_results = {
        'passed': False,
        'failures': [
            {
                'test_case': 'boundary_test',
                'message': 'IndexError: list index out of range',
                'expected': 4,
                'actual': None
            }
        ]
    }
    
    # Skills required for binary search problem
    problem_skills = [DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL]
    
    analysis = analyze_learner_submission(sample_code, sample_test_results, problem_skills)
    
    print("=== Error Mining Analysis ===")
    print(f"\nDetected {len(analysis['detected_errors'])} errors")
    print(f"Overall Severity: {analysis['overall_severity']:.2f}")
    
    print("\n--- Skills Assessment (for Member 2) ---")
    print(f"Skills CORRECT: {[s.value for s in analysis['skills_correct']]}")
    print(f"Skills INCORRECT: {[s.value for s in analysis['skills_incorrect']]}")
    
    print("\n--- Conceptual Gaps ---")
    for gap in analysis['conceptual_gaps']:
        print(f"  {gap.subskill.value}: severity={gap.severity:.2f}, errors={gap.error_count}")
        print(f"    Focus: {', '.join(gap.recommended_focus)}")
    
    print("\n--- Priority Skills for Next Quest ---")
    for skill in analysis['priority_skills']:
        print(f"  - {skill.value}")
