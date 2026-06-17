from backend import report


def test_assemble_report_aggregates_sections(monkeypatch):
    monkeypatch.setattr(report, "_call_groq_for_summary", lambda text: "Summary sentence one. Summary sentence two.")

    state = {
        "raw_text": "A requirements doc.",
        "functional_requirements": ["Login"],
        "non_functional_requirements": ["Fast response"],
        "user_stories": [{"feature": "Login", "story": "As a user, I want to log in", "priority": "High"}],
        "acceptance_criteria": [{"story_ref": "As a user, I want to log in", "given": "Given...", "when": "When...", "then": "Then..."}],
        "risks": [{"requirement": "Fast response", "reason": "vague", "suggestion": "Specify a threshold"}],
        "ambiguities": [{"requirement": "Login", "reason": "unclear", "suggestion": "Define auth method"}],
        "errors": ["minor issue"],
    }

    result = report.assemble_report(state)

    assert result["executive_summary"].startswith("Summary sentence one")
    assert result["functional_requirements"] == ["Login"]
    assert result["non_functional_requirements"] == ["Fast response"]
    assert result["suggestions"] == ["Define auth method", "Specify a threshold"]
    assert result["errors"] == ["minor issue"]
