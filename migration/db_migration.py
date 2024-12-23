from django.db import connections
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

# Tables to copy
TABLES_TO_COPY = [
    ("auth.Group", "labdb"),
    ("auth.Permission", "labdb"),
    ("auth.User", "labdb"),
]

RELATED_TABLES = [
    ("auth.User.groups.through", "labdb"),
    ("auth.User.user_permissions.through", "labdb"),
    ("auth.Group.permissions.through", "labdb"),
]

def copy_table_data(model_name, source_db, target_db="default"):
    """
    Copies data from source_db to target_db for the given model.
    """
    print(f"Copying data for {model_name} from {source_db} to {target_db}...")
    model = None

    try:
        # Fetch model
        app_label, model_name = model_name.split(".", 1)
        model = apps.get_model(app_label, model_name)

        # Fetch source data
        source_objects = model.objects.using(source_db).all()

        with transaction.atomic(using=target_db):
            for obj in source_objects:
                obj.reset_primary_key()
                obj.save(using=target_db)

        print(f"Successfully copied {source_objects.count()} records.")

    except Exception as e:
        print(f"Error copying {model_name}: {e}")

def run():
    print("Starting migration script...")

    # Add your data migration logic here
    # For example:
    print("start")
    copy_table_data()
    print("end")



