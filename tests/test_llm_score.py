from article_research.pipeline.llm_score import _parse_scores_json, llm_scoring_enabled


def test_parse_scores_json():
    text = 'Here are scores: {"123": 8.5, "456": 3}'
    scores = _parse_scores_json(text)
    assert scores["123"] == 8.5
    assert scores["456"] == 3.0


def test_llm_disabled_without_env(monkeypatch):
    monkeypatch.delenv("OPENAI_COMPAT_BASE_URL", raising=False)
    assert llm_scoring_enabled() is False