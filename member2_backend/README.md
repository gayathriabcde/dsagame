
# dsagame

# DSA Tutor Backend Base

Async learning pipeline with learner state modeling for DSA tutoring system.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Create `.env` file:

```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/dsagame
DB_NAME=dsagame
```

### 3. Run Backend

**Terminal 1: Start API Server**
```bash
python app.py
```

**Terminal 2: Start Background Worker** (Required)
```bash
python workers/learning_worker.py
```

## API Endpoints

### POST /learn
Submit learning event after student submission.

**Request:**
```json
{
  "submission_id": "unique_submission_id",
  "student_id": "student_123",
  "problem_id": "two_sum",
  "result": {
    "correct": true,
    "attempts": 1,
    "solve_time": 45.5
  },
  "diagnosis": {
    "skills": ["arrays", "hashmaps"],
    "error_type": "logic",
    "severity": 0.7
  }
}
```

**Response:**
```json
{
  "status": "accepted",
  "event_id": "507f1f77bcf86cd799439011"
}
```

### GET /event/<event_id>
Check if event processing is complete.

**Response:**
```json
{
  "event_id": "507f1f77bcf86cd799439011",
  "completed": true,
  "student_id": "student_123"
}
```

### GET /state/<student_id>
Get computed learner state.

**Response:**
```json
{
  "student_id": "student_123",
  "weak_skills": ["binary_search"],
  "learning_state": "learning",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### POST /students/create
Create a new student.

**Request:**
```json
{
  "student_id": "student_123"
}
```

## Integration Flow

```
Your Module → POST /learn → Background Worker → Mastery Update
                                    ↓
                            GET /state/<student_id>
```

**Important:** Do NOT directly modify student mastery. Always use `/learn` endpoint.

## Module Ownership

**Learner Modeling (Member 2):** This backend module  
**Error Analysis (Member 3):** Provides diagnosis data  
**Sequencing (Member 4):** Uses weak_skills for recommendations  
**Gamification (Member 5):** Uses learning_state for feedback  
**Content (Member 1):** Provides problems mapped to skills.json

## Skills

Available skills defined in `skills.json`:
- arrays
- strings
- two_pointers
- binary_search
- hashmaps
- recursion
- stack_queue
- sliding_window
- dynamic_programming
- graphs

## Architecture

- **Async Event-Driven:** Events processed in background
- **Concurrency-Safe:** Multiple workers supported
- **Idempotent:** Safe network retries with submission_id
- **Temporal Ordering:** Per-student event ordering maintained

## Notes

- Worker must be running for event processing
- Poll `/event/<event_id>` for completion before fetching state
- Use unique `submission_id` for each submission
- Learning state: "struggling" | "learning" | "mastered"
- Weak skills: mastery < 0.4
