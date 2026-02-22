"""
API Endpoints for Member 3 - Submission Processing with MongoDB
Flask core_routes for submission analysis and error retrieval
"""

from flask import Flask, request, jsonify
from submission_service import SubmissionService
from execution_feedback import ExecutionFeedback, format_for_display
from error_taxonomy import DSASubskill
from member2_integration import Member2Integration
import config

app = Flask(__name__)

# Initialize core_services with MongoDB
submission_service = SubmissionService(config.MONGO_URI, config.DATABASE_NAME)
feedback_generator = ExecutionFeedback()
member2_integration = Member2Integration(config.MONGO_URI)

@app.route('/api/submit', methods=['POST'])
def submit_code():
    """
    Process code submission
    
    Request body:
    {
        "student_id": int,
        "problem_id": int,
        "code": str,
        "test_results": {...},
        "problem_skills": [str]  // e.g., ["SEARCHING", "ARRAY_TRAVERSAL"]
    }
    """
    data = request.json
    
    # Convert skill strings to DSASubskill enums
    problem_skills = [DSASubskill[s] for s in data.get('problem_skills', [])]
    
    # Process submission
    analysis = submission_service.process_submission(
        student_id=data['student_id'],
        problem_id=data['problem_id'],
        code=data['code'],
        test_results=data['test_results'],
        problem_skills=problem_skills
    )
    
    # Generate feedback
    feedback = feedback_generator.generate_feedback(analysis)
    
    return jsonify({
        'submission_id': analysis['submission_id'],
        'feedback': feedback,
        'member2_data': {  # Data specifically for Member 2
            'skills_correct': [s.value for s in analysis['skills_correct']],
            'skills_incorrect': [s.value for s in analysis['skills_incorrect']],
            'overall_severity': analysis['overall_severity'],
            'priority_skills': [s.value for s in analysis['priority_skills']]
        }
    })

@app.route('/api/member2/process', methods=['POST'])
def member2_process():
    """
    Dedicated endpoint for Member 2 integration
    Returns only what Member 2 needs
    """
    data = request.json
    problem_skills = [DSASubskill[s] for s in data.get('problem_skills', [])]
    
    updates = member2_integration.process_and_get_updates(
        student_id=data['student_id'],
        problem_id=data['problem_id'],
        code=data['code'],
        test_results=data['test_results'],
        problem_skills=problem_skills
    )
    
    return jsonify({
        'student_id': updates['student_id'],
        'problem_id': updates['problem_id'],
        'skills_to_increase': [s.value for s in updates['skills_to_increase']],
        'skills_to_decrease': [s.value for s in updates['skills_to_decrease']],
        'severity': updates['severity'],
        'submission_id': updates['submission_id']
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

@app.route('/api/member2/skill-performance/<int:student_id>', methods=['GET'])
def get_skill_performance(student_id):
    """Get skill performance for Member 2"""
    performance = member2_integration.get_skill_performance(student_id)
    return jsonify({'student_id': student_id, 'skill_performance': performance})

if __name__ == '__main__':
    app.run(debug=True, port=5003)
