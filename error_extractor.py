from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from error_taxonomy import ErrorCategory, DSASubskill, ErrorPattern, ERROR_PATTERNS

@dataclass
class DetectedError:
    error_id: str
    pattern: ErrorPattern
    confidence: float
    context: str
    line_number: Optional[int] = None

class ErrorExtractor:
    def __init__(self):
        self.patterns = ERROR_PATTERNS
        self._compile_detection_rules()
    
    def _compile_detection_rules(self):
        self.detection_rules = {
            "E001": [r"for.*range\(.*\+\s*1\)", r"while.*<=.*len", r"\[i\+1\].*range\(len"],
            "E002": [r"def.*\(.*\):.*if.*==.*:.*return(?!.*else)", r"recursion.*without.*base"],
            "E003": [r"stack\.pop\(\).*stack\.push", r"push.*before.*empty.*check"],
            "E004": [r"sort.*lambda.*[><](?!.*=)", r"compare.*swap.*wrong"],
            "E005": [r"\[.*len\(.*\)\]", r"index.*out.*of.*range", r"\[-\d+\]"],
            "E006": [r"\.next(?!.*if.*None)", r"\.left(?!.*if.*None)", r"node\..*without.*null"],
            "E007": [r"for.*for.*for", r"O\(n\^3\)", r"nested.*loop.*inefficient"],
            "E008": [r"queue.*depth", r"stack.*level.*order", r"BFS.*DFS.*mismatch"],
            "E009": [r"dict\[.*\](?!.*try|.*get)", r"hash.*collision.*unhandled"],
            "E010": [r"left\+\+.*right\+\+", r"two.*pointer.*same.*direction"],
            "E011": [r"window.*size.*\+\s*1", r"sliding.*window.*off"],
            "E012": [r"greedy.*local.*not.*global", r"max.*immediate.*not.*optimal"],
            "E013": [r"dp\[i\].*dp\[i\]", r"state.*transition.*self.*reference"],
            "E014": [r"heap.*parent.*child.*wrong", r"heapify.*property.*violated"],
            "E015": [r"backtrack.*no.*pruning", r"explore.*all.*paths.*inefficient"],
            "E016": [r"new.*Node.*no.*delete", r"linked.*list.*memory.*leak"],
            "E017": [r"<<.*>>.*reversed", r"bit.*shift.*wrong.*direction"],
            "E018": [r"mid.*=.*\(left.*right\).*\/.*2(?!.*\+)", r"binary.*search.*bound.*error"],
        }
    
    def extract_from_code(self, code: str, test_results: Dict) -> List[DetectedError]:
        detected = []
        lines = code.split('\n')
        test_detected_ids = {e.error_id for e in self._extract_from_test_results(test_results)}

        for error_id, regex_list in self.detection_rules.items():
            for regex in regex_list:
                for i, line in enumerate(lines):
                    if re.search(regex, line, re.IGNORECASE):
                        pattern = self.patterns[error_id]
                        # Higher confidence if both regex and test result agree
                        confidence = 0.9 if error_id in test_detected_ids else 0.7
                        detected.append(DetectedError(
                            error_id=error_id,
                            pattern=pattern,
                            confidence=confidence,
                            context=line.strip(),
                            line_number=i+1
                        ))

        detected.extend(self._extract_from_test_results(test_results))
        return self._deduplicate(detected)
    
    def _extract_from_test_results(self, test_results: Dict) -> List[DetectedError]:
        detected = []

        if not test_results.get('passed', True):
            failures = test_results.get('failures', [])

            for failure in failures:
                error_msg = failure.get('message', '').lower()
                test_case = failure.get('test_case', '').lower()
                matched = False

                if 'index' in error_msg and 'out of' in error_msg:
                    detected.append(DetectedError("E005", self.patterns["E005"], 0.9, error_msg))
                    matched = True
                elif 'none' in error_msg and 'attribute' in error_msg:
                    detected.append(DetectedError("E006", self.patterns["E006"], 0.85, error_msg))
                    matched = True
                elif 'recursion' in error_msg or 'maximum recursion' in error_msg:
                    detected.append(DetectedError("E002", self.patterns["E002"], 0.9, error_msg))
                    matched = True
                elif 'timeout' in error_msg or 'time limit' in error_msg:
                    detected.append(DetectedError("E007", self.patterns["E007"], 0.85, error_msg))
                    matched = True
                elif 'key' in error_msg and 'error' in error_msg:
                    detected.append(DetectedError("E009", self.patterns["E009"], 0.8, error_msg))
                    matched = True
                elif 'heap' in error_msg or 'heapify' in error_msg:
                    detected.append(DetectedError("E014", self.patterns["E014"], 0.8, error_msg))
                    matched = True
                elif 'wrong answer' in error_msg or 'assertion' in error_msg:
                    if 'boundary' in test_case or 'edge' in test_case:
                        detected.append(DetectedError("E001", self.patterns["E001"], 0.75, error_msg))
                        matched = True
                    elif 'sort' in test_case:
                        detected.append(DetectedError("E004", self.patterns["E004"], 0.7, error_msg))
                        matched = True
                    elif 'search' in test_case:
                        detected.append(DetectedError("E018", self.patterns["E018"], 0.75, error_msg))
                        matched = True

                # Unknown error — test failed but we couldn't identify the specific pattern
                if not matched:
                    unknown_pattern = ErrorPattern(
                        error_id="E000",
                        category=ErrorCategory.LOGIC,
                        description=f"Test failed: {failure.get('message', 'Unknown error')}",
                        affected_subskills=set(),
                        severity=0.5
                    )
                    detected.append(DetectedError("E000", unknown_pattern, 0.5, error_msg))

        return detected
    
    def _deduplicate(self, errors: List[DetectedError]) -> List[DetectedError]:
        seen = set()
        unique = []
        for error in errors:
            if error.error_id not in seen:
                seen.add(error.error_id)
                unique.append(error)
        return unique

class ErrorClassifier:
    def classify_by_category(self, errors: List[DetectedError]) -> Dict[ErrorCategory, List[DetectedError]]:
        categorized = {cat: [] for cat in ErrorCategory}
        for error in errors:
            categorized[error.pattern.category].append(error)
        return categorized
    
    def classify_by_subskill(self, errors: List[DetectedError]) -> Dict[DSASubskill, List[DetectedError]]:
        skill_map = {skill: [] for skill in DSASubskill}
        for error in errors:
            for skill in error.pattern.affected_subskills:
                skill_map[skill].append(error)
        return skill_map
    
    def get_severity_score(self, errors: List[DetectedError]) -> float:
        if not errors:
            return 0.0
        return sum(e.pattern.severity * e.confidence for e in errors) / len(errors)
