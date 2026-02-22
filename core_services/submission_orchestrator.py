from core_services.judge_service import JudgeService
from core_services.kff_sequencer import KFFSequencer
from member2_backend.services.learning_service import LearningService
from error_mining_interface import analyze_learner_submission
from core_models.problem_model import ProblemModel
from core_models.sequence_log_model import SequenceLogModel
from member2_backend.models.student_model import StudentModel


class SubmissionOrchestrator:
    @staticmethod
    def process_submission(student_id: str, problem_id: str, code: str, attempts: int):
        # 1. Fetch Problem Data
        problem = ProblemModel.get_problem_by_id(problem_id)
        if not problem:
            return {"error": "Problem not found"}

        problem_skills = problem.get('skills', [])

        # 2. Execute Code (Judge)
        test_results = JudgeService.execute_code(code, problem.get('test_cases', []))
        is_correct = test_results['passed']

        # 3. Analyze Errors (Member 3)
        # Note: We pass the problem_skills so ErrorMining can map gaps correctly
        analysis = analyze_learner_submission(code, test_results, problem_skills)

        # Extract the primary error type for Member 2
        error_type = analysis['detected_errors'][0].error_id if analysis['detected_errors'] else "none"

        # 4. Update Learner State (Member 2)
        result_payload = {
            "correct": is_correct,
            "attempts": attempts,
            "solve_time": test_results['solve_time']
        }
        diagnosis_payload = {
            "skills": problem_skills,
            "error_type": error_type,
        }

        # This synchronously updates BKT via Member 2's service
        m2_state = LearningService.process_learning_event(
            student_id, problem_id, result_payload, diagnosis_payload
        )

        # Calculate overall mastery for KFF from Member 2's updated data
        all_masteries = StudentModel.get_student_skills(student_id)
        overall_mastery = sum(all_masteries.values()) / max(len(all_masteries), 1)

        # 5. Adaptive Sequencing (Member 4 - KFF)
        sequencer = KFFSequencer()
        next_problem, flow_metrics = sequencer.get_next_problem(
            student_id=student_id,
            current_problem_id=problem_id,
            weak_skills=m2_state.get('weak_skills', []),
            bkt_mastery=overall_mastery
        )

        # 6. Log Sequence Decision for Member 6 Metrics
        if next_problem:
            SequenceLogModel.log_decision(
                student_id=student_id,
                prev_problem_id=problem_id,
                next_problem_id=str(next_problem['_id']),
                mastery=flow_metrics['mastery'],
                momentum=flow_metrics['momentum'],
                target_challenge=flow_metrics['target_challenge'],
                was_correct=is_correct
            )
            next_problem['_id'] = str(next_problem['_id'])

        return {
            "submission_result": test_results,
            "error_analysis": {
                "detected_errors": [e.error_id for e in analysis['detected_errors']],
                "severity": analysis.get('overall_severity')
            },
            "learner_state": m2_state,
            "next_problem": next_problem,
            "flow_metrics": flow_metrics
        }