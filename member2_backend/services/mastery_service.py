"""Mastery service for handling skill updates and logging."""
from datetime import datetime
from db import Database
from core_models.bkt_model import BKTModel
from core_models.student_model import StudentModel
from utils.skill_loader import SkillLoader

class MasteryService:
    """Service for mastery updates and performance tracking."""
    
    @staticmethod
    def update_student_performance(student_id, problem_id, skills, correct, 
                                   error_type, attempts, solve_time):
        """
        Update student mastery based on problem attempt.
        
        Args:
            student_id: Student identifier
            problem_id: Problem identifier
            skills: List of skill IDs involved
            correct: Whether attempt was correct
            error_type: Type of error (if incorrect)
            attempts: Number of attempts
            solve_time: Time taken in seconds
            
        Returns:
            dict: Updated mastery values
            
        Raises:
            ValueError: If student or skills are invalid
        """
        db = Database.get_db()
        
        if not db.students.find_one({'student_id': student_id}):
            raise ValueError(f"Student {student_id} not found")
        
        SkillLoader.validate_skill_ids(skills)
        
        timestamp = datetime.utcnow()
        updated_masteries = {}
        
        # Get all student skills for prerequisite boosting
        student_skills = StudentModel.get_student_skills(student_id)
        
        for skill_id in skills:
            skill_doc = db.student_skills.find_one({
                'student_id': student_id,
                'skill_id': skill_id
            })
            
            if not skill_doc:
                raise ValueError(f"Skill {skill_id} not initialized for student {student_id}")
            
            old_mastery = skill_doc['mastery']
            attempt_count = skill_doc.get('attempt_count', 0)
            
            # Apply BKT update
            new_mastery, posterior, confidence, bkt_params = BKTModel.update_mastery(
                old_mastery, correct, skill_id, error_type, attempts, solve_time
            )
            
            # Apply prerequisite boost if applicable
            if attempt_count == 0:  # First attempt
                boost = BKTModel.get_prerequisite_boost(skill_id, student_skills)
                new_mastery = min(0.9, new_mastery + boost)
            
            # Re-estimate mastery after first 3 problems
            if attempt_count == 2:  # After 3rd attempt (0, 1, 2)
                new_mastery = MasteryService._recalibrate_mastery(
                    student_id, skill_id, new_mastery
                )
            
            db.student_skills.update_one(
                {'student_id': student_id, 'skill_id': skill_id},
                {
                    '$set': {
                        'mastery': new_mastery,
                        'last_updated': timestamp
                    },
                    '$inc': {'attempt_count': 1}
                }
            )
            
            db.skill_history.insert_one({
                'student_id': student_id,
                'skill_id': skill_id,
                'old_mastery': old_mastery,
                'new_mastery': new_mastery,
                'problem_id': problem_id,
                'error_type': error_type,
                'timestamp': timestamp,
                'posterior': posterior,
                'confidence': confidence,
                'evidence_type': 'correct' if correct else (error_type or 'incorrect'),
                'bkt_params_used': bkt_params
            })
            
            updated_masteries[skill_id] = new_mastery
        
        db.performance_history.insert_one({
            'student_id': student_id,
            'problem_id': problem_id,
            'skills': skills,
            'correct': correct,
            'attempts': attempts,
            'solve_time': solve_time,
            'error_type': error_type,
            'timestamp': timestamp
        })
        
        return updated_masteries
    
    @staticmethod
    def _recalibrate_mastery(student_id, skill_id, current_mastery):
        """
        Re-estimate mastery after first 3 problems using mean posterior.
        
        Args:
            student_id: Student identifier
            skill_id: Skill identifier
            current_mastery: Current mastery value
            
        Returns:
            float: Recalibrated mastery
        """
        db = Database.get_db()
        
        # Get last 3 skill history entries
        history = list(db.skill_history.find({
            'student_id': student_id,
            'skill_id': skill_id
        }).sort('timestamp', -1).limit(3))
        
        if len(history) < 3:
            return current_mastery
        
        # Calculate mean posterior probability
        posteriors = [h.get('posterior', h['new_mastery']) for h in history]
        mean_posterior = sum(posteriors) / len(posteriors)
        
        # Blend with current mastery (70% mean posterior, 30% current)
        recalibrated = 0.7 * mean_posterior + 0.3 * current_mastery
        
        return BKTModel.clamp_mastery(recalibrated)
