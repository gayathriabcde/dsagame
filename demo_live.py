"""
DSA Game - Live Demo
Shows Member 3 analyzing different student submissions
"""

from error_mining_interface import analyze_learner_submission
from error_taxonomy import DSASubskill
from member2_bridge import convert_to_member2_format
import json

print("=" * 80)
print("DSA GAME - MEMBER 3 ERROR ANALYSIS DEMO")
print("=" * 80)

# Test Case 1: Binary Search with boundary error
print("\n[TEST 1] Binary Search - Boundary Error")
print("-" * 80)
code1 = """
def binary_search(arr, target):
    left, right = 0, len(arr)  # Bug: should be len(arr)-1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
"""
test1 = {'passed': False, 'failures': [{'message': 'IndexError: list index out of range'}]}
analysis1 = analyze_learner_submission(code1, test1, [DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL])
print(f"Errors: {len(analysis1['detected_errors'])}")
print(f"Severity: {analysis1['overall_severity']:.2f}")
print(f"Skills Incorrect: {[s.value for s in analysis1['skills_incorrect']]}")

# Test Case 2: Recursion without base case
print("\n[TEST 2] Factorial - Missing Base Case")
print("-" * 80)
code2 = """
def factorial(n):
    return n * factorial(n-1)  # Missing base case
"""
test2 = {'passed': False, 'failures': [{'message': 'RecursionError: maximum recursion depth'}]}
analysis2 = analyze_learner_submission(code2, test2, [DSASubskill.RECURSION])
print(f"Errors: {len(analysis2['detected_errors'])}")
print(f"Severity: {analysis2['overall_severity']:.2f}")
print(f"Skills Incorrect: {[s.value for s in analysis2['skills_incorrect']]}")

# Test Case 3: Correct solution
print("\n[TEST 3] Two Sum - Correct Solution")
print("-" * 80)
code3 = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
    return []
"""
test3 = {'passed': True, 'failures': []}
analysis3 = analyze_learner_submission(code3, test3, [DSASubskill.HASH_TABLE, DSASubskill.ARRAY_TRAVERSAL])
print(f"Errors: {len(analysis3['detected_errors'])}")
print(f"Severity: {analysis3['overall_severity']:.2f}")
print(f"Skills Correct: {[s.value for s in analysis3['skills_correct']]}")

# Show Member 2 integration
print("\n[INTEGRATION] Converting to Member 2 Format")
print("-" * 80)
payload = convert_to_member2_format(
    submission_id="demo_001",
    student_id="student_demo",
    problem_id="binary_search",
    code=code1,
    test_results=test1,
    problem_skills=[DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL],
    attempts=1,
    solve_time=60.0
)
print(json.dumps(payload, indent=2))

print("\n" + "=" * 80)
print("DEMO COMPLETE - Member 3 Error Analysis Working!")
print("=" * 80)
