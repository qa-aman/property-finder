from property_finder.infrastructure.places import GooglePlacesAdapter


def _geocode_response():
    return {"results": [{"geometry": {"location": {"lat": 19.1, "lng": 72.8}}}]}


def _places(names):
    return {"places": [{"displayName": {"text": n}} for n in names]}


def test_find_societies_uses_nearby_when_enough(httpx_mock):
    httpx_mock.add_response(method="GET", json=_geocode_response())  # geocode
    httpx_mock.add_response(method="POST",
                            json=_places(["A Heights", "B Residency", "C Greens"]))  # nearby

    adapter = GooglePlacesAdapter("key")
    out = adapter.find_societies("Andheri", "Mumbai")

    assert out == ["A Heights", "B Residency", "C Greens"]


def test_falls_back_to_text_search_when_thin(httpx_mock):
    httpx_mock.add_response(method="GET", json=_geocode_response())  # geocode
    httpx_mock.add_response(method="POST", json=_places(["Only One"]))  # nearby (< 2)
    httpx_mock.add_response(method="POST",
                            json=_places(["Only One", "Text Two", "Text Three"]))  # text

    adapter = GooglePlacesAdapter("key")
    out = adapter.find_societies("Andheri", "Mumbai")

    # Deduplicated merge of nearby + text results.
    assert out == ["Only One", "Text Two", "Text Three"]


def test_no_geocode_match_returns_text_search_only(httpx_mock):
    httpx_mock.add_response(method="GET", json={"results": []})  # geocode misses
    httpx_mock.add_response(method="POST", json=_places(["Text One", "Text Two"]))  # text

    adapter = GooglePlacesAdapter("key")
    out = adapter.find_societies("Nowhere", "Mumbai")

    assert out == ["Text One", "Text Two"]
