"""Student model for database operations."""
from datetime import datetime
from db import Database
from utils.skill_loader import SkillLoader

class StudentModel:
    """Handles student data operations."""
    
    @staticmethod
    def create_student(student_id):
        """
        Create a new student and initialize all skills.
        
        Args:
            student_id: Unique student identifier
            
        Returns:
            dict: Created student document
            
        Raises:
            ValueError: If student already exists
        """
        db = Database.get_db()
        
        if db.students.find_one({'student_id': student_id}):
            raise ValueError(f"Student {student_id} already exists")
        
        student_doc = {
            'student_id': student_id,
            'created_at': datetime.utcnow()
        }
        db.students.insert_one(student_doc)
        
        skills = SkillLoader.load_skills()
        skill_docs = [
            {
                'student_id': student_id,
                'skill_id': skill['id'],
                'mastery': 0.2,
                'last_updated': datetime.utcnow(),
                'attempt_count': 0
            }
            for skill in skills
        ]
        db.student_skills.insert_many(skill_docs)
        
        return student_doc
    
    @staticmethod
    def get_student(student_id):
        """
        Get student by ID.
        
        Args:
            student_id: Student identifier
            
        Returns:
            dict: Student document or None
        """
        db = Database.get_db()
        return db.students.find_one({'student_id': student_id})
    
    @staticmethod
    def get_student_skills(student_id):
        """
        Get all skills for a student.
        
        Args:
            student_id: Student identifier
            
        Returns:
            dict: Mapping of skill_id to mastery value
        """
        db = Database.get_db()
        skills = db.student_skills.find({'student_id': student_id})
        return {skill['skill_id']: skill['mastery'] for skill in skills}
    
    @staticmethod
    def get_weakest_skills(student_id, limit=3):
        """
        Get weakest skills for a student.
        
        Args:
            student_id: Student identifier
            limit: Number of skills to return
            
        Returns:
            list: List of dicts with skill_id and mastery
        """
        db = Database.get_db()
        skills = db.student_skills.find(
            {'student_id': student_id}
        ).sort('mastery', 1).limit(limit)
        
        return [
            {'skill_id': skill['skill_id'], 'mastery': skill['mastery']}
            for skill in skills
        ]
