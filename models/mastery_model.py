"""Mastery update model with deterministic calculations (DEPRECATED - Use BKT)."""
from config import Config

class MasteryModel:
    """Legacy deterministic mastery update calculations."""
    
    @staticmethod
    def update_mastery(old_mastery, correct):
        """
        Calculate new mastery value based on performance (LEGACY).
        
        NOTE: This is deprecated. Use BKTModel for probabilistic updates.
        Kept for backward compatibility only.
        
        Args:
            old_mastery: Current mastery value (0.0-1.0)
            correct: Whether the attempt was correct
            
        Returns:
            float: New mastery value clamped to [MIN_MASTERY, MAX_MASTERY]
        """
        if correct:
            new_mastery = old_mastery + Config.LEARN_GAIN * (1 - old_mastery)
        else:
            new_mastery = old_mastery - Config.ERROR_PENALTY * old_mastery
        
        return max(Config.MIN_MASTERY, min(Config.MAX_MASTERY, new_mastery))
    @staticmethod
    def clamp_mastery(mastery):
        """
        Clamp mastery value to valid range (LEGACY).
        
        Args:
            mastery: Mastery value to clamp
            
        Returns:
            float: Clamped mastery value
        """
        return max(Config.MIN_MASTERY, min(Config.MAX_MASTERY, mastery))
