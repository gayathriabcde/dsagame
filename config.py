"""
MongoDB Atlas Configuration
Update with your actual connection string
"""

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"

# Database name
DATABASE_NAME = "dsagame"

# Collections
COLLECTIONS = {
    "submissions": "submissions",
    "error_logs": "error_logs",
    "students": "students",  # For Member 2
    "student_skills": "student_skills"  # For Member 2
}

# Example: How to set up MongoDB Atlas
"""
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Create database user
4. Whitelist your IP (or use 0.0.0.0/0 for testing)
5. Get connection string
6. Replace <username>, <password>, <cluster> in MONGO_URI above
"""

# For local testing (without Atlas)
LOCAL_MONGO_URI = "mongodb://localhost:27017/"
