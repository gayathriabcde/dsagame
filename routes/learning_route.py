"""
Learning Route - Concurrency-safe asynchronous event ingestion.

POST /learn - Idempotent event ingestion with submission_id
GET /state/<student_id> - Returns computed learner state
GET /event/<event_id> - Returns event completion status
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from db import Database
from pymongo.errors import DuplicateKeyError

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/learn', methods=['POST'])
def ingest_learning_event():
    """
    Ingest a learning event with idempotency protection.
    
    Request JSON:
        {
            "submission_id": "unique_submission_id",  # REQUIRED for idempotency
            "student_id": "s1",
            "problem_id": "binary_search_01",
            "result": {"correct": false, "attempts": 2, "solve_time": 83},
            "diagnosis": {"skills": ["binary_search"], "error_type": "off_by_one"}
        }
    
    Response JSON:
        {
            "status": "accepted",
            "event_id": "507f1f77bcf86cd799439011"
        }
    
    Status Codes:
        202 - Accepted (new event)
        200 - OK (duplicate submission_id, returns existing event_id)
        400 - Invalid input
        500 - Internal error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate submission_id (required for idempotency)
        if 'submission_id' not in data:
            return jsonify({'error': 'submission_id is required'}), 400
        
        if not isinstance(data['submission_id'], str) or not data['submission_id']:
            return jsonify({'error': 'submission_id must be a non-empty string'}), 400
        
        # Validate required fields
        required_fields = ['student_id', 'problem_id', 'result', 'diagnosis']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {missing}'}), 400
        
        # Validate result structure
        result = data['result']
        result_fields = ['correct', 'attempts', 'solve_time']
        missing_result = [f for f in result_fields if f not in result]
        if missing_result:
            return jsonify({'error': f'Missing result fields: {missing_result}'}), 400
        
        # Validate diagnosis structure
        diagnosis = data['diagnosis']
        if 'skills' not in diagnosis:
            return jsonify({'error': 'Missing diagnosis.skills'}), 400
        
        if not isinstance(diagnosis['skills'], list) or not diagnosis['skills']:
            return jsonify({'error': 'diagnosis.skills must be a non-empty list'}), 400
        
        # Validate data types
        if not isinstance(result['correct'], bool):
            return jsonify({'error': 'result.correct must be boolean'}), 400
        
        if not isinstance(result['attempts'], int) or result['attempts'] < 1:
            return jsonify({'error': 'result.attempts must be positive integer'}), 400
        
        if not isinstance(result['solve_time'], (int, float)) or result['solve_time'] < 0:
            return jsonify({'error': 'result.solve_time must be non-negative number'}), 400
        
        db = Database.get_db()
        
        # Check if submission_id already exists (idempotency)
        existing_event = db.learning_events.find_one({'submission_id': data['submission_id']})
        
        if existing_event:
            # Return existing event_id (idempotent)
            return jsonify({
                'status': 'accepted',
                'event_id': str(existing_event['_id'])
            }), 200
        
        # Store new event
        event_doc = {
            'submission_id': data['submission_id'],
            'student_id': data['student_id'],
            'problem_id': data['problem_id'],
            'timestamp': datetime.utcnow(),
            'result': result,
            'diagnosis': diagnosis,
            'processing': {
                'bkt': False,
                'learner_state': False
            },
            'completed': False
        }
        
        try:
            insert_result = db.learning_events.insert_one(event_doc)
            
            return jsonify({
                'status': 'accepted',
                'event_id': str(insert_result.inserted_id)
            }), 202
            
        except DuplicateKeyError:
            # Race condition: another request inserted same submission_id
            existing_event = db.learning_events.find_one({'submission_id': data['submission_id']})
            return jsonify({
                'status': 'accepted',
                'event_id': str(existing_event['_id'])
            }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500


@learning_bp.route('/event/<event_id>', methods=['GET'])
def get_event_status(event_id):
    """
    Get event completion status.
    
    Frontend polls this to check if event processing is complete.
    
    Response JSON:
        {
            "event_id": "507f1f77bcf86cd799439011",
            "completed": true,
            "student_id": "s1"
        }
    
    Status Codes:
        200 - Success
        404 - Event not found
        500 - Internal error
    """
    try:
        from bson import ObjectId
        
        # Validate ObjectId format
        try:
            obj_id = ObjectId(event_id)
        except:
            return jsonify({'error': 'Invalid event_id format'}), 400
        
        db = Database.get_db()
        
        event = db.learning_events.find_one({'_id': obj_id})
        
        if not event:
            return jsonify({'error': f'Event {event_id} not found'}), 404
        
        return jsonify({
            'event_id': event_id,
            'completed': event.get('completed', False),
            'student_id': event['student_id']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500


@learning_bp.route('/state/<student_id>', methods=['GET'])
def get_learner_state(student_id):
    """
    Get computed learner state for a student.
    
    Response JSON:
        {
            "student_id": "s1",
            "weak_skills": ["binary_search"],
            "learning_state": "struggling",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    
    Status Codes:
        200 - Success
        404 - State not found
        500 - Internal error
    """
    try:
        db = Database.get_db()
        
        state = db.learner_state.find_one(
            {'student_id': student_id},
            sort=[('updated_at', -1)]
        )
        
        if not state:
            return jsonify({
                'error': f'No learner state found for student {student_id}. '
                        'Events may still be processing.'
            }), 404
        
        state.pop('_id', None)
        
        if 'updated_at' in state:
            state['updated_at'] = state['updated_at'].isoformat()
        
        return jsonify(state), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500
