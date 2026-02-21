"""
Execution Feedback Module - Code Editor Integration
Interprets test results and produces readable mistake explanations
"""

from typing import Dict, List
from error_taxonomy import ERROR_PATTERNS

class ExecutionFeedback:
    def __init__(self):
        self.patterns = ERROR_PATTERNS
    
    def generate_feedback(self, analysis: Dict) -> Dict:
        """
        Generate user-friendly feedback from error analysis
        
        Args:
            analysis: Output from analyze_learner_submission
        
        Returns:
            Structured feedback for code editor display
        """
        feedback = {
            'status': 'failed' if analysis['overall_severity'] > 0 else 'passed',
            'severity_level': self._get_severity_level(analysis['overall_severity']),
            'summary': self._generate_summary(analysis),
            'mistakes': self._explain_mistakes(analysis['detected_errors']),
            'recommendations': self._generate_recommendations(analysis['conceptual_gaps']),
            'skills_status': {
                'correct': [s.value for s in analysis.get('skills_correct', [])],
                'incorrect': [s.value for s in analysis.get('skills_incorrect', [])]
            }
        }
        return feedback
    
    def _get_severity_level(self, severity: float) -> str:
        """Convert severity score to readable level"""
        if severity == 0:
            return "Perfect"
        elif severity < 0.3:
            return "Minor Issues"
        elif severity < 0.6:
            return "Moderate Issues"
        elif severity < 0.8:
            return "Significant Issues"
        else:
            return "Critical Issues"
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Generate overall summary message"""
        error_count = len(analysis['detected_errors'])
        severity = analysis['overall_severity']
        
        if error_count == 0:
            return "Great job! Your code passed all tests."
        
        if severity < 0.5:
            return f"Your code has {error_count} minor issue(s). Let's fix them!"
        elif severity < 0.8:
            return f"Found {error_count} issue(s) that need attention."
        else:
            return f"Your code has {error_count} critical issue(s). Review the feedback below."
    
    def _explain_mistakes(self, errors: List) -> List[Dict]:
        """Convert detected errors into readable explanations"""
        explanations = []
        
        for error in errors:
            explanation = {
                'type': error.pattern.category.value,
                'title': self._get_error_title(error.error_id),
                'description': error.pattern.description,
                'location': f"Line {error.line_number}" if error.line_number else "Unknown",
                'code_snippet': error.context,
                'severity': error.pattern.severity,
                'hint': self._get_hint(error.error_id)
            }
            explanations.append(explanation)
        
        return explanations
    
    def _get_error_title(self, error_id: str) -> str:
        """Get user-friendly title for error"""
        titles = {
            'E001': "Off-by-One Error in Loop",
            'E002': "Missing Base Case in Recursion",
            'E003': "Incorrect Stack Operation Order",
            'E004': "Wrong Sorting Comparison",
            'E005': "Array Index Out of Bounds",
            'E006': "Missing Null/None Check",
            'E007': "Inefficient Nested Loops",
            'E008': "Wrong Graph Traversal Method",
            'E009': "Hash Collision Not Handled",
            'E010': "Incorrect Two-Pointer Movement",
            'E011': "Sliding Window Size Error",
            'E012': "Greedy Choice Not Optimal",
            'E013': "Dynamic Programming State Error",
            'E014': "Heap Property Violation",
            'E015': "Missing Backtracking Pruning",
            'E016': "Memory Leak in Linked List",
            'E017': "Bit Shift Direction Wrong",
            'E018': "Binary Search Bounds Incorrect"
        }
        return titles.get(error_id, "Unknown Error")
    
    def _get_hint(self, error_id: str) -> str:
        """Get actionable hint for fixing the error"""
        hints = {
            'E001': "Check your loop bounds. Should it be < len(arr) or <= len(arr)-1?",
            'E002': "Add a base case that stops recursion (e.g., if n <= 0: return ...)",
            'E003': "Remember: push before checking if empty, or check before pop",
            'E004': "Review your comparison logic. For ascending sort, use <",
            'E005': "Ensure array indices are within 0 to len(arr)-1",
            'E006': "Add: if node is None: return ... before accessing node.next",
            'E007': "Can you solve this with a single loop? Consider hash tables or two-pointers",
            'E008': "Use BFS for shortest path, DFS for exploring all paths",
            'E009': "Use .get() method or handle KeyError exceptions",
            'E010': "Move pointers in opposite directions or based on conditions",
            'E011': "Window size = right - left + 1. Check your calculation",
            'E012': "Greedy doesn't always work. Consider if you need dynamic programming",
            'E013': "Check your state transition. Does dp[i] depend on dp[i]?",
            'E014': "Parent should be <= children (min-heap) or >= children (max-heap)",
            'E015': "Add conditions to skip branches that can't lead to solution",
            'E016': "Delete nodes when removing from list to free memory",
            'E017': "Left shift (<<) multiplies by 2, right shift (>>) divides by 2",
            'E018': "Use: left = 0, right = len(arr) - 1 (not len(arr))"
        }
        return hints.get(error_id, "Review the code carefully and check edge cases")
    
    def _generate_recommendations(self, gaps: List) -> List[Dict]:
        """Generate learning recommendations from conceptual gaps"""
        recommendations = []
        
        for gap in gaps[:3]:  # Top 3 gaps
            rec = {
                'skill': gap.subskill.value,
                'priority': 'High' if gap.severity > 0.7 else 'Medium',
                'focus_areas': gap.recommended_focus,
                'message': f"Practice {gap.subskill.value.replace('_', ' ')} - focus on: {', '.join(gap.recommended_focus[:2])}"
            }
            recommendations.append(rec)
        
        return recommendations

def format_for_display(feedback: Dict) -> str:
    """Format feedback as readable text for console/UI display"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"STATUS: {feedback['status'].upper()} - {feedback['severity_level']}")
    output.append(f"{'='*60}")
    output.append(f"\n{feedback['summary']}\n")
    
    if feedback['mistakes']:
        output.append("MISTAKES FOUND:")
        for i, mistake in enumerate(feedback['mistakes'], 1):
            output.append(f"\n{i}. {mistake['title']} ({mistake['location']})")
            output.append(f"   {mistake['description']}")
            output.append(f"   Hint: {mistake['hint']}")
    
    if feedback['recommendations']:
        output.append("\n\nRECOMMENDATIONS:")
        for rec in feedback['recommendations']:
            output.append(f"  • {rec['message']}")
    
    output.append(f"\n{'='*60}\n")
    return '\n'.join(output)
