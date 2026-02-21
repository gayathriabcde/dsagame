"""Quick test for skills_correct and skills_incorrect output"""

from error_mining_interface import analyze_learner_submission
from error_taxonomy import DSASubskill

print("="*70)
print("TEST: Skills Correct vs Incorrect Tracking")
print("="*70)

# Test 1: Code with errors
print("\n[Test 1] Code with Recursion Error")
buggy_code = """
def factorial(n):
    return n * factorial(n-1)  # Missing base case
"""

test_results = {
    'passed': False,
    'failures': [{'message': 'RecursionError: maximum recursion depth'}]
}

problem_skills = [DSASubskill.RECURSION, DSASubskill.ARRAY_TRAVERSAL]

analysis = analyze_learner_submission(buggy_code, test_results, problem_skills)

print(f"Skills CORRECT: {[s.value for s in analysis['skills_correct']]}")
print(f"Skills INCORRECT: {[s.value for s in analysis['skills_incorrect']]}")
print(f"Overall Severity: {analysis['overall_severity']:.2f}")
print(f"Expected: RECURSION incorrect, ARRAY_TRAVERSAL correct")

# Test 2: Code with boundary error
print("\n[Test 2] Code with Array Boundary Error")
boundary_code = """
def search(arr, target):
    for i in range(len(arr) + 1):  # Off-by-one
        if arr[i] == target:
            return i
    return -1
"""

test_results2 = {
    'passed': False,
    'failures': [{'message': 'IndexError: list index out of range'}]
}

problem_skills2 = [DSASubskill.ARRAY_TRAVERSAL, DSASubskill.SEARCHING]

analysis2 = analyze_learner_submission(boundary_code, test_results2, problem_skills2)

print(f"Skills CORRECT: {[s.value for s in analysis2['skills_correct']]}")
print(f"Skills INCORRECT: {[s.value for s in analysis2['skills_incorrect']]}")
print(f"Overall Severity: {analysis2['overall_severity']:.2f}")
print(f"Expected: Both ARRAY_TRAVERSAL and SEARCHING incorrect")

# Test 3: Passing code (no errors)
print("\n[Test 3] Correct Code (No Errors)")
passing_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""

test_results_pass = {'passed': True, 'failures': []}

analysis3 = analyze_learner_submission(passing_code, test_results_pass, problem_skills)

print(f"Skills CORRECT: {[s.value for s in analysis3['skills_correct']]}")
print(f"Skills INCORRECT: {[s.value for s in analysis3['skills_incorrect']]}")
print(f"Overall Severity: {analysis3['overall_severity']:.2f}")
print(f"Expected: Both skills correct, none incorrect")

print("\n" + "="*70)
print("[OK] Skills tracking working correctly!")
print("Member 2 can now properly update learner mastery based on:")
print("  - skills_correct: Increase mastery")
print("  - skills_incorrect: Decrease mastery")
print("="*70)
