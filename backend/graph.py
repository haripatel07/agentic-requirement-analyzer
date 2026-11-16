"""Pipeline orchestration built on a LangGraph StateGraph.

Public API (unchanged):
  run_pipeline_partial(filename) -> state dict  (agents 1-3)
  run_pipeline_full(filename)    -> {"state": ..., "report": ...}  (agents 1-6 + report)

Each node reads the shared PipelineState and returns only the keys it owns;
LangGraph merges them. `errors` uses an additive reducer so every agent's
errors are kept.
"""
import operator
from typing import Annotated, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph

from .state import empty_state


class GraphState(TypedDict, total=False):
    raw_text: str
    filename: str
    actors: List[str]
    features: List[str]
    constraints: List[str]
    functional_requirements: List[str]
    non_functional_requirements: List[str]
    user_stories: List[dict]
    acceptance_criteria: List[dict]
    risks: List[dict]
    ambiguities: List[dict]
    errors: Annotated[List[str], operator.add]


def _node(module_name, func_name, owned_keys):
    """Wrap an agent so it only writes the keys it owns plus new errors.

    The agent function is resolved at call time so it can be patched in tests.
    """

    def run(state: GraphState) -> Dict:
        import importlib

        agent_fn = getattr(importlib.import_module(f"backend.agents.{module_name}"), func_name)
        out = agent_fn(dict(state)) or {}
        update = {k: out[k] for k in owned_keys if k in out}
        if out.get("errors"):
            update["errors"] = list(out["errors"])
        return update

    return run


def _build(full: bool):
    stages = [
        ("parse", ("parser", "parse_document"), ("raw_text",)),
        ("analyze", ("analyzer", "analyze_requirements"), ("actors", "features", "constraints")),
        (
            "classify",
            ("classifier", "classify_requirements"),
            ("functional_requirements", "non_functional_requirements"),
        ),
    ]
    if full:
        stages += [
            ("stories", ("story_generator", "generate_user_stories"), ("user_stories",)),
            ("acceptance", ("acceptance", "generate_acceptance_criteria"), ("acceptance_criteria",)),
            ("risk", ("risk_detector", "detect_risks_ambiguity"), ("risks", "ambiguities")),
        ]

    graph = StateGraph(GraphState)
    for name, (mod, fn), keys in stages:
        graph.add_node(name, _node(mod, fn, keys))
    graph.add_edge(START, stages[0][0])
    for (a, _, _), (b, _, _) in zip(stages, stages[1:]):
        graph.add_edge(a, b)
    graph.add_edge(stages[-1][0], END)
    return graph.compile()


_PARTIAL = None
_FULL = None


def get_graph(full: bool = True):
    """Compiled LangGraph app (cached)."""
    global _PARTIAL, _FULL
    if full:
        if _FULL is None:
            _FULL = _build(True)
        return _FULL
    if _PARTIAL is None:
        _PARTIAL = _build(False)
    return _PARTIAL


def run_pipeline_partial(filename: str) -> Dict:
    """Agents 1-3: parse -> analyze -> classify."""
    state = empty_state(filename)
    return dict(get_graph(False).invoke(state))


def run_pipeline_full(filename: str) -> Dict:
    """Agents 1-6, then assemble the final report."""
    from . import report as report_mod

    state = dict(get_graph(True).invoke(empty_state(filename)))
    return {"state": state, "report": report_mod.assemble_report(state)}


if __name__ == "__main__":
    import pathlib

    sample = pathlib.Path(__file__).resolve().parents[1] / "sample_docs" / "sample_requirement.txt"
    print(run_pipeline_partial(str(sample)))
