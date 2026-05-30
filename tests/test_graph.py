from backend import graph


def test_run_pipeline_partial_merges_agent_outputs(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.agents.parser.parse_document", lambda state: {"raw_text": "Parsed text"})
    monkeypatch.setattr("backend.agents.analyzer.analyze_requirements", lambda state: {"actors": ["User"], "features": ["Register"], "constraints": ["Secure"]})
    monkeypatch.setattr("backend.agents.classifier.classify_requirements", lambda state: {"functional_requirements": ["Register"], "non_functional_requirements": ["Secure"]})

    result = graph.run_pipeline_partial(str(tmp_path / "doc.txt"))

    assert result["raw_text"] == "Parsed text"
    assert result["actors"] == ["User"]
    assert result["features"] == ["Register"]
    assert result["functional_requirements"] == ["Register"]
    assert result["non_functional_requirements"] == ["Secure"]


def test_run_pipeline_full_adds_story_acceptance_risk_and_report(monkeypatch, tmp_path):
    monkeypatch.setattr("backend.agents.parser.parse_document", lambda state: {"raw_text": "Parsed text"})
    monkeypatch.setattr("backend.agents.analyzer.analyze_requirements", lambda state: {"actors": ["User"], "features": ["Register"], "constraints": ["Secure"]})
    monkeypatch.setattr("backend.agents.classifier.classify_requirements", lambda state: {"functional_requirements": ["Register"], "non_functional_requirements": ["Secure"]})
    monkeypatch.setattr("backend.agents.story_generator.generate_user_stories", lambda state: {"user_stories": [{"feature": "Register", "story": "As a user, I want to register", "priority": "High"}]})
    monkeypatch.setattr("backend.agents.acceptance.generate_acceptance_criteria", lambda state: {"acceptance_criteria": [{"story_ref": "As a user, I want to register", "given": "Given a user", "when": "When they submit", "then": "Then they can register"}]})
    monkeypatch.setattr("backend.agents.risk_detector.detect_risks_ambiguity", lambda state: {"risks": [{"requirement": "Secure", "reason": "vague", "suggestion": "Specify security controls"}], "ambiguities": [{"requirement": "Secure", "reason": "vague", "suggestion": "Specify security controls"}]})
    monkeypatch.setattr("backend.report.assemble_report", lambda state: {"executive_summary": "Summary", "functional_requirements": state["functional_requirements"], "non_functional_requirements": state["non_functional_requirements"], "user_stories": state["user_stories"], "acceptance_criteria": state["acceptance_criteria"], "risks": state["risks"], "ambiguities": state["ambiguities"], "suggestions": ["Specify security controls"], "errors": state["errors"]})

    result = graph.run_pipeline_full(str(tmp_path / "doc.txt"))

    assert result["state"]["user_stories"][0]["story"] == "As a user, I want to register"
    assert result["report"]["executive_summary"] == "Summary"
    assert result["report"]["suggestions"] == ["Specify security controls"]
