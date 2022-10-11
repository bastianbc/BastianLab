from django.urls import path
from . import views

urlpatterns = [
    path("", views.methods, name="methods"),
    path("new", views.new_method, name="new-method"),
    path("edit/<int:id>", views.edit_method, name="edit-method"),
    path("delete/<int:id>", views.delete_method, name="delete-method"),
    path("filter_methods", views.filter_methods, name="filter-methods"),
]
