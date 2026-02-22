"""Student API core_routes."""
from flask import Blueprint, request, jsonify
from core_models.student_model import StudentModel
from core_services.mastery_service import MasteryService

student_bp = Blueprint('students', __name__, url_prefix='/students')

@student_bp.route('/create', methods=['POST'])
def create_student():
    """
    Create a new student and initialize all skills.
    
    Request JSON:
        {
            "student_id": "string"
        }
    
    Returns:
        JSON: Created student info with status 201
    """
    try:
        data = request.get_json()
        
        if not data or 'student_id' not in data:
            return jsonify({'error': 'student_id is required'}), 400
        
        student_id = data['student_id']
        
        if not student_id or not isinstance(student_id, str):
            return jsonify({'error': 'student_id must be a non-empty string'}), 400
        
        student = StudentModel.create_student(student_id)
        skills = StudentModel.get_student_skills(student_id)
        
        return jsonify({
            'student_id': student_id,
            'created_at': student['created_at'].isoformat(),
            'skills_initialized': len(skills)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@student_bp.route('/<student_id>/state', methods=['GET'])
def get_student_state(student_id):
    """
    Get student mastery state for all skills.
    
    Returns:
        JSON: Dictionary mapping skill_id to mastery value
    """
    try:
        student = StudentModel.get_student(student_id)
        
        if not student:
            return jsonify({'error': f'Student {student_id} not found'}), 404
        
        skills = StudentModel.get_student_skills(student_id)
        
        return jsonify({
            'student_id': student_id,
            'mastery': skills
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@student_bp.route('/<student_id>/update', methods=['POST'])
def update_student(student_id):
    """
    Update student mastery based on problem attempt.
    
    Request JSON:
        {
            "problem_id": "string",
            "skills": ["skill1", "skill2"],
            "correct": true/false,
            "error_type": "string" (optional),
            "attempts": int,
            "solve_time": float
        }
    
    Returns:
        JSON: Updated mastery values
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['problem_id', 'skills', 'correct', 'attempts', 'solve_time']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            return jsonify({'error': f'Missing required fields: {missing}'}), 400
        
        problem_id = data['problem_id']
        skills = data['skills']
        correct = data['correct']
        error_type = data.get('error_type')
        attempts = data['attempts']
        solve_time = data['solve_time']
        
        if not isinstance(skills, list) or not skills:
            return jsonify({'error': 'skills must be a non-empty list'}), 400
        
        if not isinstance(correct, bool):
            return jsonify({'error': 'correct must be a boolean'}), 400
        
        if not isinstance(attempts, int) or attempts < 1:
            return jsonify({'error': 'attempts must be a positive integer'}), 400
        
        if not isinstance(solve_time, (int, float)) or solve_time < 0:
            return jsonify({'error': 'solve_time must be a non-negative number'}), 400
        
        updated_masteries = MasteryService.update_student_performance(
            student_id, problem_id, skills, correct, error_type, attempts, solve_time
        )
        
        return jsonify({
            'student_id': student_id,
            'problem_id': problem_id,
            'updated_masteries': updated_masteries
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@student_bp.route('/<student_id>/weak-skills', methods=['GET'])
def get_weak_skills(student_id):
    """
    Get the 3 weakest skills for a student.
    
    Returns:
        JSON: List of weakest skills with mastery values
    """
    try:
        student = StudentModel.get_student(student_id)
        
        if not student:
            return jsonify({'error': f'Student {student_id} not found'}), 404
        
        weak_skills = StudentModel.get_weakest_skills(student_id, limit=3)
        
        return jsonify({
            'student_id': student_id,
            'weak_skills': weak_skills
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500
