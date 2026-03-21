"""
API Endpoints for Member 3 - Submission Processing with MongoDB
Flask routes for submission analysis and error retrieval
"""

from flask import Flask, request, jsonify
from submission_service import SubmissionService
from execution_feedback import ExecutionFeedback
from error_taxonomy import DSASubskill
from member2_bridge import convert_to_member2_format, send_to_member2
import config

app = Flask(__name__)

submission_service = SubmissionService(config.MONGO_URI, config.DATABASE_NAME)
feedback_generator = ExecutionFeedback()

@app.route('/api/submit', methods=['POST'])
def submit_code():
    """
    Called by Member 4 after code execution.
    Analyzes submission, sends diagnosis to Member 2, returns feedback.

    Request body:
    {
        "submission_id": str,
        "student_id": str,
        "problem_id": str,
        "code": str,
        "test_results": {"passed": bool, "failures": [...]},
        "problem_skills": ["SEARCHING", "ARRAY_TRAVERSAL"],
        "attempts": int,
        "solve_time": float
    }
    """
    data = request.json

    problem_skills = [DSASubskill[s] for s in data.get('problem_skills', [])]

    # Process submission and generate feedback
    analysis = submission_service.process_submission(
        student_id=data['student_id'],
        problem_id=data['problem_id'],
        code=data['code'],
        test_results=data['test_results'],
        problem_skills=problem_skills
    )
    feedback = feedback_generator.generate_feedback(analysis)

    # Convert and send to Member 2 learner state backend
    member2_payload = convert_to_member2_format(
        submission_id=data['submission_id'],
        student_id=str(data['student_id']),
        problem_id=str(data['problem_id']),
        code=data['code'],
        test_results=data['test_results'],
        problem_skills=problem_skills,
        attempts=data.get('attempts', 1),
        solve_time=data.get('solve_time', 0)
    )
    try:
        send_to_member2(config.MEMBER2_URL, member2_payload)
    except Exception:
        pass  # Member 2 backend may not be running yet

    return jsonify({
        'submission_id': analysis['submission_id'],
        'feedback': feedback,
        'diagnosis': {
            'skills_correct': [s.value for s in analysis['skills_correct']],
            'skills_incorrect': [s.value for s in analysis['skills_incorrect']],
            'overall_severity': analysis['overall_severity'],
            'priority_skills': [s.value for s in analysis['priority_skills']]
        }
    })



@app.route('/api/submissions/<int:student_id>', methods=['GET'])
def get_submissions(student_id):
    """Get submission history for a student"""
    limit = request.args.get('limit', 10, type=int)
    history = submission_service.get_submission_history(student_id, limit)
    return jsonify({'submissions': history})

@app.route('/api/submission/<submission_id>', methods=['GET'])
def get_submission(submission_id):
    """Get specific submission details"""
    submission = submission_service.get_submission_by_id(submission_id)
    if submission:
        return jsonify(submission)
    return jsonify({'error': 'Submission not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
