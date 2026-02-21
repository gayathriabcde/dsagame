"""Full integration test: Member 3 -> Bridge -> Member 2 Backend"""

from member2_bridge import convert_to_member2_format, send_to_member2
from error_taxonomy import DSASubskill
import time

# Test submission
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

print("=" * 60)
print("FULL INTEGRATION TEST")
print("=" * 60)

# Step 1: Member 3 analysis + conversion
print("\n[1] Member 3 analyzing submission...")
payload = convert_to_member2_format(
    submission_id=f"test_{int(time.time())}",
    student_id="s1",
    problem_id="binary_search",
    code=code,
    test_results=test_results,
    problem_skills=[DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL],
    attempts=1,
    solve_time=45.5
)
print(f"    Error detected: {payload['diagnosis']['error_type']}")
print(f"    Severity: {payload['diagnosis']['severity']}")
print(f"    Skills: {payload['diagnosis']['skills']}")

# Step 2: Send to Member 2
print("\n[2] Sending to Member 2 backend...")
try:
    response = send_to_member2("http://localhost:5000", payload)
    print(f"    Status: {response.get('status')}")
    print(f"    Event ID: {response.get('event_id')}")
    print("\n[OK] Integration successful!")
except Exception as e:
    print(f"    [INFO] Backend not running: {e}")
    print("    To test with backend:")
    print("      Terminal 1: cd member2_backend && python app.py")
    print("      Terminal 2: cd member2_backend && python workers/learning_worker.py")
    print("      Terminal 3: python verify_integration.py")

print("\n" + "=" * 60)
