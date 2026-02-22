import math
from models.problem_model import ProblemModel
from models.sequence_log_model import SequenceLogModel

class KFFSequencer:
    def __init__(self, gamma=0.25, alpha=1.0, beta=0.6):
        self.gamma = gamma
        self.alpha = alpha
        self.beta = beta

    def calculate_momentum(self, recent_results: list) -> float:
        if not recent_results: return 0.0
        momentum = 0.0
        decay = 0.75
        for i, res in enumerate(reversed(recent_results)):
            weight = math.pow(decay, i)
            impact = 1.0 if res.get('correct') else -1.0
            momentum += impact * weight
        return max(-1.0, min(1.0, momentum / len(recent_results)))

    def get_next_problem(self, student_id: str, current_problem_id: str, weak_skills: list,
                         bkt_mastery: float) -> tuple:
        # 1. Calculate Target Challenge First
        recent_results = SequenceLogModel.get_recent_results(student_id)
        v = self.calculate_momentum(recent_results)
        target_challenge = max(0.0, min(1.0, bkt_mastery + (self.gamma * v)))

        # 2. Let MongoDB do the heavy filtering
        candidate_problems = ProblemModel.get_candidate_problems(
            weak_skills=weak_skills,
            current_problem_id=current_problem_id,
            target_challenge=target_challenge
        )

        best_problem = None
        lowest_energy = float('inf')
        recent_skills = SequenceLogModel.get_recent_skills(student_id)

        # 3. Run the objective function only on the highly relevant subset
        for prob in candidate_problems:
            difficulty = prob.get('difficulty', 0.5)
            stagnation = 1.0 if prob.get('primary_skill') in recent_skills else 0.0

            # Flow Divergence Energy
            energy = (self.alpha * (difficulty - target_challenge) ** 2) + (self.beta * stagnation)

            if energy < lowest_energy:
                lowest_energy = energy
                best_problem = prob

        metrics = {"mastery": bkt_mastery, "momentum": v, "target_challenge": target_challenge}
        return best_problem, metrics