from django.urls import path
from django.conf import settings
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    path("train_story_documents", views.train_story_documents, name="train_story_documents"),

] + staticfiles_urlpatterns()
