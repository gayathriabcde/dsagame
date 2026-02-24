"""Database connection module."""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

class Database:
    """MongoDB database connection manager."""
    
    _client = None
    _db = None
    
    @classmethod
    def initialize(cls):
        """Initialize MongoDB connection with validation."""
        try:
            cls._client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            cls._client.admin.command('ping')
            cls._db = cls._client[Config.DB_NAME]
            cls._create_indexes()
            print(f"✓ Connected to MongoDB: {Config.DB_NAME}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"✗ MongoDB connection failed: {e}")
            raise
    
    @classmethod
    def _create_indexes(cls):
        """Create necessary indexes for performance."""
        cls._db.students.create_index('student_id', unique=True)
        cls._db.student_skills.create_index([('student_id', 1), ('skill_id', 1)], unique=True)
        cls._db.skill_history.create_index([('student_id', 1), ('timestamp', -1)])
        cls._db.performance_history.create_index([('student_id', 1), ('timestamp', -1)])
    
    @classmethod
    def get_db(cls):
        """Get database instance."""
        if cls._db is None:
            cls.initialize()
        return cls._db
    
    @classmethod
    def close(cls):
        """Close database connection."""
        if cls._client:
            cls._client.close()
