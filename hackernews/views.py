from django.forms import model_to_dict
from django.http import HttpRequest
from django.http.response import HttpResponseBase, JsonResponse
from django.shortcuts import redirect

from hackernews.models import Item


def index(request: HttpRequest) -> HttpResponseBase:
    """
    Redirect any requests that don't specify an endpoint to the `items` endpoint
    """
    return redirect("/hackernews/items")


def item(request: HttpRequest, item_id: int) -> HttpResponseBase:
    """
    Return json representing the item with passed in id in the following structure:
    {
      "id": (int), HackerNews API id
      "author": (str), username of the item's author
      "time": (str), ISO-8601 formatted timestamp of the item's creation date/time
      "score": (int), score of the item
      "title": (str), title of the item
      "url": (str), URL of the item
      "type": (str), type of the item, generally a "story"
    }
    If there is no item with the passed in id, return a 404

    This method is implemented to illustrate different ways of accessing
    the database in django, as well as simple ways to get HTTP parameters
    and return a json response with a given status.
    """
    # Example of getting query parameter values:
    raw_sql = bool(request.GET.get("raw_sql", False))
    filter_in_memory = bool(request.GET.get("filter_in_memory", False))

    if not filter_in_memory and not raw_sql:
        # Can use django QuerySet functionality to find the item by id in the database:
        # ( https://docs.djangoproject.com/en/3.2/ref/models/querysets/ )
        data_list = Item.objects.filter(id=item_id)
    elif not raw_sql:
        # or load all items and filter in python
        data_list = [i for i in Item.objects.all() if i.id == item_id]
    else:
        # or use raw sql to do the same:
        data_list = Item.objects.raw(
            "select id,author,time,score,title,url,type from hackernews_item where id = %s",
            [item_id],
        )
    # Then can translate to a json response:
    data = data_list[0] if len(data_list) == 1 else None
    if data:
        json_data = model_to_dict(data)
        status = 200
    else:
        json_data = {"message": f"item {item_id} not found"}
        status = 404
    return JsonResponse(data=json_data, status=status)


def items(request: HttpRequest) -> HttpResponseBase:
    """
    Should accept optional `page` and `limit` query parameters to control pagination.
    Return json representing a paginated list of all items in the database, with each item
    in the same format as `item`:
    {
      "next_page": (str|None), page to request to get the next paginated list of items, if this is not the last page
      "items": [{
        "id": (int), HackerNews API id
        "author": (str), username of the item's author
        "time": (str), ISO-8601 formatted timestamp of the item's creation date/time
        "score": (int), score of the item
        "title": (str), title of the item
        "url": (str), URL of the item
        "type": (str), type of the item, generally a "story"
      }]
    }
    """
    raise NotImplementedError("TODO: implement!")


def users(request: HttpRequest) -> HttpResponseBase:
    """
    Should accept optional `page` and `limit` query parameters to control pagination.
    Return json representing a paginated list of aggregated information about the users
    who authored items in the database, in the following structure:
    {
      "next_page": (str|None), page to request to get the next paginated list of items, if this is not the last page
      "users": [{
        "name": (str), username
        "item_count": (int), number of items authored by the user
        "score": (int), aggregate score (summed) of all items authored by the user
      }]
    }
    """
    raise NotImplementedError("TODO: implement!")
