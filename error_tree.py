from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from error_taxonomy import DSASubskill, ErrorCategory
from error_extractor import DetectedError

@dataclass
class ConceptualGap:
    subskill: DSASubskill
    severity: float
    error_count: int
    recommended_focus: List[str]

@dataclass
class ErrorTreeNode:
    condition: str
    threshold: float
    left: Optional['ErrorTreeNode'] = None
    right: Optional['ErrorTreeNode'] = None
    diagnosis: Optional[ConceptualGap] = None

class ErrorTree:
    def __init__(self):
        self.root = self._build_tree()
    
    def _build_tree(self) -> ErrorTreeNode:
        # Root: Check error category distribution
        root = ErrorTreeNode("category_diversity", 0.5)
        
        # Left: Low diversity (focused errors)
        logic_node = ErrorTreeNode("logic_errors", 0.6)
        logic_node.left = ErrorTreeNode("recursion_errors", 0.5,
            diagnosis=ConceptualGap(DSASubskill.RECURSION, 0.8, 0, 
                ["base case design", "recursive relation", "stack overflow prevention"]))
        logic_node.right = ErrorTreeNode("pointer_errors", 0.5,
            diagnosis=ConceptualGap(DSASubskill.TWO_POINTER, 0.7, 0,
                ["pointer movement logic", "termination conditions"]))
        
        boundary_node = ErrorTreeNode("boundary_errors", 0.6)
        boundary_node.left = ErrorTreeNode("array_bounds", 0.5,
            diagnosis=ConceptualGap(DSASubskill.ARRAY_TRAVERSAL, 0.75, 0,
                ["index management", "loop bounds", "edge cases"]))
        boundary_node.right = ErrorTreeNode("search_bounds", 0.5,
            diagnosis=ConceptualGap(DSASubskill.SEARCHING, 0.7, 0,
                ["binary search bounds", "mid calculation"]))
        
        root.left = ErrorTreeNode("error_type", 0.5)
        root.left.left = logic_node
        root.left.right = boundary_node
        
        # Right: High diversity (broad gaps)
        ds_node = ErrorTreeNode("data_structure_errors", 0.6)
        ds_node.left = ErrorTreeNode("linear_ds", 0.5,
            diagnosis=ConceptualGap(DSASubskill.LINKED_LIST_OPS, 0.8, 0,
                ["pointer manipulation", "null handling", "memory management"]))
        ds_node.right = ErrorTreeNode("tree_ds", 0.5,
            diagnosis=ConceptualGap(DSASubskill.TREE_TRAVERSAL, 0.75, 0,
                ["traversal patterns", "null checks", "recursion in trees"]))
        
        algo_node = ErrorTreeNode("algorithm_errors", 0.6)
        algo_node.left = ErrorTreeNode("optimization", 0.5,
            diagnosis=ConceptualGap(DSASubskill.DYNAMIC_PROGRAMMING, 0.9, 0,
                ["state definition", "transition formula", "memoization"]))
        algo_node.right = ErrorTreeNode("graph_algo", 0.5,
            diagnosis=ConceptualGap(DSASubskill.GRAPH_TRAVERSAL, 0.8, 0,
                ["BFS vs DFS", "visited tracking", "graph representation"]))
        
        root.right = ErrorTreeNode("complexity_check", 0.5)
        root.right.left = ds_node
        root.right.right = algo_node
        
        return root
    
    def diagnose(self, errors: List[DetectedError]) -> List[ConceptualGap]:
        if not errors:
            return []
        
        error_stats = self._compute_error_stats(errors)
        gaps = []
        
        # Traverse tree with error statistics
        gaps.extend(self._traverse(self.root, error_stats))
        
        # Direct mapping for high-confidence errors
        gaps.extend(self._direct_mapping(errors))
        
        return self._merge_gaps(gaps)
    
    def _compute_error_stats(self, errors: List[DetectedError]) -> Dict:
        categories = {}
        subskills = {}
        
        for error in errors:
            cat = error.pattern.category
            categories[cat] = categories.get(cat, 0) + 1
            
            for skill in error.pattern.affected_subskills:
                subskills[skill] = subskills.get(skill, 0) + error.pattern.severity
        
        total = len(errors)
        return {
            'category_diversity': len(categories) / len(ErrorCategory),
            'categories': categories,
            'subskills': subskills,
            'total': total,
            'avg_severity': sum(e.pattern.severity for e in errors) / total
        }
    
    def _traverse(self, node: ErrorTreeNode, stats: Dict) -> List[ConceptualGap]:
        if node.diagnosis:
            gap = ConceptualGap(
                node.diagnosis.subskill,
                stats['avg_severity'],
                stats['total'],
                node.diagnosis.recommended_focus
            )
            return [gap]
        
        if node.condition == "category_diversity":
            if stats['category_diversity'] < node.threshold:
                return self._traverse(node.left, stats) if node.left else []
            else:
                return self._traverse(node.right, stats) if node.right else []
        
        elif node.condition == "error_type":
            logic_count = stats['categories'].get(ErrorCategory.LOGIC, 0)
            boundary_count = stats['categories'].get(ErrorCategory.BOUNDARY, 0)
            if logic_count > boundary_count:
                return self._traverse(node.left, stats) if node.left else []
            else:
                return self._traverse(node.right, stats) if node.right else []
        
        elif node.condition == "complexity_check":
            ds_count = stats['categories'].get(ErrorCategory.DATA_STRUCTURE, 0)
            algo_count = stats['categories'].get(ErrorCategory.ALGORITHM, 0)
            if ds_count > algo_count:
                return self._traverse(node.left, stats) if node.left else []
            else:
                return self._traverse(node.right, stats) if node.right else []
        
        return []
    
    def _direct_mapping(self, errors: List[DetectedError]) -> List[ConceptualGap]:
        skill_errors = {}
        
        for error in errors:
            for skill in error.pattern.affected_subskills:
                if skill not in skill_errors:
                    skill_errors[skill] = []
                skill_errors[skill].append(error)
        
        gaps = []
        for skill, errs in skill_errors.items():
            if len(errs) >= 2:  # Multiple errors in same skill
                severity = sum(e.pattern.severity * e.confidence for e in errs) / len(errs)
                gaps.append(ConceptualGap(
                    skill,
                    severity,
                    len(errs),
                    self._get_focus_areas(skill)
                ))
        
        return gaps
    
    def _get_focus_areas(self, skill: DSASubskill) -> List[str]:
        focus_map = {
            DSASubskill.ARRAY_TRAVERSAL: ["loop bounds", "index arithmetic", "edge cases"],
            DSASubskill.RECURSION: ["base cases", "recursive calls", "return values"],
            DSASubskill.LINKED_LIST_OPS: ["pointer updates", "null checks", "edge nodes"],
            DSASubskill.TREE_TRAVERSAL: ["traversal order", "null handling", "recursion"],
            DSASubskill.DYNAMIC_PROGRAMMING: ["state definition", "transitions", "base cases"],
            DSASubskill.TWO_POINTER: ["pointer movement", "termination", "invariants"],
            DSASubskill.SLIDING_WINDOW: ["window size", "boundary updates", "optimization"],
            DSASubskill.GRAPH_TRAVERSAL: ["visited set", "BFS/DFS choice", "termination"],
            DSASubskill.SEARCHING: ["bounds", "mid calculation", "termination"],
            DSASubskill.SORTING: ["comparison logic", "stability", "complexity"],
        }
        return focus_map.get(skill, ["fundamentals", "practice", "edge cases"])
    
    def _merge_gaps(self, gaps: List[ConceptualGap]) -> List[ConceptualGap]:
        merged = {}
        for gap in gaps:
            if gap.subskill in merged:
                existing = merged[gap.subskill]
                merged[gap.subskill] = ConceptualGap(
                    gap.subskill,
                    max(existing.severity, gap.severity),
                    existing.error_count + gap.error_count,
                    list(set(existing.recommended_focus + gap.recommended_focus))
                )
            else:
                merged[gap.subskill] = gap
        
        return sorted(merged.values(), key=lambda x: x.severity, reverse=True)

class ErrorMiningPipeline:
    def __init__(self):
        from error_extractor import ErrorExtractor, ErrorClassifier
        self.extractor = ErrorExtractor()
        self.classifier = ErrorClassifier()
        self.error_tree = ErrorTree()
    
    def analyze(self, code: str, test_results: Dict) -> Dict:
        # Extract errors
        errors = self.extractor.extract_from_code(code, test_results)
        
        # Classify errors
        by_category = self.classifier.classify_by_category(errors)
        by_subskill = self.classifier.classify_by_subskill(errors)
        severity = self.classifier.get_severity_score(errors)
        
        # Diagnose conceptual gaps
        gaps = self.error_tree.diagnose(errors)
        
        return {
            'detected_errors': errors,
            'by_category': by_category,
            'by_subskill': by_subskill,
            'overall_severity': severity,
            'conceptual_gaps': gaps,
            'priority_skills': [gap.subskill for gap in gaps[:3]]
        }
