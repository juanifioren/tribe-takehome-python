from django.db import models


class Item(models.Model):
    """
    A model representing a HackerNews item.
    The primary key should be set to the id of the item in the HackerNews API.
    The `author` field should be the username of the item's author (returned as `by` in the HackerNews API).
    The `time` field should be stored as a UTC datetime in the database.
    The `score` field should be the item's score.
    The `title` field should be the item's title.
    The `url` field should be the item's URL.
    The `type` field should be the item's type
        ("job", "story", "comment", "poll", or "pollopt"), and will generally be "story".
    """

    author = models.CharField(max_length=1024)
    time = models.DateTimeField()
    score = models.IntegerField()
    title = models.CharField(max_length=1024)
    url = models.CharField(max_length=1024)
    type = models.CharField(max_length=1024)
