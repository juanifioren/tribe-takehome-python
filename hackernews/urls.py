from django.urls import path

from . import views, load

urlpatterns = [
    path("", views.index, name="index"),
    path("item/<int:item_id>", views.item, name="item"),
    path("items", views.items, name="items"),
    path("users", views.users, name="users"),
    path("load", load.load_items_from_hackernews, name="load"),
]
