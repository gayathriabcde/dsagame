from member2_backend.db import Database

class ProblemModel:
    @staticmethod
    def get_candidate_problems(weak_skills: list, current_problem_id: str, target_challenge: float,
                               margin: float = 0.2):
        """
        Fetches only problems matching the student's weak skills and within the target difficulty range.
        """
        db = Database.get_db()

        query = {
            "_id": {"$ne": str(current_problem_id)},
            "skills": {"$in": weak_skills},
            "difficulty": {
                "$gte": max(0.0, target_challenge - margin),
                "$lte": min(1.0, target_challenge + margin)
            }
        }

        candidates = list(db.problems.find(query))

        if not candidates:
            fallback_query = {
                "_id": {"$ne": str(current_problem_id)},
                "skills": {"$in": weak_skills}
            }
            candidates = list(db.problems.find(fallback_query))

        if not candidates:
            final_query = {
                "_id": {"$ne": str(current_problem_id)},
                "difficulty": {
                    "$gte": max(0.0, target_challenge - margin),
                    "$lte": min(1.0, target_challenge + margin)
                }
            }
            candidates = list(db.problems.find(final_query))

        return candidates

    @staticmethod
    def get_problem_by_id(problem_id):
        db = Database.get_db()
        return db.problems.find_one({"_id": str(problem_id)})