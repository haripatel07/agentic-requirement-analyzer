from backend.agents import analyzer, classifier, story_generator, acceptance, risk_detector


def test_analyzer_parses_json_response(monkeypatch):
    monkeypatch.setattr(analyzer, "_call_groq", lambda prompt: '{"actors": ["User"], "features": ["Register"], "constraints": ["Must be secure"]}')

    result = analyzer.analyze_requirements({"raw_text": "dummy"})

    assert result == {"actors": ["User"], "features": ["Register"], "constraints": ["Must be secure"]}


def test_classifier_parses_json_response(monkeypatch):
    monkeypatch.setattr(classifier, "_call_groq", lambda prompt: '{"functional_requirements": ["Login"], "non_functional_requirements": ["Fast response"]}')

    result = classifier.classify_requirements({"raw_text": "dummy", "features": ["Login"], "constraints": ["Fast response"]})

    assert result == {"functional_requirements": ["Login"], "non_functional_requirements": ["Fast response"]}


def test_story_generator_parses_json_response(monkeypatch):
    monkeypatch.setattr(story_generator, "_call_groq", lambda prompt: '{"user_stories": [{"feature": "Login", "story": "As a user, I want to log in", "priority": "High"}]}')

    result = story_generator.generate_user_stories({"raw_text": "dummy", "functional_requirements": ["Login"]})

    assert result == {
        "user_stories": [
            {"feature": "Login", "story": "As a user, I want to log in", "priority": "High"}
        ]
    }


def test_acceptance_generator_parses_json_response(monkeypatch):
    monkeypatch.setattr(acceptance, "_call_groq", lambda prompt: '{"acceptance_criteria": [{"story_ref": "As a user, I want to log in", "given": "Given valid credentials", "when": "When I submit", "then": "Then I am logged in"}]}')

    result = acceptance.generate_acceptance_criteria({"raw_text": "dummy", "user_stories": [{"story": "As a user, I want to log in"}]})

    assert result == {
        "acceptance_criteria": [
            {
                "story_ref": "As a user, I want to log in",
                "given": "Given valid credentials",
                "when": "When I submit",
                "then": "Then I am logged in",
            }
        ]
    }


def test_risk_detector_flags_ambiguous_phrase_without_embeddings(monkeypatch):
    monkeypatch.setattr(risk_detector, "_embed_model", None)
    monkeypatch.setattr(risk_detector, "_faiss_index", None)

    result = risk_detector.detect_risks_ambiguity({"functional_requirements": ["Images should load quickly"], "non_functional_requirements": ["System should be scalable"]})

    assert result["risks"] == []
    assert result["errors"] == []
    assert result["ambiguities"]
    assert result["ambiguities"][0]["requirement"] in {"Images should load quickly", "System should be scalable"}
