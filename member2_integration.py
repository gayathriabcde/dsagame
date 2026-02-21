"""
Member 2 Integration Helper - Smooth integration between Member 3 and Member 2
Provides easy-to-use functions for updating learner state
"""

from submission_service import SubmissionService
from error_taxonomy import DSASubskill
from typing import Dict, List

class Member2Integration:
    """
    Helper class for Member 2 to easily integrate with Member 3
    """
    
    def __init__(self, connection_string: str = None):
        self.service = SubmissionService(connection_string)
    
    def process_and_get_updates(self, student_id: int, problem_id: int, 
                                code: str, test_results: Dict, 
                                problem_skills: List[DSASubskill]) -> Dict:
        """
        Process submission and return ONLY what Member 2 needs
        
        Returns:
            {
                'student_id': int,
                'problem_id': int,
                'skills_to_increase': [DSASubskill],  # Got correct
                'skills_to_decrease': [DSASubskill],  # Got wrong
                'severity': float,  # How much to decrease (0.0-1.0)
                'submission_id': str
            }
        """
        # Process submission
        analysis = self.service.process_submission(
            student_id, problem_id, code, test_results, problem_skills
        )
        
        # Return clean format for Member 2
        return {
            'student_id': student_id,
            'problem_id': problem_id,
            'skills_to_increase': analysis['skills_correct'],
            'skills_to_decrease': analysis['skills_incorrect'],
            'severity': analysis['overall_severity'],
            'submission_id': analysis['submission_id'],
            'conceptual_gaps': analysis['conceptual_gaps']  # For deeper analysis
        }
    
    def get_skill_performance(self, student_id: int) -> Dict:
        """
        Get aggregated skill performance for a student
        
        Returns:
            {
                'recursion': {'correct': 5, 'incorrect': 2},
                'array_traversal': {'correct': 8, 'incorrect': 1},
                ...
            }
        """
        return self.service.get_student_skill_performance(student_id)
    
    def get_recent_submissions(self, student_id: int, limit: int = 10) -> List[Dict]:
        """Get recent submission history"""
        return self.service.get_submission_history(student_id, limit)
    
    def calculate_mastery_update(self, current_mastery: float, 
                                 is_correct: bool, severity: float = 0.5) -> float:
        """
        Helper to calculate new mastery value
        
        Args:
            current_mastery: Current mastery level (0.0-1.0)
            is_correct: True if skill was correct, False if incorrect
            severity: Error severity (0.0-1.0), only used if is_correct=False
        
        Returns:
            New mastery value (0.0-1.0)
        """
        if is_correct:
            # Increase mastery (diminishing returns as mastery increases)
            increase = 0.1 * (1 - current_mastery)
            return min(1.0, current_mastery + increase)
        else:
            # Decrease mastery based on severity
            decrease = severity * 0.2
            return max(0.0, current_mastery - decrease)


# Example usage for Member 2
if __name__ == "__main__":
    print("="*70)
    print("MEMBER 2 INTEGRATION EXAMPLE")
    print("="*70)
    
    # Initialize integration
    integration = Member2Integration()
    
    # Sample submission
    student_id = 1
    problem_id = 101
    code = """
def factorial(n):
    return n * factorial(n-1)  # Missing base case
"""
    test_results = {
        'passed': False,
        'failures': [{'message': 'RecursionError: maximum recursion depth'}]
    }
    problem_skills = [DSASubskill.RECURSION, DSASubskill.ARRAY_TRAVERSAL]
    
    # Process submission
    print("\n[1] Processing submission...")
    updates = integration.process_and_get_updates(
        student_id, problem_id, code, test_results, problem_skills
    )
    
    print(f"    Submission ID: {updates['submission_id']}")
    print(f"    Skills to INCREASE: {[s.value for s in updates['skills_to_increase']]}")
    print(f"    Skills to DECREASE: {[s.value for s in updates['skills_to_decrease']]}")
    print(f"    Severity: {updates['severity']:.2f}")
    
    # Update learner mastery (Member 2's job)
    print("\n[2] Updating learner mastery...")
    current_mastery = {
        DSASubskill.RECURSION: 0.6,
        DSASubskill.ARRAY_TRAVERSAL: 0.7
    }
    
    for skill in updates['skills_to_increase']:
        old = current_mastery[skill]
        new = integration.calculate_mastery_update(old, is_correct=True)
        print(f"    {skill.value}: {old:.2f} -> {new:.2f} (INCREASED)")
        current_mastery[skill] = new
    
    for skill in updates['skills_to_decrease']:
        old = current_mastery[skill]
        new = integration.calculate_mastery_update(old, is_correct=False, 
                                                   severity=updates['severity'])
        print(f"    {skill.value}: {old:.2f} -> {new:.2f} (DECREASED)")
        current_mastery[skill] = new
    
    # Get skill performance
    print("\n[3] Getting skill performance history...")
    performance = integration.get_skill_performance(student_id)
    for skill, stats in performance.items():
        print(f"    {skill}: {stats['correct']} correct, {stats['incorrect']} incorrect")
    
    print("\n" + "="*70)
    print("INTEGRATION COMPLETE - Member 2 can now update learner state!")
    print("="*70)
