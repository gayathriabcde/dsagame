"""
Submission Processing Service - MongoDB Atlas Backend for Member 3
Handles submission storage, error detection, and error mapping
"""

from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from error_mining_interface import analyze_learner_submission
from error_taxonomy import DSASubskill

class SubmissionService:
    def __init__(self, connection_string: str = None, db_name: str = "dsagame"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB Atlas connection string
            db_name: Database name
        """
        if connection_string is None:
            connection_string = "mongodb://localhost:27017/"  # Default for local testing
        
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.submissions = self.db["submissions"]
        self.error_logs = self.db["error_logs"]
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for performance"""
        self.submissions.create_index([("student_id", 1), ("submitted_at", -1)])
        self.submissions.create_index([("problem_id", 1)])
        self.error_logs.create_index([("student_id", 1), ("detected_at", -1)])
        self.error_logs.create_index([("submission_id", 1)])
    
    def process_submission(self, student_id: int, problem_id: int, code: str,
                          test_results: Dict, problem_skills: List[DSASubskill]) -> Dict:
        """
        Process submission and return analysis for Member 2
        
        Returns:
            Complete analysis with submission_id for Member 2 integration
        """
        # Analyze submission using Member 3 core
        analysis = analyze_learner_submission(code, test_results, problem_skills)
        
        # Prepare submission document
        submission_doc = {
            "student_id": student_id,
            "problem_id": problem_id,
            "code": code,
            "language": "python",
            "test_passed": test_results.get('passed', False),
            "overall_severity": analysis['overall_severity'],
            "skills_correct": [s.value for s in analysis['skills_correct']],
            "skills_incorrect": [s.value for s in analysis['skills_incorrect']],
            "submitted_at": datetime.utcnow(),
            "errors": []
        }
        
        # Embed error details
        for error in analysis['detected_errors']:
            error_doc = {
                "error_id": error.error_id,
                "error_category": error.pattern.category.value,
                "confidence": error.confidence,
                "context": error.context,
                "line_number": error.line_number,
                "affected_subskills": [s.value for s in error.pattern.affected_subskills],
                "severity": error.pattern.severity,
                "recommended_focus": self._get_focus_areas(error.pattern.affected_subskills)
            }
            submission_doc["errors"].append(error_doc)
        
        # Insert submission
        result = self.submissions.insert_one(submission_doc)
        submission_id = str(result.inserted_id)
        
        # Store separate error logs for analytics
        for error in analysis['detected_errors']:
            error_log = {
                "submission_id": result.inserted_id,
                "student_id": student_id,
                "problem_id": problem_id,
                "error_id": error.error_id,
                "error_category": error.pattern.category.value,
                "confidence": error.confidence,
                "context": error.context,
                "line_number": error.line_number,
                "affected_subskills": [s.value for s in error.pattern.affected_subskills],
                "severity": error.pattern.severity,
                "detected_at": datetime.utcnow()
            }
            self.error_logs.insert_one(error_log)
        
        # Add submission_id to analysis
        analysis['submission_id'] = submission_id
        return analysis
    
    def _get_focus_areas(self, skills) -> List[str]:
        """Get focus areas for skills"""
        from error_tree import ErrorTree
        tree = ErrorTree()
        focus = []
        for skill in skills:
            focus.extend(tree._get_focus_areas(skill))
        return list(set(focus))
    
    def get_submission_history(self, student_id: int, limit: int = 10) -> List[Dict]:
        """Get recent submissions for a student"""
        cursor = self.submissions.find(
            {"student_id": student_id}
        ).sort("submitted_at", -1).limit(limit)
        
        submissions = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            submissions.append(doc)
        return submissions
    
    def get_submission_by_id(self, submission_id: str) -> Optional[Dict]:
        """Get submission by ID"""
        doc = self.submissions.find_one({"_id": ObjectId(submission_id)})
        if doc:
            doc['_id'] = str(doc['_id'])
        return doc
    
    def get_student_skill_performance(self, student_id: int) -> Dict:
        """
        Get aggregated skill performance for Member 2
        Returns skill-wise correct/incorrect counts
        """
        pipeline = [
            {"$match": {"student_id": student_id}},
            {"$project": {
                "skills_correct": 1,
                "skills_incorrect": 1,
                "overall_severity": 1
            }}
        ]
        
        results = list(self.submissions.aggregate(pipeline))
        
        skill_stats = {}
        for result in results:
            for skill in result.get('skills_correct', []):
                if skill not in skill_stats:
                    skill_stats[skill] = {"correct": 0, "incorrect": 0}
                skill_stats[skill]["correct"] += 1
            
            for skill in result.get('skills_incorrect', []):
                if skill not in skill_stats:
                    skill_stats[skill] = {"correct": 0, "incorrect": 0}
                skill_stats[skill]["incorrect"] += 1
        
        return skill_stats
    
    def get_error_analysis(self, submission_id: str) -> Dict:
        """Get detailed error analysis for a submission"""
        submission = self.get_submission_by_id(submission_id)
        if not submission:
            return {"error": "Submission not found"}
        
        return {
            "submission_id": submission_id,
            "student_id": submission["student_id"],
            "problem_id": submission["problem_id"],
            "test_passed": submission["test_passed"],
            "overall_severity": submission["overall_severity"],
            "skills_correct": submission["skills_correct"],
            "skills_incorrect": submission["skills_incorrect"],
            "errors": submission["errors"]
        }
