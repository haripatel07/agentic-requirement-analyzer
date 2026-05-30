from backend.state import empty_state


def test_empty_state_has_expected_defaults():
    state = empty_state("example.txt")

    assert state["filename"] == "example.txt"
    assert state["raw_text"] == ""
    assert state["actors"] == []
    assert state["features"] == []
    assert state["constraints"] == []
    assert state["functional_requirements"] == []
    assert state["non_functional_requirements"] == []
    assert state["user_stories"] == []
    assert state["acceptance_criteria"] == []
    assert state["risks"] == []
    assert state["ambiguities"] == []
    assert state["errors"] == []
