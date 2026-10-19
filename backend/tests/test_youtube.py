import pytest
from unittest.mock import patch
from backend.services.youtube import (
    extract_youtube_video_id,
    normalize_youtube_url,
    fetch_youtube_metadata,
    fetch_return_youtube_dislike,
    extract_youtube_comments,
)


def test_youtube_url_extraction_valid():
    valid_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtube.com/watch?v=dQw4w9WgXcQ&feature=shared", "dQw4w9WgXcQ"),
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ?t=42", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ]
    for url, expected_id in valid_cases:
        assert extract_youtube_video_id(url) == expected_id, f"Failed on URL: {url}"


def test_youtube_url_extraction_invalid():
    invalid_cases = [
        "",
        "   ",
        "https://example.com/watch?v=dQw4w9WgXcQ",
        "https://vimeo.com/12345678",
        "https://youtube.com/watch?v=short", # < 11 chars
        "https://youtube.com/watch?v=waytoolongvideoid123456",
        "not_a_valid_url_at_all",
        "https://youtube.com/user/channelname",
    ]
    for url in invalid_cases:
        assert extract_youtube_video_id(url) is None, f"Should be invalid: {url}"


def test_normalize_youtube_url():
    assert normalize_youtube_url("dQw4w9WgXcQ") == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@patch("requests.get")
def test_fetch_youtube_metadata_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "title": "Rick Astley - Never Gonna Give You Up",
        "author_name": "Rick Astley",
        "thumbnail_url": "https://example.com/thumb.jpg",
    }
    title, author, thumb = fetch_youtube_metadata("dQw4w9WgXcQ")
    assert title == "Rick Astley - Never Gonna Give You Up"
    assert author == "Rick Astley"
    assert thumb == "https://example.com/thumb.jpg"


@patch("requests.get")
def test_fetch_youtube_metadata_failure(mock_get):
    mock_get.side_effect = Exception("Network timeout")
    title, author, thumb = fetch_youtube_metadata("dQw4w9WgXcQ")
    assert title is None
    assert author is None
    assert "dQw4w9WgXcQ" in thumb


@patch("requests.get")
def test_fetch_return_youtube_dislike_labeling(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": "dQw4w9WgXcQ",
        "likes": 15000000,
        "dislikes": 400000,
        "viewCount": 1500000000,
        "rating": 4.88,
    }
    dislikes_obj, views, likes = fetch_return_youtube_dislike("dQw4w9WgXcQ")
    assert views == 1500000000
    assert likes == 15000000
    assert dislikes_obj is not None
    assert dislikes_obj.is_estimate is True
    assert dislikes_obj.estimated_dislikes == 400000
    assert dislikes_obj.source == "Return YouTube Dislike API"
    assert "Third-party statistical estimate" in dislikes_obj.limitations_note


@patch("backend.services.youtube.YoutubeCommentDownloader")
def test_extract_youtube_comments_disabled(mock_downloader_cls):
    mock_instance = mock_downloader_cls.return_value
    mock_instance.get_comments_from_url.side_effect = Exception("Comments are disabled for this video.")

    items, diag = extract_youtube_comments("dQw4w9WgXcQ", sample_limit=10)
    assert len(items) == 0
    assert diag.retrieved_records_count == 0
    assert diag.usable_text_count == 0
    assert diag.comments_disabled is True
    assert diag.extraction_status == "disabled"
    assert "disabled" in diag.failure_reason.lower()


@patch("backend.services.youtube.YoutubeCommentDownloader")
def test_extract_youtube_comments_empty(mock_downloader_cls):
    mock_instance = mock_downloader_cls.return_value
    mock_instance.get_comments_from_url.return_value = iter([])

    items, diag = extract_youtube_comments("dQw4w9WgXcQ", sample_limit=10)
    assert len(items) == 0
    assert diag.retrieved_records_count == 0
    assert diag.usable_text_count == 0
    assert diag.comments_disabled is False
    assert diag.extraction_status == "empty"
