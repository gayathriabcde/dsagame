"""Skill loader utility for reading skills.json."""
import json
import os

class SkillLoader:
    """Loads and validates skills from skills.json."""
    
    _skills = None
    _skill_ids = None
    
    @classmethod
    def load_skills(cls):
        """Load skills from skills.json file."""
        if cls._skills is None:
            skills_path = os.path.join(os.path.dirname(__file__), '..', 'skills.json')
            with open(skills_path, 'r') as f:
                data = json.load(f)
                cls._skills = data['skills']
                cls._skill_ids = {skill['id'] for skill in cls._skills}
        return cls._skills
    
    @classmethod
    def get_skill_ids(cls):
        """Get set of valid skill IDs."""
        if cls._skill_ids is None:
            cls.load_skills()
        return cls._skill_ids
    
    @classmethod
    def validate_skill_id(cls, skill_id):
        """Check if skill_id exists in skills.json."""
        return skill_id in cls.get_skill_ids()
    
    @classmethod
    def validate_skill_ids(cls, skill_ids):
        """Validate multiple skill IDs."""
        valid_ids = cls.get_skill_ids()
        invalid = [sid for sid in skill_ids if sid not in valid_ids]
        if invalid:
            raise ValueError(f"Invalid skill IDs: {invalid}")
        return True
