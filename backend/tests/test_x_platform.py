import pytest
from unittest.mock import patch
from backend.services.x_platform import (
    extract_x_post_id,
    normalize_x_url,
    fetch_x_post_data,
)


def test_x_url_extraction_valid():
    cases = [
        ("https://x.com/jack/status/20", ("20", "jack")),
        ("https://twitter.com/jack/status/20", ("20", "jack")),
        ("https://mobile.twitter.com/user123/status/987654321", ("987654321", "user123")),
        ("https://x.com/i/status/1234567890123456789", ("1234567890123456789", "i")),
        ("20", ("20", None)),
    ]
    for url, expected in cases:
        result = extract_x_post_id(url)
        assert result is not None, f"Failed on URL: {url}"
        assert result[0] == expected[0]
        if expected[1] is not None:
            assert result[1] == expected[1]


def test_x_url_extraction_invalid():
    invalid_cases = [
        "",
        "   ",
        "https://facebook.com/post/123",
        "https://x.com/home",
        "https://twitter.com/explore",
        "https://x.com/user/status/notanumber",
        "not_a_valid_url",
    ]
    for url in invalid_cases:
        assert extract_x_post_id(url) is None, f"Should be invalid: {url}"


def test_normalize_x_url():
    assert normalize_x_url("20", "jack") == "https://x.com/jack/status/20"
    assert normalize_x_url("20", None) == "https://x.com/i/status/20"


@patch("requests.get")
def test_fetch_x_post_data_restricted_replies(mock_get):
    """
    Test when tweet metadata and metrics are accessible, but anonymous replies
    are blocked by platform login walls. Verify truth policy: 0 fabricated replies.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id_str": "20",
        "text": "just setting up my twttr",
        "user": {"name": "Jack", "screen_name": "jack"},
        "favorite_count": 310000,
        "conversation_count": 18000,
        "retweet_count": 120000,
    }

    post_info, engagement, diag, raw_items = fetch_x_post_data("20")

    assert post_info is not None
    assert post_info["author_name"] == "Jack"
    assert post_info["text"] == "just setting up my twttr"

    assert engagement is not None
    assert engagement.likes == 310000
    assert engagement.comments == 18000
    assert engagement.reposts == 120000
    assert engagement.third_party_dislikes is None # strictly None for X

    # Diagnostics verification: NO fabricated sentiment!
    assert len(raw_items) == 0
    assert diag.retrieved_records_count == 0
    assert diag.usable_text_count == 0
    assert diag.extraction_status == "restricted"
    assert "login walls" in diag.failure_reason.lower()


@patch("requests.get")
def test_fetch_x_post_data_with_parent(mock_get):
    """
    Test when syndication data includes accessible parent/thread context.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id_str": "100",
        "text": "Here is the reply tweet",
        "user": {"name": "ReplyAuthor", "screen_name": "reply_user"},
        "favorite_count": 50,
        "conversation_count": 1,
        "parent": {
            "id_str": "99",
            "text": "Great initial question!",
            "user": {"name": "OriginalPoster", "screen_name": "op"},
            "favorite_count": 10,
            "created_at": "2026-10-17T10:00:00Z",
        },
    }

    post_info, engagement, diag, raw_items = fetch_x_post_data("100")
    assert post_info is not None
    assert len(raw_items) == 1
    assert raw_items[0].text == "Great initial question!"
    assert diag.retrieved_records_count == 1
    assert diag.extraction_status == "partial"


@patch("requests.get")
def test_fetch_x_post_not_found(mock_get):
    mock_get.return_value.status_code = 404
    post_info, engagement, diag, raw_items = fetch_x_post_data("999999999")
    assert post_info is None
    assert engagement is None
    assert diag.extraction_status == "error"
    assert "not found" in diag.failure_reason.lower()
