from article_research.sources.rss import _parse_feed_xml, _entry_id


RSS_SAMPLE = """<?xml version="1.0"?>
<rss><channel>
<item>
  <title>Hello MCP</title>
  <link>https://example.com/post/1</link>
  <description>About model context protocol</description>
  <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
</item>
</channel></rss>"""


def test_parse_rss_item():
    entries = _parse_feed_xml(RSS_SAMPLE, "https://feed.test/rss")
    assert len(entries) == 1
    assert entries[0]["source"] == "rss"
    assert entries[0]["title"] == "Hello MCP"
    assert entries[0]["url"] == "https://example.com/post/1"
    assert entries[0]["id"] == _entry_id("https://example.com/post/1")