from error_tree import ErrorMiningPipeline
from error_taxonomy import DSASubskill

def analyze_learner_submission(code: str, test_results: dict) -> dict:
    """
    Main interface for Member 2 (Learner State) and Member 4 (Adaptive Sequencing)
    
    Args:
        code: Learner's submitted code
        test_results: Test execution results with pass/fail info
    
    Returns:
        Analysis containing detected errors, conceptual gaps, and priority skills
    """
    pipeline = ErrorMiningPipeline()
    return pipeline.analyze(code, test_results)

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
    
    analysis = analyze_learner_submission(sample_code, sample_test_results)
    
    print("=== Error Mining Analysis ===")
    print(f"\nDetected {len(analysis['detected_errors'])} errors")
    print(f"Overall Severity: {analysis['overall_severity']:.2f}")
    
    print("\n--- Conceptual Gaps ---")
    for gap in analysis['conceptual_gaps']:
        print(f"  {gap.subskill.value}: severity={gap.severity:.2f}, errors={gap.error_count}")
        print(f"    Focus: {', '.join(gap.recommended_focus)}")
    
    print("\n--- Priority Skills for Next Quest ---")
    for skill in analysis['priority_skills']:
        print(f"  - {skill.value}")
