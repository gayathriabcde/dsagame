"""
Learning Service - Core business logic for adaptive learning pipeline.

Orchestrates the learning event processing:
1. Update student mastery (BKT)
2. Compute weak skills
3. Determine learning state
"""

from datetime import datetime
from services.mastery_service import MasteryService
from models.student_model import StudentModel

class LearningService:
    """Orchestrates learning event processing."""
    
    @staticmethod
    def process_learning_event(student_id, problem_id, result, diagnosis):
        """
        Process a learning event and update student model.
        
        Args:
            student_id: Student identifier
            problem_id: Problem identifier
            result: Dict with {correct, attempts, solve_time}
            diagnosis: Dict with {skills, error_type, concept, severity}
            
        Returns:
            dict: {
                status: "updated",
                mastery_update: {skill_id: {old, new}},
                weak_skills: [skill_ids],
                learning_state: "struggling" | "learning" | "mastered"
            }
            
        Raises:
            ValueError: If student not found or invalid input
        """
        # Validate student exists
        student = StudentModel.get_student(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Get current mastery before update
        old_masteries = StudentModel.get_student_skills(student_id)
        
        # Extract data from result and diagnosis
        correct = result['correct']
        attempts = result['attempts']
        solve_time = result['solve_time']
        
        skills = diagnosis['skills']
        error_type = diagnosis.get('error_type')
        
        # Update mastery using existing BKT service
        updated_masteries = MasteryService.update_student_performance(
            student_id=student_id,
            problem_id=problem_id,
            skills=skills,
            correct=correct,
            error_type=error_type,
            attempts=attempts,
            solve_time=solve_time
        )
        
        # Build mastery update response
        mastery_update = {}
        for skill_id in skills:
            mastery_update[skill_id] = {
                'old': old_masteries.get(skill_id, 0.2),
                'new': updated_masteries[skill_id]
            }
        
        # Get all current masteries for analysis
        all_masteries = StudentModel.get_student_skills(student_id)
        
        # Compute weak skills (mastery < 0.4)
        weak_skills = [
            skill_id for skill_id, mastery in all_masteries.items()
            if mastery < 0.4
        ]
        
        # Determine learning state based on average mastery
        avg_mastery = sum(all_masteries.values()) / len(all_masteries)
        learning_state = LearningService._compute_learning_state(avg_mastery)
        
        return {
            'status': 'updated',
            'mastery_update': mastery_update,
            'weak_skills': weak_skills,
            'learning_state': learning_state
        }
    
    @staticmethod
    def _compute_learning_state(avg_mastery):
        """
        Compute learning state from average mastery.
        
        Args:
            avg_mastery: Average mastery across all skills
            
        Returns:
            str: "struggling" | "learning" | "mastered"
        """
        if avg_mastery < 0.4:
            return "struggling"
        elif avg_mastery <= 0.7:
            return "learning"
        else:
            return "mastered"
