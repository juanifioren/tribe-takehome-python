import json
import re
from unittest.mock import patch

from django.test import TestCase, Client

from hackernews.models import Item


def mock_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, code, data):
            self.data = data
            self.status_code = code
            self.text = json.dumps(data)
            self.encoding = "utf-8"
            self.content = bytes(self.text, self.encoding)
            self.ok = self.status_code < 400

        def json(self):
            return self.data

    url = kwargs.get("url") or args[0]

    if url.endswith("topstories.json"):
        return MockResponse(200, [1, 2, 3])
    elif url.endswith("beststories.json"):
        return MockResponse(200, [3, 4, 5, 6])
    elif url.endswith("newstories.json"):
        return MockResponse(200, [0, 7, 8, 9])
    # only matches items 1-9, item 0 will 404
    elif match := re.match(".*/([1-9])\\.json$", url):
        story_id = match.group(1)
        return MockResponse(
            200,
            {
                "id": story_id,
                "by": f"user{story_id}",
                "score": int(story_id) * 10,
                "time": 1175714200,
                "title": f"title {story_id}",
                "type": "story",
                "url": f"https://cool_story.com/{story_id}",
            },
        )
    return MockResponse(404, None)


@patch("hackernews.load.requests.get", side_effect=mock_requests_get)
class LoadTests(TestCase):
    """
    Tests of loading items from HackerNews.  Starts with an empty database for each test.
    requests.get() is mocked to support calls to topstories.json, beststories.json,
    newstories.json, and item/<item-id>.json hackernews endpoints.  If using a mechanism
    other than requests.get() to implement loading, you may need to update the patch
    decoration above.
    """

    fixtures = []
    test_client = Client()

    def test_load_top(self, requests_get_mock):
        """
        Test that loading with type=top inserts items 1, 2 and 3
        """
        response = self.test_client.post(
            "/hackernews/load", {"type": "top"}, content_type="application/json"
        )
        self.assertEquals(response.json()["saved"], 3)
        in_db = Item.objects.all()
        self.assertEquals(len(in_db), 3)
        self.assertEquals([i.id for i in in_db], [1, 2, 3])

    def test_load_top_two(self, requests_get_mock):
        """
        Test that loading with type=top, limit=2 inserts items 1 and 2
        """
        response = self.test_client.post(
            "/hackernews/load",
            {"type": "top", "limit": 2},
            content_type="application/json",
        )
        self.assertEquals(response.json()["saved"], 2)
        in_db = Item.objects.all()
        self.assertEquals(len(in_db), 2)
        self.assertEquals([i.id for i in in_db], [1, 2])

    def test_load_best(self, requests_get_mock):
        """
        Test that loading with type=best inserts items 3, 4, 5 and 6
        """
        response = self.test_client.post(
            "/hackernews/load", {"type": "best"}, content_type="application/json"
        )
        self.assertEquals(response.json()["saved"], 4)
        in_db = Item.objects.all()
        self.assertEquals(len(in_db), 4)
        self.assertEquals([i.id for i in in_db], [3, 4, 5, 6])

    def test_load_new(self, requests_get_mock):
        """
        Test that loading with type=new inserts items 7, 8 and 9, and
        loading is not broken by item 0's error state
        """
        response = self.test_client.post(
            "/hackernews/load", {"type": "new"}, content_type="application/json"
        )
        self.assertEquals(response.json()["saved"], 3)
        in_db = Item.objects.all()
        self.assertEquals(len(in_db), 3)
        self.assertEquals([i.id for i in in_db], [7, 8, 9])

    def test_load_top_and_best(self, requests_get_mock):
        """
        Test that loading with type=top, then type=best inserts items 1 through 6,
        without duplicating item 3 which exists in both types
        """
        response = self.test_client.post(
            "/hackernews/load", {"type": "top"}, content_type="application/json"
        )
        self.assertEquals(response.json()["saved"], 3)
        response = self.test_client.post(
            "/hackernews/load", {"type": "best"}, content_type="application/json"
        )
        self.assertEquals(response.json()["saved"], 4)
        in_db = Item.objects.all()
        self.assertEquals(len(in_db), 6)
        self.assertEquals([i.id for i in in_db], [1, 2, 3, 4, 5, 6])
