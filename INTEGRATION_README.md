# Member 2 + Member 3 Integration

## Architecture

```
Student Submission
       ↓
Member 3: Error Analysis (error_mining_interface.py)
       ↓
Bridge: member2_bridge.py (converts format)
       ↓
Member 2: POST /learn (member2_backend/app.py)
       ↓
Background Worker: Updates mastery
       ↓
GET /state/<student_id> → Weak skills for sequencing
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r member2_backend/requirements.txt
```

### 2. Setup MongoDB
Update `member2_backend/.env`:
```
MONGO_URI=your_mongodb_uri
DB_NAME=dsagame
```

### 3. Run Member 2 Backend
**Terminal 1:**
```bash
cd member2_backend
python app.py
```

**Terminal 2:**
```bash
cd member2_backend
python workers/learning_worker.py
```

### 4. Test Integration
```bash
python test_integration.py
```

## Usage

```python
from member2_bridge import convert_to_member2_format, send_to_member2
from error_taxonomy import DSASubskill

# After student submission
payload = convert_to_member2_format(
    submission_id="unique_id",
    student_id="s1",
    problem_id="binary_search",
    code=student_code,
    test_results=test_results,
    problem_skills=[DSASubskill.SEARCHING, DSASubskill.ARRAY_TRAVERSAL],
    attempts=1,
    solve_time=45.5
)

# Send to Member 2
response = send_to_member2("http://localhost:5000", payload)
```

## Files

- `member2_bridge.py` - Converts Member 3 → Member 2 format
- `member2_backend/` - Your Member 2 learner state backend
- `error_mining_interface.py` - Member 3's analysis interface
- `error_taxonomy.py` - Shared skill definitions
