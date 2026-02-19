# Team Backend Integration Guide

This backend already contains the learner modeling system (knowledge estimation).
Do NOT modify its internal logic. You only send learning events to it.

The backend is event-driven.

---

SYSTEM FLOW

Your module → POST /learn → Worker → Mastery Update → GET /state

You never update skills yourself.

---

HOW TO RUN BACKEND

1. Install
   pip install -r requirements.txt

2. Setup database
   Create MongoDB Atlas database named: dsagame

Add .env file:
MONGO_URI=mongodb+srv://ginikuntahasini_db_user:VzUfsnHtCvlXcjwc@cluster0.eu6m8hq.mongodb.net/
DB_NAME=adaptive_tutor

3. Start server
   python app.py

4. Start worker (required)
   python workers/learning_worker.py

---

HOW YOUR MODULE SENDS DATA

After a student submission, send ONE request:

POST /learn

Body:
{
"submission_id": "unique_id",
"student_id": "s1",
"problem_id": "two_sum",
"result": {
"correct": true,
"attempts": 1,
"solve_time": 40
},
"diagnosis": {
"skills": ["arrays","hashmaps"],
"error_type": "logic",
"severity": 0.5
}
}

Do NOT compute mastery yourself.

---

WAIT FOR PROCESSING

Poll event status:

GET /event/<event_id>

When completed=true, fetch state:

GET /state/<student_id>

Response:
{
"weak_skills": [...],
"learning_state": "learning"
}

Use this to decide next action.

---

WHAT EACH TEAM MEMBER SHOULD DO

Member 3 (Error Analysis)

* Detect errors
* Map to skills
* Send diagnosis

Member 4 (Sequencer)

* Read weak_skills
* Choose next problem

Member 5 (Gamification)

* Show feedback based on learning_state

Member 1 (Content)

* Provide problems mapped to skills.json

Member 2 (Backend – already done)

* Maintains student knowledge model

---

IMPORTANT RULES

Never:

* update student_skills collection
* modify mastery values
* reorder events
* bypass /learn endpoint

Always:

* send submission_id
* send mapped skills
* wait for completion before next recommendation

---

If you break these rules the learner model becomes invalid.
Treat it as a black-box knowledge engine.
