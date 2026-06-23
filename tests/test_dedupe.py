from article_research.pipeline.dedupe import dedupe_articles


def test_dedupe_by_url():
    items = [
        {"title": "A", "url": "https://dev.to/x/1"},
        {"title": "B", "url": "https://dev.to/x/1/"},
        {"title": "C", "url": "https://dev.to/y/2"},
    ]
    out = dedupe_articles(items)
    assert len(out) == 2
    assert out[0]["title"] == "A"
    assert out[1]["title"] == "C"