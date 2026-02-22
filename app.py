"""Main Flask application for Learner State & Mastery Modeling."""
from flask import Flask, jsonify
from db import Database
from core_routes.student_routes import student_bp
from core_routes.learning_route import learning_bp
from core_routes.submission_routes import submission_bp
from utils.skill_loader import SkillLoader

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Learner State & Mastery Modeling',
        'version': '1.0.0'
    }), 200

@app.route('/skills', methods=['GET'])
def get_skills():
    """Get all available skills."""
    skills = SkillLoader.load_skills()
    return jsonify({'skills': skills}), 200

app.register_blueprint(student_bp)
app.register_blueprint(learning_bp)
app.register_blueprint(submission_bp)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

def initialize_app():
    """Initialize database and load skills."""
    try:
        Database.initialize()
        SkillLoader.load_skills()
        print(f"✓ Loaded {len(SkillLoader.get_skill_ids())} skills")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        raise

if __name__ == '__main__':
    initialize_app()
    print("=" * 50)
    print("Learner State & Mastery Modeling API")
    print("=" * 50)
    print("Server running on http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
