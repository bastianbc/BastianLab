from django.urls import path
from . import views

urlpatterns = [
    path("", views.accounts, name="accounts"),
    path("new", views.new_account, name="new-account"),
    path("edit/<int:id>", views.edit_account, name="edit-account"),
    path("delete/<int:id>", views.delete_account, name="delete-account"),
    path("filter_accounts", views.filter_accounts, name="filter-accounts"),
    path("reset_password/<int:id>", views.reset_password, name="reset-password"),
]
