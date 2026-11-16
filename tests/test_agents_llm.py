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
                "given": "valid credentials",
                "when": "I submit",
                "then": "I am logged in",
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


def test_acceptance_labels_are_stripped_so_ui_adds_them_once():
    assert acceptance._strip_label("Given valid credentials") == "valid credentials"
    assert acceptance._strip_label("when I submit") == "I submit"
    assert acceptance._strip_label("Then: I am logged in") == "I am logged in"
    assert acceptance._strip_label("a user is Given access") == "a user is Given access"


def test_risk_detector_populates_risks_separately_from_ambiguities(monkeypatch):
    monkeypatch.setattr(risk_detector, "_embed_model", None)
    monkeypatch.setattr(risk_detector, "_call_groq", lambda prompt: (_ for _ in ()).throw(RuntimeError("no llm")))

    result = risk_detector.detect_risks_ambiguity({
        "functional_requirements": ["Patients must log in with a password"],
        "non_functional_requirements": ["System should be fast"],
    })

    assert any("password" in r["requirement"] for r in result["risks"])
    assert any("fast" in a["requirement"] for a in result["ambiguities"])


def test_acceptance_generator_batches_stories_and_survives_a_failed_batch(monkeypatch):
    monkeypatch.setattr(acceptance, "BATCH_SIZE", 1)
    monkeypatch.setattr(acceptance.time, "sleep", lambda s: None)
    calls = []

    def fake(prompt):
        calls.append(prompt)
        if "story B" in prompt:
            return "not json"
        return '{"acceptance_criteria": [{"story_ref": "r", "given": "g%d", "when": "w", "then": "t"}]}' % len(calls)

    monkeypatch.setattr(acceptance, "_call_groq", fake)
    stories = [{"story": "story A"}, {"story": "story B"}, {"story": "story C"}]

    result = acceptance.generate_acceptance_criteria({"raw_text": "", "user_stories": stories})

    assert len(result["acceptance_criteria"]) == 2
    assert result["errors"]
