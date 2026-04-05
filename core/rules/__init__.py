from .ambiguity import AmbiguityRule
from .missing_ac import MissingACRule
from .contradiction import ContradictionRule
from .dependency_gap import DependencyGapRule
from .completeness import CompletenessRule

ALL_RULES = [
    AmbiguityRule(),
    MissingACRule(),
    ContradictionRule(),
    DependencyGapRule(),
    CompletenessRule(),
]
