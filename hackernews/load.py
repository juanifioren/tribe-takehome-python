import json

from django.http import HttpRequest
from django.http.response import HttpResponseBase


def load_items_from_hackernews(request: HttpRequest) -> HttpResponseBase:
    """
    Accepts a POST request with Content-Type: application/json
    and a json object with the following structure:
    {
      "type": (str), type of HackerNews API request: new|top|best
      "limit": (int), optionally only save up to this many items (default of 0 means save all items returned by HN)
    }

    Saves items from the HackerNews API into the local database, and returns json indicating
    how many items were saved in the following structure:
    {
      "saved": (int), number of items saved to the database
    }
    """
    #  NOTE: we recommend using requests.get() to call the HN API.  If you choose to use something else,
    #        you'll need to update the mock patch in test_load.py correspondingly.
    #  Once you've constructed an Item (from hackernews.models import Item) instance, calling item.save()
    #  will persist to the database
    data = json.loads(request.body) if request.body else {}  # load json POST data
    raise NotImplementedError("TODO: implement!")
