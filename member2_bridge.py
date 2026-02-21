"""
Bridge: Member 3 Error Analysis → Member 2 Learner State
Converts Member 3's output to Member 2's /learn endpoint format
"""

import sys
sys.path.append('../member2_work')

from error_mining_interface import analyze_learner_submission
from error_taxonomy import DSASubskill
import requests

# Member 2 skill mapping
SKILL_MAP = {
    DSASubskill.ARRAY_TRAVERSAL: "arrays",
    DSASubskill.ARRAY_MANIPULATION: "arrays",
    DSASubskill.SEARCHING: "binary_search",
    DSASubskill.TWO_POINTER: "two_pointers",
    DSASubskill.HASH_TABLE: "hashmaps",
    DSASubskill.RECURSION: "recursion",
    DSASubskill.STACK_OPS: "stack_queue",
    DSASubskill.QUEUE_OPS: "stack_queue",
    DSASubskill.SLIDING_WINDOW: "sliding_window",
    DSASubskill.DYNAMIC_PROGRAMMING: "dynamic_programming",
    DSASubskill.GRAPH_TRAVERSAL: "graphs",
    DSASubskill.GRAPH_ALGORITHMS: "graphs",
}

def convert_to_member2_format(submission_id: str, student_id: str, problem_id: str,
                               code: str, test_results: dict, problem_skills: list,
                               attempts: int = 1, solve_time: float = 0) -> dict:
    """
    Convert Member 3 analysis to Member 2 /learn format
    
    Returns: dict ready for POST /learn
    """
    analysis = analyze_learner_submission(code, test_results, problem_skills)
    
    # Map skills to Member 2 format
    mapped_skills = list(set(
        SKILL_MAP.get(skill, skill.value) 
        for skill in problem_skills 
        if skill in SKILL_MAP
    ))
    
    # Determine error type
    error_type = "none"
    if analysis['detected_errors']:
        error_type = analysis['detected_errors'][0].pattern.category.value
    
    return {
        "submission_id": submission_id,
        "student_id": student_id,
        "problem_id": problem_id,
        "result": {
            "correct": test_results.get('passed', False),
            "attempts": attempts,
            "solve_time": solve_time
        },
        "diagnosis": {
            "skills": mapped_skills,
            "error_type": error_type,
            "severity": analysis['overall_severity']
        }
    }

def send_to_member2(member2_url: str, payload: dict) -> dict:
    """Send to Member 2 backend"""
    response = requests.post(f"{member2_url}/learn", json=payload)
    return response.json()

# Example usage
if __name__ == "__main__":
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
        submission_id="sub_001",
        student_id="s1",
        problem_id="binary_search_problem",
        code=code,
        test_results=test_results,
        problem_skills=[DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL],
        attempts=1,
        solve_time=45.5
    )
    
    print("Payload for Member 2:")
    print(payload)
