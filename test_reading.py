from reading import build_prompt, is_grounded, cited_ids

TWINS = [{"date": "1969-07-20", "score": 0.95,
          "events": [{"text": "Apollo 11 lands on the Moon", "page_title": "", "url": ""}]}]

def test_prompt_assigns_ids():
    _, ids = build_prompt("2000-01-01", TWINS)
    assert ids == {"E1"}

def test_grounded_reading_passes():
    assert is_grounded("A bold day [E1].", {"E1"})

def test_invented_citation_fails():
    assert not is_grounded("Something happened [E9].", {"E1"})

def test_no_citations_fails():
    assert not is_grounded("Vibes only.", {"E1"})

def test_cited_ids():
    assert cited_ids("see [E1] and [E3]") == {"E1", "E3"}