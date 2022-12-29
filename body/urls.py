from django.urls import path
from . import views

urlpatterns = [
    path("", views.bodys, name="bodys"),
    path("new", views.new_body, name="new-body"),
    path("edit/<int:id>", views.edit_body, name="edit-body"),
    path("delete/<int:id>", views.delete_body, name="delete-body"),
    path("filter_bodys", views.filter_bodys, name="filter-bodys"),
    path("get_bodies", views.get_bodies, name="get-bodies"),
]
