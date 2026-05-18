from typing import TypedDict, List


class PipelineState(TypedDict):
    raw_text: str
    filename: str
    actors: List[str]
    features: List[str]
    constraints: List[str]
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    user_stories: List[dict]          # {feature, story, priority}
    acceptance_criteria: List[dict]   # {story_ref, given, when, then}
    risks: List[dict]                 # {requirement, reason, suggestion}
    ambiguities: List[dict]           # {requirement, reason, suggestion}
    errors: List[str]


def empty_state(filename: str) -> PipelineState:
    return {
        "raw_text": "",
        "filename": filename,
        "actors": [],
        "features": [],
        "constraints": [],
        "functional_requirements": [],
        "non_functional_requirements": [],
        "user_stories": [],
        "acceptance_criteria": [],
        "risks": [],
        "ambiguities": [],
        "errors": [],
    }
