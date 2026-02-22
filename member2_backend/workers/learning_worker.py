"""
Learning Worker - Concurrency-safe background processor.

Features:
1. Atomic event claiming (no duplicate processing)
2. Per-student ordering (temporal correctness)
3. Event completion tracking
4. Safe for multiple workers
"""

import time
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import Database
from core_services.mastery_service import MasteryService
from core_models.student_model import StudentModel
from pymongo import ReturnDocument

class LearningWorker:
    """Concurrency-safe background worker."""
    
    def __init__(self, poll_interval=1.0):
        self.poll_interval = poll_interval
        self.running = False
    
    def claim_event_atomic(self, student_id):
        """
        Atomically claim the earliest unprocessed event for a student.
        
        Args:
            student_id: Student identifier
            
        Returns:
            event document or None
        """
        db = Database.get_db()
        
        # Atomic find and update
        event = db.learning_events.find_one_and_update(
            {
                'student_id': student_id,
                'processing.bkt': False
            },
            {
                '$set': {'processing.bkt': 'processing'}
            },
            sort=[('timestamp', 1)],  # Earliest first (temporal order)
            return_document=ReturnDocument.AFTER
        )
        
        return event
    
    def process_bkt_update(self, event):
        """
        Process BKT update for an event.
        
        Args:
            event: Learning event document
            
        Returns:
            bool: True if successful
        """
        try:
            student_id = event['student_id']
            problem_id = event['problem_id']
            result = event['result']
            diagnosis = event['diagnosis']
            
            # Update mastery using existing service
            MasteryService.update_student_performance(
                student_id=student_id,
                problem_id=problem_id,
                skills=diagnosis['skills'],
                correct=result['correct'],
                error_type=diagnosis.get('error_type'),
                attempts=result['attempts'],
                solve_time=result['solve_time']
            )
            
            return True
            
        except Exception as e:
            print(f"Error processing BKT for event {event['_id']}: {e}")
            return False
    
    def compute_learner_state(self, student_id):
        """
        Compute and store learner state.
        
        Args:
            student_id: Student identifier
            
        Returns:
            bool: True if successful
        """
        try:
            all_masteries = StudentModel.get_student_skills(student_id)
            
            if not all_masteries:
                return False
            
            # Compute weak skills (mastery < 0.4)
            weak_skills = [
                skill_id for skill_id, mastery in all_masteries.items()
                if mastery < 0.4
            ]
            
            # Determine learning state
            avg_mastery = sum(all_masteries.values()) / len(all_masteries)
            
            if avg_mastery < 0.4:
                learning_state = "struggling"
            elif avg_mastery <= 0.7:
                learning_state = "learning"
            else:
                learning_state = "mastered"
            
            # Store in learner_state collection
            db = Database.get_db()
            state_doc = {
                'student_id': student_id,
                'weak_skills': weak_skills,
                'learning_state': learning_state,
                'updated_at': datetime.utcnow()
            }
            
            db.learner_state.insert_one(state_doc)
            
            return True
            
        except Exception as e:
            print(f"Error computing learner state for {student_id}: {e}")
            return False
    
    def mark_event_complete(self, event_id):
        """
        Mark event as fully completed.
        
        Args:
            event_id: Event ObjectId
        """
        db = Database.get_db()
        db.learning_events.update_one(
            {'_id': event_id},
            {
                '$set': {
                    'processing.bkt': True,
                    'processing.learner_state': True,
                    'completed': True
                }
            }
        )
    
    def mark_event_failed(self, event_id):
        """
        Mark event as failed (reset for retry).
        
        Args:
            event_id: Event ObjectId
        """
        db = Database.get_db()
        db.learning_events.update_one(
            {'_id': event_id},
            {'$set': {'processing.bkt': False}}
        )
    
    def get_students_with_pending_events(self):
        """
        Get list of students with unprocessed events.
        
        Returns:
            list: Student IDs with pending events
        """
        db = Database.get_db()
        
        # Get distinct student_ids with unprocessed events
        student_ids = db.learning_events.distinct(
            'student_id',
            {'processing.bkt': False}
        )
        
        return student_ids
    
    def process_events(self):
        """
        Process events with per-student ordering.
        
        Returns:
            int: Number of events processed
        """
        # Get students with pending events
        students = self.get_students_with_pending_events()
        
        if not students:
            return 0
        
        processed_count = 0
        
        # Process one event per student (maintains temporal order)
        for student_id in students:
            # Atomically claim earliest event for this student
            event = self.claim_event_atomic(student_id)
            
            if not event:
                # Another worker claimed it
                continue
            
            event_id = event['_id']
            
            try:
                # Process BKT update
                if self.process_bkt_update(event):
                    # Compute learner state
                    if self.compute_learner_state(student_id):
                        # Mark as fully completed
                        self.mark_event_complete(event_id)
                        processed_count += 1
                    else:
                        # BKT succeeded but state failed - mark BKT done
                        db = Database.get_db()
                        db.learning_events.update_one(
                            {'_id': event_id},
                            {'$set': {'processing.bkt': True}}
                        )
                else:
                    # BKT failed - reset for retry
                    self.mark_event_failed(event_id)
                    
            except Exception as e:
                print(f"Error processing event {event_id}: {e}")
                # Reset for retry
                self.mark_event_failed(event_id)
        
        return processed_count
    
    def run(self):
        """Run worker loop."""
        self.running = True
        print("=" * 60)
        print("Learning Worker Started (Concurrency-Safe)")
        print("=" * 60)
        print(f"Poll interval: {self.poll_interval}s")
        print("Features:")
        print("  - Atomic event claiming")
        print("  - Per-student ordering")
        print("  - Event completion tracking")
        print("  - Safe for multiple workers")
        print()
        print("Waiting for events...")
        print()
        
        try:
            while self.running:
                processed = self.process_events()
                
                if processed > 0:
                    print(f"[{datetime.utcnow().isoformat()}] Processed {processed} events")
                
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\nShutting down worker...")
            self.running = False
    
    def stop(self):
        """Stop worker."""
        self.running = False


def main():
    """Main entry point."""
    # Initialize database
    Database.initialize()
    
    # Create indexes for concurrency safety
    db = Database.get_db()
    
    # Unique index on submission_id (idempotency)
    db.learning_events.create_index('submission_id', unique=True)
    
    # Compound index for atomic claiming
    db.learning_events.create_index([
        ('student_id', 1),
        ('processing.bkt', 1),
        ('timestamp', 1)
    ])
    
    print("✓ Database indexes created")
    
    # Create and run worker
    worker = LearningWorker(poll_interval=1.0)
    
    try:
        worker.run()
    except Exception as e:
        print(f"Worker error: {e}")
        raise


if __name__ == '__main__':
    main()
