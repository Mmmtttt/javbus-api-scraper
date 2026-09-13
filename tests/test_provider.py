from __future__ import annotations

from ultimate_provider import JavbusProvider


class FakeAdapter:
    def search_videos(self, keyword, page=1, max_pages=1):
        return {"keyword": keyword, "page": page, "max_pages": max_pages}

    def get_video_detail(self, video_id):
        return {"video_id": video_id}

    def search_actor(self, actor_name):
        return [{"actor_name": actor_name}]

    def get_actor_works(self, actor_id, page=1, max_pages=1):
        return {"actor_id": actor_id, "page": page, "max_pages": max_pages}


def test_provider_maps_protocol_capabilities_to_adapter(monkeypatch):
    provider = JavbusProvider()
    monkeypatch.setattr(provider, "_get_adapter", lambda params: FakeAdapter())

    assert provider.execute("catalog.search", {"keyword": "ABP", "page": 2, "max_pages": 3}, {}, {}) == {
        "keyword": "ABP", "page": 2, "max_pages": 3
    }
    assert provider.execute("catalog.detail", {"video_id": "ABP-123"}, {}, {}) == {"video_id": "ABP-123"}
    assert provider.execute("person.search", {"actor_name": "Alice"}, {}, {}) == [{"actor_name": "Alice"}]
    assert provider.execute("person.works", {"actor_id": "star-1", "page": 2, "max_pages": 4}, {}, {}) == {
        "actor_id": "star-1", "page": 2, "max_pages": 4
    }


def test_provider_health_reflects_enabled_configuration():
    provider = JavbusProvider()

    assert provider.execute("health.query.status", {}, {}, {"enabled": True})["configured"] is True
    assert provider.execute("health.query.status", {}, {}, {"enabled": False})["configured"] is False
