# DSA Game - Member 2 + Member 3 Integration

## Project Structure

```
DSA_GAME/
├── Member 3: Error Mining (Root)
│   ├── error_taxonomy.py          # Error patterns & DSA skills
│   ├── error_extractor.py         # Error detection
│   ├── error_tree.py              # ErrorTree decision framework
│   ├── error_mining_interface.py  # Main interface for other members
│   ├── submission_service.py      # Submission storage
│   ├── execution_feedback.py      # User-friendly feedback
│   └── api_endpoints.py           # Member 3 REST API
│
├── Member 2: Learner State (member2_backend/)
│   ├── app.py                     # Flask API server
│   ├── workers/learning_worker.py # Background processor
│   ├── models/                    # BKT & mastery models
│   ├── routes/                    # API routes
│   └── services/                  # Learning services
│
└── Integration
    ├── member2_bridge.py          # Member 3 → Member 2 converter
    └── test_full_flow.py          # E2E test
```

## Quick Start

### Member 3 Only (Error Analysis)
```bash
pip install -r requirements.txt
python test_member3.py
```

### Member 2 Only (Learner State)
```bash
cd member2_backend
pip install -r requirements.txt
python app.py  # Terminal 1
python workers/learning_worker.py  # Terminal 2
```

### Full Integration
```bash
# Install both
pip install -r requirements.txt
cd member2_backend && pip install -r requirements.txt && cd ..

# Run Member 2 backend
cd member2_backend
start python app.py
start python workers/learning_worker.py
cd ..

# Test integration
python test_full_flow.py
```

## Integration Flow

```
Student Submission
       ↓
Member 3: error_mining_interface.analyze_learner_submission()
       ↓
Bridge: member2_bridge.convert_to_member2_format()
       ↓
Member 2: POST /learn
       ↓
Background Worker: Update mastery
       ↓
GET /state/<student_id> → weak_skills
```

## For Other Members

### Member 4 (Adaptive Sequencing)
Use Member 3's output:
```python
from error_mining_interface import analyze_learner_submission

analysis = analyze_learner_submission(code, test_results, problem_skills)
priority_skills = analysis['priority_skills']  # What to teach next
conceptual_gaps = analysis['conceptual_gaps']  # Specific weaknesses
```

### Member 5 (Gamification)
Use Member 2's output:
```python
import requests
response = requests.get('http://localhost:5000/state/student_1')
state = response.json()
# state['learning_state']: "struggling" | "learning" | "mastered"
# state['weak_skills']: List of skills needing practice
```

## API Endpoints

### Member 3 (Port 5001)
- `POST /api/submit` - Analyze code submission
- `GET /api/submissions/<student_id>` - Get history
- `GET /api/errors/<submission_id>` - Get error details

### Member 2 (Port 5000)
- `POST /learn` - Submit learning event
- `GET /state/<student_id>` - Get learner state
- `GET /event/<event_id>` - Check processing status

## Testing

```bash
# Test Member 3
python test_member3.py

# Test integration
python test_full_flow.py

# Test with live backend
python verify_integration.py
```

See `INTEGRATION_README.md` for detailed setup.
