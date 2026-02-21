# Member 3 Files - Simple Explanation for Member 2 (MongoDB Version)

## What Member 3 Does
When a student submits code, Member 3 analyzes it and tells you:
- Which skills the student got RIGHT ✓
- Which skills the student got WRONG ✗
- How severe the mistakes are (0.0 = perfect, 1.0 = critical)
- **Stores everything in MongoDB Atlas**

---

## Files You Need to Know About

### 1. **member2_integration.py** - YOUR MAIN FILE ⭐⭐⭐
**What it does:** The ONE class you use for everything

**How to use:**
```python
from member2_integration import Member2Integration
from error_taxonomy import DSASubskill

# Initialize once
integration = Member2Integration("your_mongodb_atlas_uri")

# When student submits code
updates = integration.process_and_get_updates(
    student_id=1,
    problem_id=101,
    code="student's code",
    test_results={'passed': False, 'failures': [...]},
    problem_skills=[DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL]
)

# What you get:
updates['skills_to_increase']  # List[DSASubskill] - increase mastery
updates['skills_to_decrease']  # List[DSASubskill] - decrease mastery
updates['severity']            # float (0.0-1.0) - how much to decrease
updates['submission_id']       # str - MongoDB document ID
```

**Helper function for mastery calculation:**
```python
# Calculate new mastery value
new_mastery = integration.calculate_mastery_update(
    current_mastery=0.6,
    is_correct=False,
    severity=0.8
)
# Returns: 0.44 (decreased by 0.8 * 0.2 = 0.16)
```

---

### 2. **error_taxonomy.py** - The Dictionary
**What it does:** Defines all possible errors and skills

**Contains:**
- 20 DSA skills (RECURSION, ARRAY_TRAVERSAL, SEARCHING, etc.)
- 18 error patterns

**For Member 2:** Import DSASubskill from here
```python
from error_taxonomy import DSASubskill

# Use these in your learner state
all_skills = list(DSASubskill)
```

---

### 3. **submission_service.py** - MongoDB Manager
**What it does:** Handles all MongoDB operations

**MongoDB Collections:**
- `submissions` - All student code submissions
- `error_logs` - Detected errors for analytics

**For Member 2:** You don't call this directly, use member2_integration.py instead

---

### 4. **config.py** - MongoDB Configuration
**What it does:** Stores MongoDB Atlas connection string

**Setup:**
```python
# Update this file with your MongoDB Atlas URI
MONGO_URI = "mongodb+srv://<username>:<password>@cluster.mongodb.net/"
DATABASE_NAME = "dsagame"
```

---

### 5. **api_endpoints.py** - REST API (Optional)
**What it does:** Provides HTTP endpoints

**Special endpoint for Member 2:**
```
POST /api/member2/process
{
  "student_id": 1,
  "problem_id": 101,
  "code": "...",
  "test_results": {...},
  "problem_skills": ["SEARCHING", "ARRAY_TRAVERSAL"]
}

Returns:
{
  "skills_to_increase": [...],
  "skills_to_decrease": [...],
  "severity": 0.8,
  "submission_id": "..."
}
```

---

## MongoDB Atlas Setup (5 minutes)

1. **Create free cluster:** https://www.mongodb.com/cloud/atlas
2. **Create database user** with password
3. **Whitelist IP:** 0.0.0.0/0 (for testing)
4. **Get connection string** from "Connect" button
5. **Update config.py** with your connection string

---

## Complete Member 2 Integration Example

```python
from member2_integration import Member2Integration
from error_taxonomy import DSASubskill
import config

class LearnerState:
    def __init__(self, student_id):
        self.student_id = student_id
        self.mastery = {skill: 0.5 for skill in DSASubskill}
        # Initialize Member 3 integration
        self.member3 = Member2Integration(config.MONGO_URI)
    
    def process_submission(self, problem_id, code, test_results, problem_skills):
        """Process submission and update mastery"""
        
        # Get updates from Member 3
        updates = self.member3.process_and_get_updates(
            self.student_id, problem_id, code, test_results, problem_skills
        )
        
        # Update mastery for correct skills (INCREASE)
        for skill in updates['skills_to_increase']:
            self.mastery[skill] = self.member3.calculate_mastery_update(
                self.mastery[skill],
                is_correct=True
            )
        
        # Update mastery for incorrect skills (DECREASE)
        for skill in updates['skills_to_decrease']:
            self.mastery[skill] = self.member3.calculate_mastery_update(
                self.mastery[skill],
                is_correct=False,
                severity=updates['severity']
            )
        
        return updates
    
    def get_skill_history(self):
        """Get historical skill performance"""
        return self.member3.get_skill_performance(self.student_id)

# Usage
learner = LearnerState(student_id=1)
updates = learner.process_submission(
    problem_id=101,
    code="...",
    test_results={...},
    problem_skills=[DSASubskill.SEARCHING]
)
```

---

## Summary - What Member 2 Needs

**ONE class to use:**
```python
Member2Integration(mongodb_uri)
```

**ONE method to call:**
```python
process_and_get_updates(student_id, problem_id, code, test_results, problem_skills)
```

**THREE things you get:**
1. `skills_to_increase` - Increase mastery for these
2. `skills_to_decrease` - Decrease mastery for these
3. `severity` - How much to decrease (0.0-1.0)

**BONUS helper:**
```python
calculate_mastery_update(current, is_correct, severity)
```

**That's it!** Everything is stored in MongoDB Atlas automatically.
