from django.test import TestCase, Client


class ViewTests(TestCase):
    """
    Test cases of read-only view endpoints that read data
    from unmodified fixtures
    """

    fixtures = ["items.json"]
    test_client = Client()

    def test_index(self):
        """
        Test that the index redirects to the items endpoint
        """
        response = self.test_client.get("/hackernews")
        # follow any intermediate redirects
        while (
            response.headers["Location"]
            and response.headers["Location"] != "/hackernews/items"
        ):
            response = self.test_client.get(response.headers["Location"])
        self.assertGreater(response.status_code, 300)
        self.assertLess(response.status_code, 400)
        self.assertEquals(response.headers["Location"], "/hackernews/items")

    def test_successful_lookup(self):
        """
        Test that a simple item lookup returns json in the correct format
        """
        response = self.test_client.get("/hackernews/item/1")
        self.assertEquals(response.status_code, 200)
        json = response.json()
        self.assertEquals(json["id"], 1)
        self.assertEquals(json["author"], "abc")
        self.assertEquals(json["score"], 200)
        self.assertEquals(json["title"], "A good post")
        self.assertEquals(json["url"], "https://neato.com/mid_post_url")
        self.assertEquals(json["type"], "story")
        self.assertEquals(json["time"], "2021-06-07T19:39:42Z")

    def test_failed_lookup(self):
        """
        Test that a item lookup returns 404 if there is no corresponding item
        """
        response = self.test_client.get("/hackernews/item/123")
        self.assertEquals(response.status_code, 404)

    def test_list_items(self):
        """
        Test that a list returns all items from fixtures, and that at least
        the first item is in the correct json format
        """
        response = self.test_client.get("/hackernews/items?limit=1")
        self.assertEquals(response.status_code, 200)
        response_json = response.json()
        json = response_json["items"]
        self.assertLessEqual(len(response_json["items"]), 1)
        while response_json["next_page"]:
            response = self.test_client.get(
                f"/hackernews/items?page={response_json['next_page']}&limit=1"
            )
            response_json = response.json()
            json.extend(response_json["items"])
            self.assertLessEqual(len(response_json["items"]), 1)
        self.assertEqual(len(json), 4)
        self.assertEqual([i["id"] for i in json], [1, 2, 3, 4])
        json = json[0]
        self.assertEquals(json["id"], 1)
        self.assertEquals(json["author"], "abc")
        self.assertEquals(json["score"], 200)
        self.assertEquals(json["title"], "A good post")
        self.assertEquals(json["url"], "https://neato.com/mid_post_url")
        self.assertEquals(json["type"], "story")
        self.assertEquals(json["time"], "2021-06-07T19:39:42Z")

    def test_user_aggregation(self):
        """
        Test that user aggregation response calculates the correct item_count and score,
        and returns in the correct json format
        """
        response = self.test_client.get("/hackernews/users?limit=1")
        self.assertEquals(response.status_code, 200)
        response_json = response.json()
        json = response_json["users"]
        self.assertLessEqual(len(response_json["users"]), 1)
        while response_json["next_page"]:
            response = self.test_client.get(
                f"/hackernews/users?page={response_json['next_page']}&limit=1"
            )
            response_json = response.json()
            json.extend(response_json["users"])
            self.assertLessEqual(len(response_json["users"]), 1)
        self.assertEqual(len(json), 2)
        abc_user = [u for u in json if u["name"] == "abc"][0]
        self.assertEqual(abc_user["item_count"], 3)
        self.assertEqual(abc_user["score"], 450)
        cba_user = [u for u in json if u["name"] == "cba"][0]
        self.assertEqual(cba_user["item_count"], 1)
        self.assertEqual(cba_user["score"], 300)
