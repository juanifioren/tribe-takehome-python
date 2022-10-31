from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from enum import Enum
import json

from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.http.response import HttpResponseBase, JsonResponse
from django.views.decorators.http import require_http_methods
import pytz
import requests

from hackernews.models import Item


class ItemsType(Enum):
    NEW = 'new'
    TOP = 'top'
    BEST = 'best'


def get_item_from_hackernews(item_id):
    try:
        api_response = requests.get(settings.HN_API_URL + 'item/{0}.json'.format(item_id))
    except requests.exceptions.SSLError as e:
        return

    if api_response.ok:
        item_data = api_response.json()
        return item_data


@require_http_methods(['POST'])
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
    try:
        data = json.loads(request.body) if request.body else {}  # load json POST data
    except json.JSONDecodeError:
        return JsonResponse(data={'message': 'invalid data.'}, status=400)

    if not data.get('type') in [t.value for t in ItemsType]:
        return JsonResponse(data={'message': 'invalid or missing type.'}, status=400)

    limit = data.get('limit')
    if limit and not isinstance(limit, int):
        return JsonResponse(data={'message': 'invalid limit.'}, status=400)

    api_response = requests.get(settings.HN_API_URL + '{0}stories.json'.format(data['type']))

    if api_response.ok:
        items_ids = api_response.json()
        if limit:
            items_ids = items_ids[:limit]

        # Send batched requests to get items data concurrently.
        processes = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            for item_id in items_ids:
                processes.append(executor.submit(get_item_from_hackernews, item_id))

        # Update or create all items in one db commit.
        saved_count = 0
        with transaction.atomic():
            for task in as_completed(processes):
                item_data = task.result()
                if not item_data:
                    continue
                obj, created = Item.objects.update_or_create(id=item_data['id'], defaults={
                    'author': item_data['by'],
                    'time': datetime.fromtimestamp(item_data['time'], pytz.timezone('UTC')),
                    'score': item_data.get('score', ''),
                    'title': item_data.get('title', ''),
                    'url': item_data.get('url', ''),
                    'type': item_data['type'],
                })
                saved_count += 1

    return JsonResponse(data={'saved': saved_count}, status=200)
