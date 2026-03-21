"""Bayesian Knowledge Tracing model for probabilistic mastery updates."""
import json
import os

class BKTModel:
    """Bayesian Knowledge Tracing implementation."""
    
    _params = None
    _prerequisites = None
    _error_weights = None
    
    @classmethod
    def load_params(cls):
        """Load BKT parameters from configuration file."""
        if cls._params is None:
            params_path = os.path.join(os.path.dirname(__file__), '..', 'bkt_params.json')
            with open(params_path, 'r') as f:
                data = json.load(f)
                cls._params = {k: v for k, v in data.items() 
                              if k not in ['error_type_weights', 'skill_prerequisites']}
                cls._error_weights = data.get('error_type_weights', {})
                cls._prerequisites = data.get('skill_prerequisites', {})
        return cls._params
    
    @classmethod
    def get_skill_params(cls, skill_id):
        """
        Get BKT parameters for a specific skill.
        
        Args:
            skill_id: Skill identifier
            
        Returns:
            dict: BKT parameters {T, G, S}
        """
        params = cls.load_params()
        return params.get(skill_id, params['default'])
    
    @classmethod
    def compute_posterior(cls, prior, correct, skill_id):
        """
        Compute posterior probability using BKT.
        
        Formula:
        If correct: P(L|correct) = P(L)(1-S) / [P(L)(1-S) + (1-P(L))G]
        If incorrect: P(L|incorrect) = P(L)S / [P(L)S + (1-P(L))(1-G)]
        
        Args:
            prior: Prior mastery probability P(L)
            correct: Whether answer was correct
            skill_id: Skill identifier for parameters
            
        Returns:
            float: Posterior probability
        """
        params = cls.get_skill_params(skill_id)
        G = params['G']  # Guess probability
        S = params['S']  # Slip probability
        
        if correct:
            numerator = prior * (1 - S)
            denominator = prior * (1 - S) + (1 - prior) * G
        else:
            numerator = prior * S
            denominator = prior * S + (1 - prior) * (1 - G)
        
        # Avoid division by zero
        if denominator < 1e-10:
            return prior
        
        return numerator / denominator
    
    @classmethod
    def apply_learning(cls, posterior, skill_id):
        """
        Apply learning transition probability.
        
        Formula: P(L_next) = posterior + (1 - posterior) * T
        
        Args:
            posterior: Posterior probability after evidence
            skill_id: Skill identifier
            
        Returns:
            float: Updated mastery with learning
        """
        params = cls.get_skill_params(skill_id)
        T = params['T']  # Learning transition probability
        
        return posterior + (1 - posterior) * T
    
    @classmethod
    def get_error_weight(cls, error_type):
        """
        Get evidence weight based on error type.
        
        Args:
            error_type: Type of error made
            
        Returns:
            float: Weight multiplier (default 1.0)
        """
        if cls._error_weights is None:
            cls.load_params()
        
        if not error_type:
            return 1.0
        
        # Match error type (case-insensitive, partial match)
        error_lower = error_type.lower()
        for key, weight in cls._error_weights.items():
            if key in error_lower or error_lower in key:
                return weight
        
        return 1.0
    
    @classmethod
    def compute_confidence(cls, attempts, solve_time):
        """
        Compute confidence weight based on attempts and time.
        
        Formula: confidence = 1 / (1 + attempts * 0.3 + time_minutes * 0.05)
        
        Args:
            attempts: Number of attempts
            solve_time: Time taken in seconds
            
        Returns:
            float: Confidence weight [0, 1]
        """
        time_minutes = solve_time / 60.0
        confidence = 1.0 / (1.0 + attempts * 0.3 + time_minutes * 0.05)
        return max(0.01, min(1.0, confidence))
    
    @classmethod
    def update_mastery(cls, old_mastery, correct, skill_id, error_type=None, 
                      attempts=1, solve_time=0.0):
        """
        Full BKT mastery update with all enhancements.
        
        Args:
            old_mastery: Current mastery value
            correct: Whether answer was correct
            skill_id: Skill identifier
            error_type: Type of error (if incorrect)
            attempts: Number of attempts
            solve_time: Time taken in seconds
            
        Returns:
            tuple: (new_mastery, posterior, confidence, bkt_params)
        """
        # Get BKT parameters
        params = cls.get_skill_params(skill_id)
        
        # Compute posterior probability
        posterior = cls.compute_posterior(old_mastery, correct, skill_id)
        
        # Apply error type weighting for incorrect answers
        if not correct and error_type:
            error_weight = cls.get_error_weight(error_type)
            # Adjust posterior toward lower mastery for severe errors
            if error_weight > 1.0:
                posterior = posterior / error_weight
                posterior = max(0.01, posterior)
        
        # Apply learning transition
        p_l_next = cls.apply_learning(posterior, skill_id)
        
        # Compute confidence weight
        confidence = cls.compute_confidence(attempts, solve_time)
        
        # Weighted update
        new_mastery = old_mastery + confidence * (p_l_next - old_mastery)
        
        # Clamp to valid range
        new_mastery = max(0.01, min(0.99, new_mastery))
        
        return new_mastery, posterior, confidence, params
    
    @classmethod
    def get_prerequisite_boost(cls, skill_id, student_skills):
        """
        Calculate mastery boost from prerequisite skills.
        
        Args:
            skill_id: Target skill identifier
            student_skills: Dict of skill_id -> mastery
            
        Returns:
            float: Boost amount (0.0 to 0.05)
        """
        if cls._prerequisites is None:
            cls.load_params()
        
        prerequisites = cls._prerequisites.get(skill_id, [])
        if not prerequisites:
            return 0.0
        
        # Check if all prerequisites are mastered (>0.75)
        boost = 0.0
        for prereq in prerequisites:
            prereq_mastery = student_skills.get(prereq, 0.0)
            if prereq_mastery > 0.75:
                boost += 0.05
        
        return min(boost, 0.05)  # Max boost of 0.05
    
    @classmethod
    def clamp_mastery(cls, mastery):
        """
        Clamp mastery to valid BKT range.
        
        Args:
            mastery: Mastery value
            
        Returns:
            float: Clamped value [0.01, 0.99]
        """
        return max(0.01, min(0.99, mastery))
