"""Test Member 2 + Member 3 Integration"""

from member2_bridge import convert_to_member2_format
from error_taxonomy import DSASubskill

# Test case
code = """
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

test_results = {
    'passed': False,
    'failures': [{'message': 'IndexError: list index out of range'}]
}

payload = convert_to_member2_format(
    submission_id="test_001",
    student_id="s1",
    problem_id="binary_search",
    code=code,
    test_results=test_results,
    problem_skills=[DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL],
    attempts=1,
    solve_time=45.5
)

print("✓ Member 3 analysis complete")
print("✓ Converted to Member 2 format")
print("\nPayload:")
import json
print(json.dumps(payload, indent=2))
print("\n✓ Ready to send to Member 2 backend at POST /learn")
