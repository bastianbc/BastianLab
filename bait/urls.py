from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("", views.baits, name="baits"),
    path("new", views.new_bait, name="new-bait"),
    path("edit/<int:id>", views.edit_bait, name="edit-bait"),
    path("delete/<int:id>", views.delete_bait, name="delete-bait"),
    path("filter_baits", views.filter_baits, name="filter-baits"),
    path("get_bait_choices", views.get_bait_choices, name="get-bait-choices"),
] + staticfiles_urlpatterns()
