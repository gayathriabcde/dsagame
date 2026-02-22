from flask import Blueprint, request, jsonify
from core_services.submission_orchestrator import SubmissionOrchestrator

submission_bp = Blueprint('submission', __name__)


@submission_bp.route('/api/submit', methods=['POST'])
def handle_submission():
    data = request.json

    student_id = data.get('student_id')
    problem_id = data.get('problem_id')
    code = data.get('code')
    attempts = data.get('attempts', 1)

    if not all([student_id, problem_id, code]):
        return jsonify({"error": "Missing required fields"}), 400

    result = SubmissionOrchestrator.process_submission(student_id, problem_id, code, attempts)

    if "error" in result:
        return jsonify(result), 404

    return jsonify(result), 200