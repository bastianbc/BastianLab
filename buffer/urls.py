from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.buffers, name="buffers"),
    path("new", views.new_buffer, name="new-buffer"),
    path("edit/<int:id>", views.edit_buffer, name="edit-buffer"),
    path("delete/<int:id>", views.delete_buffer, name="delete-buffer"),
    path("filter_buffers", views.filter_buffers, name="filter-buffers"),
    path("get_buffer_choices", views.get_buffer_choices, name="get-buffer-choices"),
] + staticfiles_urlpatterns()
