"""
MongoDB Backend Demo - Member 3 with Member 2 Integration
Demonstrates submission processing with MongoDB Atlas
"""

from member2_integration import Member2Integration
from error_taxonomy import DSASubskill

def demo_mongodb_integration():
    """Demo: Complete MongoDB integration with Member 2"""
    
    print("\n" + "="*70)
    print("MEMBER 3 - MONGODB ATLAS INTEGRATION DEMO")
    print("="*70)
    
    # Initialize (uses local MongoDB for demo, replace with Atlas URI)
    integration = Member2Integration()
    
    # Sample buggy code
    buggy_code = """
def binary_search(arr, target):
    left, right = 0, len(arr)  # Wrong bound
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
    
    # Process submission (Member 2 calls this)
    print("\n[1] Member 2 processes submission...")
    updates = integration.process_and_get_updates(
        student_id=1,
        problem_id=101,
        code=buggy_code,
        test_results=test_results,
        problem_skills=problem_skills
    )
    
    print(f"    Submission ID: {updates['submission_id']}")
    print(f"    Skills to INCREASE: {[s.value for s in updates['skills_to_increase']]}")
    print(f"    Skills to DECREASE: {[s.value for s in updates['skills_to_decrease']]}")
    print(f"    Severity: {updates['severity']:.2f}")
    
    # Member 2 updates learner mastery
    print("\n[2] Member 2 updates learner mastery...")
    
    # Simulate current mastery
    current_mastery = {
        DSASubskill.SEARCHING: 0.7,
        DSASubskill.ARRAY_TRAVERSAL: 0.6
    }
    
    print("    Before:")
    for skill, mastery in current_mastery.items():
        print(f"      {skill.value}: {mastery:.2f}")
    
    # Update mastery
    for skill in updates['skills_to_increase']:
        old = current_mastery[skill]
        new = integration.calculate_mastery_update(old, is_correct=True)
        current_mastery[skill] = new
    
    for skill in updates['skills_to_decrease']:
        old = current_mastery[skill]
        new = integration.calculate_mastery_update(old, is_correct=False, 
                                                   severity=updates['severity'])
        current_mastery[skill] = new
    
    print("    After:")
    for skill, mastery in current_mastery.items():
        print(f"      {skill.value}: {mastery:.2f}")
    
    # Get skill performance history
    print("\n[3] Member 2 retrieves skill performance...")
    performance = integration.get_skill_performance(student_id=1)
    if performance:
        for skill, stats in list(performance.items())[:3]:
            print(f"    {skill}: {stats['correct']} correct, {stats['incorrect']} incorrect")
    else:
        print("    (No historical data yet)")
    
    # Get recent submissions
    print("\n[4] Member 2 retrieves submission history...")
    history = integration.get_recent_submissions(student_id=1, limit=3)
    for sub in history:
        print(f"    - Submission {sub['_id']}: Problem {sub['problem_id']}, "
              f"Passed: {sub['test_passed']}, Severity: {sub['overall_severity']:.2f}")
    
    print("\n" + "="*70)
    print("MONGODB INTEGRATION COMPLETE!")
    print("="*70)
    print("\nMember 2 can now:")
    print("  1. Process submissions and get skill updates")
    print("  2. Update learner mastery based on correct/incorrect skills")
    print("  3. Retrieve skill performance history")
    print("  4. Access submission history")
    print("\nAll data stored in MongoDB Atlas!")
    print("="*70)

if __name__ == "__main__":
    try:
        demo_mongodb_integration()
    except Exception as e:
        print(f"\nNote: {e}")
        print("\nTo run with MongoDB Atlas:")
        print("1. Update config.py with your MongoDB Atlas connection string")
        print("2. Install: pip install pymongo dnspython")
        print("3. Run this demo again")
