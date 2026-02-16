from enum import Enum
from dataclasses import dataclass
from typing import List, Set

class ErrorCategory(Enum):
    LOGIC = "logic"
    BOUNDARY = "boundary"
    COMPLEXITY = "complexity"
    DATA_STRUCTURE = "data_structure"
    ALGORITHM = "algorithm"
    SYNTAX = "syntax"
    MEMORY = "memory"

class DSASubskill(Enum):
    ARRAY_TRAVERSAL = "array_traversal"
    ARRAY_MANIPULATION = "array_manipulation"
    LINKED_LIST_OPS = "linked_list_ops"
    STACK_OPS = "stack_ops"
    QUEUE_OPS = "queue_ops"
    TREE_TRAVERSAL = "tree_traversal"
    TREE_MANIPULATION = "tree_manipulation"
    GRAPH_TRAVERSAL = "graph_traversal"
    GRAPH_ALGORITHMS = "graph_algorithms"
    SORTING = "sorting"
    SEARCHING = "searching"
    RECURSION = "recursion"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    BACKTRACKING = "backtracking"
    TWO_POINTER = "two_pointer"
    SLIDING_WINDOW = "sliding_window"
    HASH_TABLE = "hash_table"
    HEAP_OPS = "heap_ops"
    BIT_MANIPULATION = "bit_manipulation"

@dataclass
class ErrorPattern:
    error_id: str
    category: ErrorCategory
    description: str
    affected_subskills: Set[DSASubskill]
    severity: float  # 0.0 to 1.0

ERROR_PATTERNS = {
    "E001": ErrorPattern("E001", ErrorCategory.BOUNDARY, "Off-by-one in loop", 
                        {DSASubskill.ARRAY_TRAVERSAL}, 0.6),
    "E002": ErrorPattern("E002", ErrorCategory.LOGIC, "Incorrect base case in recursion",
                        {DSASubskill.RECURSION}, 0.8),
    "E003": ErrorPattern("E003", ErrorCategory.DATA_STRUCTURE, "Wrong stack operation order",
                        {DSASubskill.STACK_OPS}, 0.7),
    "E004": ErrorPattern("E004", ErrorCategory.ALGORITHM, "Incorrect sorting comparison",
                        {DSASubskill.SORTING}, 0.7),
    "E005": ErrorPattern("E005", ErrorCategory.BOUNDARY, "Array index out of bounds",
                        {DSASubskill.ARRAY_TRAVERSAL, DSASubskill.ARRAY_MANIPULATION}, 0.8),
    "E006": ErrorPattern("E006", ErrorCategory.LOGIC, "Missing null check",
                        {DSASubskill.LINKED_LIST_OPS, DSASubskill.TREE_TRAVERSAL}, 0.9),
    "E007": ErrorPattern("E007", ErrorCategory.COMPLEXITY, "Nested loop inefficiency",
                        {DSASubskill.DYNAMIC_PROGRAMMING, DSASubskill.ARRAY_TRAVERSAL}, 0.5),
    "E008": ErrorPattern("E008", ErrorCategory.ALGORITHM, "Wrong BFS/DFS choice",
                        {DSASubskill.GRAPH_TRAVERSAL, DSASubskill.TREE_TRAVERSAL}, 0.7),
    "E009": ErrorPattern("E009", ErrorCategory.DATA_STRUCTURE, "Hash collision not handled",
                        {DSASubskill.HASH_TABLE}, 0.6),
    "E010": ErrorPattern("E010", ErrorCategory.LOGIC, "Incorrect two-pointer movement",
                        {DSASubskill.TWO_POINTER}, 0.7),
    "E011": ErrorPattern("E011", ErrorCategory.BOUNDARY, "Window size calculation error",
                        {DSASubskill.SLIDING_WINDOW}, 0.6),
    "E012": ErrorPattern("E012", ErrorCategory.ALGORITHM, "Greedy choice not optimal",
                        {DSASubskill.GREEDY}, 0.8),
    "E013": ErrorPattern("E013", ErrorCategory.LOGIC, "DP state transition error",
                        {DSASubskill.DYNAMIC_PROGRAMMING}, 0.9),
    "E014": ErrorPattern("E014", ErrorCategory.DATA_STRUCTURE, "Heap property violation",
                        {DSASubskill.HEAP_OPS}, 0.8),
    "E015": ErrorPattern("E015", ErrorCategory.ALGORITHM, "Backtracking pruning missing",
                        {DSASubskill.BACKTRACKING}, 0.6),
    "E016": ErrorPattern("E016", ErrorCategory.MEMORY, "Memory leak in linked list",
                        {DSASubskill.LINKED_LIST_OPS}, 0.7),
    "E017": ErrorPattern("E017", ErrorCategory.LOGIC, "Bit shift direction wrong",
                        {DSASubskill.BIT_MANIPULATION}, 0.5),
    "E018": ErrorPattern("E018", ErrorCategory.BOUNDARY, "Binary search bounds incorrect",
                        {DSASubskill.SEARCHING}, 0.8),
}
