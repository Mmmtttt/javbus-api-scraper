from __future__ import annotations

from types import SimpleNamespace

from lib.javbus_adapter import JavbusAdapter


def test_parse_movie_item_normalizes_urls_and_fields():
    adapter = JavbusAdapter()
    item = adapter._parse_movie_item(
        SimpleNamespace(
            select_one=lambda selector: {
                ".photo-frame img": SimpleNamespace(get=lambda key, default="": {"src": "//img.example/cover.jpg", "title": "Example title"}.get(key, default)),
                "a": SimpleNamespace(get=lambda key, default="": "/ABP-123" if key == "href" else default),
            }.get(selector),
            select=lambda selector: {
                ".photo-info date": [SimpleNamespace(text="ABP-123"), SimpleNamespace(text="2026-01-02")],
                ".item-tag button": [SimpleNamespace(text="字幕")],
            }.get(selector, []),
        )
    )

    assert item == {
        "video_id": "ABP-123",
        "code": "ABP-123",
        "title": "Example title",
        "date": "2026-01-02",
        "tags": ["字幕"],
        "actors": [],
        "cover_url": "https://img.example/cover.jpg",
        "thumbnail_url": "https://img.example/cover.jpg",
        "rating": "",
    }


def test_search_videos_forwards_pages_and_stops_after_requested_page(monkeypatch):
    adapter = JavbusAdapter()
    responses = [
        SimpleNamespace(
            text='<div id="waterfall"><div class="item"></div></div><ul class="pagination"><li><a id="next">next</a></li></ul>',
            raise_for_status=lambda: None,
        ),
        SimpleNamespace(
            text='<div id="waterfall"><div class="item"></div></div>',
            raise_for_status=lambda: None,
        ),
    ]
    urls = []
    monkeypatch.setattr(adapter, "_get", lambda url: urls.append(url) or responses.pop(0))
    monkeypatch.setattr(adapter, "_parse_movie_item", lambda item: {"video_id": "ABP-123"})
    monkeypatch.setattr("lib.javbus_adapter.time.sleep", lambda _seconds: None)

    result = adapter.search_videos("ABP", page=1, max_pages=2)

    assert urls == ["https://www.javbus.com/search/ABP?type=1", "https://www.javbus.com/search/ABP/2?type=1"]
    assert result["page"] == 1
    assert result["has_next"] is False
    assert result["videos"] == [{"video_id": "ABP-123"}, {"video_id": "ABP-123"}]


def test_get_video_detail_parses_core_fields_and_actor_links(monkeypatch):
    adapter = JavbusAdapter()

    html = """
    <div class="container">
      <h3>Fixture title</h3>
      <div class="movie">
        <a class="bigImage" href="//img.example/full.jpg"><img src="/small.jpg"></a>
        <div class="info">
          <p><span class="header">發行日期:</span> 2026-01-02</p>
          <p><span class="header">長度:</span> 120分鐘</p>
          <p class="genre"><label><a href="/genre/action">Action</a></label></p>
          <p class="genre" onmouseover="fixture"><a href="/star/actor-1">Fixture Actor</a></p>
        </div>
      </div>
    </div>
    """

    monkeypatch.setattr(adapter, "_get", lambda url: SimpleNamespace(text=html, raise_for_status=lambda: None))
    monkeypatch.setattr(adapter, "_get_actor_avatar", lambda *args, **kwargs: None)

    result = adapter.get_video_detail("FIX-001")

    assert result["video_id"] == "FIX-001"
    assert result["title"] == "Fixture title"
    assert result["cover_url"] == "https://img.example/full.jpg"
    assert result["date"] == "2026-01-02"
    assert result["video_length"] == 120
    assert result["actors"] == ["Fixture Actor"]
    assert result["actors_detail"][0]["id"] == "actor-1"
