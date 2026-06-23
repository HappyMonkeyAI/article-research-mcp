from article_research.sources.hn import normalize_hit


def test_normalize_hit_story():
    hit = {
        "objectID": "123",
        "title": "Show HN: FastMCP",
        "url": "https://example.com",
        "points": 42,
        "num_comments": 7,
        "created_at_i": 1700000000,
        "author": "alice",
    }
    out = normalize_hit(hit)
    assert out["source"] == "hn"
    assert out["id"] == 123
    assert out["public_reactions_count"] == 42
    assert out["comments_count"] == 7
    assert "example.com" in out["url"]