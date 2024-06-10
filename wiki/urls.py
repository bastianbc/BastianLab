from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.articles, name="articles"),
    path("new", views.new_article, name="new-article"),
    path("<str:slug>", views.view_article, name="view-article"),
    path("<str:slug>/edit", views.edit_article, name="edit-article"),
    path("<str:slug>/delete", views.delete_article, name="delete-article"),
] + staticfiles_urlpatterns()
