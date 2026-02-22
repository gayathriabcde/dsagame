from member2_backend.db import Database
from datetime import datetime


class SequenceLogModel:
    @staticmethod
    def log_decision(student_id, prev_problem_id, next_problem_id, mastery, momentum, target_challenge, was_correct):
        db = Database.get_db()
        log_entry = {
            "student_id": student_id,
            "prev_problem_id": prev_problem_id,
            "next_problem_id": next_problem_id,
            "was_correct": was_correct,
            "state_snapshot": {
                "mastery": mastery,
                "momentum": momentum,
                "target_challenge": target_challenge
            },
            "timestamp": datetime.utcnow()
        }
        db.sequence_logs.insert_one(log_entry)

    @staticmethod
    def get_recently_failed_skills(student_id, limit=10):
        db = Database.get_db()
        # Find wrong answers in the current session
        logs = list(db.sequence_logs.find({"student_id": student_id, "was_correct": False})
                    .sort("timestamp", -1)
                    .limit(limit))
        failed_skills = []
        for log in logs:
            prob = db.problems.find_one({"_id": log.get("next_problem_id")})
            if prob and 'primary_skill' in prob:
                failed_skills.append(prob['primary_skill'])
        return failed_skills

    @staticmethod
    def get_recent_results(student_id, limit=5):
        db = Database.get_db()
        logs = list(db.sequence_logs.find({"student_id": student_id})
                    .sort("timestamp", -1)
                    .limit(limit))
        return [{"correct": log.get("was_correct", False)} for log in logs]

    @staticmethod
    def get_recent_skills(student_id, limit=3):
        db = Database.get_db()
        logs = list(db.sequence_logs.find({"student_id": student_id})
                    .sort("timestamp", -1)
                    .limit(limit))
        recent_skills = []
        for log in logs:
            prob = db.problems.find_one({"_id": log.get("next_problem_id")})
            if prob and 'primary_skill' in prob:
                recent_skills.append(prob['primary_skill'])
        return recent_skills