"""
Complete Example: Member 3 - Backend & Code Editor Integration
Demonstrates submission processing, error analysis, and execution feedback
"""

from submission_service import SubmissionService
from execution_feedback import ExecutionFeedback, format_for_display
from error_taxonomy import DSASubskill

def demo_submission_processing():
    """Demo: Complete submission processing flow"""
    
    print("\n" + "="*70)
    print("MEMBER 3 - SUBMISSION PROCESSING DEMO")
    print("="*70)
    
    # Initialize services
    service = SubmissionService(db_path="demo.db")
    feedback_gen = ExecutionFeedback()
    
    # Sample buggy code
    buggy_code = """
def binary_search(arr, target):
    left, right = 0, len(arr)  # E018: Wrong bound
    while left <= right:
        mid = (left + right) / 2  # Should use //
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
    
    test_results = {
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
    
    problem_skills = [DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL]
    
    # Process submission
    print("\n[1] Processing submission...")
    analysis = service.process_submission(
        student_id=1,
        problem_id=101,
        code=buggy_code,
        test_results=test_results,
        problem_skills=problem_skills
    )
    
    print(f"    Submission ID: {analysis['submission_id']}")
    print(f"    Errors detected: {len(analysis['detected_errors'])}")
    print(f"    Overall severity: {analysis['overall_severity']:.2f}")
    
    # Generate feedback
    print("\n[2] Generating execution feedback...")
    feedback = feedback_gen.generate_feedback(analysis)
    
    print(f"    Status: {feedback['status']}")
    print(f"    Severity level: {feedback['severity_level']}")
    print(f"    Mistakes found: {len(feedback['mistakes'])}")
    print(f"    Recommendations: {len(feedback['recommendations'])}")
    
    # Display formatted feedback (as shown in code editor)
    print("\n[3] Code Editor Display:")
    print(format_for_display(feedback))
    
    # Show skills assessment for Member 2
    print("\n[4] Skills Assessment (for Member 2):")
    print(f"    Skills CORRECT: {[s.value for s in analysis['skills_correct']]}")
    print(f"    Skills INCORRECT: {[s.value for s in analysis['skills_incorrect']]}")
    
    # Retrieve submission history
    print("\n[5] Submission History:")
    history = service.get_submission_history(student_id=1, limit=5)
    for sub in history:
        print(f"    - Submission {sub['submission_id']}: "
              f"Problem {sub['problem_id']}, "
              f"Passed: {sub['test_passed']}, "
              f"Severity: {sub['overall_severity']:.2f}")
    
    # Get detailed error analysis
    print("\n[6] Detailed Error Analysis:")
    error_analysis = service.get_error_analysis(analysis['submission_id'])
    for error in error_analysis['errors']:
        print(f"    - {error['error_id']}: {error['error_category']} "
              f"(confidence: {error['confidence']:.2f})")
        for mapping in error.get('mappings', []):
            print(f"      -> Affects: {mapping['subskill']} "
                  f"(severity: {mapping['severity']:.2f})")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE - All Member 3 components working!")
    print("="*70)

if __name__ == "__main__":
    demo_submission_processing()
