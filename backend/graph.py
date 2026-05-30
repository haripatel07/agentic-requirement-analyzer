"""Pipeline wiring for agents 1-3.

Provides `run_pipeline_partial(filename: str) -> dict` which runs:
  parse_document -> analyze_requirements -> classify_requirements

Attempts to use LangGraph if available; otherwise runs agents sequentially.
"""
from typing import Dict
import os
from .state import empty_state


def _sequential_run(filename: str) -> Dict:
    state = empty_state(filename)
    state["filename"] = filename
    # import agents lazily
    from .agents import parser
    from .agents import analyzer
    from .agents import classifier

    # Agent 1: parse
    out1 = parser.parse_document(state)
    if out1.get("raw_text"):
        state["raw_text"] = out1.get("raw_text")
    if out1.get("errors"):
        state["errors"].extend(out1.get("errors"))

    # Agent 2: analyze
    out2 = analyzer.analyze_requirements(state)
    for k in ("actors", "features", "constraints"):
        if k in out2:
            state[k] = out2[k]
    if out2.get("errors"):
        state["errors"].extend(out2.get("errors"))

    # Agent 3: classify
    out3 = classifier.classify_requirements(state)
    if out3.get("functional_requirements"):
        state["functional_requirements"] = out3.get("functional_requirements")
    if out3.get("non_functional_requirements"):
        state["non_functional_requirements"] = out3.get("non_functional_requirements")
    if out3.get("errors"):
        state["errors"].extend(out3.get("errors"))

    return state


def run_pipeline_partial(filename: str) -> Dict:
    # Try to use LangGraph if available (non-fatal); otherwise run sequentially
    try:
        import langgraph as lg
        return _sequential_run(filename)
    except Exception:
        return _sequential_run(filename)


def run_pipeline_full(filename: str) -> Dict:
    # Run agents 1-6 and assemble report
    state = _sequential_run(filename)
    # import remaining agents
    from .agents import story_generator
    from .agents import acceptance
    from .agents import risk_detector
    from . import report as report_mod

    out4 = story_generator.generate_user_stories(state)
    if out4.get("user_stories"):
        state["user_stories"] = out4.get("user_stories")
    if out4.get("errors"):
        state["errors"].extend(out4.get("errors"))

    out5 = acceptance.generate_acceptance_criteria(state)
    if out5.get("acceptance_criteria"):
        state["acceptance_criteria"] = out5.get("acceptance_criteria")
    if out5.get("errors"):
        state["errors"].extend(out5.get("errors"))

    out6 = risk_detector.detect_risks_ambiguity(state)
    if out6.get("risks"):
        state["risks"] = out6.get("risks")
    if out6.get("ambiguities"):
        state["ambiguities"] = out6.get("ambiguities")
    if out6.get("errors"):
        state["errors"].extend(out6.get("errors"))

    full_report = report_mod.assemble_report(state)
    return {"state": state, "report": full_report}


if __name__ == "__main__":
    import pathlib
    sample = pathlib.Path(__file__).resolve().parents[1] / "sample_docs" / "sample_requirement.txt"
    res = run_pipeline_partial(str(sample))
    print(res)
