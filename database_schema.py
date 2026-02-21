"""
MongoDB Schema for Member 3 - Submission Processing Layer
Collections: submissions, error_logs
"""

# MongoDB Atlas connection configuration
MONGO_CONFIG = {
    "connection_string": "mongodb+srv://<username>:<password>@cluster.mongodb.net/",
    "database_name": "dsagame",
    "collections": {
        "submissions": "submissions",
        "error_logs": "error_logs"
    }
}

# Collection Schemas (for documentation)
SUBMISSION_SCHEMA = {
    "_id": "ObjectId",  # Auto-generated
    "student_id": "int",
    "problem_id": "int",
    "code": "string",
    "language": "string",
    "test_passed": "bool",
    "overall_severity": "float",
    "skills_correct": ["string"],  # List of skill names
    "skills_incorrect": ["string"],  # List of skill names
    "submitted_at": "datetime",
    "errors": [  # Embedded error documents
        {
            "error_id": "string",
            "error_category": "string",
            "confidence": "float",
            "context": "string",
            "line_number": "int",
            "affected_subskills": ["string"],
            "severity": "float",
            "recommended_focus": ["string"]
        }
    ]
}

ERROR_LOG_SCHEMA = {
    "_id": "ObjectId",
    "submission_id": "ObjectId",  # Reference to submission
    "student_id": "int",
    "problem_id": "int",
    "error_id": "string",
    "error_category": "string",
    "confidence": "float",
    "context": "string",
    "line_number": "int",
    "affected_subskills": ["string"],
    "severity": "float",
    "detected_at": "datetime"
}

# Indexes for performance
INDEXES = {
    "submissions": [
        {"keys": [("student_id", 1), ("submitted_at", -1)]},
        {"keys": [("problem_id", 1)]}
    ],
    "error_logs": [
        {"keys": [("student_id", 1), ("detected_at", -1)]},
        {"keys": [("submission_id", 1)]}
    ]
}

def get_schema_info():
    """Returns MongoDB schema information"""
    return {
        "config": MONGO_CONFIG,
        "submission_schema": SUBMISSION_SCHEMA,
        "error_log_schema": ERROR_LOG_SCHEMA,
        "indexes": INDEXES
    }
